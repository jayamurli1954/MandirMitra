"""
Financial Period Management Models
Handles financial year, month-end, and year-end closing
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class PeriodStatus(str, enum.Enum):
    """Financial period status"""
    OPEN = "open"
    CLOSED = "closed"
    LOCKED = "locked"


class ClosingType(str, enum.Enum):
    """Type of closing"""
    MONTH_END = "month_end"
    YEAR_END = "year_end"


class FinancialYear(Base):
    """Financial year definition"""
    __tablename__ = "financial_years"
    
    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # Financial year
    year_code = Column(String(10), nullable=False, unique=True, index=True)  # e.g., "2024-25"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Opening balances (carried forward from previous year)
    opening_balance_carried_forward = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    periods = relationship("FinancialPeriod", back_populates="financial_year", cascade="all, delete-orphan")
    closing_entries = relationship("PeriodClosing", back_populates="financial_year")


class FinancialPeriod(Base):
    """Monthly/Quarterly period within a financial year"""
    __tablename__ = "financial_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    financial_year_id = Column(Integer, ForeignKey("financial_years.id"), nullable=False, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # Period details
    period_name = Column(String(50), nullable=False)  # e.g., "April 2024", "Q1 2024-25"
    period_type = Column(String(20), nullable=False)  # "month", "quarter", "year"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(PeriodStatus), default=PeriodStatus.OPEN)
    is_locked = Column(Boolean, default=False)
    
    # Closing
    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    financial_year = relationship("FinancialYear", back_populates="periods")
    closing_entries = relationship("PeriodClosing", back_populates="period")


class PeriodClosing(Base):
    """Period closing record (month-end or year-end)"""
    __tablename__ = "period_closings"
    
    id = Column(Integer, primary_key=True, index=True)
    financial_year_id = Column(Integer, ForeignKey("financial_years.id"), nullable=False, index=True)
    period_id = Column(Integer, ForeignKey("financial_periods.id"), nullable=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # Closing details
    closing_type = Column(SQLEnum(ClosingType), nullable=False)
    closing_date = Column(Date, nullable=False, index=True)
    
    # Financial summary
    total_income = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    net_surplus = Column(Float, default=0.0)  # Income - Expenses
    
    # Closing journal entry
    closing_journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    
    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    financial_year = relationship("FinancialYear", back_populates="closing_entries")
    period = relationship("FinancialPeriod", back_populates="closing_entries")
    closing_journal_entry = relationship("JournalEntry")






