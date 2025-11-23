"""
Pydantic Schemas for Vendor Management
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class VendorBase(BaseModel):
    """Base schema for Vendor"""
    vendor_name: str
    vendor_type: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    alternate_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gstin: Optional[str] = None
    pan_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    account_holder_name: Optional[str] = None
    service_categories: Optional[str] = None
    rating: Optional[int] = None
    notes: Optional[str] = None
    is_preferred: bool = False


class VendorCreate(VendorBase):
    """Schema for creating a vendor"""
    temple_id: int


class VendorUpdate(BaseModel):
    """Schema for updating a vendor"""
    vendor_name: Optional[str] = None
    vendor_type: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    alternate_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gstin: Optional[str] = None
    pan_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    account_holder_name: Optional[str] = None
    service_categories: Optional[str] = None
    rating: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    is_preferred: Optional[bool] = None


class VendorResponse(VendorBase):
    """Schema for vendor response"""
    id: int
    temple_id: int
    vendor_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
