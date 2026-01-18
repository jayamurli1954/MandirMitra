"""
Seva Exchange Request Model
Handles exchange/swap of seva booking dates between two devotees
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, foreign
from app.core.database import Base
from datetime import datetime
import enum


class ExchangeRequestStatus(str, enum.Enum):
    """Exchange request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SevaExchangeRequest(Base):
    """Seva exchange request model - for swapping booking dates between two devotees"""
    __tablename__ = "seva_exchange_requests"

    id = Column(Integer, primary_key=True, index=True)
    
    # The two bookings to exchange
    booking_a_id = Column(Integer, ForeignKey("seva_bookings.id"), nullable=False)
    booking_b_id = Column(Integer, ForeignKey("seva_bookings.id"), nullable=False)
    
    # Reason for exchange
    reason = Column(Text, nullable=False)
    
    # Status tracking
    status = Column(SQLEnum(ExchangeRequestStatus), default=ExchangeRequestStatus.PENDING, nullable=False)
    
    # Who requested and approved
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Clerk/staff who initiated
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin who approved/rejected
    
    # Consent from Devotee A (booking_a)
    consent_a_method = Column(String(50), nullable=True)  # in_person, phone, whatsapp, email, other
    consent_a_notes = Column(Text, nullable=True)  # Details of how consent was obtained
    
    # Consent from Devotee B (booking_b)
    consent_b_method = Column(String(50), nullable=True)
    consent_b_notes = Column(Text, nullable=True)
    
    # Admin notes (when approving/rejecting)
    admin_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    booking_a = relationship("SevaBooking", foreign_keys=[booking_a_id])
    booking_b = relationship("SevaBooking", foreign_keys=[booking_b_id])
    requested_by = relationship(
        "User",
        foreign_keys=[requested_by_id],
        primaryjoin="SevaExchangeRequest.requested_by_id == foreign(User.id)"
    )
    approved_by = relationship(
        "User",
        foreign_keys=[approved_by_id],
        primaryjoin="SevaExchangeRequest.approved_by_id == foreign(User.id)",
        overlaps="requested_by"
    )
























