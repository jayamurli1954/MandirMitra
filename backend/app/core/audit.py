"""
Audit Trail Utilities
Helper functions to create audit logs for all user actions
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, date

from app.models.audit_log import AuditLog
from app.models.user import User


def log_action(
    db: Session,
    user: User,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """
    Create an audit log entry
    
    Args:
        db: Database session
        user: User performing the action
        action: Action type (CREATE, UPDATE, DELETE, VIEW, etc.)
        entity_type: Type of entity (Donation, SevaBooking, etc.)
        entity_id: ID of the affected entity
        old_values: Previous state (for updates)
        new_values: New state
        description: Human-readable description
        ip_address: User's IP address
        user_agent: User's browser/client info
    
    Returns:
        Created AuditLog entry
    """
    # Calculate changes if both old and new values provided
    changes = None
    if old_values and new_values:
        changes = {}
        for key in set(list(old_values.keys()) + list(new_values.keys())):
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            if old_val != new_val:
                changes[key] = {
                    "old": old_val,
                    "new": new_val
                }
    
    audit_log = AuditLog(
        user_id=user.id,
        user_name=user.full_name,
        user_email=user.email,
        user_role=user.role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        changes=changes,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.utcnow()
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log


def get_entity_dict(obj: Any, exclude_fields: Optional[list] = None) -> Dict[str, Any]:
    """
    Convert SQLAlchemy model instance to dictionary for audit logging
    
    Args:
        obj: SQLAlchemy model instance
        exclude_fields: Fields to exclude from logging
    
    Returns:
        Dictionary representation
    """
    if obj is None:
        return {}
    
    exclude_fields = exclude_fields or ['password_hash', 'password', 'token', 'secret']
    
    result = {}
    for column in obj.__table__.columns:
        if column.name not in exclude_fields:
            value = getattr(obj, column.name, None)
            # Convert datetime to ISO string for JSON serialization
            if isinstance(value, datetime):
                value = value.isoformat()
            # Convert date to ISO string for JSON serialization
            elif isinstance(value, date):
                value = value.isoformat()
            result[column.name] = value
    
    return result


