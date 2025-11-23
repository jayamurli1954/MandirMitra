"""
Donation Models - Donations and Categories
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class DonationCategory(Base):
    """Donation categories (configurable per temple)"""
    
    __tablename__ = "donation_categories"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Temple
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # Category Details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Tax Exemption
    is_80g_eligible = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)

    # Accounting Link
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationships
    temple = relationship("Temple", back_populates="donation_categories")
    donations = relationship("Donation", back_populates="category")
    account = relationship("Account")
    
    def __repr__(self):
        return f"<DonationCategory(id={self.id}, name='{self.name}')>"


class Donation(Base):
    """Donation transactions"""
    
    __tablename__ = "donations"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Temple
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # Relationships
    devotee_id = Column(Integer, ForeignKey("devotees.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("donation_categories.id"), nullable=False)
    
    # Receipt
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Amount
    amount = Column(Float, nullable=False)
    
    # Payment Details
    payment_mode = Column(String(20), nullable=False)
    # Options: cash, card, upi, cheque, online
    
    transaction_id = Column(String(100))  # For online payments
    
    # Cheque Details (if payment_mode = 'cheque')
    cheque_number = Column(String(50))
    cheque_date = Column(Date)
    bank_name = Column(String(100))
    
    # Donation Details
    is_anonymous = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Date
    donation_date = Column(Date, nullable=False, index=True)
    financial_year = Column(String(10))  # e.g., '2024-25'
    
    # Status
    is_cancelled = Column(Boolean, default=False)
    cancelled_at = Column(String)
    cancellation_reason = Column(Text)
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    temple = relationship("Temple", back_populates="donations")
    devotee = relationship("Devotee", back_populates="donations")
    category = relationship("DonationCategory", back_populates="donations")
    
    def __repr__(self):
        return f"<Donation(id={self.id}, receipt='{self.receipt_number}', amount={self.amount})>"


