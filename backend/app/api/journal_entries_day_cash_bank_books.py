"""
Day Book, Cash Book, and Bank Book Reports
Append these endpoints to journal_entries.py
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.accounting import (
    Account, JournalEntry, JournalLine,
    JournalEntryStatus, AccountType, AccountSubType
)
from app.schemas.accounting import (
    DayBookResponse, DayBookEntry,
    CashBookResponse, CashBookEntry,
    BankBookResponse, BankBookEntry
)

# These endpoints should be added to the journal_entries router
# Copy the code below and add to backend/app/api/journal_entries.py after the balance sheet endpoint

@router.get("/reports/day-book", response_model=DayBookResponse)
def get_day_book(
    date: date = Query(default_factory=date.today, description="Date for day book"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate Day Book - All transactions for a specific day
    Shows all receipts and payments for the day with opening/closing balance
    """
    temple_id = current_user.temple_id
    
    # Get all journal entries for the day
    entry_filter = [
        func.date(JournalEntry.entry_date) == date,
        JournalEntry.status == JournalEntryStatus.POSTED
    ]
    if temple_id is not None:
        entry_filter.append(JournalEntry.temple_id == temple_id)
    
    entries = db.query(JournalEntry).filter(*entry_filter).order_by(JournalEntry.entry_date).all()
    
    # Calculate opening balance (balance before this date)
    opening_filter = [
        func.date(JournalEntry.entry_date) < date,
        JournalEntry.status == JournalEntryStatus.POSTED
    ]
    if temple_id is not None:
        opening_filter.append(JournalEntry.temple_id == temple_id)
    
    # Get cash and bank accounts for opening balance
    cash_accounts = db.query(Account).filter(
        Account.account_type == AccountType.ASSET,
        Account.account_subtype.in_([AccountSubType.CASH_BANK, AccountSubType.CURRENT_ASSET]),
        Account.is_active == True
    )
    if temple_id is not None:
        cash_accounts = cash_accounts.filter(Account.temple_id == temple_id)
    cash_accounts = cash_accounts.all()
    
    opening_balance = 0.0
    for acc in cash_accounts:
        balance_filter = [
            JournalLine.account_id == acc.id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            func.date(JournalEntry.entry_date) < date
        ]
        if temple_id is not None:
            balance_filter.append(JournalEntry.temple_id == temple_id)
        
        balance_query = db.query(
            func.sum(JournalLine.debit_amount).label('total_debit'),
            func.sum(JournalLine.credit_amount).label('total_credit')
        ).join(JournalLine.journal_entry).filter(*balance_filter).first()
        
        debit = float(balance_query.total_debit or 0) + acc.opening_balance_debit
        credit = float(balance_query.total_credit or 0) + acc.opening_balance_credit
        opening_balance += (debit - credit)
    
    # Separate receipts and payments
    receipts = []
    payments = []
    total_receipts = 0.0
    total_payments = 0.0
    
    for entry in entries:
        # Get all lines for this entry
        lines = db.query(JournalLine).filter(JournalLine.journal_entry_id == entry.id).all()
        
        for line in lines:
            account = db.query(Account).filter(Account.id == line.account_id).first()
            if not account:
                continue
            
            # Determine if this is a receipt (money coming in) or payment (money going out)
            is_cash_bank = account.account_subtype in [AccountSubType.CASH_BANK, AccountSubType.CURRENT_ASSET]
            is_income = account.account_type == AccountType.INCOME
            is_expense = account.account_type == AccountType.EXPENSE
            
            if is_cash_bank and line.debit_amount > 0:
                # Money received (cash/bank debited)
                receipts.append(DayBookEntry(
                    entry_number=entry.entry_number,
                    entry_date=entry.entry_date,
                    narration=entry.narration or line.description or "",
                    voucher_type=entry.reference_type or "Manual",
                    debit_amount=line.debit_amount,
                    credit_amount=0.0,
                    account_name=account.account_name,
                    party_name=None
                ))
                total_receipts += line.debit_amount
            elif is_cash_bank and line.credit_amount > 0:
                # Money paid (cash/bank credited)
                payments.append(DayBookEntry(
                    entry_number=entry.entry_number,
                    entry_date=entry.entry_date,
                    narration=entry.narration or line.description or "",
                    voucher_type=entry.reference_type or "Manual",
                    debit_amount=0.0,
                    credit_amount=line.credit_amount,
                    account_name=account.account_name,
                    party_name=None
                ))
                total_payments += line.credit_amount
            elif is_income and line.credit_amount > 0:
                # Income recognized (receipt)
                receipts.append(DayBookEntry(
                    entry_number=entry.entry_number,
                    entry_date=entry.entry_date,
                    narration=entry.narration or line.description or "",
                    voucher_type=entry.reference_type or "Manual",
                    debit_amount=0.0,
                    credit_amount=line.credit_amount,
                    account_name=account.account_name,
                    party_name=None
                ))
                total_receipts += line.credit_amount
            elif is_expense and line.debit_amount > 0:
                # Expense incurred (payment)
                payments.append(DayBookEntry(
                    entry_number=entry.entry_number,
                    entry_date=entry.entry_date,
                    narration=entry.narration or line.description or "",
                    voucher_type=entry.reference_type or "Manual",
                    debit_amount=line.debit_amount,
                    credit_amount=0.0,
                    account_name=account.account_name,
                    party_name=None
                ))
                total_payments += line.debit_amount
    
    net_cash_flow = total_receipts - total_payments
    closing_balance = opening_balance + net_cash_flow
    
    return DayBookResponse(
        date=date,
        opening_balance=opening_balance,
        receipts=receipts,
        total_receipts=total_receipts,
        payments=payments,
        total_payments=total_payments,
        net_cash_flow=net_cash_flow,
        closing_balance=closing_balance
    )


