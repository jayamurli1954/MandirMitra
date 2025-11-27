"""
Bank Reconciliation API Endpoints
Handles bank statement import, matching, and reconciliation
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import date, datetime
import csv
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.accounting import Account, JournalEntry, JournalLine, JournalEntryStatus, AccountSubType
from app.models.bank_reconciliation import (
    BankStatement, BankStatementEntry, BankReconciliation, ReconciliationOutstandingItem,
    ReconciliationStatus, StatementEntryType
)
from app.schemas.bank_reconciliation import (
    BankStatementCreate, BankStatementResponse, BankStatementEntryResponse,
    BankReconciliationCreate, BankReconciliationResponse,
    ReconciliationMatchRequest, ReconciliationSummaryResponse,
    ReconciliationOutstandingItemResponse
)

router = APIRouter(prefix="/api/v1/bank-reconciliation", tags=["bank-reconciliation"])


@router.get("/accounts", response_model=List[dict])
def get_bank_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of bank accounts for reconciliation"""
    temple_id = current_user.temple_id
    
    query = db.query(Account).filter(
        Account.account_type == "asset",
        Account.account_subtype == AccountSubType.CASH_BANK,
        Account.is_active == True
    )
    
    if temple_id is not None:
        query = query.filter(Account.temple_id == temple_id)
    
    accounts = query.all()
    
    return [
        {
            "id": acc.id,
            "code": acc.account_code,
            "name": acc.account_name,
            "opening_balance": acc.opening_balance_debit - acc.opening_balance_credit
        }
        for acc in accounts
    ]


