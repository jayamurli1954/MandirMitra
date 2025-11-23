"""
Pydantic Schemas for UPI Payment Logging
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.upi_banking import UpiPaymentPurpose


class UpiPaymentBase(BaseModel):
    """Base schema for UPI Payment"""
    amount: float
    payment_datetime: datetime
    sender_upi_id: Optional[str] = None
    sender_phone: Optional[str] = None
    upi_reference_number: Optional[str] = None
    payment_purpose: UpiPaymentPurpose
    notes: Optional[str] = None


class UpiPaymentCreate(UpiPaymentBase):
    """Schema for creating/logging a UPI payment"""
    temple_id: int
    devotee_id: int
    # Optional: Link to specific transaction
    donation_id: Optional[int] = None
    seva_booking_id: Optional[int] = None
    sponsorship_id: Optional[int] = None


class UpiPaymentQuickLog(BaseModel):
    """
    Quick logging schema for UPI payments (simplified for mobile entry)
    Admin logs payment immediately after receiving SMS
    """
    amount: float
    sender_phone: str  # Will be extracted from UPI ID
    devotee_id: int
    payment_purpose: UpiPaymentPurpose
    # Optional fields
    seva_id: Optional[int] = None  # If purpose is SEVA
    sponsorship_id: Optional[int] = None  # If purpose is SPONSORSHIP
    upi_reference_number: Optional[str] = None
    notes: Optional[str] = None


class UpiPaymentResponse(UpiPaymentBase):
    """Schema for UPI payment response"""
    id: int
    temple_id: int
    devotee_id: int
    devotee_name: Optional[str] = None
    receipt_number: Optional[str] = None
    donation_id: Optional[int] = None
    seva_booking_id: Optional[int] = None
    sponsorship_id: Optional[int] = None
    is_bank_reconciled: bool
    bank_statement_matched_at: Optional[datetime] = None
    journal_entry_id: Optional[int] = None
    logged_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DailyUpiSummary(BaseModel):
    """Daily summary of UPI payments"""
    date: str
    total_amount: float
    total_count: int
    by_purpose: dict
    reconciled_count: int
    unreconciled_count: int
