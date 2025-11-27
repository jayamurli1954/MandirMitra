"""
Budget Management Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from app.models.budget import BudgetStatus, BudgetType


class BudgetItemBase(BaseModel):
    account_id: int
    budgeted_amount: float = Field(..., gt=0)
    notes: Optional[str] = None


class BudgetItemCreate(BudgetItemBase):
    pass


class BudgetItemUpdate(BaseModel):
    budgeted_amount: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None


class BudgetItemResponse(BudgetItemBase):
    id: int
    budget_id: int
    account_code: Optional[str] = None
    account_name: Optional[str] = None
    actual_amount: Optional[float] = 0.0
    variance: Optional[float] = 0.0
    variance_percentage: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    budget_name: str = Field(..., max_length=200)
    budget_type: BudgetType = BudgetType.ANNUAL
    budget_period_start: date
    budget_period_end: date
    financial_year_id: int
    notes: Optional[str] = None


class BudgetCreate(BudgetBase):
    budget_items: List[BudgetItemCreate] = []


class BudgetUpdate(BaseModel):
    budget_name: Optional[str] = Field(None, max_length=200)
    budget_type: Optional[BudgetType] = None
    budget_period_start: Optional[date] = None
    budget_period_end: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[BudgetStatus] = None


class BudgetResponse(BudgetBase):
    id: int
    temple_id: Optional[int] = None
    status: BudgetStatus
    total_budgeted_amount: float
    total_actual_amount: Optional[float] = 0.0
    total_variance: Optional[float] = 0.0
    submitted_by: Optional[int] = None
    submitted_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    budget_items: List[BudgetItemResponse] = []
    
    class Config:
        from_attributes = True


class BudgetApprovalRequest(BaseModel):
    approve: bool = True
    rejection_reason: Optional[str] = None


class BudgetVsActualResponse(BaseModel):
    """Budget vs Actual comparison report"""
    budget_id: int
    budget_name: str
    period_start: date
    period_end: date
    total_budgeted: float
    total_actual: float
    total_variance: float
    total_variance_percentage: float
    items: List[BudgetItemResponse]
    
    class Config:
        from_attributes = True

