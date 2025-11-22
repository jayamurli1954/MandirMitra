"""
User Model - System users (admin, staff, priests)
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """System users (admins, staff, priests)"""
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Temple (for multi-tenant in SaaS mode)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # Authentication
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(200), nullable=False)
    
    # Role
    role = Column(String(50), default="staff", index=True)
    # Roles: super_admin, temple_manager, accountant, counter_staff, priest
    
    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Security
    last_login_at = Column(String)
    last_password_change = Column(String, default=lambda: datetime.utcnow().isoformat())
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(String)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    temple = relationship("Temple", back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