@router.get("/reports/cash-book", response_model=CashBookResponse)
def get_cash_book(
    from_date: date = Query(...),
    to_date: date = Query(...),
    counter_id: Optional[int] = Query(None, description="Counter ID if multiple counters"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate Cash Book - All cash transactions for a date range
    Shows all cash receipts and payments with running balance
    """
    temple_id = current_user.temple_id
    
    # Get cash accounts
    cash_account_filter = [
        Account.account_type == AccountType.ASSET,
        Account.account_subtype == AccountSubType.CASH_BANK,
        Account.is_active == True
    ]
    if temple_id is not None:
        cash_account_filter.append(Account.temple_id == temple_id)
    if counter_id:
        # If counter-specific, filter by account code pattern
        cash_account_filter.append(Account.account_code.like(f'110{counter_id}%'))
    
    cash_accounts = db.query(Account).filter(*cash_account_filter).all()
    
    if not cash_accounts:
        # Return empty cash book
        return CashBookResponse(
            from_date=from_date,
            to_date=to_date,
            opening_balance=0.0,
            entries=[],
            closing_balance=0.0,
            total_receipts=0.0,
            total_payments=0.0
        )
    
    cash_account_ids = [acc.id for acc in cash_accounts]
    
    # Calculate opening balance
    opening_filter = [
        JournalLine.account_id.in_(cash_account_ids),
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) < from_date
    ]
    if temple_id is not None:
        opening_filter.append(JournalEntry.temple_id == temple_id)
    
    opening_query = db.query(
        func.sum(JournalLine.debit_amount).label('total_debit'),
        func.sum(JournalLine.credit_amount).label('total_credit')
    ).join(JournalLine.journal_entry).filter(*opening_filter).first()
    
    opening_debit = float(opening_query.total_debit or 0)
    opening_credit = float(opening_query.total_credit or 0)
    
    # Add opening balances from accounts
    for acc in cash_accounts:
        opening_debit += acc.opening_balance_debit
        opening_credit += acc.opening_balance_credit
    
    opening_balance = opening_debit - opening_credit
    
    # Get all transactions in date range
    lines_filter = [
        JournalLine.account_id.in_(cash_account_ids),
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) >= from_date,
        func.date(JournalEntry.entry_date) <= to_date
    ]
    if temple_id is not None:
        lines_filter.append(JournalEntry.temple_id == temple_id)
    
    lines = db.query(JournalLine).join(JournalLine.journal_entry).filter(*lines_filter).order_by(
        JournalEntry.entry_date, JournalEntry.id
    ).all()
    
    # Build cash book entries
    entries = []
    running_balance = opening_balance
    total_receipts = 0.0
    total_payments = 0.0
    
    for line in lines:
        account = db.query(Account).filter(Account.id == line.account_id).first()
        entry = line.journal_entry
        
        receipt_amount = 0.0
        payment_amount = 0.0
        
        if line.debit_amount > 0:
            # Cash received
            receipt_amount = line.debit_amount
            total_receipts += receipt_amount
            running_balance += receipt_amount
        elif line.credit_amount > 0:
            # Cash paid
            payment_amount = line.credit_amount
            total_payments += payment_amount
            running_balance -= payment_amount
        
        entries.append(CashBookEntry(
            date=entry.entry_date.date() if hasattr(entry.entry_date, 'date') else entry.entry_date,
            entry_number=entry.entry_number,
            narration=entry.narration or line.description or "",
            receipt_amount=receipt_amount,
            payment_amount=payment_amount,
            running_balance=running_balance,
            voucher_type=entry.reference_type or "Manual",
            party_name=None
        ))
    
    return CashBookResponse(
        from_date=from_date,
        to_date=to_date,
        opening_balance=opening_balance,
        entries=entries,
        closing_balance=running_balance,
        total_receipts=total_receipts,
        total_payments=total_payments
    )


@router.get("/reports/bank-book", response_model=BankBookResponse)
def get_bank_book(
    account_id: int = Query(..., description="Bank account ID"),
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate Bank Book - All bank transactions for a specific bank account
    Shows deposits, withdrawals, and cheque tracking
    """
    temple_id = current_user.temple_id
    
    # Get bank account
    account_filter = [Account.id == account_id]
    if temple_id is not None:
        account_filter.append(Account.temple_id == temple_id)
    
    account = db.query(Account).filter(*account_filter).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    if account.account_subtype != AccountSubType.CASH_BANK:
        raise HTTPException(status_code=400, detail="Account is not a bank account")
    
    # Calculate opening balance
    opening_filter = [
        JournalLine.account_id == account_id,
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) < from_date
    ]
    if temple_id is not None:
        opening_filter.append(JournalEntry.temple_id == temple_id)
    
    opening_query = db.query(
        func.sum(JournalLine.debit_amount).label('total_debit'),
        func.sum(JournalLine.credit_amount).label('total_credit')
    ).join(JournalLine.journal_entry).filter(*opening_filter).first()
    
    opening_debit = float(opening_query.total_debit or 0) + account.opening_balance_debit
    opening_credit = float(opening_query.total_credit or 0) + account.opening_balance_credit
    opening_balance = opening_debit - opening_credit
    
    # Get all transactions in date range
    lines_filter = [
        JournalLine.account_id == account_id,
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) >= from_date,
        func.date(JournalEntry.entry_date) <= to_date
    ]
    if temple_id is not None:
        lines_filter.append(JournalEntry.temple_id == temple_id)
    
    lines = db.query(JournalLine).join(JournalLine.journal_entry).filter(*lines_filter).order_by(
        JournalEntry.entry_date, JournalEntry.id
    ).all()
    
    # Build bank book entries
    entries = []
    outstanding_cheques = []
    running_balance = opening_balance
    total_deposits = 0.0
    total_withdrawals = 0.0
    
    for line in lines:
        entry = line.journal_entry
        
        deposit_amount = 0.0
        withdrawal_amount = 0.0
        cheque_number = None
        cleared = True
        
        if line.debit_amount > 0:
            # Deposit
            deposit_amount = line.debit_amount
            total_deposits += deposit_amount
            running_balance += deposit_amount
        elif line.credit_amount > 0:
            # Withdrawal
            withdrawal_amount = line.credit_amount
            total_withdrawals += withdrawal_amount
            running_balance -= withdrawal_amount
            
            # Try to extract cheque number from narration or reference
            narration = entry.narration or line.description or ""
            if 'cheque' in narration.lower() or 'chq' in narration.lower():
                # Extract cheque number (simple pattern matching)
                import re
                chq_match = re.search(r'ch[eq]*\s*[#:]?\s*(\d+)', narration, re.IGNORECASE)
                if chq_match:
                    cheque_number = chq_match.group(1)
                    # For now, assume cheques are cleared. In real system, track clearance status
                    cleared = True
        
        entries.append(BankBookEntry(
            date=entry.entry_date.date() if hasattr(entry.entry_date, 'date') else entry.entry_date,
            entry_number=entry.entry_number,
            narration=entry.narration or line.description or "",
            cheque_number=cheque_number,
            deposit_amount=deposit_amount,
            withdrawal_amount=withdrawal_amount,
            running_balance=running_balance,
            voucher_type=entry.reference_type or "Manual",
            cleared=cleared
        ))
        
        # Track outstanding cheques (not cleared)
        if cheque_number and not cleared:
            outstanding_cheques.append(BankBookEntry(
                date=entry.entry_date.date() if hasattr(entry.entry_date, 'date') else entry.entry_date,
                entry_number=entry.entry_number,
                narration=entry.narration or line.description or "",
                cheque_number=cheque_number,
                deposit_amount=0.0,
                withdrawal_amount=withdrawal_amount,
                running_balance=0.0,
                voucher_type=entry.reference_type or "Manual",
                cleared=False
            ))
    
    # Get bank details from account name or separate bank table (if exists)
    bank_name = None
    account_number = None
    # Try to extract from account name (e.g., "Bank - SBI Current Account")
    if ' - ' in account.account_name:
        parts = account.account_name.split(' - ')
        if len(parts) >= 2:
            bank_name = parts[0].replace('Bank', '').strip()
            account_number = parts[1] if len(parts) > 1 else None
    
    return BankBookResponse(
        account_id=account_id,
        account_code=account.account_code,
        account_name=account.account_name,
        bank_name=bank_name,
        account_number=account_number,
        from_date=from_date,
        to_date=to_date,
        opening_balance=opening_balance,
        entries=entries,
        closing_balance=running_balance,
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        outstanding_cheques=outstanding_cheques
    )

