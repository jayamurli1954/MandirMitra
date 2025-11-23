"""
Pydantic Schemas for Sponsorships
Devotees sponsoring specific temple expenses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.models.inkind_sponsorship import SponsorshipPaymentMode, SponsorshipStatus


# ===== SPONSORSHIP SCHEMAS =====

class SponsorshipBase(BaseModel):
    """Base schema for Sponsorship"""
    devotee_id: int
    sponsorship_category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    committed_amount: float = Field(..., gt=0)
    payment_mode: SponsorshipPaymentMode
    event_name: Optional[str] = None
    event_date: Optional[date] = None


class SponsorshipCreate(SponsorshipBase):
    """Schema for creating sponsorship"""
    temple_id: int
    receipt_date: datetime = Field(default_factory=datetime.utcnow)

    # For Direct Payment Mode
    vendor_id: Optional[int] = None
    vendor_invoice_number: Optional[str] = None
    vendor_invoice_date: Optional[date] = None
    vendor_invoice_amount: Optional[float] = None
    vendor_invoice_document_url: Optional[str] = None


class SponsorshipUpdate(BaseModel):
    """Schema for updating sponsorship"""
    sponsorship_category: Optional[str] = None
    description: Optional[str] = None
    committed_amount: Optional[float] = None
    status: Optional[SponsorshipStatus] = None
    event_name: Optional[str] = None
    event_date: Optional[date] = None
    vendor_id: Optional[int] = None
    vendor_invoice_number: Optional[str] = None
    vendor_invoice_date: Optional[date] = None
    vendor_invoice_amount: Optional[float] = None
    vendor_invoice_document_url: Optional[str] = None


class SponsorshipResponse(SponsorshipBase):
    """Schema for sponsorship response"""
    id: int
    temple_id: int
    receipt_number: str
    receipt_date: datetime
    amount_paid: float
    status: SponsorshipStatus
    fulfilled_date: Optional[datetime] = None
    vendor_id: Optional[int] = None
    vendor_invoice_number: Optional[str] = None
    vendor_invoice_date: Optional[date] = None
    vendor_invoice_amount: Optional[float] = None
    vendor_invoice_document_url: Optional[str] = None
    journal_entry_id_commitment: Optional[int] = None
    journal_entry_id_payment: Optional[int] = None
    journal_entry_id_expense: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # Dynamic fields (populated by API)
    devotee_name: Optional[str] = None
    vendor_name: Optional[str] = None

    class Config:
        from_attributes = True


class SponsorshipFulfill(BaseModel):
    """Schema for fulfilling a sponsorship"""
    fulfilled_date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


# ===== SPONSORSHIP PAYMENT SCHEMAS =====

class SponsorshipPaymentBase(BaseModel):
    """Base schema for Sponsorship Payment"""
    sponsorship_id: int
    amount_paid: float = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1, max_length=50)
    transaction_reference: Optional[str] = None


class SponsorshipPaymentCreate(SponsorshipPaymentBase):
    """Schema for creating sponsorship payment"""
    temple_id: int
    payment_date: datetime = Field(default_factory=datetime.utcnow)


class SponsorshipPaymentResponse(SponsorshipPaymentBase):
    """Schema for sponsorship payment response"""
    id: int
    temple_id: int
    payment_date: datetime
    journal_entry_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===== DIRECT PAYMENT SCHEMA =====

class DirectPaymentRecord(BaseModel):
    """Schema for recording direct vendor payment by devotee"""
    vendor_invoice_number: str
    vendor_invoice_date: date
    vendor_invoice_amount: float = Field(..., gt=0)
    vendor_invoice_document_url: Optional[str] = None
    payment_date: datetime = Field(default_factory=datetime.utcnow)
