from typing import Optional

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.models.temple import Temple
from app.models.user import User

TEMPLE_CONTEXT_HEADER = "X-Temple-Id"


def is_platform_super_admin(current_user: User) -> bool:
    return current_user.role == "super_admin"


def can_access_all_temples(current_user: User) -> bool:
    return is_platform_super_admin(current_user)


def has_any_system_role(
    current_user: User,
    allowed_roles: set[str] | list[str] | tuple[str, ...],
    *,
    allow_platform_super_admin: bool = True,
) -> bool:
    if current_user.role in allowed_roles:
        return True
    return allow_platform_super_admin and is_platform_super_admin(current_user)


def require_system_roles(
    current_user: User,
    allowed_roles: set[str] | list[str] | tuple[str, ...],
    *,
    detail: str,
    allow_platform_super_admin: bool = True,
) -> None:
    if not has_any_system_role(
        current_user,
        allowed_roles,
        allow_platform_super_admin=allow_platform_super_admin,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def extract_requested_temple_id(request: Optional[Request]) -> Optional[int]:
    if request is None:
        return None

    raw_value = request.headers.get(TEMPLE_CONTEXT_HEADER)
    if raw_value is None:
        return None

    normalized = raw_value.strip()
    if not normalized:
        return None

    try:
        temple_id = int(normalized)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{TEMPLE_CONTEXT_HEADER} must be a positive integer",
        ) from exc

    if temple_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{TEMPLE_CONTEXT_HEADER} must be a positive integer",
        )

    return temple_id


def attach_requested_temple_context(current_user: User, request: Optional[Request]) -> User:
    requested_temple_id = extract_requested_temple_id(request)
    if requested_temple_id is not None:
        setattr(current_user, "_requested_temple_id", requested_temple_id)
    return current_user


def resolve_temple_id_for_user(
    db: Session,
    current_user: User,
    *,
    requested_temple_id: Optional[int] = None,
    fallback_to_first: bool = True,
    active_only: bool = True,
) -> Optional[int]:
    requested_id = requested_temple_id
    if requested_id is None:
        requested_id = getattr(current_user, "_requested_temple_id", None)

    if requested_id is not None:
        if can_access_all_temples(current_user):
            query = db.query(Temple.id).filter(Temple.id == requested_id)
            if active_only:
                query = query.filter(Temple.is_active == True)
            row = query.first()
            if not row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temple not found")
            return row.id

        if current_user.temple_id is not None and current_user.temple_id != requested_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Temple access denied")

    if can_access_all_temples(current_user):
        if not fallback_to_first:
            return None

        query = db.query(Temple.id)
        if active_only:
            query = query.filter(Temple.is_active == True)
        first_temple = query.order_by(Temple.id.asc()).first()
        return first_temple.id if first_temple else None

    if current_user.temple_id is not None:
        return current_user.temple_id

    if not fallback_to_first:
        return None

    query = db.query(Temple.id)
    if active_only:
        query = query.filter(Temple.is_active == True)
    first_temple = query.order_by(Temple.id.asc()).first()
    return first_temple.id if first_temple else None


def has_temple_write_access(db: Session, current_user: User, temple_id: int) -> bool:
    if not can_access_all_temples(current_user):
        return current_user.temple_id == temple_id

    temple = (
        db.query(Temple.id, Temple.platform_owner_user_id, Temple.allow_platform_writes)
        .filter(Temple.id == temple_id)
        .first()
    )
    if not temple:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temple not found")

    owner_id = getattr(temple, 'platform_owner_user_id', None)
    allow_platform_writes = bool(getattr(temple, 'allow_platform_writes', False))
    return allow_platform_writes and owner_id == current_user.id


def require_temple_write_access_to_temple(db: Session, current_user: User, temple_id: int) -> int:
    if not has_temple_write_access(db, current_user, temple_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This tenant is read-only for the current platform administrator",
        )
    return temple_id


def require_temple_write_access(
    db: Session,
    current_user: User,
    *,
    requested_temple_id: Optional[int] = None,
    active_only: bool = True,
) -> int:
    temple_id = require_temple_id_for_user(
        db,
        current_user,
        requested_temple_id=requested_temple_id,
        active_only=active_only,
    )
    return require_temple_write_access_to_temple(db, current_user, temple_id)


def require_temple_id_for_user(
    db: Session,
    current_user: User,
    *,
    requested_temple_id: Optional[int] = None,
    active_only: bool = True,
) -> int:
    temple_id = resolve_temple_id_for_user(
        db,
        current_user,
        requested_temple_id=requested_temple_id,
        fallback_to_first=False,
        active_only=active_only,
    )
    if temple_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Temple context is required",
        )
    return temple_id
