"""
Pydantic Schemas for Hundi Management
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.hundi import HundiStatus


# ===== HUNDI MASTER SCHEMAS =====

class HundiMasterBase(BaseModel):
    """Base schema for Hundi Master"""
    hundi_code: str = Field(..., min_length=1, max_length=50)
    hundi_name: str = Field(..., min_length=1, max_length=200)
    hundi_location: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    requires_verification: bool = True
    min_verifiers: int = Field(default=2, ge=1, le=3)
    default_bank_account_id: Optional[int] = None


class HundiMasterCreate(HundiMasterBase):
    """Schema for creating a hundi master"""
    pass


class HundiMasterUpdate(BaseModel):
    """Schema for updating a hundi master"""
    hundi_name: Optional[str] = None
    hundi_location: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    requires_verification: Optional[bool] = None
    min_verifiers: Optional[int] = None
    default_bank_account_id: Optional[int] = None


class HundiMasterResponse(HundiMasterBase):
    """Schema for hundi master response"""
    id: int
    temple_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== DENOMINATION COUNT SCHEMAS =====

class DenominationCountBase(BaseModel):
    """Base schema for denomination count"""
    denomination_value: float = Field(..., gt=0)
    denomination_type: str = Field(..., pattern="^(note|coin)$")
    currency: str = Field(default="INR", max_length=10)
    quantity: int = Field(..., ge=0)
    total_amount: float = Field(..., ge=0)
    notes: Optional[str] = None


class DenominationCountCreate(DenominationCountBase):
    """Schema for creating denomination count"""
    pass


class DenominationCountUpdate(BaseModel):
    """Schema for updating denomination count"""
    quantity: Optional[int] = Field(None, ge=0)
    total_amount: Optional[float] = Field(None, ge=0)
    verified: Optional[bool] = None
    notes: Optional[str] = None


class DenominationCountResponse(DenominationCountBase):
    """Schema for denomination count response"""
    id: int
    hundi_opening_id: int
    counted_by_user_id: Optional[int]
    counted_at: datetime
    verified: bool
    verified_by_user_id: Optional[int]
    verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== HUNDI OPENING SCHEMAS =====

class HundiOpeningBase(BaseModel):
    """Base schema for Hundi Opening"""
    hundi_code: str = Field(..., min_length=1, max_length=50)
    hundi_name: Optional[str] = None
    hundi_location: Optional[str] = None
    scheduled_date: date
    scheduled_time: Optional[str] = None
    sealed_number: Optional[str] = None
    notes: Optional[str] = None


class HundiOpeningCreate(HundiOpeningBase):
    """Schema for creating a hundi opening"""
    pass


class HundiOpeningUpdate(BaseModel):
    """Schema for updating a hundi opening"""
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[str] = None
    actual_opened_date: Optional[date] = None
    actual_opened_time: Optional[str] = None
    sealed_number: Optional[str] = None
    status: Optional[HundiStatus] = None
    notes: Optional[str] = None
    has_discrepancy: Optional[bool] = None
    discrepancy_amount: Optional[float] = None
    discrepancy_reason: Optional[str] = None
    bank_account_id: Optional[int] = None
    bank_deposit_date: Optional[date] = None
    bank_deposit_reference: Optional[str] = None
    bank_deposit_amount: Optional[float] = None


class HundiOpeningResponse(HundiOpeningBase):
    """Schema for hundi opening response"""
    id: int
    temple_id: Optional[int]
    actual_opened_date: Optional[date]
    actual_opened_time: Optional[str]
    status: HundiStatus
    total_amount: float
    counting_started_at: Optional[datetime]
    counting_completed_at: Optional[datetime]
    verified_by_user_1_id: Optional[int]
    verified_by_user_2_id: Optional[int]
    verified_by_user_3_id: Optional[int]
    verified_at: Optional[datetime]
    has_discrepancy: bool
    discrepancy_amount: float
    discrepancy_reason: Optional[str]
    discrepancy_resolved: bool
    bank_account_id: Optional[int]
    bank_deposit_date: Optional[date]
    bank_deposit_reference: Optional[str]
    bank_deposit_amount: Optional[float]
    journal_entry_id: Optional[int]
    reconciled: bool
    reconciled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    
    # Related data
    denomination_counts: List[DenominationCountResponse] = []
    verified_by_user_1_name: Optional[str] = None
    verified_by_user_2_name: Optional[str] = None
    verified_by_user_3_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class HundiOpeningListResponse(BaseModel):
    """Schema for listing hundi openings"""
    id: int
    hundi_code: str
    hundi_name: Optional[str]
    scheduled_date: date
    status: HundiStatus
    total_amount: float
    verified: bool
    deposited: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== COUNTING SCHEMAS =====

class StartCountingRequest(BaseModel):
    """Schema for starting counting"""
    pass


class CompleteCountingRequest(BaseModel):
    """Schema for completing counting"""
    denomination_counts: List[DenominationCountCreate]
    notes: Optional[str] = None


class VerifyCountingRequest(BaseModel):
    """Schema for verifying counting"""
    verified_by_user_2_id: Optional[int] = None
    verified_by_user_3_id: Optional[int] = None
    notes: Optional[str] = None


class ReportDiscrepancyRequest(BaseModel):
    """Schema for reporting discrepancy"""
    discrepancy_amount: float
    discrepancy_reason: str


class ResolveDiscrepancyRequest(BaseModel):
    """Schema for resolving discrepancy"""
    resolution_notes: str


class RecordBankDepositRequest(BaseModel):
    """Schema for recording bank deposit"""
    bank_account_id: int
    bank_deposit_date: date
    bank_deposit_reference: str
    bank_deposit_amount: float
    notes: Optional[str] = None


class ReconcileHundiRequest(BaseModel):
    """Schema for reconciling hundi"""
    notes: Optional[str] = None


# ===== REPORT SCHEMAS =====

class HundiReportResponse(BaseModel):
    """Schema for hundi report"""
    from_date: date
    to_date: date
    total_openings: int
    total_amount: float
    total_deposited: float
    total_pending: float
    hundi_wise_breakdown: List[dict]
    daily_breakdown: List[dict]
    denomination_wise_summary: List[dict]
