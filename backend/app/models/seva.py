"""
Seva (Temple Service) Models
Handles temple sevas/poojas/archanas
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum

class SevaCategory(str, enum.Enum):
    """Seva categories"""
    ABHISHEKA = "abhisheka"
    ALANKARA = "alankara"
    POOJA = "pooja"
    ARCHANA = "archana"
    VAHANA_SEVA = "vahana_seva"
    SPECIAL = "special"
    FESTIVAL = "festival"

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
    category = Column(SQLEnum(SevaCategory), nullable=False)
    amount = Column(Float, nullable=False)
    min_amount = Column(Float, nullable=True)  # For variable amount sevas
    max_amount = Column(Float, nullable=True)

    # Availability settings
    availability = Column(SQLEnum(SevaAvailability), nullable=False, default=SevaAvailability.DAILY)
    specific_day = Column(Integer, nullable=True)  # 0=Sunday, 1=Monday, etc.
    except_day = Column(Integer, nullable=True)
    time_slot = Column(String(50), nullable=True)  # e.g., "Morning", "Evening", "6:00 AM"

    # Booking settings
    max_bookings_per_day = Column(Integer, nullable=True)
    advance_booking_days = Column(Integer, default=30)
    requires_approval = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Accounting Link
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    # Additional info
    benefits = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

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
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    receipt_number = Column(String(100), nullable=True, unique=True)

    # Additional details
    devotee_names = Column(Text, nullable=True)  # JSON or comma-separated names
    gotra = Column(String(100), nullable=True)
    nakshatra = Column(String(50), nullable=True)
    special_request = Column(Text, nullable=True)

    # Admin notes
    admin_notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    seva = relationship("Seva", back_populates="bookings")
    devotee = relationship("Devotee")
    user = relationship("User")
