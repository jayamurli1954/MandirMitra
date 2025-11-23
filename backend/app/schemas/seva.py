"""
Seva API Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class SevaCategory(str, Enum):
    abhisheka = "abhisheka"
    alankara = "alankara"
    pooja = "pooja"
    archana = "archana"
    vahana_seva = "vahana_seva"
    special = "special"
    festival = "festival"

class SevaAvailability(str, Enum):
    daily = "daily"
    weekday = "weekday"
    weekend = "weekend"
    specific_day = "specific_day"
    except_day = "except_day"
    festival_only = "festival_only"

class SevaBookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"

# Seva Schemas
class SevaBase(BaseModel):
    name_english: str = Field(..., max_length=200)
    name_kannada: Optional[str] = Field(None, max_length=200)
    name_sanskrit: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: SevaCategory
    amount: float = Field(..., gt=0)
    min_amount: Optional[float] = Field(None, gt=0)
    max_amount: Optional[float] = Field(None, gt=0)
    availability: SevaAvailability = SevaAvailability.daily
    specific_day: Optional[int] = Field(None, ge=0, le=6)  # 0=Sunday, 6=Saturday
    except_day: Optional[int] = Field(None, ge=0, le=6)
    time_slot: Optional[str] = Field(None, max_length=50)
    max_bookings_per_day: Optional[int] = Field(None, gt=0)
    advance_booking_days: int = Field(30, ge=0)
    requires_approval: bool = False
    is_active: bool = True
    benefits: Optional[str] = None
    instructions: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)

class SevaCreate(SevaBase):
    pass

class SevaUpdate(BaseModel):
    name_english: Optional[str] = Field(None, max_length=200)
    name_kannada: Optional[str] = Field(None, max_length=200)
    name_sanskrit: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[SevaCategory] = None
    amount: Optional[float] = Field(None, gt=0)
    min_amount: Optional[float] = Field(None, gt=0)
    max_amount: Optional[float] = Field(None, gt=0)
    availability: Optional[SevaAvailability] = None
    specific_day: Optional[int] = Field(None, ge=0, le=6)
    except_day: Optional[int] = Field(None, ge=0, le=6)
    time_slot: Optional[str] = Field(None, max_length=50)
    max_bookings_per_day: Optional[int] = Field(None, gt=0)
    advance_booking_days: Optional[int] = Field(None, ge=0)
    requires_approval: Optional[bool] = None
    is_active: Optional[bool] = None
    benefits: Optional[str] = None
    instructions: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)

class SevaResponse(SevaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Seva Booking Schemas
class SevaBookingBase(BaseModel):
    seva_id: int
    devotee_id: int
    booking_date: date
    booking_time: Optional[str] = Field(None, max_length=50)
    amount_paid: float = Field(..., gt=0)
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_reference: Optional[str] = Field(None, max_length=100)
    devotee_names: Optional[str] = None
    gotra: Optional[str] = Field(None, max_length=100)
    nakshatra: Optional[str] = Field(None, max_length=50)
    rashi: Optional[str] = Field(None, max_length=50)
    special_request: Optional[str] = None

class SevaBookingCreate(SevaBookingBase):
    pass

class SevaBookingUpdate(BaseModel):
    booking_date: Optional[date] = None
    booking_time: Optional[str] = Field(None, max_length=50)
    status: Optional[SevaBookingStatus] = None
    amount_paid: Optional[float] = Field(None, gt=0)
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_reference: Optional[str] = Field(None, max_length=100)
    receipt_number: Optional[str] = Field(None, max_length=100)
    devotee_names: Optional[str] = None
    gotra: Optional[str] = Field(None, max_length=100)
    nakshatra: Optional[str] = Field(None, max_length=50)
    rashi: Optional[str] = Field(None, max_length=50)
    special_request: Optional[str] = None
    admin_notes: Optional[str] = None

class SevaBookingResponse(SevaBookingBase):
    id: int
    user_id: Optional[int]
    status: SevaBookingStatus
    receipt_number: Optional[str]
    admin_notes: Optional[str]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Nested relationships
    seva: Optional[SevaResponse] = None

    class Config:
        from_attributes = True

class SevaListResponse(BaseModel):
    """Response for seva listing with booking availability"""
    id: int
    name_english: str
    name_kannada: Optional[str]
    name_sanskrit: Optional[str]
    description: Optional[str]
    category: SevaCategory
    amount: float
    min_amount: Optional[float]
    max_amount: Optional[float]
    availability: SevaAvailability
    specific_day: Optional[int]
    except_day: Optional[int]
    time_slot: Optional[str]
    is_active: bool
    is_available_today: bool = False
    bookings_available: Optional[int] = None

    class Config:
        from_attributes = True
