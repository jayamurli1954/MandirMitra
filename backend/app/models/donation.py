"""
Donation Models - Donations and Categories
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


# Enums

class DonationType(str, enum.Enum):
    """Type of donation"""
    CASH = "cash"  # Normal monetary donation (default)
    IN_KIND = "in_kind"  # In-kind donation (goods, services, assets)


class InKindDonationSubType(str, enum.Enum):
    """Sub-type of in-kind donation"""
    INVENTORY = "inventory"  # Consumables: Rice, Dal, Oil, Sugar, etc.
    EVENT_SPONSORSHIP = "event_sponsorship"  # Flower decoration, Lighting, etc.
    ASSET = "asset"  # Gold, Silver, Jewellery, Idols, Movable/Immovable assets


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
    
    # Donation Type
    donation_type = Column(SQLEnum(DonationType), nullable=False, default=DonationType.CASH, index=True)
    
    # Amount (for cash donations) or Assessed Value (for in-kind donations)
    amount = Column(Float, nullable=False)
    
    # Payment Details (for cash donations)
    payment_mode = Column(String(20), nullable=True)  # Made nullable for in-kind donations
    # Options: cash, card, upi, cheque, online
    
    transaction_id = Column(String(100))  # For online payments
    
    # Cheque Details (if payment_mode = 'cheque')
    cheque_number = Column(String(50))
    cheque_date = Column(Date)
    bank_name = Column(String(100))
    
    # Donation Details
    is_anonymous = Column(Boolean, default=False)
    notes = Column(Text)
    
    # In-Kind Donation Details (only for donation_type = IN_KIND)
    inkind_subtype = Column(SQLEnum(InKindDonationSubType), nullable=True, index=True)
    item_name = Column(String(200))  # Name of donated item
    item_description = Column(Text)  # Detailed description
    quantity = Column(Float)  # Quantity donated
    unit = Column(String(50))  # Unit of measurement (kg, grams, pieces, etc.)
    value_assessed = Column(Float)  # Assessed/estimated value (same as amount for in-kind)
    appraised_by = Column(String(200))  # Name of appraiser (for precious items)
    appraisal_date = Column(Date)  # Date of appraisal
    
    # For Precious Items (Gold, Silver, Jewellery)
    purity = Column(String(50))  # 22K, 24K, 925 (for silver), etc.
    weight_gross = Column(Float)  # Gross weight in grams
    weight_net = Column(Float)  # Net weight in grams
    
    # For Event Sponsorship
    event_name = Column(String(200))  # Name of event being sponsored
    event_date = Column(Date)  # Date of event
    sponsorship_category = Column(String(100))  # flower_decoration, lighting, tent, etc.
    
    # Links to Inventory or Asset (if applicable)
    inventory_item_id = Column(Integer, ForeignKey("items.id"), nullable=True)  # If linked to inventory item
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)  # If linked to asset register
    
    # For Inventory Items - Stock Tracking
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)  # Store where inventory is received
    current_balance = Column(Float, default=0.0)  # Remaining quantity (for consumables)
    
    # Photo/Document URLs
    photo_url = Column(String(500))  # Photo of donated item
    document_url = Column(String(500))  # Appraisal certificate, receipt, etc.
    
    # Date
    donation_date = Column(Date, nullable=False, index=True)
    financial_year = Column(String(10))  # e.g., '2024-25'
    
    # Status
    is_cancelled = Column(Boolean, default=False)
    cancelled_at = Column(String)
    cancellation_reason = Column(Text)
    
    # Accounting Integration
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    temple = relationship("Temple", back_populates="donations")
    devotee = relationship("Devotee", back_populates="donations")
    category = relationship("DonationCategory", back_populates="donations")
    journal_entry = relationship("JournalEntry")
    inventory_item = relationship("Item", foreign_keys=[inventory_item_id])
    asset = relationship("Asset", foreign_keys=[asset_id])
    store = relationship("Store", foreign_keys=[store_id])
    
    def __repr__(self):
        donation_type_str = self.donation_type.value if self.donation_type else "cash"
        return f"<Donation(id={self.id}, receipt='{self.receipt_number}', type={donation_type_str}, amount={self.amount})>"


