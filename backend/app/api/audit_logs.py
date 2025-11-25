"""
Audit Logs API
View audit trail of all user actions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/api/v1/audit-logs", tags=["audit-logs"])


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
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
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs (admin only)
    Comprehensive audit trail of all user actions
    """
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only admins can view audit logs"
        )
    
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if from_date:
        query = query.filter(AuditLog.created_at >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        query = query.filter(AuditLog.created_at <= datetime.combine(to_date, datetime.max.time()))
    
    # Order by most recent first
    query = query.order_by(desc(AuditLog.created_at))
    
    logs = query.offset(skip).limit(limit).all()
    return logs


@router.get("/summary")
def get_audit_summary(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit log summary statistics (admin only)
    """
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only admins can view audit summary"
        )
    
    query = db.query(AuditLog)
    
    if from_date:
        query = query.filter(AuditLog.created_at >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        query = query.filter(AuditLog.created_at <= datetime.combine(to_date, datetime.max.time()))
    
    total_logs = query.count()
    
    # Group by action
    from sqlalchemy import func
    action_counts = db.query(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    )
    
    if from_date:
        action_counts = action_counts.filter(AuditLog.created_at >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        action_counts = action_counts.filter(AuditLog.created_at <= datetime.combine(to_date, datetime.max.time()))
    
    action_counts = action_counts.group_by(AuditLog.action).all()
    
    # Group by user
    user_counts = db.query(
        AuditLog.user_name,
        AuditLog.user_email,
        func.count(AuditLog.id).label('count')
    )
    
    if from_date:
        user_counts = user_counts.filter(AuditLog.created_at >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        user_counts = user_counts.filter(AuditLog.created_at <= datetime.combine(to_date, datetime.max.time()))
    
    user_counts = user_counts.group_by(AuditLog.user_name, AuditLog.user_email).all()
    
    return {
        "total_logs": total_logs,
        "from_date": from_date.isoformat() if from_date else None,
        "to_date": to_date.isoformat() if to_date else None,
        "by_action": [
            {"action": action, "count": count}
            for action, count in action_counts
        ],
        "by_user": [
            {"user_name": name, "user_email": email, "count": count}
            for name, email, count in user_counts
        ]
    }



