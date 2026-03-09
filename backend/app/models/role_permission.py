"""
Temple-scoped role permission profiles and user role assignments.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String, UniqueConstraint

from app.core.database import Base


class RolePermissionProfile(Base):
    """Temple-specific business role template with configurable permissions."""

    __tablename__ = "role_permission_profiles"
    __table_args__ = (
        UniqueConstraint("temple_id", "role_key", name="uq_role_permission_profile_temple_role"),
    )

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)
    role_key = Column(String(50), nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(String(255))
    mapped_system_role = Column(String(50), nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    module_permissions = Column(JSON, default=dict, nullable=False)
    action_permissions = Column(JSON, default=dict, nullable=False)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(
        String,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat(),
    )


class UserRoleAssignment(Base):
    """Business role assigned to a user while keeping the legacy system role for compatibility."""

    __tablename__ = "user_role_assignments"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_role_assignment_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)
    role_key = Column(String(50), nullable=False, index=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(
        String,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat(),
    )
