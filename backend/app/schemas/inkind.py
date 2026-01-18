"""
Pydantic Schemas for In-Kind Donations
Non-monetary donations like rice, gold, furniture, etc.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.models.inkind_sponsorship import InKindDonationType, InKindStatus


# ===== IN-KIND DONATION SCHEMAS =====


class InKindDonationBase(BaseModel):
    """Base schema for In-Kind Donation"""

    devotee_id: int
    donation_type: InKindDonationType
    item_name: str = Field(..., min_length=1, max_length=200)
    item_category: Optional[str] = Field(None, max_length=100)
    item_description: Optional[str] = None
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    value_assessed: float = Field(..., ge=0)
    value_per_unit: Optional[float] = Field(None, ge=0)
    purpose: Optional[str] = None


class InKindDonationCreate(InKindDonationBase):
    """Schema for creating in-kind donation"""

    temple_id: int
    receipt_date: datetime = Field(default_factory=datetime.utcnow)

    # For Precious Items
    purity: Optional[str] = None
    weight_gross: Optional[float] = None
    weight_net: Optional[float] = None
    appraised_by: Optional[str] = None
    appraisal_date: Optional[date] = None

    # Photos/Documents
    photo_url: Optional[str] = None
    document_url: Optional[str] = None


class InKindDonationUpdate(BaseModel):
    """Schema for updating in-kind donation"""

    item_name: Optional[str] = None
    item_category: Optional[str] = None
    item_description: Optional[str] = None
    quantity: Optional[float] = None
    value_assessed: Optional[float] = None
    value_per_unit: Optional[float] = None
    status: Optional[InKindStatus] = None
    purpose: Optional[str] = None
    photo_url: Optional[str] = None
    document_url: Optional[str] = None
    purity: Optional[str] = None
    weight_gross: Optional[float] = None
    weight_net: Optional[float] = None
    appraised_by: Optional[str] = None
    appraisal_date: Optional[date] = None


class InKindDonationResponse(InKindDonationBase):
    """Schema for in-kind donation response"""

    id: int
    temple_id: int
    receipt_number: str
    receipt_date: datetime
    current_balance: float
    consumed_quantity: float
    status: InKindStatus
    purity: Optional[str] = None
    weight_gross: Optional[float] = None
    weight_net: Optional[float] = None
    appraised_by: Optional[str] = None
    appraisal_date: Optional[date] = None
    photo_url: Optional[str] = None
    document_url: Optional[str] = None
    journal_entry_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # Dynamic fields (populated by API)
    devotee_name: Optional[str] = None

    class Config:
        from_attributes = True


# ===== IN-KIND CONSUMPTION SCHEMAS =====


class InKindConsumptionBase(BaseModel):
    """Base schema for In-Kind Consumption"""

    inkind_donation_id: int
    consumption_date: datetime = Field(default_factory=datetime.utcnow)
    quantity_consumed: float = Field(..., gt=0)
    purpose: Optional[str] = None
    event_name: Optional[str] = None
    event_date: Optional[date] = None


class InKindConsumptionCreate(InKindConsumptionBase):
    """Schema for creating consumption record"""

    temple_id: int


class InKindConsumptionResponse(InKindConsumptionBase):
    """Schema for consumption response"""

    id: int
    temple_id: int
    journal_entry_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===== INVENTORY SUMMARY SCHEMA =====


class InventoryItem(BaseModel):
    """Inventory summary item"""

    item_name: str
    item_category: str
    total_quantity: float
    consumed_quantity: float
    current_balance: float
    unit: str
    total_value: float
    donation_count: int


class InventorySummary(BaseModel):
    """Inventory summary by type"""

    donation_type: InKindDonationType
    items: list[InventoryItem]
    total_value: float
    total_items: int
