"""
Vendor Management Models
Track vendors/suppliers for temple services and purchases
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Vendor(Base):
    """
    Vendor/Supplier Master
    Stores information about service providers and suppliers
    """

    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)

    # Temple Reference
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)

    # Basic Information
    vendor_name = Column(String(200), nullable=False, index=True)
    vendor_code = Column(String(50), unique=True, index=True)  # Auto-generated: VEND001, VEND002
    vendor_type = Column(
        String(100), index=True
    )  # florist, caterer, electrician, tent_supplier, etc.

    # Contact Details
    contact_person = Column(String(200))
    phone = Column(String(20), index=True)
    email = Column(String(100))
    alternate_phone = Column(String(20))

    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))

    # Tax & Banking
    gstin = Column(String(20))
    pan_number = Column(String(20))
    bank_name = Column(String(200))
    bank_account_number = Column(String(50))
    bank_ifsc_code = Column(String(20))
    account_holder_name = Column(String(200))

    # Service Categories (comma-separated)
    service_categories = Column(Text)  # "flower_decoration,pooja_items,festival_supplies"

    # Rating & Feedback
    rating = Column(Integer)  # 1-5 stars
    notes = Column(Text)  # Internal notes about vendor

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_preferred = Column(Boolean, default=False)  # Mark preferred vendors

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    sponsorships = relationship("Sponsorship", back_populates="vendor")

    def __repr__(self):
        return f"<Vendor(code='{self.vendor_code}', name='{self.vendor_name}', type='{self.vendor_type}')>"
