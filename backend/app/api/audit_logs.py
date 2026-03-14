"""
Audit Logs API
View audit trail of all user actions
"""

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.role_permissions import require_action_permission
from app.core.security import get_current_user
from app.core.temple_context import can_access_all_temples, resolve_temple_id_for_user
from app.models.audit_log import AuditLog
from app.models.user import User

router = APIRouter(prefix="/api/v1/audit-logs", tags=["audit-logs"])


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    temple_id: Optional[int]
    user_name: str
    user_email: str
    user_role: str
    action: str
    entity_type: str
    entity_id: Optional[int]
    old_values: Optional[dict]
    new_values: Optional[dict]
    changes: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


def _resolve_audit_scope(db: Session, current_user: User) -> Optional[int]:
    temple_id = resolve_temple_id_for_user(
        db,
        current_user,
        fallback_to_first=False,
        active_only=False,
    )
    if temple_id is None and not can_access_all_temples(current_user):
        raise HTTPException(status_code=400, detail="Temple context is required")
    return temple_id


def _require_audit_access(db: Session, current_user: User, temple_id: Optional[int]) -> None:
    try:
        require_action_permission(
            db,
            current_user,
            "view_audit_logs",
            temple_id=temple_id,
            detail="You do not have permission to view audit logs",
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit logs for the current tenant scope."""
    temple_id = _resolve_audit_scope(db, current_user)
    _require_audit_access(db, current_user, temple_id)

    query = db.query(AuditLog)
    if temple_id is not None:
        query = query.filter(AuditLog.temple_id == temple_id)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if from_date:
        query = query.filter(
            AuditLog.created_at >= datetime.combine(from_date, datetime.min.time())
        )
    if to_date:
        query = query.filter(AuditLog.created_at <= datetime.combine(to_date, datetime.max.time()))

    return query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()


@router.get("/summary")
def get_audit_summary(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit log summary statistics for the current tenant scope."""
    from sqlalchemy import func

    temple_id = _resolve_audit_scope(db, current_user)
    _require_audit_access(db, current_user, temple_id)

    query = db.query(AuditLog)
    if temple_id is not None:
        query = query.filter(AuditLog.temple_id == temple_id)

    if from_date:
        query = query.filter(
            AuditLog.created_at >= datetime.combine(from_date, datetime.min.time())
        )
    if to_date:
        query = query.filter(AuditLog.created_at <= datetime.combine(to_date, datetime.max.time()))

    total_logs = query.count()

    action_counts = db.query(AuditLog.action, func.count(AuditLog.id).label("count"))
    if temple_id is not None:
        action_counts = action_counts.filter(AuditLog.temple_id == temple_id)
    if from_date:
        action_counts = action_counts.filter(
            AuditLog.created_at >= datetime.combine(from_date, datetime.min.time())
        )
    if to_date:
        action_counts = action_counts.filter(
            AuditLog.created_at <= datetime.combine(to_date, datetime.max.time())
        )
    action_counts = action_counts.group_by(AuditLog.action).all()

    user_counts = db.query(
        AuditLog.user_name,
        AuditLog.user_email,
        func.count(AuditLog.id).label("count"),
    )
    if temple_id is not None:
        user_counts = user_counts.filter(AuditLog.temple_id == temple_id)
    if from_date:
        user_counts = user_counts.filter(
            AuditLog.created_at >= datetime.combine(from_date, datetime.min.time())
        )
    if to_date:
        user_counts = user_counts.filter(
            AuditLog.created_at <= datetime.combine(to_date, datetime.max.time())
        )
    user_counts = user_counts.group_by(AuditLog.user_name, AuditLog.user_email).all()

    return {
        "total_logs": total_logs,
        "from_date": from_date.isoformat() if from_date else None,
        "to_date": to_date.isoformat() if to_date else None,
        "by_action": [{"action": action_name, "count": count} for action_name, count in action_counts],
        "by_user": [
            {"user_name": name, "user_email": email, "count": count}
            for name, email, count in user_counts
        ],
    }
