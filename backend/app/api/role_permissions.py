"""
Temple-scoped configurable role-permission profiles.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.users import _is_admin_user, _resolve_temple_id
from app.core.database import get_db
from app.core.role_permissions import (
    ACTION_PERMISSION_DEFINITIONS,
    MODULE_PERMISSION_DEFINITIONS,
    get_assignable_role_options,
    get_effective_role_profiles,
    upsert_role_profile,
)
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/role-permissions", tags=["role-permissions"])


class RolePermissionUpdate(BaseModel):
    is_enabled: bool
    module_permissions: dict[str, bool]
    action_permissions: dict[str, bool]


@router.get("")
def list_role_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _is_admin_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can manage role permissions")

    temple_id = _resolve_temple_id(db, current_user)
    if not temple_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temple not found")

    return {
        "temple_id": temple_id,
        "policy_notice": "Accounting transactions must not be deleted or cancelled in-place. Use reversal with reason and approval to preserve audit trail.",
        "modules": MODULE_PERMISSION_DEFINITIONS,
        "actions": ACTION_PERMISSION_DEFINITIONS,
        "roles": get_effective_role_profiles(db, temple_id),
    }


@router.get("/assignable")
def list_assignable_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    temple_id = _resolve_temple_id(db, current_user)
    return {"roles": get_assignable_role_options(db, temple_id)}


@router.put("/{role_key}")
def update_role_permissions(
    role_key: str,
    payload: RolePermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _is_admin_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can manage role permissions")

    temple_id = _resolve_temple_id(db, current_user)
    if not temple_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temple not found")

    try:
        updated_profile = upsert_role_profile(
            db=db,
            temple_id=temple_id,
            role_key=role_key,
            is_enabled=payload.is_enabled,
            module_permissions=payload.module_permissions,
            action_permissions=payload.action_permissions,
        )
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    return {"role": updated_profile}
