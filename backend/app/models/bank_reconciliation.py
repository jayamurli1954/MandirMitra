"""
Bank Reconciliation Models
Handles bank statement import, matching, and reconciliation
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    Date,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship, foreign
from datetime import datetime
import enum

from app.core.database import Base


class ReconciliationStatus(str, enum.Enum):
    """Reconciliation status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RECONCILED = "reconciled"
    DISCREPANCY = "discrepancy"


class StatementEntryType(str, enum.Enum):
    """Bank statement entry type"""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    CHEQUE = "cheque"
    TRANSFER = "transfer"
    CHARGES = "charges"
    INTEREST = "interest"


class BankStatement(Base):
    """Imported bank statement"""

    __tablename__ = "bank_statements"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Statement period
    statement_date = Column(Date, nullable=False, index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)

    # Statement details
    opening_balance = Column(Float, nullable=False)
    closing_balance = Column(Float, nullable=False)

    # Import metadata
    imported_at = Column(DateTime, default=datetime.utcnow)
    imported_by = Column(Integer, ForeignKey("users.id"))
    source_file = Column(String(500))  # Original file name

    # Status
    is_reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime, nullable=True)
    reconciled_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    account = relationship("Account")
    entries = relationship(
        "BankStatementEntry", back_populates="statement", cascade="all, delete-orphan"
    )
    reconciliation = relationship("BankReconciliation", back_populates="statement", uselist=False)


class BankStatementEntry(Base):
    """Individual entry in bank statement"""

    __tablename__ = "bank_statement_entries"

    id = Column(Integer, primary_key=True, index=True)
    statement_id = Column(Integer, ForeignKey("bank_statements.id"), nullable=False, index=True)

    # Transaction details
    transaction_date = Column(Date, nullable=False, index=True)
    value_date = Column(Date, nullable=True)  # Value date (when money actually moves)
    entry_type = Column(SQLEnum(StatementEntryType), nullable=False)
    amount = Column(Float, nullable=False)

    # Description and reference
    description = Column(Text, nullable=True)
    reference_number = Column(String(100))  # Cheque number, UPI ref, etc.
    narration = Column(Text, nullable=True)

    # Balance
    balance_after = Column(Float, nullable=True)  # Balance after this transaction

    # Matching
    is_matched = Column(Boolean, default=False)
    matched_journal_line_id = Column(Integer, ForeignKey("journal_lines.id"), nullable=True)
    matched_at = Column(DateTime, nullable=True)
    matched_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Manual notes
    notes = Column(Text, nullable=True)

    # Relationships
    statement = relationship("BankStatement", back_populates="entries")
    matched_journal_line = relationship("JournalLine")


class BankReconciliation(Base):
    """Bank reconciliation record"""

    __tablename__ = "bank_reconciliations"

    id = Column(Integer, primary_key=True, index=True)
    # Note: id is used as remote_side for many-to-one relationships
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    statement_id = Column(Integer, ForeignKey("bank_statements.id"), nullable=False, unique=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Reconciliation period
    reconciliation_date = Column(Date, nullable=False, index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)

    # Book balances
    book_balance_as_on = Column(Float, nullable=False)  # Balance as per books
    book_opening_balance = Column(Float, nullable=False)

    # Bank balances
    bank_balance_as_per_statement = Column(Float, nullable=False)
    bank_opening_balance = Column(Float, nullable=False)

    # Adjustments
    deposits_in_transit = Column(Float, default=0.0)  # Deposits not yet credited
    cheques_issued_not_cleared = Column(Float, default=0.0)  # Cheques not yet cleared
    bank_charges_not_recorded = Column(Float, default=0.0)
    interest_credited_not_recorded = Column(Float, default=0.0)
    other_adjustments = Column(Float, default=0.0)

    # Calculated
    adjusted_book_balance = Column(Float, nullable=False)
    adjusted_bank_balance = Column(Float, nullable=False)
    difference = Column(Float, default=0.0)  # Should be 0 if reconciled

    # Status
    status = Column(SQLEnum(ReconciliationStatus), default=ReconciliationStatus.PENDING)

    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    discrepancy_notes = Column(Text, nullable=True)

    # Relationships
    account = relationship("Account")
    statement = relationship("BankStatement", back_populates="reconciliation")
    # One-to-many relationship: one reconciliation has many items
    outstanding_items = relationship(
        "ReconciliationOutstandingItem",
        foreign_keys="[ReconciliationOutstandingItem.reconciliation_id]",
        back_populates="reconciliation",
        cascade="all, delete-orphan",
    )


class ReconciliationOutstandingItem(Base):
    """Outstanding items from reconciliation (cheques not cleared, deposits not credited)"""

    __tablename__ = "reconciliation_outstanding_items"

    id = Column(Integer, primary_key=True, index=True)
    reconciliation_id = Column(
        Integer, ForeignKey("bank_reconciliations.id"), nullable=False, index=True
    )

    # Item details
    item_type = Column(
        String(50), nullable=False
    )  # "cheque_issued", "deposit_in_transit", "bank_charge", etc.
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    # Reference
    reference_number = Column(String(100))  # Cheque number, transaction ID, etc.
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    statement_entry_id = Column(Integer, ForeignKey("bank_statement_entries.id"), nullable=True)

    # Status
    is_cleared = Column(Boolean, default=False)
    cleared_at = Column(DateTime, nullable=True)
    cleared_in_reconciliation_id = Column(
        Integer, ForeignKey("bank_reconciliations.id"), nullable=True
    )

    # Notes
    notes = Column(Text, nullable=True)

    # Relationships
    # Many-to-one relationship: many items belong to one reconciliation
    reconciliation = relationship(
        "BankReconciliation", foreign_keys=[reconciliation_id], back_populates="outstanding_items"
    )
    cleared_in_reconciliation = relationship(
        "BankReconciliation",
        foreign_keys=[cleared_in_reconciliation_id],
        primaryjoin="ReconciliationOutstandingItem.cleared_in_reconciliation_id == foreign(BankReconciliation.id)",
        overlaps="outstanding_items",
    )
    journal_entry = relationship("JournalEntry")
