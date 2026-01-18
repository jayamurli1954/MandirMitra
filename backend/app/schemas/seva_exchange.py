"""
Seva Exchange Request Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class ExchangeRequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class ConsentMethod(str, Enum):
    in_person = "in_person"
    phone = "phone"
    whatsapp = "whatsapp"
    email = "email"
    other = "other"


class BookingSummary(BaseModel):
    """Summary of a booking for exchange display"""
    id: int
    devotee_name: str
    devotee_mobile: Optional[str] = None
    seva_name: str
    booking_date: date
    receipt_number: Optional[str] = None
    
    class Config:
        from_attributes = True


class SevaExchangeRequestCreate(BaseModel):
    """Schema for creating an exchange request (clerk)"""
    booking_a_id: int = Field(..., description="First booking ID")
    booking_b_id: int = Field(..., description="Second booking ID")
    reason: str = Field(..., min_length=10, description="Reason for exchange (min 10 characters)")
    consent_a_method: ConsentMethod = Field(..., description="How consent was obtained from Devotee A")
    consent_a_notes: str = Field(..., min_length=5, description="Details of consent from Devotee A")
    consent_b_method: ConsentMethod = Field(..., description="How consent was obtained from Devotee B")
    consent_b_notes: str = Field(..., min_length=5, description="Details of consent from Devotee B")


class ExchangeDecision(BaseModel):
    """Schema for admin decision on exchange request"""
    status: ExchangeRequestStatus = Field(..., description="approve or reject")
    admin_notes: Optional[str] = Field(None, description="Admin notes (optional)")


class SevaExchangeRequestResponse(BaseModel):
    """Full exchange request response"""
    id: int
    booking_a_id: int
    booking_b_id: int
    reason: str
    status: ExchangeRequestStatus
    requested_by_id: int
    approved_by_id: Optional[int] = None
    consent_a_method: Optional[str] = None
    consent_a_notes: Optional[str] = None
    consent_b_method: Optional[str] = None
    consent_b_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    
    # Embedded booking summaries
    booking_a: Optional[BookingSummary] = None
    booking_b: Optional[BookingSummary] = None
    requested_by_name: Optional[str] = None
    approved_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SevaExchangeRequestListResponse(BaseModel):
    """List response with pagination"""
    items: List[SevaExchangeRequestResponse]
    total: int
    page: int = 1
    page_size: int = 20
























