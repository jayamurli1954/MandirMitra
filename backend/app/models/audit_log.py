"""
Audit Log Model
Tracks all user actions for accountability and audit trail
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class AuditLog(Base):
    """
    Comprehensive audit trail for all user actions
    Tracks: Who did what, when, and what changed
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User who performed the action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_name = Column(String(200), nullable=False)  # Denormalized for performance
    user_email = Column(String(100), nullable=False)  # Denormalized for performance
    user_role = Column(String(50), nullable=False)  # Denormalized for performance
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # e.g., "CREATE_DONATION", "UPDATE_SEVA", "DELETE_ACCOUNT"
    entity_type = Column(String(100), nullable=False, index=True)  # e.g., "Donation", "SevaBooking", "Account"
    entity_id = Column(Integer, nullable=True, index=True)  # ID of the affected entity
    
    # Change details
    old_values = Column(JSON, nullable=True)  # Previous state (for updates)
    new_values = Column(JSON, nullable=True)  # New state
    changes = Column(JSON, nullable=True)  # Diff of what changed
    
    # Additional context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)  # Human-readable description
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user='{self.user_name}', action='{self.action}', entity='{self.entity_type}')>"









