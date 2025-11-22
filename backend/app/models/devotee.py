"""
Devotee Model - Devotee/CRM data
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Devotee(Base):
    """Devotee/CRM data"""
    
    __tablename__ = "devotees"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Temple (for multi-tenant)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # Basic Information
    name = Column(String(200), nullable=False)
    full_name = Column(String(200))  # For backward compatibility
    
    # Contact
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100))
    
    # Address
    address = Column(Text)  # Street address
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    country = Column(String(100), default="India")
    
    # Optional Details
    date_of_birth = Column(Date)
    gothra = Column(String(100))
    nakshatra = Column(String(50))
    
    # Family
    family_head_id = Column(Integer, ForeignKey("devotees.id"), nullable=True)
    
    # Communication Preferences
    preferred_language = Column(String(10), default="en")
    receive_sms = Column(Boolean, default=True)
    receive_email = Column(Boolean, default=True)
    
    # Tags & Segmentation
    tags = Column(Text)  # JSON array of tags
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    temple = relationship("Temple", back_populates="devotees")
    donations = relationship("Donation", back_populates="devotee")
    family_head = relationship("Devotee", remote_side=[id], backref="family_members")
    
    def __repr__(self):
        return f"<Devotee(id={self.id}, name='{self.name}', phone='{self.phone}')>"

