"""
Bank Reconciliation Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class StatementEntryType(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    cheque = "cheque"
    transfer = "transfer"
    charges = "charges"
    interest = "interest"


class ReconciliationStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    reconciled = "reconciled"
    discrepancy = "discrepancy"


# Bank Statement Schemas
class BankStatementEntryCreate(BaseModel):
    transaction_date: date
    value_date: Optional[date] = None
    entry_type: StatementEntryType
    amount: float
    description: Optional[str] = None
    reference_number: Optional[str] = None
    narration: Optional[str] = None
    balance_after: Optional[float] = None


class BankStatementCreate(BaseModel):
    account_id: int
    statement_date: date
    from_date: date
    to_date: date
    opening_balance: float
    closing_balance: float
    entries: List[BankStatementEntryCreate]
    source_file: Optional[str] = None


class BankStatementEntryResponse(BaseModel):
    id: int
    transaction_date: date
    value_date: Optional[date]
    entry_type: StatementEntryType
    amount: float
    description: Optional[str]
    reference_number: Optional[str]
    narration: Optional[str]
    balance_after: Optional[float]
    is_matched: bool
    matched_journal_line_id: Optional[int]
    notes: Optional[str]

    class Config:
        from_attributes = True


class BankStatementResponse(BaseModel):
    id: int
    account_id: int
    statement_date: date
    from_date: date
    to_date: date
    opening_balance: float
    closing_balance: float
    imported_at: datetime
    is_reconciled: bool
    entries: List[BankStatementEntryResponse] = []
    total_entries: Optional[int] = None

    class Config:
        from_attributes = True


# Reconciliation Schemas
class ReconciliationOutstandingItemResponse(BaseModel):
    id: int
    item_type: str
    description: str
    amount: float
    date: date
    reference_number: Optional[str]
    is_cleared: bool
    notes: Optional[str]

    class Config:
        from_attributes = True


class BankReconciliationCreate(BaseModel):
    account_id: int
    statement_id: int
    reconciliation_date: date
    notes: Optional[str] = None


class BankReconciliationResponse(BaseModel):
    id: int
    account_id: int
    statement_id: int
    reconciliation_date: date
    from_date: date
    to_date: date
    book_balance_as_on: float
    bank_balance_as_per_statement: float
    deposits_in_transit: float
    cheques_issued_not_cleared: float
    bank_charges_not_recorded: float
    interest_credited_not_recorded: float
    other_adjustments: float
    adjusted_book_balance: float
    adjusted_bank_balance: float
    difference: float
    status: ReconciliationStatus
    notes: Optional[str]
    discrepancy_notes: Optional[str]
    outstanding_items: List[ReconciliationOutstandingItemResponse] = []
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReconciliationMatchRequest(BaseModel):
    """Request to match a statement entry with a journal line"""

    statement_entry_id: int
    journal_line_id: int
    notes: Optional[str] = None


class ReconciliationSummaryResponse(BaseModel):
    """Summary of reconciliation status"""

    account_id: int
    account_name: str
    last_reconciled_date: Optional[date]
    last_reconciliation_id: Optional[int]
    book_balance: float
    statement_balance: Optional[float]
    unmatched_statement_entries: int
    unmatched_book_entries: int
    outstanding_cheques_count: int
    outstanding_cheques_amount: float
    deposits_in_transit_count: int
    deposits_in_transit_amount: float
    matched_count: Optional[int] = None
    total_count: Optional[int] = None
    difference: Optional[float] = None
    bank_balance: Optional[float] = None