@router.post("/statements/import", response_model=BankStatementResponse)
async def import_bank_statement(
    account_id: int = Query(...),
    statement_date: date = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import bank statement from CSV file
    Expected CSV format:
    Date,Value Date,Description,Debit,Credit,Balance,Reference
    """
    # Verify account
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    if account.account_subtype != AccountSubType.CASH_BANK:
        raise HTTPException(status_code=400, detail="Account is not a bank account")
    
    # Read CSV
    contents = await file.read()
    csv_data = io.StringIO(contents.decode('utf-8'))
    reader = csv.DictReader(csv_data)
    
    entries_data = []
    min_date = None
    max_date = None
    opening_balance = None
    closing_balance = None
    
    for row in reader:
        # Parse date
        try:
            trans_date = datetime.strptime(row.get('Date', row.get('Transaction Date', '')), '%Y-%m-%d').date()
            if min_date is None or trans_date < min_date:
                min_date = trans_date
            if max_date is None or trans_date > max_date:
                max_date = trans_date
        except:
            continue
        
        # Parse amounts
        debit = float(row.get('Debit', row.get('Withdrawal', '0') or '0'))
        credit = float(row.get('Credit', row.get('Deposit', '0') or '0'))
        amount = credit if credit > 0 else -debit
        
        # Determine entry type
        desc = row.get('Description', '').lower()
        if 'cheque' in desc or 'chq' in desc:
            entry_type = StatementEntryType.CHEQUE
        elif 'interest' in desc:
            entry_type = StatementEntryType.INTEREST
        elif 'charge' in desc or 'fee' in desc:
            entry_type = StatementEntryType.CHARGES
        elif credit > 0:
            entry_type = StatementEntryType.DEPOSIT
        else:
            entry_type = StatementEntryType.WITHDRAWAL
        
        # Balance
        balance = float(row.get('Balance', '0') or '0')
        if opening_balance is None:
            opening_balance = balance - amount  # Opening = first balance - first transaction
        
        closing_balance = balance
        
        entries_data.append({
            "transaction_date": trans_date,
            "value_date": datetime.strptime(row.get('Value Date', row.get('Date', '')), '%Y-%m-%d').date() if row.get('Value Date') else None,
            "entry_type": entry_type,
            "amount": amount,
            "description": row.get('Description', ''),
            "reference_number": row.get('Reference', row.get('Cheque Number', '')),
            "narration": row.get('Narration', ''),
            "balance_after": balance
        })
    
    if not entries_data:
        raise HTTPException(status_code=400, detail="No valid entries found in CSV")
    
    # Create statement
    statement = BankStatement(
        account_id=account_id,
        temple_id=current_user.temple_id,
        statement_date=statement_date,
        from_date=min_date,
        to_date=max_date,
        opening_balance=opening_balance or 0.0,
        closing_balance=closing_balance or 0.0,
        imported_by=current_user.id,
        source_file=file.filename
    )
    db.add(statement)
    db.flush()
    
    # Create entries
    for entry_data in entries_data:
        entry = BankStatementEntry(
            statement_id=statement.id,
            **entry_data
        )
        db.add(entry)
    
    db.commit()
    db.refresh(statement)
    
    return statement


@router.get("/statements/{statement_id}", response_model=BankStatementResponse)
def get_statement(
    statement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bank statement with entries"""
    statement = db.query(BankStatement).filter(BankStatement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    return statement


@router.get("/statements/{statement_id}/entries", response_model=List[BankStatementEntryResponse])
def get_statement_entries(
    statement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all entries for a bank statement"""
    statement = db.query(BankStatement).filter(BankStatement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    entries = db.query(BankStatementEntry).filter(
        BankStatementEntry.statement_id == statement_id
    ).order_by(BankStatementEntry.transaction_date, BankStatementEntry.id).all()
    
    return entries


@router.get("/statements/{statement_id}/summary", response_model=ReconciliationSummaryResponse)
def get_statement_summary(
    statement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reconciliation summary for a statement"""
    statement = db.query(BankStatement).filter(BankStatement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    # Get all entries
    entries = db.query(BankStatementEntry).filter(
        BankStatementEntry.statement_id == statement_id
    ).all()
    
    matched_count = sum(1 for e in entries if e.is_matched)
    total_count = len(entries)
    
    # Calculate book balance
    account = db.query(Account).filter(Account.id == statement.account_id).first()
    temple_id = current_user.temple_id
    
    balance_filter = [
        JournalLine.account_id == statement.account_id,
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) <= statement.to_date
    ]
    if temple_id is not None:
        balance_filter.append(JournalEntry.temple_id == temple_id)
    
    balance_query = db.query(
        func.sum(JournalLine.debit_amount).label('total_debit'),
        func.sum(JournalLine.credit_amount).label('total_credit')
    ).join(JournalLine.journal_entry).filter(*balance_filter).first()
    
    book_balance = (float(balance_query.total_debit or 0) + account.opening_balance_debit) - \
                   (float(balance_query.total_credit or 0) + account.opening_balance_credit)
    
    difference = abs(book_balance - statement.closing_balance)
    
    return ReconciliationSummaryResponse(
        account_id=statement.account_id,
        account_name=account.account_name,
        last_reconciled_date=statement.reconciled_at.date() if statement.reconciled_at else None,
        last_reconciliation_id=None,
        book_balance=book_balance,
        statement_balance=statement.closing_balance,
        bank_balance=statement.closing_balance,
        unmatched_statement_entries=total_count - matched_count,
        unmatched_book_entries=0,
        outstanding_cheques_count=0,
        outstanding_cheques_amount=0.0,
        deposits_in_transit_count=0,
        deposits_in_transit_amount=0.0,
        matched_count=matched_count,
        total_count=total_count,
        difference=difference
    )


@router.get("/statements/{statement_id}/unmatched-book-entries", response_model=List[dict])
def get_unmatched_book_entries(
    statement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unmatched book entries for matching with statement"""
    statement = db.query(BankStatement).filter(BankStatement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    temple_id = current_user.temple_id
    
    # Get journal lines for this account in the statement period
    lines = db.query(JournalLine).join(JournalLine.journal_entry).filter(
        JournalLine.account_id == statement.account_id,
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) >= statement.from_date,
        func.date(JournalEntry.entry_date) <= statement.to_date
    )
    if temple_id is not None:
        lines = lines.filter(JournalEntry.temple_id == temple_id)
    
    lines = lines.all()
    
    # Get matched journal line IDs
    matched_line_ids = db.query(BankStatementEntry.matched_journal_line_id).filter(
        BankStatementEntry.statement_id == statement_id,
        BankStatementEntry.is_matched == True,
        BankStatementEntry.matched_journal_line_id.isnot(None)
    ).all()
    matched_ids = [m[0] for m in matched_line_ids]
    
    # Filter unmatched
    unmatched = [line for line in lines if line.id not in matched_ids]
    
    return [
        {
            "id": line.id,
            "entry_number": line.journal_entry.entry_number,
            "entry_date": line.journal_entry.entry_date.isoformat() if hasattr(line.journal_entry.entry_date, 'isoformat') else str(line.journal_entry.entry_date),
            "narration": line.journal_entry.narration or line.description or "",
            "debit_amount": line.debit_amount,
            "credit_amount": line.credit_amount,
            "amount": line.debit_amount or line.credit_amount or 0.0
        }
        for line in unmatched
    ]


@router.post("/match", response_model=dict)
def match_entry(
    match_request: ReconciliationMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Match a statement entry with a journal line"""
    statement_entry = db.query(BankStatementEntry).filter(
        BankStatementEntry.id == match_request.statement_entry_id
    ).first()
    
    if not statement_entry:
        raise HTTPException(status_code=404, detail="Statement entry not found")
    
    journal_line = db.query(JournalLine).filter(JournalLine.id == match_request.journal_line_id).first()
    if not journal_line:
        raise HTTPException(status_code=404, detail="Journal line not found")
    
    # Verify amounts match (with tolerance)
    tolerance = 0.01
    entry_amount = abs(statement_entry.amount)
    line_amount = abs(journal_line.debit_amount or journal_line.credit_amount or 0)
    
    if abs(entry_amount - line_amount) > tolerance:
        raise HTTPException(
            status_code=400,
            detail=f"Amounts don't match: Statement {entry_amount} vs Book {line_amount}"
        )
    
    # Match
    statement_entry.is_matched = True
    statement_entry.matched_journal_line_id = journal_line.id
    statement_entry.matched_at = datetime.utcnow()
    statement_entry.matched_by = current_user.id
    if match_request.notes:
        statement_entry.notes = match_request.notes
    
    db.commit()
    
    return {"message": "Entry matched successfully"}


@router.post("/statements/{statement_id}/match", response_model=dict)
def match_statement_entry(
    statement_id: int,
    match_request: ReconciliationMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Match a statement entry with a journal line"""
    statement_entry = db.query(BankStatementEntry).filter(
        BankStatementEntry.id == match_request.statement_entry_id,
        BankStatementEntry.statement_id == statement_id
    ).first()
    
    if not statement_entry:
        raise HTTPException(status_code=404, detail="Statement entry not found")
    
    journal_line = db.query(JournalLine).filter(JournalLine.id == match_request.journal_line_id).first()
    if not journal_line:
        raise HTTPException(status_code=404, detail="Journal line not found")
    
    # Verify amounts match (with tolerance)
    tolerance = 0.01
    entry_amount = abs(statement_entry.amount)
    line_amount = abs(journal_line.debit_amount or journal_line.credit_amount or 0)
    
    if abs(entry_amount - line_amount) > tolerance:
        raise HTTPException(
            status_code=400,
            detail=f"Amounts don't match: Statement {entry_amount} vs Book {line_amount}"
        )
    
    # Match
    statement_entry.is_matched = True
    statement_entry.matched_journal_line_id = journal_line.id
    statement_entry.matched_at = datetime.utcnow()
    statement_entry.matched_by = current_user.id
    if match_request.notes:
        statement_entry.notes = match_request.notes
    
    db.commit()
    
    return {"message": "Entry matched successfully"}


@router.post("/reconcile", response_model=BankReconciliationResponse)
def create_reconciliation(
    reconciliation_data: BankReconciliationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create bank reconciliation"""
    account = db.query(Account).filter(Account.id == reconciliation_data.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    statement = db.query(BankStatement).filter(BankStatement.id == reconciliation_data.statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    if statement.account_id != account.id:
        raise HTTPException(status_code=400, detail="Statement doesn't belong to this account")
    
    # Calculate book balance
    temple_id = current_user.temple_id
    book_balance_filter = [
        JournalLine.account_id == account.id,
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) <= reconciliation_data.reconciliation_date
    ]
    if temple_id is not None:
        book_balance_filter.append(JournalEntry.temple_id == temple_id)
    
    book_query = db.query(
        func.sum(JournalLine.debit_amount).label('total_debit'),
        func.sum(JournalLine.credit_amount).label('total_credit')
    ).join(JournalLine.journal_entry).filter(*book_balance_filter).first()
    
    book_debit = float(book_query.total_debit or 0) + account.opening_balance_debit
    book_credit = float(book_query.total_credit or 0) + account.opening_balance_credit
    book_balance = book_debit - book_credit
    
    # Get unmatched entries
    unmatched_statement = db.query(BankStatementEntry).filter(
        BankStatementEntry.statement_id == statement.id,
        BankStatementEntry.is_matched == False
    ).all()
    
    unmatched_book = db.query(JournalLine).join(JournalLine.journal_entry).filter(
        JournalLine.account_id == account.id,
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) >= statement.from_date,
        func.date(JournalEntry.entry_date) <= statement.to_date
    ).all()
    
    # Calculate adjustments
    deposits_in_transit = sum(e.amount for e in unmatched_statement if e.entry_type == StatementEntryType.DEPOSIT and e.amount > 0)
    cheques_not_cleared = sum(abs(e.amount) for e in unmatched_book if e.credit_amount > 0)
    bank_charges = sum(abs(e.amount) for e in unmatched_statement if e.entry_type == StatementEntryType.CHARGES)
    interest = sum(e.amount for e in unmatched_statement if e.entry_type == StatementEntryType.INTEREST and e.amount > 0)
    
    adjusted_book = book_balance + deposits_in_transit - cheques_not_cleared
    adjusted_bank = statement.closing_balance - bank_charges + interest
    difference = abs(adjusted_book - adjusted_bank)
    
    # Create reconciliation
    reconciliation = BankReconciliation(
        account_id=account.id,
        statement_id=statement.id,
        temple_id=current_user.temple_id,
        reconciliation_date=reconciliation_data.reconciliation_date,
        from_date=statement.from_date,
        to_date=statement.to_date,
        book_balance_as_on=book_balance,
        book_opening_balance=statement.opening_balance,
        bank_balance_as_per_statement=statement.closing_balance,
        bank_opening_balance=statement.opening_balance,
        deposits_in_transit=deposits_in_transit,
        cheques_issued_not_cleared=cheques_not_cleared,
        bank_charges_not_recorded=bank_charges,
        interest_credited_not_recorded=interest,
        adjusted_book_balance=adjusted_book,
        adjusted_bank_balance=adjusted_bank,
        difference=difference,
        status=ReconciliationStatus.RECONCILED if difference < 0.01 else ReconciliationStatus.DISCREPANCY,
        notes=reconciliation_data.notes,
        created_by=current_user.id
    )
    db.add(reconciliation)
    
    # Create outstanding items
    for entry in unmatched_statement:
        if entry.entry_type == StatementEntryType.DEPOSIT and entry.amount > 0:
            item = ReconciliationOutstandingItem(
                reconciliation_id=reconciliation.id,
                item_type="deposit_in_transit",
                description=entry.description or "Deposit in transit",
                amount=entry.amount,
                date=entry.transaction_date,
                reference_number=entry.reference_number,
                statement_entry_id=entry.id
            )
            db.add(item)
    
    for line in unmatched_book:
        if line.credit_amount > 0:  # Cheque issued
            item = ReconciliationOutstandingItem(
                reconciliation_id=reconciliation.id,
                item_type="cheque_issued",
                description="Cheque issued not cleared",
                amount=line.credit_amount,
                date=line.journal_entry.entry_date.date() if hasattr(line.journal_entry.entry_date, 'date') else line.journal_entry.entry_date,
                journal_entry_id=line.journal_entry_id
            )
            db.add(item)
    
    db.commit()
    db.refresh(reconciliation)
    
    # Mark statement as reconciled
    statement.is_reconciled = True
    statement.reconciled_at = datetime.utcnow()
    statement.reconciled_by = current_user.id
    db.commit()
    
    return reconciliation


@router.get("/reconciliations/{reconciliation_id}", response_model=BankReconciliationResponse)
def get_reconciliation(
    reconciliation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reconciliation details"""
    reconciliation = db.query(BankReconciliation).filter(BankReconciliation.id == reconciliation_id).first()
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    
    return reconciliation


@router.get("/summary/{account_id}", response_model=ReconciliationSummaryResponse)
def get_reconciliation_summary(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reconciliation summary for an account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Get last reconciliation
    last_recon = db.query(BankReconciliation).filter(
        BankReconciliation.account_id == account_id
    ).order_by(BankReconciliation.reconciliation_date.desc()).first()
    
    # Calculate current book balance
    temple_id = current_user.temple_id
    balance_filter = [
        JournalLine.account_id == account_id,
        JournalEntry.status == JournalEntryStatus.POSTED
    ]
    if temple_id is not None:
        balance_filter.append(JournalEntry.temple_id == temple_id)
    
    balance_query = db.query(
        func.sum(JournalLine.debit_amount).label('total_debit'),
        func.sum(JournalLine.credit_amount).label('total_credit')
    ).join(JournalLine.journal_entry).filter(*balance_filter).first()
    
    book_balance = (float(balance_query.total_debit or 0) + account.opening_balance_debit) - \
                   (float(balance_query.total_credit or 0) + account.opening_balance_credit)
    
    # Get outstanding items
    if last_recon:
        outstanding = db.query(ReconciliationOutstandingItem).filter(
            ReconciliationOutstandingItem.reconciliation_id == last_recon.id,
            ReconciliationOutstandingItem.is_cleared == False
        ).all()
        
        cheques = [item for item in outstanding if item.item_type == "cheque_issued"]
        deposits = [item for item in outstanding if item.item_type == "deposit_in_transit"]
    else:
        cheques = []
        deposits = []
    
    return ReconciliationSummaryResponse(
        account_id=account.id,
        account_name=account.account_name,
        last_reconciled_date=last_recon.reconciliation_date if last_recon else None,
        last_reconciliation_id=last_recon.id if last_recon else None,
        book_balance=book_balance,
        statement_balance=None,  # Would need latest statement
        unmatched_statement_entries=0,  # Would need to query
        unmatched_book_entries=0,  # Would need to query
        outstanding_cheques_count=len(cheques),
        outstanding_cheques_amount=sum(c.amount for c in cheques),
        deposits_in_transit_count=len(deposits),
        deposits_in_transit_amount=sum(d.amount for d in deposits)
    )






