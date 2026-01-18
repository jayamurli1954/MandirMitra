"""
Seva (Temple Service) Models
Handles temple sevas/poojas/archanas
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    TypeDecorator,
)
from sqlalchemy.orm import relationship, foreign
from app.core.database import Base
from datetime import datetime
import enum


class SevaCategory(str, enum.Enum):
    """Seva categories"""

    SEVA = "seva"
    ABHISHEKA = "abhisheka"
    ALANKARA = "alankara"
    POOJA = "pooja"
    ARCHANA = "archana"
    VAHANA_SEVA = "vahana_seva"
    SPECIAL = "special"
    FESTIVAL = "festival"


class SevaCategoryDecorator(TypeDecorator):
    """Custom type decorator to ensure lowercase enum values are stored"""

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert enum to string value - use .value (lowercase) which should work with VARCHAR"""
        if value is None:
            return None
        if isinstance(value, SevaCategory):
            # The database column should be VARCHAR (not enum) due to TypeDecorator using String
            # So we can use the lowercase .value
            result = value.value  # Returns lowercase string like "seva"
            print(
                f"🔧 SevaCategoryDecorator.process_bind_param: enum {value.name}={value.value} -> '{result}'"
            )
            return result
        if isinstance(value, str):
            # If it's already a string, use as-is (TypeDecorator stores as VARCHAR)
            result = value.lower()  # Normalize to lowercase
            print(f"🔧 SevaCategoryDecorator.process_bind_param: string '{value}' -> '{result}'")
            return result
        # For any other type, convert to lowercase string
        result = str(value).lower()
        print(
            f"🔧 SevaCategoryDecorator.process_bind_param: other {type(value)} {value} -> '{result}'"
        )
        return result

    def process_result_value(self, value, dialect):
        """Convert string from database to enum"""
        if value is None:
            return None
        try:
            return SevaCategory(value.lower())
        except ValueError:
            return value  # Return as-is if not a valid enum value


class SevaAvailability(str, enum.Enum):
    """Seva availability"""

    DAILY = "daily"
    WEEKDAY = "weekday"
    WEEKEND = "weekend"
    SPECIFIC_DAY = "specific_day"
    EXCEPT_DAY = "except_day"
    FESTIVAL_ONLY = "festival_only"


