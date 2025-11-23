"""
Temple Model - Master temple data
"""

from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Temple(Base):
    """Temple master data"""

    __tablename__ = "temples"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    name = Column(String(200), nullable=False)  # English name
    name_kannada = Column(String(200))
    name_sanskrit = Column(String(200))
    slug = Column(String(100), unique=True, nullable=False, index=True)
    primary_deity = Column(String(100))
    deity_name_kannada = Column(String(100))
    deity_name_sanskrit = Column(String(100))
    
    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    
    # Contact
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(200))
    
    # Registration & Tax
    registration_number = Column(String(100))
    trust_name = Column(String(200))
    pan_number = Column(String(20))
    tan_number = Column(String(20))

    # Tax Exemption Certificates
    certificate_80g_number = Column(String(100))
    certificate_80g_valid_from = Column(String)
    certificate_80g_valid_to = Column(String)
    certificate_12a_number = Column(String(100))
    certificate_12a_valid_from = Column(String)
    fcra_registration_number = Column(String(100))
    fcra_valid_from = Column(String)
    fcra_valid_to = Column(String)

    # Banking Information
    bank_name = Column(String(200))
    bank_account_number = Column(String(50))
    bank_ifsc_code = Column(String(20))
    bank_branch = Column(String(200))
    bank_account_type = Column(String(50))  # Current/Savings
    upi_id = Column(String(100))

    # Additional Bank Accounts (for multiple accounts)
    bank_name_2 = Column(String(200))
    bank_account_number_2 = Column(String(50))
    bank_ifsc_code_2 = Column(String(20))

    # Financial Configuration
    financial_year_start_month = Column(Integer, default=4)  # April = 4
    receipt_prefix_donation = Column(String(20), default='DON')
    receipt_prefix_seva = Column(String(20), default='SEVA')
    receipt_prefix_sponsorship = Column(String(20), default='SP')
    receipt_prefix_inkind = Column(String(20), default='IK')

    # Management
    chairman_name = Column(String(100))
    chairman_phone = Column(String(20))
    chairman_email = Column(String(100))

    # Authorized Signatory
    authorized_signatory_name = Column(String(200))
    authorized_signatory_designation = Column(String(100))
    signature_image_url = Column(String(500))
    
    # Timings
    opening_time = Column(String(10))  # HH:MM format
    closing_time = Column(String(10))  # HH:MM format
    
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

