"""
Temple Model - Master temple data
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Time
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Temple(Base):
    """Temple master data"""
    
    __tablename__ = "temples"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    primary_deity = Column(String(100))
    
    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    
    # Contact
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(200))
    
    # Registration
    registration_number = Column(String(100))
    trust_name = Column(String(200))
    
    # Management
    chairman_name = Column(String(100))
    chairman_phone = Column(String(20))
    chairman_email = Column(String(100))
    
    # Timings
    opening_time = Column(Time)
    closing_time = Column(Time)
    
    # Media
    logo_url = Column(String(500))
    banner_url = Column(String(500))
    
    # Description
    description = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    users = relationship("User", back_populates="temple")
    donations = relationship("Donation", back_populates="temple")
    donation_categories = relationship("DonationCategory", back_populates="temple")
    devotees = relationship("Devotee", back_populates="temple")
    panchang_display_settings = relationship(
        "PanchangDisplaySettings",
        back_populates="temple",
        uselist=False  # One-to-one relationship
    )
    
    def __repr__(self):
        return f"<Temple(id={self.id}, name='{self.name}', slug='{self.slug}')>"