class SevaBookingStatus(str, enum.Enum):
    """Booking status"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Seva(Base):
    """Seva/Pooja service model"""

    __tablename__ = "sevas"

    id = Column(Integer, primary_key=True, index=True)
    name_english = Column(String(200), nullable=False)
    name_kannada = Column(String(200), nullable=True)
    name_sanskrit = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(SevaCategoryDecorator(50), nullable=False)
    amount = Column(Float, nullable=False)
    min_amount = Column(Float, nullable=True)  # For variable amount sevas
    max_amount = Column(Float, nullable=True)

    # Availability settings
    availability = Column(
        SQLEnum(SevaAvailability, native_enum=False), nullable=False, default=SevaAvailability.DAILY
    )
    specific_day = Column(Integer, nullable=True)  # 0=Sunday, 1=Monday, etc. (for SPECIFIC_DAY)
    except_day = Column(
        Integer, nullable=True
    )  # Single excluded day (legacy, for backward compatibility)
    except_days = Column(
        Text, nullable=True
    )  # JSON array of excluded days: [1, 3, 6] for Monday, Wednesday, Saturday (0=Sunday, 1=Monday, etc.)
    time_slot = Column(String(50), nullable=True)  # e.g., "Morning", "Evening", "6:00 AM"

    # Booking settings
    max_bookings_per_day = Column(Integer, nullable=True)
    advance_booking_days = Column(Integer, default=30)
    requires_approval = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Token Seva Settings (for small-value sevas)
    is_token_seva = Column(
        Boolean, default=False
    )  # If True, uses pre-printed tokens instead of receipts
    token_color = Column(
        String(50), nullable=True
    )  # Color code for token (e.g., "RED", "BLUE", "GREEN")
    token_threshold = Column(Float, nullable=True)  # Amount threshold (default from temple config)

    # Accounting Link
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    # Additional info
    benefits = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    # materials_required column may not exist in database - handle gracefully
    # materials_required = Column(Text, nullable=True)  # JSON array or comma-separated list of materials

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = relationship("SevaBooking", back_populates="seva")
    account = relationship("Account")


class SevaBooking(Base):
    """Seva booking model"""

    __tablename__ = "seva_bookings"

    id = Column(Integer, primary_key=True, index=True)
    seva_id = Column(Integer, ForeignKey("sevas.id"), nullable=False)
    devotee_id = Column(Integer, ForeignKey("devotees.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Booking details
    booking_date = Column(Date, nullable=False)
    booking_time = Column(String(50), nullable=True)
    status = Column(SQLEnum(SevaBookingStatus), default=SevaBookingStatus.PENDING)

    # Payment
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=True)  # Cash, Card, UPI, Cheque, Online
    payment_reference = Column(String(100), nullable=True)  # Legacy field

    # UPI Payment Details (if payment_method = 'UPI')
    sender_upi_id = Column(String(100), nullable=True)  # Sender's UPI ID (e.g., 9876543210@paytm)
    upi_reference_number = Column(String(100), nullable=True)  # UPI transaction reference (UTR/RRN)

    # Cheque Details (if payment_method = 'Cheque')
    cheque_number = Column(String(50), nullable=True)
    cheque_date = Column(Date, nullable=True)
    cheque_bank_name = Column(String(100), nullable=True)  # Name of bank
    cheque_branch = Column(String(100), nullable=True)  # Branch name

    # Online Transfer Details (if payment_method = 'Online')
    utr_number = Column(
        String(100), nullable=True
    )  # UTR (Unique Transfer Reference) or transaction reference
    payer_name = Column(
        String(200), nullable=True
    )  # Payer's name (may be different from devotee/seva kartha)

    receipt_number = Column(String(100), nullable=True, unique=True)

    # Additional details
    devotee_names = Column(Text, nullable=True)  # JSON or comma-separated names
    gotra = Column(String(100), nullable=True)
    nakshatra = Column(String(50), nullable=True)
    rashi = Column(String(50), nullable=True)
    special_request = Column(Text, nullable=True)

    # Priest assignment
    priest_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Assigned priest

    # Admin notes
    admin_notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Reschedule fields (for postpone/prepone with approval)
    original_booking_date = Column(Date, nullable=True)  # Original date before reschedule
    reschedule_requested_date = Column(Date, nullable=True)  # Requested new date
    reschedule_reason = Column(Text, nullable=True)  # Reason for reschedule
    reschedule_approved = Column(
        Boolean, nullable=True
    )  # NULL = not requested, True = approved, False = rejected
    reschedule_approved_by = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # Admin who approved
    reschedule_approved_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    seva = relationship("Seva", back_populates="bookings")
    devotee = relationship("Devotee")
    # User who created the booking - explicit primaryjoin to avoid ambiguity
    user = relationship(
        "User", foreign_keys=[user_id], primaryjoin="SevaBooking.user_id == foreign(User.id)"
    )
    # Admin who approved reschedule - explicit primaryjoin to avoid ambiguity
    reschedule_approved_by_user = relationship(
        "User",
        foreign_keys=[reschedule_approved_by],
        primaryjoin="SevaBooking.reschedule_approved_by == foreign(User.id)",
        overlaps="user",  # Silence warning about overlapping foreign keys
    )
    # Assigned priest - explicit primaryjoin to avoid ambiguity
    priest = relationship(
        "User",
        foreign_keys=[priest_id],
        primaryjoin="SevaBooking.priest_id == foreign(User.id)",
        overlaps="user,reschedule_approved_by_user",
    )
