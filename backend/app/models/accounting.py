"""
Accounting Models - Double-Entry Bookkeeping
Chart of Accounts, Journal Entries, and related models
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    ForeignKey,
    Enum as SQLEnum,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


# Enums


class AccountType(str, enum.Enum):
    """Account Types in Chart of Accounts"""

    ASSET = "asset"
    LIABILITY = "liability"
    INCOME = "income"
    EXPENSE = "expense"
    EQUITY = "equity"


class AccountSubType(str, enum.Enum):
    """Account Sub-types for better categorization"""

    # Assets
    CURRENT_ASSET = "current_asset"
    FIXED_ASSET = "fixed_asset"
    PRECIOUS_ASSET = "precious_asset"
    INVENTORY = "inventory"
    RECEIVABLE = "receivable"
    CASH_BANK = "cash_bank"

    # Liabilities
    CURRENT_LIABILITY = "current_liability"
    LONG_TERM_LIABILITY = "long_term_liability"

    # Income
    DONATION_INCOME = "donation_income"
    SEVA_INCOME = "seva_income"
    SPONSORSHIP_INCOME = "sponsorship_income"
    OTHER_INCOME = "other_income"

    # Expense
    OPERATIONAL_EXPENSE = "operational_expense"
    RITUAL_EXPENSE = "ritual_expense"
    ADMINISTRATIVE_EXPENSE = "administrative_expense"
    FESTIVAL_EXPENSE = "festival_expense"

    # Equity
    CORPUS_FUND = "corpus_fund"
    GENERAL_FUND = "general_fund"


class JournalEntryStatus(str, enum.Enum):
    """Journal Entry Status"""

    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"
    REVERSED = "reversed"  # Entry that has been reversed (for corrections)


class TransactionType(str, enum.Enum):
    """Transaction Types for reference"""

    DONATION = "donation"
    SEVA = "seva"
    SPONSORSHIP = "sponsorship"
    IN_KIND_DONATION = "in_kind_donation"
    UPI_PAYMENT = "upi_payment"
    EXPENSE = "expense"
    VENDOR_PAYMENT = "vendor_payment"
    MANUAL = "manual"
    BANK_RECONCILIATION = "bank_reconciliation"
    INVENTORY_PURCHASE = "inventory_purchase"
    INVENTORY_ISSUE = "inventory_issue"
    INVENTORY_ADJUSTMENT = "inventory_adjustment"
    ADVANCE_SEVA_TRANSFER = "advance_seva_transfer"


# Models


class Account(Base):
    """
    Chart of Accounts - All accounts in the accounting system
    Supports hierarchical structure with parent-child relationships
    """

    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    # Account Identification
    account_code = Column(String(20), unique=True, nullable=False, index=True)
    account_name = Column(String(200), nullable=False, index=True)
    account_name_kannada = Column(String(200))
    description = Column(Text)

    # Account Classification
    account_type = Column(SQLEnum(AccountType), nullable=False, index=True)
    account_subtype = Column(SQLEnum(AccountSubType), nullable=True, index=True)

    # Hierarchy - For parent-child relationships
    parent_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    # Temple Reference
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)

    # Flags
    is_active = Column(Boolean, default=True, index=True)
    is_system_account = Column(Boolean, default=False)  # Cannot be deleted if True
    allow_manual_entry = Column(Boolean, default=True)  # Can create manual journal entries

    # Opening Balance (for migration/setup)
    opening_balance_debit = Column(Float, default=0.0)
    opening_balance_credit = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    parent_account = relationship("Account", remote_side=[id], backref="sub_accounts")
    journal_lines = relationship("JournalLine", back_populates="account")

    def __repr__(self):
        return f"<Account(code='{self.account_code}', name='{self.account_name}', type='{self.account_type}')>"


class JournalEntry(Base):
    """
    Journal Entry - Header for all accounting transactions
    Each entry must have balanced debits and credits
    """

    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)

    # Entry Identification
    entry_number = Column(String(50), unique=True, nullable=False, index=True)
    entry_date = Column(DateTime, nullable=False, index=True)

    # Reference to source transaction
    reference_type = Column(SQLEnum(TransactionType), nullable=True, index=True)
    reference_id = Column(Integer, nullable=True, index=True)  # ID of donation/seva/etc

    # Temple Reference
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False, index=True)

    # Entry Details
    narration = Column(Text, nullable=False)
    total_amount = Column(Float, nullable=False)  # Total debit (should equal total credit)

    # Status
    status = Column(SQLEnum(JournalEntryStatus), default=JournalEntryStatus.DRAFT, index=True)

    # Integrity Protection (for tampering detection)
    # TEMPORARILY DISABLED: Column doesn't exist in database yet
    # Uncomment after running migration: python scripts/add_integrity_hash_column.py
    # integrity_hash = Column(String(64), nullable=True)  # Hash chain for tampering detection - index will be added by migration

    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    posted_at = Column(DateTime, nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    created_by_user = relationship("User", foreign_keys=[created_by])
    posted_by_user = relationship("User", foreign_keys=[posted_by])
    cancelled_by_user = relationship("User", foreign_keys=[cancelled_by])
    journal_lines = relationship(
        "JournalLine", back_populates="journal_entry", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<JournalEntry(number='{self.entry_number}', date='{self.entry_date}', amount={self.total_amount})>"


class JournalLine(Base):
    """
    Journal Line - Individual debit/credit entries within a journal entry
    Each journal entry must have balanced total debits and credits
    """

    __tablename__ = "journal_lines"

    id = Column(Integer, primary_key=True, index=True)

    # Journal Entry Reference
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False, index=True)

    # Account Reference
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)

    # Amounts
    debit_amount = Column(Float, default=0.0)
    credit_amount = Column(Float, default=0.0)

    # Description
    description = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="journal_lines")
    account = relationship("Account", back_populates="journal_lines")

    def __repr__(self):
        return f"<JournalLine(account={self.account_id}, debit={self.debit_amount}, credit={self.credit_amount})>"
