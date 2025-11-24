"""
User Management API
Handles user creation, updates, and management for multi-user support
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.core.audit import log_action
from app.core.password_policy import default_policy
from app.models.user import User
from app.models.temple import Temple

router = APIRouter(prefix="/api/v1/users", tags=["users"])


# ===== SCHEMAS =====

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str = "staff"  # admin, staff, clerk, accountant, priest
    is_active: bool = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None  # For password change

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    is_superuser: bool
    last_login_at: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


# ===== USER MANAGEMENT =====

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """
    Create a new user (admin only)
    For standalone: Creates clerk1, clerk2, clerk3, etc.
    """
    # Only admin can create users
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Validate password policy
    is_valid, error_msg = default_policy.validate(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Get temple_id (for standalone, use current user's temple_id)
    temple_id = current_user.temple_id
    
    # Create user
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        is_active=user_data.is_active,
        temple_id=temple_id,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Audit log
    log_action(
        db=db,
        user=current_user,
        action="CREATE_USER",
        entity_type="User",
        entity_id=new_user.id,
        new_values={
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role
        },
        description=f"Created user: {new_user.full_name} ({new_user.email})",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return new_user


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all users (admin only)
    """
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view user list"
        )
    
    query = db.query(User)
    
    # Filter by temple in standalone mode
    if current_user.temple_id:
        query = query.filter(User.temple_id == current_user.temple_id)
    
    # Filter by role if provided
    if role:
        query = query.filter(User.role == role)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current logged-in user's information
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user details (admin only, or own profile)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Users can view their own profile, admins can view any
    if current_user.id != user_id and current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """
    Update user (admin only, or own profile for limited fields)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get old values for audit
    old_values = {
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role,
        "is_active": user.is_active
    }
    
    # Permission check
    is_admin = current_user.role == "admin" or current_user.is_superuser
    is_own_profile = current_user.id == user_id
    
    if not is_admin and not is_own_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Non-admins can only update limited fields
    if not is_admin:
        if user_data.role is not None or user_data.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change role or active status"
            )
    
    # Update fields
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.phone is not None:
        user.phone = user_data.phone
    if is_admin and user_data.role is not None:
        user.role = user_data.role
    if is_admin and user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.password is not None:
        # Validate password policy
        is_valid, error_msg = default_policy.validate(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        user.password_hash = get_password_hash(user_data.password)
        user.last_password_change = datetime.utcnow().isoformat()
    
    user.updated_at = datetime.utcnow().isoformat()
    
    db.commit()
    db.refresh(user)
    
    # Audit log
    new_values = {
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role,
        "is_active": user.is_active
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
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """
    Delete user (admin only, cannot delete self)
    """
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete users"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete (deactivate) instead of hard delete
    user.is_active = False
    user.updated_at = datetime.utcnow().isoformat()
    
    db.commit()
    
    # Audit log
    log_action(
        db=db,
        user=current_user,
        action="DELETE_USER",
        entity_type="User",
        entity_id=user_id,
        old_values={"is_active": True},
        new_values={"is_active": False},
        description=f"Deactivated user: {user.full_name} ({user.email})",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return None

