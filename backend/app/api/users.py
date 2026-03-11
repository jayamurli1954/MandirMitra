"""
User Management API
Handles user creation, updates, and management for multi-user support
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.database import get_db
from app.core.temple_context import resolve_temple_id_for_user
from app.core.password_policy import default_policy
from app.core.role_permissions import get_user_role_context, resolve_role_input, assign_role_to_user
from app.core.security import get_current_user, get_password_hash, verify_password
from app.models.user import User

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def _is_admin_user(current_user: User) -> bool:
    return current_user.role in {"admin", "temple_manager"} or bool(current_user.is_superuser)


def _resolve_temple_id(db: Session, current_user: User) -> int | None:
    return resolve_temple_id_for_user(db, current_user, fallback_to_first=True)


def _ensure_user_in_scope(user: User, temple_id: int | None) -> None:
    if temple_id is None:
        return
    if user.temple_id != temple_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


def _serialize_user_response(db: Session, user: User, temple_id: int | None = None) -> dict:
    role_context = get_user_role_context(db, user, temple_id=temple_id)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role,
        "system_role": role_context["system_role"],
        "role_key": role_context["role_key"],
        "role_label": role_context["role_label"],
        "module_permissions": role_context["module_permissions"],
        "action_permissions": role_context["action_permissions"],
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "last_login_at": user.last_login_at,
        "created_at": user.created_at,
    }


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str = "priest_operator"
    is_active: bool = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    current_password: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    system_role: str
    role_key: str
    role_label: str
    module_permissions: dict[str, bool]
    action_permissions: dict[str, bool]
    is_active: bool
    is_superuser: bool
    last_login_at: Optional[str]
    created_at: str


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    if not _is_admin_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create users")

    normalized_email = str(user_data.email).strip().lower()
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    is_valid, error_msg = default_policy.validate(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    temple_id = _resolve_temple_id(db, current_user)

    try:
        system_role, role_key, role_label = resolve_role_input(db, temple_id, user_data.role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    new_user = User(
        email=normalized_email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=system_role,
        is_active=user_data.is_active,
        temple_id=temple_id,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
    )

    db.add(new_user)
    db.flush()
    assign_role_to_user(db, new_user, temple_id, role_key)
    db.commit()
    db.refresh(new_user)

    log_action(
        db=db,
        user=current_user,
        action="CREATE_USER",
        entity_type="User",
        entity_id=new_user.id,
        new_values={
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": system_role,
            "role_key": role_key,
            "role_label": role_label,
        },
        description=f"Created user: {new_user.full_name} ({new_user.email})",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )

    return _serialize_user_response(db, new_user, temple_id=temple_id)


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _is_admin_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view user list")

    query = db.query(User)
    temple_id = _resolve_temple_id(db, current_user)
    if temple_id:
        query = query.filter(User.temple_id == temple_id)

    if role:
        query = query.filter(User.role == role)

    users = query.offset(skip).limit(limit).all()
    return [_serialize_user_response(db, user, temple_id=temple_id) for user in users]


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    temple_id = _resolve_temple_id(db, current_user)
    return _serialize_user_response(db, current_user, temple_id=temple_id)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    temple_id = _resolve_temple_id(db, current_user)
    if current_user.id != user_id:
        if not _is_admin_user(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user")
        _ensure_user_in_scope(user, temple_id)

    return _serialize_user_response(db, user, temple_id=temple_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    old_values = {
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role,
        "is_active": user.is_active,
    }

    is_admin = _is_admin_user(current_user)
    is_own_profile = current_user.id == user_id
    temple_id = _resolve_temple_id(db, current_user)

    if not is_admin and not is_own_profile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

    if is_admin and not is_own_profile:
        _ensure_user_in_scope(user, temple_id)

    if not is_admin:
        if user_data.role is not None or user_data.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change role or active status",
            )

    if user_data.email is not None:
        normalized_email = str(user_data.email).strip().lower()
        existing_user = db.query(User).filter(User.email == normalized_email, User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
        user.email = normalized_email

    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.phone is not None:
        user.phone = user_data.phone
    if is_admin and user_data.role is not None:
        try:
            system_role, role_key, _role_label = resolve_role_input(db, temple_id, user_data.role)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        user.role = system_role
        assign_role_to_user(db, user, temple_id or user.temple_id, role_key)
    if is_admin and user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.password is not None:
        is_valid, error_msg = default_policy.validate(user_data.password)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        if is_own_profile:
            if not user_data.current_password:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is required")
            if not verify_password(user_data.current_password, user.password_hash):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

        user.password_hash = get_password_hash(user_data.password)
        user.last_password_change = datetime.utcnow().isoformat()

    user.updated_at = datetime.utcnow().isoformat()

    db.commit()
    db.refresh(user)

    new_values = {
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role,
        "is_active": user.is_active,
    }

    log_action(
        db=db,
        user=current_user,
        action="UPDATE_USER",
        entity_type="User",
        entity_id=user_id,
        old_values=old_values,
        new_values=new_values,
        description=f"Updated user: {user.full_name} ({user.email})",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )

    return _serialize_user_response(db, user, temple_id=temple_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    if not _is_admin_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete users")

    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    temple_id = _resolve_temple_id(db, current_user)
    _ensure_user_in_scope(user, temple_id)

    user.is_active = False
    user.updated_at = datetime.utcnow().isoformat()

    db.commit()

    log_action(
        db=db,
        user=current_user,
        action="DELETE_USER",
        entity_type="User",
        entity_id=user_id,
        old_values={"is_active": True},
        new_values={"is_active": False},
        description=f"Deactivated user: {user.full_name} ({user.email})",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )

    return None
