"""
In-Kind Donations and Sponsorship Models
Handle non-monetary donations and expense sponsorships
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    ForeignKey,
    Enum as SQLEnum,
    DateTime,
    Date,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


# Enums


class InKindDonationType(str, enum.Enum):
    """Type of in-kind donation"""

    CONSUMABLE = "consumable"  # Rice, Dal, Oil - for Annadana
    PRECIOUS = "precious"  # Gold, Silver ornaments
    ASSET = "asset"  # Furniture, Equipment
    GENERAL = "general"  # Cloth, Books, etc.


class InKindStatus(str, enum.Enum):
    """Status of in-kind donation"""

    RECEIVED = "received"
    IN_STOCK = "in_stock"  # For consumables
    CONSUMED = "consumed"  # For consumables
    IN_USE = "in_use"  # For assets
    SOLD = "sold"  # If sold/melted
    TRANSFERRED = "transferred"  # If transferred


class SponsorshipPaymentMode(str, enum.Enum):
    """How sponsorship payment is handled"""

    TEMPLE_PAYMENT = "temple_payment"  # Devotee pays temple, temple pays vendor
    DIRECT_PAYMENT = "direct_payment"  # Devotee pays vendor directly


class SponsorshipStatus(str, enum.Enum):
    """Status of sponsorship"""

    COMMITTED = "committed"  # Devotee committed but not paid
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"  # Paid to temple (for temple_payment mode)
    FULFILLED = "fulfilled"  # Service completed
    CANCELLED = "cancelled"


# Models


class InKindDonation(Base):
    """
    In-Kind Donations
    Tracks non-monetary donations like rice, gold, furniture, etc.
    """

    __tablename__ = "inkind_donations"

    id = Column(Integer, primary_key=True, index=True)

    # Temple & Devotee
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)
    devotee_id = Column(Integer, ForeignKey("devotees.id"), nullable=False, index=True)

    # Receipt
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    receipt_date = Column(DateTime, nullable=False, index=True)

    # Donation Type
    donation_type = Column(SQLEnum(InKindDonationType), nullable=False, index=True)

    # Item Details
    item_name = Column(String(200), nullable=False, index=True)
    item_category = Column(String(100), index=True)  # rice, gold_chain, furniture, etc.
    item_description = Column(Text)

    # Quantity
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)  # kg, grams, pieces, liters

    # Valuation
    value_assessed = Column(Float, nullable=False)  # Estimated/assessed value
    value_per_unit = Column(Float)  # Rate per kg/gram/piece
    appraised_by = Column(String(200))  # For precious items - name of appraiser
    appraisal_date = Column(Date)

    # For Precious Items
    purity = Column(String(50))  # 22K, 24K for gold
    weight_gross = Column(Float)  # Gross weight in grams
    weight_net = Column(Float)  # Net weight in grams

    # For Consumables - Inventory Tracking
    current_balance = Column(Float, default=0.0)  # Remaining quantity
    consumed_quantity = Column(Float, default=0.0)

    # Status
    status = Column(SQLEnum(InKindStatus), default=InKindStatus.RECEIVED, index=True)

    # Purpose
    purpose = Column(Text)  # Annadana, Temple decoration, etc.

    # Photo/Document
    photo_url = Column(String(500))
    document_url = Column(String(500))  # Appraisal certificate for precious items

    # Accounting Integration
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    devotee = relationship("Devotee")
    journal_entry = relationship("JournalEntry")
    consumption_transactions = relationship("InKindConsumption", back_populates="inkind_donation")

    def __repr__(self):
        return f"<InKindDonation(receipt='{self.receipt_number}', item='{self.item_name}', qty={self.quantity})>"


class InKindConsumption(Base):
    """
    Track consumption of in-kind donations (mainly consumables)
    """

    __tablename__ = "inkind_consumptions"

    id = Column(Integer, primary_key=True, index=True)

    # In-Kind Donation Reference
    inkind_donation_id = Column(
        Integer, ForeignKey("inkind_donations.id"), nullable=False, index=True
    )

    # Temple
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)

    # Consumption Details
    consumption_date = Column(DateTime, nullable=False, index=True)
    quantity_consumed = Column(Float, nullable=False)
    purpose = Column(Text)  # Annadana on specific date, festival, etc.

    # Event Reference (if consumed for specific event)
    event_name = Column(String(200))
    event_date = Column(Date)

    # Accounting Integration
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inkind_donation = relationship("InKindDonation", back_populates="consumption_transactions")
    temple = relationship("Temple")
    journal_entry = relationship("JournalEntry")

    def __repr__(self):
        return f"<InKindConsumption(item={self.inkind_donation_id}, qty={self.quantity_consumed})>"


class Sponsorship(Base):
    """
    Sponsorships - Devotees sponsoring specific temple expenses
    Handles both temple payment and direct vendor payment scenarios
    """

    __tablename__ = "sponsorships"

    id = Column(Integer, primary_key=True, index=True)

    # Temple & Devotee
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)
    devotee_id = Column(Integer, ForeignKey("devotees.id"), nullable=False, index=True)

    # Receipt
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    receipt_date = Column(DateTime, nullable=False, index=True)

    # Sponsorship Details
    sponsorship_category = Column(
        String(100), nullable=False, index=True
    )  # flower_decoration, tent, lighting, etc.
    description = Column(Text, nullable=False)

    # Amount
    committed_amount = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)

    # Payment Mode
    payment_mode = Column(SQLEnum(SponsorshipPaymentMode), nullable=False, index=True)

    # For Direct Payment Mode
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True, index=True)
    vendor_invoice_number = Column(String(100))
    vendor_invoice_date = Column(Date)
    vendor_invoice_amount = Column(Float)
    vendor_invoice_document_url = Column(String(500))

    # Event Details
    event_name = Column(String(200))
    event_date = Column(Date, index=True)

    # Status
    status = Column(SQLEnum(SponsorshipStatus), default=SponsorshipStatus.COMMITTED, index=True)
    fulfilled_date = Column(DateTime)

    # Accounting Integration
    journal_entry_id_commitment = Column(
        Integer, ForeignKey("journal_entries.id"), nullable=True
    )  # When committed
    journal_entry_id_payment = Column(
        Integer, ForeignKey("journal_entries.id"), nullable=True
    )  # When paid
    journal_entry_id_expense = Column(
        Integer, ForeignKey("journal_entries.id"), nullable=True
    )  # When vendor paid/direct payment

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    devotee = relationship("Devotee")
    vendor = relationship("Vendor", back_populates="sponsorships")
    sponsorship_payments = relationship("SponsorshipPayment", back_populates="sponsorship")

    def __repr__(self):
        return f"<Sponsorship(receipt='{self.receipt_number}', category='{self.sponsorship_category}', amount={self.committed_amount})>"


class SponsorshipPayment(Base):
    """
    Track payments for sponsorships (for temple_payment mode)
    """

    __tablename__ = "sponsorship_payments"

    id = Column(Integer, primary_key=True, index=True)

    # Sponsorship Reference
    sponsorship_id = Column(Integer, ForeignKey("sponsorships.id"), nullable=False, index=True)

    # Temple
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)

    # Payment Details
    payment_date = Column(DateTime, nullable=False, index=True)
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, upi, bank_transfer

    # Reference
    transaction_reference = Column(String(100))  # UPI ref, cheque number, etc.

    # Accounting Integration
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sponsorship = relationship("Sponsorship", back_populates="sponsorship_payments")
    temple = relationship("Temple")
    journal_entry = relationship("JournalEntry")

    def __repr__(self):
        return f"<SponsorshipPayment(sponsorship={self.sponsorship_id}, amount={self.amount_paid})>"
