"""
Stock Audit Models
Handles stock audit, wastage recording, and related workflows
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    Date,
    ForeignKey,
    Enum as SQLEnum,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class AuditStatus(str, enum.Enum):
    """Stock audit status"""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    DISCREPANCY = "discrepancy"


class WastageReason(str, enum.Enum):
    """Reasons for wastage"""

    EXPIRED = "expired"
    DAMAGED = "damaged"
    SPOILED = "spoiled"
    THEFT = "theft"
    LOSS = "loss"
    OTHER = "other"


class StockAudit(Base):
    """Stock Audit Master"""

    __tablename__ = "stock_audits"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Audit Details
    audit_number = Column(String(50), unique=True, nullable=False, index=True)  # AUD/2025/001
    audit_date = Column(Date, nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)

    # Status
    status = Column(SQLEnum(AuditStatus), default=AuditStatus.DRAFT, index=True)

    # Audit Team
    conducted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Dates
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Summary
    total_items_audited = Column(Integer, default=0)
    items_with_discrepancy = Column(Integer, default=0)
    total_discrepancy_value = Column(Float, default=0.0)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    store = relationship("Store")
    conducted_by_user = relationship("User", foreign_keys=[conducted_by])
    verified_by_user = relationship("User", foreign_keys=[verified_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    audit_items = relationship(
        "StockAuditItem", back_populates="audit", cascade="all, delete-orphan"
    )


class StockAuditItem(Base):
    """Stock Audit Items"""

    __tablename__ = "stock_audit_items"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(
        Integer, ForeignKey("stock_audits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)

    # Book Balance (from system)
    book_quantity = Column(Float, nullable=False)
    book_value = Column(Float, nullable=False)

    # Physical Count (actual count)
    physical_quantity = Column(Float, nullable=False)
    physical_value = Column(Float, nullable=False)

    # Discrepancy
    quantity_discrepancy = Column(Float, default=0.0)  # physical - book
    value_discrepancy = Column(Float, default=0.0)

    # Reason for discrepancy (if any)
    discrepancy_reason = Column(Text, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit = relationship("StockAudit", back_populates="audit_items")
    item = relationship("Item")


class StockWastage(Base):
    """Stock Wastage Recording"""

    __tablename__ = "stock_wastages"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Wastage Details
    wastage_number = Column(String(50), unique=True, nullable=False, index=True)  # WST/2025/001
    wastage_date = Column(Date, nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)

    # Quantity and Value
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)

    # Reason
    reason = Column(SQLEnum(WastageReason), nullable=False)
    reason_details = Column(Text, nullable=True)

    # Approval
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Accounting
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    item = relationship("Item")
    store = relationship("Store")
    recorded_by_user = relationship("User", foreign_keys=[recorded_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    journal_entry = relationship("JournalEntry")
