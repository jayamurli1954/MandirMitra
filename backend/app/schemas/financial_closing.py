"""
Financial Closing Schemas
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class ClosingType(str, Enum):
    month_end = "month_end"
    year_end = "year_end"


class FinancialYearCreate(BaseModel):
    year_code: str  # e.g., "2024-25"
    start_date: date
    end_date: date


class FinancialYearResponse(BaseModel):
    id: int
    year_code: str
    start_date: date
    end_date: date
    is_active: bool
    is_closed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PeriodClosingRequest(BaseModel):
    financial_year_id: int
    closing_date: date
    notes: Optional[str] = None


class PeriodClosingResponse(BaseModel):
    id: int
    financial_year_id: int
    closing_type: ClosingType
    closing_date: date
    total_income: float
    total_expenses: float
    net_surplus: float
    is_completed: bool
    completed_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


class ClosingSummaryResponse(BaseModel):
    period_start: date
    period_end: date
    total_income: float
    total_expenses: float
    net_surplus: float
    transaction_count: int


