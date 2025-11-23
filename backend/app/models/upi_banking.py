"""
UPI Payment and Bank Reconciliation Models
Track UPI payments and reconcile with bank statements
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, Enum as SQLEnum, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


# Enums

class UpiPaymentPurpose(str, enum.Enum):
    """Purpose of UPI payment"""
    DONATION = "donation"
    SEVA = "seva"
    SPONSORSHIP = "sponsorship"
    ANNADANA = "annadana"
    OTHER = "other"


class BankTransactionType(str, enum.Enum):
    """Type of bank transaction"""
    CREDIT = "credit"  # Money received
    DEBIT = "debit"  # Money paid


# Models

class UpiPayment(Base):
    """
    UPI Payment Log
    Quick entry for UPI payments received via static QR code
    Admin logs payments manually as they receive SMS notifications
    """
    __tablename__ = "upi_payments"

    id = Column(Integer, primary_key=True, index=True)

    # Temple
    temple_id = Column(Integer, ForeignKey('temples.id'), nullable=False, index=True)

    # Devotee
    devotee_id = Column(Integer, ForeignKey('devotees.id'), nullable=False, index=True)

    # Payment Details
    amount = Column(Float, nullable=False)
    payment_datetime = Column(DateTime, nullable=False, index=True)

    # UPI Details (from SMS)
    sender_upi_id = Column(String(100), index=True)  # 9876543210@paytm
    sender_phone = Column(String(20), index=True)  # Extracted from UPI ID
    upi_reference_number = Column(String(100), index=True)  # Transaction ref from SMS

    # Purpose
    payment_purpose = Column(SQLEnum(UpiPaymentPurpose), nullable=False, index=True)

    # Reference to linked transaction
    donation_id = Column(Integer, ForeignKey('donations.id'), nullable=True)
    seva_booking_id = Column(Integer, ForeignKey('seva_bookings.id'), nullable=True)
    sponsorship_id = Column(Integer, ForeignKey('sponsorships.id'), nullable=True)

    # Receipt
    receipt_number = Column(String(50), index=True)

    # Additional Details
    notes = Column(Text)

    # Bank Reconciliation
    is_bank_reconciled = Column(Boolean, default=False, index=True)
    bank_statement_matched_at = Column(DateTime)
    bank_transaction_id = Column(Integer, ForeignKey('bank_transactions.id'), nullable=True)

    # Accounting Integration
    journal_entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=True)

    # Audit
    logged_by = Column(Integer, ForeignKey('users.id'), nullable=False)  # Who entered this payment

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    devotee = relationship("Devotee")
    logged_by_user = relationship("User")
    donation = relationship("Donation")
    seva_booking = relationship("SevaBooking")
    sponsorship = relationship("Sponsorship")
    bank_transaction = relationship("BankTransaction", foreign_keys="[UpiPayment.bank_transaction_id]")
    journal_entry = relationship("JournalEntry")

    def __repr__(self):
        return f"<UpiPayment(amount={self.amount}, phone='{self.sender_phone}', purpose='{self.payment_purpose}')>"


class BankAccount(Base):
    """
    Bank Accounts
    Master list of temple's bank accounts
    """
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)

    # Temple
    temple_id = Column(Integer, ForeignKey('temples.id'), nullable=False, index=True)

    # Account Details
    account_name = Column(String(200), nullable=False)  # "SBI Current Account", "HDFC Savings"
    bank_name = Column(String(200), nullable=False)
    branch_name = Column(String(200))
    account_number = Column(String(50), nullable=False)
    ifsc_code = Column(String(20), nullable=False)
    account_type = Column(String(50))  # Current, Savings

    # Account in Chart of Accounts
    chart_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_primary = Column(Boolean, default=False)  # Primary account for UPI/online

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    chart_account = relationship("Account")
    bank_transactions = relationship("BankTransaction", back_populates="bank_account")
    reconciliations = relationship("BankReconciliation", back_populates="bank_account")

    def __repr__(self):
        return f"<BankAccount(name='{self.account_name}', bank='{self.bank_name}')>"


class BankTransaction(Base):
    """
    Bank Transactions
    Imported from bank statements
    Used for reconciliation with system records
    """
    __tablename__ = "bank_transactions"

    id = Column(Integer, primary_key=True, index=True)

    # Bank Account
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False, index=True)

    # Temple
    temple_id = Column(Integer, ForeignKey('temples.id'), nullable=False, index=True)

    # Transaction Details
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_time = Column(String(20))  # HH:MM:SS from statement
    value_date = Column(Date)

    # Amount
    amount = Column(Float, nullable=False)
    transaction_type = Column(SQLEnum(BankTransactionType), nullable=False, index=True)

    # Bank Details
    bank_reference_number = Column(String(100), index=True)
    upi_reference = Column(String(100), index=True)
    sender_receiver_upi_id = Column(String(100), index=True)
    narration = Column(Text)  # Full narration from bank
    cheque_number = Column(String(50))

    # Balance
    balance_after = Column(Float)

    # Reconciliation
    is_reconciled = Column(Boolean, default=False, index=True)
    reconciled_at = Column(DateTime)
    reconciled_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Matched Transaction
    matched_upi_payment_id = Column(Integer, ForeignKey('upi_payments.id'), nullable=True)
    matched_donation_id = Column(Integer, ForeignKey('donations.id'), nullable=True)
    matched_journal_entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=True)

    # Import Details
    imported_from_statement = Column(Boolean, default=True)
    import_batch_id = Column(Integer, ForeignKey('bank_reconciliations.id'), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bank_account = relationship("BankAccount", back_populates="bank_transactions")
    temple = relationship("Temple")
    reconciled_by_user = relationship("User")
    matched_upi_payment = relationship("UpiPayment", foreign_keys="[BankTransaction.matched_upi_payment_id]")
    matched_donation = relationship("Donation")
    matched_journal_entry = relationship("JournalEntry")

    def __repr__(self):
        return f"<BankTransaction(date='{self.transaction_date}', amount={self.amount}, type='{self.transaction_type}')>"


class BankReconciliation(Base):
    """
    Bank Reconciliation
    Track reconciliation sessions when bank statements are uploaded and matched
    """
    __tablename__ = "bank_reconciliations"

    id = Column(Integer, primary_key=True, index=True)

    # Bank Account
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False, index=True)

    # Temple
    temple_id = Column(Integer, ForeignKey('temples.id'), nullable=False, index=True)

    # Statement Details
    statement_file_name = Column(String(500))
    statement_date_from = Column(Date, nullable=False)
    statement_date_to = Column(Date, nullable=False)

    # Summary
    total_credits = Column(Float, default=0.0)
    total_debits = Column(Float, default=0.0)
    transactions_imported = Column(Integer, default=0)
    transactions_matched = Column(Integer, default=0)
    transactions_unmatched = Column(Integer, default=0)

    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)

    # Audit
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bank_account = relationship("BankAccount", back_populates="reconciliations")
    temple = relationship("Temple")
    uploaded_by_user = relationship("User")

    def __repr__(self):
        return f"<BankReconciliation(from='{self.statement_date_from}', to='{self.statement_date_to}', txns={self.transactions_imported})>"
