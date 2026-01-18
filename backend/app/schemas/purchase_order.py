"""
Purchase Order, GRN, GIN Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from app.models.purchase_order import POStatus, GRNStatus, GINStatus


# ===== PURCHASE ORDER SCHEMAS =====


class POItemBase(BaseModel):
    item_id: int
    ordered_quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    store_id: int
    notes: Optional[str] = None


class POItemCreate(POItemBase):
    pass


class POItemResponse(POItemBase):
    id: int
    po_id: int
    received_quantity: float
    pending_quantity: float
    total_amount: float
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    unit: Optional[str] = None

    class Config:
        from_attributes = True


class POBase(BaseModel):
    po_date: date
    vendor_id: int
    expected_delivery_date: Optional[date] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


class POCreate(POBase):
    items: List[POItemCreate] = Field(..., min_items=1)


class POUpdate(BaseModel):
    expected_delivery_date: Optional[date] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


class POResponse(POBase):
    id: int
    temple_id: Optional[int] = None
    po_number: str
    status: POStatus
    total_amount: float
    tax_amount: float
    grand_total: float
    requested_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    vendor_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[POItemResponse] = []

    class Config:
        from_attributes = True


class POApprovalRequest(BaseModel):
    approve: bool = True
    rejection_reason: Optional[str] = None


# ===== GRN SCHEMAS =====


class GRNItemBase(BaseModel):
    item_id: int
    ordered_quantity: float = Field(..., gt=0)
    received_quantity: float = Field(..., gt=0)
    accepted_quantity: float = Field(..., gt=0)
    rejected_quantity: float = Field(0.0, ge=0)
    unit_price: float = Field(..., gt=0)
    store_id: int
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    quality_checked: bool = False
    quality_notes: Optional[str] = None
    notes: Optional[str] = None


class GRNItemCreate(GRNItemBase):
    po_item_id: Optional[int] = None  # Link to PO item if created from PO


class GRNItemResponse(GRNItemBase):
    id: int
    grn_id: int
    total_amount: float
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    unit: Optional[str] = None

    class Config:
        from_attributes = True


class GRNBase(BaseModel):
    grn_date: date
    po_id: Optional[int] = None
    vendor_id: int
    bill_number: Optional[str] = None
    bill_date: Optional[date] = None
    notes: Optional[str] = None


class GRNCreate(GRNBase):
    items: List[GRNItemCreate] = Field(..., min_items=1)


class GRNResponse(GRNBase):
    id: int
    temple_id: Optional[int] = None
    grn_number: str
    status: GRNStatus
    total_amount: float
    received_by: Optional[int] = None
    received_at: Optional[datetime] = None
    vendor_name: Optional[str] = None
    po_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[GRNItemResponse] = []

    class Config:
        from_attributes = True


# ===== GIN SCHEMAS =====


class GINItemBase(BaseModel):
    item_id: int
    requested_quantity: float = Field(..., gt=0)
    issued_quantity: float = Field(..., gt=0)
    notes: Optional[str] = None


class GINItemCreate(GINItemBase):
    pass


class GINItemResponse(GINItemBase):
    id: int
    gin_id: int
    unit_cost: float
    total_cost: float
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    unit: Optional[str] = None

    class Config:
        from_attributes = True


class GINBase(BaseModel):
    gin_date: date
    issued_from_store_id: int
    issued_to: str = Field(..., max_length=200)
    purpose: str = Field(..., max_length=200)
    notes: Optional[str] = None


class GINCreate(GINBase):
    items: List[GINItemCreate] = Field(..., min_items=1)


class GINUpdate(BaseModel):
    issued_to: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None


class GINResponse(GINBase):
    id: int
    temple_id: Optional[int] = None
    gin_number: str
    status: GINStatus
    requested_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    issued_by: Optional[int] = None
    issued_at: Optional[datetime] = None
    store_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[GINItemResponse] = []

    class Config:
        from_attributes = True


class GINApprovalRequest(BaseModel):
    approve: bool = True
