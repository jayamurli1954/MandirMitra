from typing import Optional

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.models.temple import Temple
from app.models.user import User

TEMPLE_CONTEXT_HEADER = "X-Temple-Id"


def can_access_all_temples(current_user: User) -> bool:
    return bool(current_user.is_superuser) or current_user.role == "super_admin"


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

    if current_user.temple_id is not None:
        return current_user.temple_id

    if not fallback_to_first:
        return None

    query = db.query(Temple.id)
    if active_only:
        query = query.filter(Temple.is_active == True)
    first_temple = query.order_by(Temple.id.asc()).first()
    return first_temple.id if first_temple else None
