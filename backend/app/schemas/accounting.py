"""
Pydantic Schemas for Accounting System
Chart of Accounts, Journal Entries, etc.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.accounting import AccountType, AccountSubType, JournalEntryStatus, TransactionType


# ===== CHART OF ACCOUNTS SCHEMAS =====

class AccountBase(BaseModel):
    """Base schema for Account"""
    account_code: str = Field(..., min_length=1, max_length=20)
    account_name: str = Field(..., min_length=1, max_length=200)
    account_name_kannada: Optional[str] = None
    description: Optional[str] = None
    account_type: AccountType
    account_subtype: Optional[AccountSubType] = None
    parent_account_id: Optional[int] = None
    is_active: bool = True
    allow_manual_entry: bool = True


class AccountCreate(AccountBase):
    """Schema for creating an account"""
    temple_id: int
    opening_balance_debit: float = 0.0
    opening_balance_credit: float = 0.0


class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    account_name: Optional[str] = None
    account_name_kannada: Optional[str] = None
    description: Optional[str] = None
    account_subtype: Optional[AccountSubType] = None
    parent_account_id: Optional[int] = None
    is_active: Optional[bool] = None
    allow_manual_entry: Optional[bool] = None


class AccountResponse(AccountBase):
    """Schema for account response"""
    id: int
    temple_id: int
    is_system_account: bool
    opening_balance_debit: float
    opening_balance_credit: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountBalance(BaseModel):
    """Schema for account balance"""
    account_id: int
    account_code: str
    account_name: str
    account_type: AccountType
    total_debit: float
    total_credit: float
    balance: float
    balance_type: str  # "debit" or "credit"


class AccountHierarchy(AccountResponse):
    """Schema for account with hierarchy (includes children)"""
    sub_accounts: List['AccountHierarchy'] = []


# Update forward refs for recursive model
AccountHierarchy.model_rebuild()


# ===== JOURNAL ENTRY SCHEMAS =====

class JournalLineBase(BaseModel):
    """Base schema for Journal Line"""
    account_id: int
    debit_amount: float = 0.0
    credit_amount: float = 0.0
    description: Optional[str] = None


class JournalLineCreate(JournalLineBase):
    """Schema for creating a journal line"""
    pass


class JournalLineResponse(JournalLineBase):
    """Schema for journal line response"""
    id: int
    journal_entry_id: int
    account_code: Optional[str] = None
    account_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JournalEntryBase(BaseModel):
    """Base schema for Journal Entry"""
    entry_date: datetime
    narration: str = Field(..., min_length=1)
    reference_type: Optional[TransactionType] = None
    reference_id: Optional[int] = None


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a journal entry"""
    temple_id: int
    journal_lines: List[JournalLineCreate] = Field(..., min_items=2)

    class Config:
        json_schema_extra = {
            "example": {
                "entry_date": "2025-11-23T10:00:00",
                "narration": "Cash donation received from devotee",
                "temple_id": 1,
                "reference_type": "donation",
                "reference_id": 123,
                "journal_lines": [
                    {
                        "account_id": 1,
                        "debit_amount": 1000.0,
                        "credit_amount": 0.0,
                        "description": "Cash in hand"
                    },
                    {
                        "account_id": 10,
                        "debit_amount": 0.0,
                        "credit_amount": 1000.0,
                        "description": "Donation income"
                    }
                ]
            }
        }


class JournalEntryUpdate(BaseModel):
    """Schema for updating a journal entry (only draft entries can be updated)"""
    entry_date: Optional[datetime] = None
    narration: Optional[str] = None
    journal_lines: Optional[List[JournalLineCreate]] = None


