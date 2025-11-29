"""
Token Seva Models
Handles small-value seva items that use pre-printed serialized tokens instead of receipts
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum

class TokenStatus(str, enum.Enum):
    """Token status"""
    AVAILABLE = "available"
    SOLD = "sold"
    USED = "used"
    LOST = "lost"
    DAMAGED = "damaged"
    EXPIRED = "expired"

class PaymentMode(str, enum.Enum):
    """Payment modes for token sales"""
    CASH = "cash"
    UPI = "upi"

class TokenInventory(Base):
    """Pre-printed token inventory with serial number control"""
    __tablename__ = "token_inventory"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)
    seva_id = Column(Integer, ForeignKey("sevas.id"), nullable=False, index=True)
    
    # Token Details
    token_color = Column(String(50), nullable=False)  # Color code for this seva type
    serial_number = Column(String(50), nullable=False, unique=True, index=True)  # Pre-printed serial number
    token_number = Column(String(50), nullable=False)  # Display number (may be same as serial)
    
    # Status
    status = Column(SQLEnum(TokenStatus), default=TokenStatus.AVAILABLE, nullable=False, index=True)
    
    # Batch Information
    batch_number = Column(String(50), nullable=True, index=True)  # Batch when tokens were printed
    printed_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)  # Optional expiry
    
    # Sale Information (when sold)
    sold_at = Column(DateTime, nullable=True)
    sold_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Counter staff who sold
    counter_number = Column(String(20), nullable=True)  # Counter identifier
    
    # Usage Information (when used)
    used_at = Column(DateTime, nullable=True)
    used_by_devotee_id = Column(Integer, ForeignKey("devotees.id"), nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    temple = relationship("Temple")
    seva = relationship("Seva")
    sold_by_user = relationship("User", foreign_keys=[sold_by])
    used_by_devotee = relationship("Devotee", foreign_keys=[used_by_devotee_id])
    
    def __repr__(self):
        return f"<TokenInventory(id={self.id}, serial={self.serial_number}, status={self.status})>"


class TokenSale(Base):
    """Token sale/collection record"""
    __tablename__ = "token_sales"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)
    seva_id = Column(Integer, ForeignKey("sevas.id"), nullable=False, index=True)
    
    # Sale Details
    sale_date = Column(Date, nullable=False, index=True)
    sale_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Token Information
    token_id = Column(Integer, ForeignKey("token_inventory.id"), nullable=False)
    token_serial_number = Column(String(50), nullable=False, index=True)  # Denormalized for quick lookup
    
    # Payment
    amount = Column(Float, nullable=False)
    payment_mode = Column(SQLEnum(PaymentMode), nullable=False)
    upi_reference = Column(String(100), nullable=True)  # UPI transaction ID if payment_mode = UPI
    
    # Counter Information
    counter_number = Column(String(20), nullable=True, index=True)
    sold_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Devotee (optional - may be anonymous)
    devotee_id = Column(Integer, ForeignKey("devotees.id"), nullable=True)
    devotee_name = Column(String(200), nullable=True)  # Denormalized for quick reference
    devotee_phone = Column(String(20), nullable=True)
    
    # Accounting
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)  # Link to accounting
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    temple = relationship("Temple")
    seva = relationship("Seva")
    token = relationship("TokenInventory")
    sold_by_user = relationship("User", foreign_keys=[sold_by])
    devotee = relationship("Devotee")
    journal_entry = relationship("JournalEntry")
    
    def __repr__(self):
        return f"<TokenSale(id={self.id}, serial={self.token_serial_number}, amount={self.amount})>"


class TokenReconciliation(Base):
    """Daily token reconciliation"""
    __tablename__ = "token_reconciliations"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)
    
    # Reconciliation Date
    reconciliation_date = Column(Date, nullable=False, unique=True, index=True)
    
    # Token Counts by Seva
    # Stored as JSON: {seva_id: {available: X, sold: Y, used: Z, lost: W}}
    token_counts = Column(Text, nullable=True)  # JSON string
    
    # Sales Summary
    total_tokens_sold = Column(Integer, default=0)
    total_amount_cash = Column(Float, default=0.0)
    total_amount_upi = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    # Counter-wise Summary
    # Stored as JSON: {counter_number: {tokens_sold: X, cash: Y, upi: Z}}
    counter_summary = Column(Text, nullable=True)  # JSON string
    
    # Reconciliation Status
    is_reconciled = Column(Boolean, default=False)
    reconciled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reconciled_at = Column(DateTime, nullable=True)
    
    # Discrepancies
    discrepancy_notes = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    temple = relationship("Temple")
    reconciled_by_user = relationship("User", foreign_keys=[reconciled_by])
    
    def __repr__(self):
        return f"<TokenReconciliation(id={self.id}, date={self.reconciliation_date}, reconciled={self.is_reconciled})>"






