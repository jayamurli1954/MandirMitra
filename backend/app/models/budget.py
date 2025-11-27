"""
Budget Management Models
Handles budget creation, tracking, and Budget vs Actual reports
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class BudgetStatus(str, enum.Enum):
    """Budget status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    CLOSED = "closed"


class BudgetType(str, enum.Enum):
    """Type of budget"""
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"


class Budget(Base):
    """Budget master"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    financial_year_id = Column(Integer, ForeignKey("financial_years.id"), nullable=False, index=True)
    
    # Budget details
    budget_name = Column(String(200), nullable=False)
    budget_type = Column(SQLEnum(BudgetType), nullable=False, default=BudgetType.ANNUAL)
    budget_period_start = Column(Date, nullable=False)
    budget_period_end = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(BudgetStatus), default=BudgetStatus.DRAFT)
    
    # Approval
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Totals
    total_budgeted_amount = Column(Float, default=0.0)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    temple = relationship("Temple")
    financial_year = relationship("FinancialYear")
    budget_items = relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")
    created_by_user = relationship("User", foreign_keys=[created_by])
    submitted_by_user = relationship("User", foreign_keys=[submitted_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])


class BudgetItem(Base):
    """Individual budget items (account-wise)"""
    __tablename__ = "budget_items"
    
    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    
    # Budget amounts
    budgeted_amount = Column(Float, nullable=False, default=0.0)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    budget = relationship("Budget", back_populates="budget_items")
    account = relationship("Account")


class BudgetRevision(Base):
    """Budget revision history"""
    __tablename__ = "budget_revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Revision details
    revision_number = Column(Integer, nullable=False)
    revision_date = Column(Date, nullable=False)
    revision_reason = Column(Text, nullable=True)
    
    # Previous and new totals
    previous_total = Column(Float, default=0.0)
    new_total = Column(Float, default=0.0)
    
    # Revised by
    revised_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    revised_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    budget = relationship("Budget")
    revised_by_user = relationship("User", foreign_keys=[revised_by])

