"""
Pydantic Schemas for Tender Management
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# ===== TENDER SCHEMAS =====

class TenderBase(BaseModel):
    """Base schema for Tender"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    tender_type: Optional[str] = None  # ASSET_PROCUREMENT, INVENTORY_PURCHASE, CONSTRUCTION, SERVICE
    estimated_value: Optional[float] = Field(None, ge=0)
    tender_issue_date: date
    last_date_submission: date
    opening_date: Optional[date] = None
    terms_conditions: Optional[str] = None


class TenderCreate(TenderBase):
    """Schema for creating a tender"""
    pass


class TenderUpdate(BaseModel):
    """Schema for updating a tender"""
    title: Optional[str] = None
    description: Optional[str] = None
    tender_type: Optional[str] = None
    estimated_value: Optional[float] = Field(None, ge=0)
    tender_issue_date: Optional[date] = None
    last_date_submission: Optional[date] = None
    opening_date: Optional[date] = None
    award_date: Optional[date] = None
    status: Optional[str] = None  # draft, published, closed, awarded, cancelled
    terms_conditions: Optional[str] = None


class TenderResponse(TenderBase):
    """Schema for tender response"""
    id: int
    temple_id: int
    tender_number: str
    status: str
    award_date: Optional[date] = None
    tender_document_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    bids_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# ===== TENDER BID SCHEMAS =====

class TenderBidBase(BaseModel):
    """Base schema for Tender Bid"""
    bid_amount: float = Field(..., gt=0)
    bid_date: date
    validity_period_days: int = Field(default=90, ge=1, le=365)
    technical_specifications: Optional[str] = None


class TenderBidCreate(TenderBidBase):
    """Schema for creating a tender bid"""
    vendor_id: int
    tender_id: int


class TenderBidUpdate(BaseModel):
    """Schema for updating a tender bid"""
    bid_amount: Optional[float] = Field(None, gt=0)
    bid_date: Optional[date] = None
    validity_period_days: Optional[int] = Field(None, ge=1, le=365)
    status: Optional[str] = None  # submitted, shortlisted, rejected, awarded
    technical_specifications: Optional[str] = None
    technical_score: Optional[float] = Field(None, ge=0, le=100)
    financial_score: Optional[float] = Field(None, ge=0, le=100)
    total_score: Optional[float] = Field(None, ge=0, le=100)
    evaluation_notes: Optional[str] = None


class TenderBidResponse(TenderBidBase):
    """Schema for tender bid response"""
    id: int
    tender_id: int
    vendor_id: int
    status: str
    technical_score: Optional[float] = None
    financial_score: Optional[float] = None
    total_score: Optional[float] = None
    evaluation_notes: Optional[str] = None
    bid_document_path: Optional[str] = None
    created_at: datetime
    evaluated_at: Optional[datetime] = None
    evaluated_by: Optional[int] = None
    vendor_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# ===== TENDER EVALUATION SCHEMAS =====

class TenderEvaluationRequest(BaseModel):
    """Schema for evaluating tender bids"""
    bid_id: int
    technical_score: float = Field(..., ge=0, le=100)
    financial_score: float = Field(..., ge=0, le=100)
    evaluation_notes: Optional[str] = None


class TenderAwardRequest(BaseModel):
    """Schema for awarding a tender"""
    bid_id: int
    award_date: date
    notes: Optional[str] = None