class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry response"""
    id: int
    entry_number: str
    temple_id: int
    total_amount: float
    status: JournalEntryStatus
    created_by: int
    posted_by: Optional[int] = None
    posted_at: Optional[datetime] = None
    cancelled_by: Optional[int] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    journal_lines: List[JournalLineResponse] = []

    class Config:
        from_attributes = True


class JournalEntryPost(BaseModel):
    """Schema for posting a journal entry"""
    pass


class JournalEntryCancel(BaseModel):
    """Schema for cancelling a journal entry"""
    cancellation_reason: str = Field(..., min_length=1)


# ===== TRIAL BALANCE SCHEMA =====

class TrialBalanceItem(BaseModel):
    """Individual account in trial balance"""
    account_code: str
    account_name: str
    account_type: AccountType
    debit_balance: float
    credit_balance: float


class TrialBalanceResponse(BaseModel):
    """Trial Balance Report"""
    as_of_date: date
    accounts: List[TrialBalanceItem]
    total_debits: float
    total_credits: float
    is_balanced: bool
    difference: float


# ===== LEDGER SCHEMA =====

class LedgerEntry(BaseModel):
    """Individual entry in account ledger"""
    entry_date: datetime
    entry_number: str
    narration: str
    debit_amount: float
    credit_amount: float
    running_balance: float
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None


class AccountLedgerResponse(BaseModel):
    """Account Ledger (Statement of Account)"""
    account_id: int
    account_code: str
    account_name: str
    account_type: AccountType
    from_date: date
    to_date: date
    opening_balance: float
    closing_balance: float
    entries: List[LedgerEntry]


# ===== PROFIT & LOSS SCHEMA =====

class PLAccountItem(BaseModel):
    """Individual account in P&L statement"""
    account_code: str
    account_name: str
    amount: float


class PLCategoryGroup(BaseModel):
    """Category group (e.g., Donation Income, Seva Income)"""
    category_name: str
    accounts: List[PLAccountItem]
    total: float


class ProfitLossResponse(BaseModel):
    """Profit & Loss Statement (Income & Expenditure)"""
    from_date: date
    to_date: date
    income_groups: List[PLCategoryGroup]
    total_income: float
    expense_groups: List[PLCategoryGroup]
    total_expenses: float
    net_surplus: float  # Positive = surplus, Negative = deficit


# ===== CATEGORY-WISE INCOME SCHEMA =====

class CategoryIncomeItem(BaseModel):
    """Category-wise income breakdown"""
    account_code: str
    account_name: str
    amount: float
    percentage: float  # Percentage of total income
    transaction_count: int


class CategoryIncomeResponse(BaseModel):
    """Category-wise Income Report"""
    from_date: date
    to_date: date
    donation_income: List[CategoryIncomeItem]
    seva_income: List[CategoryIncomeItem]
    other_income: List[CategoryIncomeItem]
    total_income: float


# ===== TOP DONORS SCHEMA =====

class TopDonorItem(BaseModel):
    """Top donor information"""
    devotee_id: int
    devotee_name: str
    total_donated: float
    donation_count: int
    last_donation_date: date
    categories: List[str]  # Categories donated to


class TopDonorsResponse(BaseModel):
    """Top Donors Report"""
    from_date: date
    to_date: date
    donors: List[TopDonorItem]
    total_donors: int
    total_amount: float


# ===== BALANCE SHEET SCHEMA =====

class BalanceSheetAccountItem(BaseModel):
    """Individual account in Balance Sheet"""
    account_code: str
    account_name: str
    current_year: float
    previous_year: Optional[float] = None


class BalanceSheetGroup(BaseModel):
    """Group of accounts in Balance Sheet (e.g., Fixed Assets, Current Assets)"""
    group_name: str
    accounts: List[BalanceSheetAccountItem]
    group_total: float
    previous_year_total: Optional[float] = None


class BalanceSheetResponse(BaseModel):
    """Balance Sheet - Financial Position Statement"""
    as_of_date: date
    previous_year_date: Optional[date] = None
    
    # Assets Side
    fixed_assets: List[BalanceSheetGroup]
    current_assets: List[BalanceSheetGroup]
    total_assets: float
    previous_year_total_assets: Optional[float] = None
    
    # Liabilities & Funds Side
    corpus_fund: float
    previous_year_corpus_fund: Optional[float] = None
    designated_funds: List[BalanceSheetGroup]
    current_liabilities: List[BalanceSheetGroup]
    total_liabilities_and_funds: float
    previous_year_total_liabilities: Optional[float] = None
    
    # Validation
    is_balanced: bool
    difference: float  # Should be 0 if balanced


# ===== DAY BOOK SCHEMA =====

class DayBookEntry(BaseModel):
    """Individual entry in Day Book"""
    entry_number: str
    entry_date: datetime
    narration: str
    voucher_type: str
    debit_amount: float
    credit_amount: float
    account_name: str
    party_name: Optional[str] = None


class DayBookResponse(BaseModel):
    """Day Book - All transactions for a day"""
    date: date
    opening_balance: float
    receipts: List[DayBookEntry]
    total_receipts: float
    payments: List[DayBookEntry]
    total_payments: float
    net_cash_flow: float
    closing_balance: float


# ===== CASH BOOK SCHEMA =====

class CashBookEntry(BaseModel):
    """Individual entry in Cash Book"""
    date: date
    entry_number: str
    narration: str
    receipt_amount: float
    payment_amount: float
    running_balance: float
    voucher_type: str
    party_name: Optional[str] = None


class CashBookResponse(BaseModel):
    """Cash Book - All cash transactions"""
    from_date: date
    to_date: date
    opening_balance: float
    entries: List[CashBookEntry]
    closing_balance: float
    total_receipts: float
    total_payments: float


# ===== BANK BOOK SCHEMA =====

class BankBookEntry(BaseModel):
    """Individual entry in Bank Book"""
    date: date
    entry_number: str
    narration: str
    cheque_number: Optional[str] = None
    deposit_amount: float
    withdrawal_amount: float
    running_balance: float
    voucher_type: str
    cleared: bool = True


class BankBookResponse(BaseModel):
    """Bank Book - All bank transactions for an account"""
    account_id: int
    account_code: str
    account_name: str
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    from_date: date
    to_date: date
    opening_balance: float
    entries: List[BankBookEntry]
    closing_balance: float
    total_deposits: float
    total_withdrawals: float
    outstanding_cheques: List[BankBookEntry] = []


# ===== DAY BOOK SCHEMA =====

class DayBookEntry(BaseModel):
    """Individual transaction in Day Book"""
    entry_number: str
    entry_date: datetime
    narration: str
    voucher_type: str  # Receipt, Payment, Journal, Contra
    debit_amount: float
    credit_amount: float
    account_name: str
    party_name: Optional[str] = None


class DayBookResponse(BaseModel):
    """Day Book - All transactions for a specific day"""
    date: date
    opening_balance: float
    receipts: List[DayBookEntry]
    total_receipts: float
    payments: List[DayBookEntry]
    total_payments: float
    net_cash_flow: float
    closing_balance: float


# ===== CASH BOOK SCHEMA =====

class CashBookEntry(BaseModel):
    """Individual transaction in Cash Book"""
    date: date
    entry_number: str
    narration: str
    receipt_amount: float
    payment_amount: float
    running_balance: float
    voucher_type: str
    party_name: Optional[str] = None


class CashBookResponse(BaseModel):
    """Cash Book - All cash transactions"""
    from_date: date
    to_date: date
    opening_balance: float
    entries: List[CashBookEntry]
    closing_balance: float
    total_receipts: float
    total_payments: float


# ===== BANK BOOK SCHEMA =====

class BankBookEntry(BaseModel):
    """Individual transaction in Bank Book"""
    date: date
    entry_number: str
    narration: str
    cheque_number: Optional[str] = None
    deposit_amount: float
    withdrawal_amount: float
    running_balance: float
    voucher_type: str
    cleared: bool = True  # Cheque cleared or not


class BankBookResponse(BaseModel):
    """Bank Book - All bank transactions for an account"""
    account_id: int
    account_code: str
    account_name: str
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    from_date: date
    to_date: date
    opening_balance: float
    entries: List[BankBookEntry]
    closing_balance: float
    total_deposits: float
    total_withdrawals: float
    outstanding_cheques: List[BankBookEntry]  # Cheques not yet cleared