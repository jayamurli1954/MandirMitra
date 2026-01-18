"""
Hundi Management Models
Handles hundi opening, counting, verification, and bank deposit
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class HundiStatus(str, enum.Enum):
    """Hundi opening status"""

    SCHEDULED = "scheduled"
    OPENED = "opened"
    COUNTING = "counting"
    VERIFIED = "verified"
    DEPOSITED = "deposited"
    RECONCILED = "reconciled"
    CANCELLED = "cancelled"


class HundiOpening(Base):
    """Hundi opening schedule and tracking"""

    __tablename__ = "hundi_openings"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Hundi Identification
    hundi_code = Column(String(50), nullable=False, index=True)  # HUNDI-001, HUNDI-002
    hundi_name = Column(String(200), nullable=False)  # Main Hundi, Special Hundi, etc.
    hundi_location = Column(String(200))  # Location description

    # Opening Schedule
    scheduled_date = Column(Date, nullable=False, index=True)
    scheduled_time = Column(String(10))  # HH:MM format
    actual_opened_date = Column(Date)
    actual_opened_time = Column(String(10))

    # Sealed Number Tracking
    sealed_number = Column(String(100))  # Sealed number on hundi
    seal_photo_url = Column(String(500))  # Photo of sealed hundi
    seal_video_url = Column(String(500))  # Video timestamp

    # Status
    status = Column(SQLEnum(HundiStatus), nullable=False, default=HundiStatus.SCHEDULED, index=True)

    # Counting Information
    counting_started_at = Column(DateTime)
    counting_completed_at = Column(DateTime)
    total_amount = Column(Float, default=0.0)  # Total amount counted

    # Verification (Multi-person)
    verified_by_user_1_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_by_user_2_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_by_user_3_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime)

    # Discrepancy Tracking
    has_discrepancy = Column(Boolean, default=False)
    discrepancy_amount = Column(Float, default=0.0)
    discrepancy_reason = Column(Text)
    discrepancy_resolved = Column(Boolean, default=False)
    discrepancy_resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    discrepancy_resolved_at = Column(DateTime)

    # Bank Deposit
    bank_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    bank_deposit_date = Column(Date)
    bank_deposit_reference = Column(String(100))  # Deposit slip number
    bank_deposit_amount = Column(Float)
    journal_entry_id = Column(
        Integer, ForeignKey("journal_entries.id"), nullable=True
    )  # Link to accounting

    # Reconciliation
    reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime)
    reconciled_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Notes and Documentation
    notes = Column(Text)
    counting_sheet_url = Column(String(500))  # Generated counting sheet PDF
    photo_urls = Column(JSON)  # Array of photo URLs
    video_urls = Column(JSON)  # Array of video URLs with timestamps

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    temple = relationship("Temple", back_populates="hundi_openings")
    verified_by_user_1 = relationship("User", foreign_keys=[verified_by_user_1_id])
    verified_by_user_2 = relationship("User", foreign_keys=[verified_by_user_2_id])
    verified_by_user_3 = relationship("User", foreign_keys=[verified_by_user_3_id])
    bank_account = relationship("Account", foreign_keys=[bank_account_id])
    journal_entry = relationship("JournalEntry", foreign_keys=[journal_entry_id])
    denomination_counts = relationship(
        "HundiDenominationCount", back_populates="hundi_opening", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<HundiOpening(code='{self.hundi_code}', date={self.scheduled_date}, amount={self.total_amount})>"


class HundiDenominationCount(Base):
    """Denomination-wise counting for each hundi opening"""

    __tablename__ = "hundi_denomination_counts"

    id = Column(Integer, primary_key=True, index=True)
    hundi_opening_id = Column(Integer, ForeignKey("hundi_openings.id"), nullable=False, index=True)

    # Denomination Details
    denomination_value = Column(
        Float, nullable=False
    )  # 2000, 500, 100, 50, 20, 10, 5, 2, 1, 0.5, 0.25
    denomination_type = Column(String(20), nullable=False)  # "note" or "coin"
    currency = Column(String(10), default="INR")

    # Count
    quantity = Column(Integer, nullable=False, default=0)  # Number of notes/coins
    total_amount = Column(Float, nullable=False, default=0.0)  # quantity * denomination_value

    # Counting Details
    counted_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    counted_at = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)
    verified_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime)

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hundi_opening = relationship("HundiOpening", back_populates="denomination_counts")
    counted_by = relationship("User", foreign_keys=[counted_by_user_id])
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])

    def __repr__(self):
        return f"<HundiDenominationCount(denomination={self.denomination_value}, quantity={self.quantity}, amount={self.total_amount})>"


class HundiMaster(Base):
    """Master data for hundis (different hundis in temple)"""

    __tablename__ = "hundi_masters"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Hundi Details
    hundi_code = Column(String(50), nullable=False, unique=True, index=True)
    hundi_name = Column(String(200), nullable=False)
    hundi_location = Column(String(200))
    description = Column(Text)

    # Configuration
    is_active = Column(Boolean, default=True)
    requires_verification = Column(Boolean, default=True)  # Requires 2-3 person verification
    min_verifiers = Column(Integer, default=2)  # Minimum number of verifiers required

    # Default Bank Account
    default_bank_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    default_bank_account = relationship("Account", foreign_keys=[default_bank_account_id])

    def __repr__(self):
        return f"<HundiMaster(code='{self.hundi_code}', name='{self.hundi_name}')>"
