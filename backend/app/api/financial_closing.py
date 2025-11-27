"""
Financial Period Closing API
Handles month-end and year-end closing processes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.accounting import Account, JournalEntry, JournalLine, JournalEntryStatus, AccountType
from app.models.financial_period import (
    FinancialYear, FinancialPeriod, PeriodClosing,
    PeriodStatus, ClosingType
)
from app.schemas.financial_closing import (
    FinancialYearCreate, FinancialYearResponse,
    PeriodClosingRequest, PeriodClosingResponse,
    ClosingSummaryResponse
)

router = APIRouter(prefix="/api/v1/financial-closing", tags=["financial-closing"])


@router.post("/financial-years", response_model=FinancialYearResponse)
def create_financial_year(
    year_data: FinancialYearCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new financial year"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can create financial years")
    
    # Check if year code already exists
    existing = db.query(FinancialYear).filter(FinancialYear.year_code == year_data.year_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Financial year {year_data.year_code} already exists")
    
    financial_year = FinancialYear(
        temple_id=current_user.temple_id,
        year_code=year_data.year_code,
        start_date=year_data.start_date,
        end_date=year_data.end_date
    )
    db.add(financial_year)
    db.commit()
    db.refresh(financial_year)
    
    return financial_year


@router.get("/financial-years", response_model=List[FinancialYearResponse])
def get_financial_years(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all financial years"""
    query = db.query(FinancialYear)
    if current_user.temple_id:
        query = query.filter(FinancialYear.temple_id == current_user.temple_id)
    
    return query.order_by(FinancialYear.start_date.desc()).all()


@router.get("/financial-years/active", response_model=FinancialYearResponse)
def get_active_financial_year(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the currently active financial year"""
    query = db.query(FinancialYear).filter(
        FinancialYear.is_active == True,
        FinancialYear.is_closed == False
    )
    if current_user.temple_id:
        query = query.filter(FinancialYear.temple_id == current_user.temple_id)
    
    financial_year = query.first()
    if not financial_year:
        raise HTTPException(status_code=404, detail="No active financial year found")
    
    return financial_year


@router.post("/close-month", response_model=PeriodClosingResponse)
def close_month(
    closing_data: PeriodClosingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform month-end closing
    Creates closing entries and locks the period
    """
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can close periods")
    
    temple_id = current_user.temple_id
    
    # Get financial year
    financial_year = db.query(FinancialYear).filter(FinancialYear.id == closing_data.financial_year_id).first()
    if not financial_year:
        raise HTTPException(status_code=404, detail="Financial year not found")
    
    if financial_year.is_closed:
        raise HTTPException(status_code=400, detail="Financial year is already closed")
    
    # Calculate income and expenses for the month
    month_start = closing_data.closing_date.replace(day=1)
    # Calculate month end correctly
    if month_start.month == 12:
        month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)
    
    # Check if period is already closed
    existing_closing = db.query(PeriodClosing).filter(
        PeriodClosing.financial_year_id == financial_year.id,
        PeriodClosing.temple_id == temple_id,
        PeriodClosing.closing_type == ClosingType.MONTH_END,
        PeriodClosing.closing_date >= month_start,
        PeriodClosing.closing_date <= month_end,
        PeriodClosing.is_completed == True
    ).first()
    if existing_closing:
        raise HTTPException(
            status_code=400,
            detail=f"Month-end closing for {month_start.strftime('%B %Y')} is already completed."
        )
    
    # Get income accounts
    income_filter = [
        Account.account_type == AccountType.INCOME,
        Account.is_active == True
    ]
    if temple_id is not None:
        income_filter.append(Account.temple_id == temple_id)
    
    income_accounts = db.query(Account).filter(*income_filter).all()
    income_account_ids = [acc.id for acc in income_accounts]
    
    # Calculate total income
    income_query = db.query(
        func.sum(JournalLine.credit_amount).label('total_income')
    ).join(JournalLine.journal_entry).filter(
        JournalLine.account_id.in_(income_account_ids),
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) >= month_start,
        func.date(JournalEntry.entry_date) <= month_end
    )
    if temple_id is not None:
        income_query = income_query.filter(JournalEntry.temple_id == temple_id)
    
    total_income = float(income_query.first().total_income or 0)
    
    # Get expense accounts
    expense_filter = [
        Account.account_type == AccountType.EXPENSE,
        Account.is_active == True
    ]
    if temple_id is not None:
        expense_filter.append(Account.temple_id == temple_id)
    
    expense_accounts = db.query(Account).filter(*expense_filter).all()
    expense_account_ids = [acc.id for acc in expense_accounts]
    
    # Calculate total expenses
    expense_query = db.query(
        func.sum(JournalLine.debit_amount).label('total_expenses')
    ).join(JournalLine.journal_entry).filter(
        JournalLine.account_id.in_(expense_account_ids),
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) >= month_start,
        func.date(JournalEntry.entry_date) <= month_end
    )
    if temple_id is not None:
        expense_query = expense_query.filter(JournalEntry.temple_id == temple_id)
    
    total_expenses = float(expense_query.first().total_expenses or 0)
    net_surplus = total_income - total_expenses
    
    # Create closing journal entry (transfer to General Fund)
    # Dr: Income Summary (if surplus) or Expense Summary (if deficit)
    # Cr: General Fund (surplus) or Dr: General Fund (deficit)
    
    # Find or create General Fund account
    general_fund = db.query(Account).filter(
        Account.account_code == '3101',  # General Fund
        Account.is_active == True
    )
    if temple_id is not None:
        general_fund = general_fund.filter(Account.temple_id == temple_id)
    general_fund = general_fund.first()
    
    if not general_fund:
        raise HTTPException(status_code=400, detail="General Fund account not found. Please create it in Chart of Accounts.")
    
    # Generate closing entry number
    year = closing_data.closing_date.year
    prefix = f"CLOSE/{year}/"
    last_entry = db.query(JournalEntry).filter(
        JournalEntry.entry_number.like(f"{prefix}%")
    ).order_by(JournalEntry.id.desc()).first()
    
    if last_entry:
        try:
            last_num = int(last_entry.entry_number.split('/')[-1])
            new_num = last_num + 1
        except:
            new_num = 1
    else:
        new_num = 1
    
    entry_number = f"{prefix}{new_num:05d}"
    
    # Create closing journal entry
    closing_entry = JournalEntry(
        temple_id=temple_id,
        entry_number=entry_number,
        entry_date=closing_data.closing_date,
        reference_type="month_end_closing",
        narration=f"Month-end closing for {closing_data.closing_date.strftime('%B %Y')}",
        status=JournalEntryStatus.POSTED,
        created_by=current_user.id
    )
    db.add(closing_entry)
    db.flush()
    
    # Create journal lines
    if net_surplus > 0:
        # Surplus: Dr Income Summary, Cr General Fund
        # For simplicity, we'll credit General Fund directly
        db.add(JournalLine(
            journal_entry_id=closing_entry.id,
            account_id=general_fund.id,
            debit_amount=0.0,
            credit_amount=net_surplus,
            description=f"Month-end surplus transferred to General Fund"
        ))
    else:
        # Deficit: Dr General Fund, Cr Expense Summary
        db.add(JournalLine(
            journal_entry_id=closing_entry.id,
            account_id=general_fund.id,
            debit_amount=abs(net_surplus),
            credit_amount=0.0,
            description=f"Month-end deficit transferred from General Fund"
        ))
    
    # Create period closing record
    period_closing = PeriodClosing(
        financial_year_id=financial_year.id,
        temple_id=temple_id,
        closing_type=ClosingType.MONTH_END,
        closing_date=closing_data.closing_date,
        period_start=month_start,
        period_end=month_end,
        total_income=total_income,
        total_expenses=total_expenses,
        net_surplus=net_surplus,
        closing_journal_entry_id=closing_entry.id,
        is_completed=True,
        completed_at=datetime.utcnow(),
        completed_by=current_user.id,
        notes=closing_data.notes
    )
    db.add(period_closing)
    
    # Lock the period (create or update FinancialPeriod)
    period = db.query(FinancialPeriod).filter(
        FinancialPeriod.financial_year_id == financial_year.id,
        FinancialPeriod.temple_id == temple_id,
        FinancialPeriod.start_date == month_start,
        FinancialPeriod.end_date == month_end
    ).first()
    
    if not period:
        period = FinancialPeriod(
            financial_year_id=financial_year.id,
            temple_id=temple_id,
            period_name=closing_data.closing_date.strftime('%B %Y'),
            period_type="month",
            start_date=month_start,
            end_date=month_end,
            status=PeriodStatus.CLOSED,
            is_locked=True,
            is_closed=True,
            closed_at=datetime.utcnow(),
            closed_by=current_user.id
        )
        db.add(period)
    else:
        period.status = PeriodStatus.CLOSED
        period.is_locked = True
        period.is_closed = True
        period.closed_at = datetime.utcnow()
        period.closed_by = current_user.id
    
    db.commit()
    db.refresh(period_closing)
    
    return period_closing


@router.post("/close-year", response_model=PeriodClosingResponse)
def close_year(
    closing_data: PeriodClosingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform year-end closing
    Closes the financial year and prepares opening balances for next year
    """
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can close financial years")
    
    temple_id = current_user.temple_id
    
    # Get financial year
    financial_year = db.query(FinancialYear).filter(
        FinancialYear.id == closing_data.financial_year_id,
        FinancialYear.temple_id == temple_id
    ).first()
    if not financial_year:
        raise HTTPException(status_code=404, detail="Financial year not found")
    
    if financial_year.is_closed:
        raise HTTPException(status_code=400, detail="Financial year is already closed")
    
    # Check if year-end closing already exists
    existing_closing = db.query(PeriodClosing).filter(
        PeriodClosing.financial_year_id == closing_data.financial_year_id,
        PeriodClosing.temple_id == temple_id,
        PeriodClosing.closing_type == ClosingType.YEAR_END,
        PeriodClosing.is_completed == True
    ).first()
    if existing_closing:
        raise HTTPException(
            status_code=400,
            detail=f"Year-end closing for {financial_year.year_code} is already completed."
        )
    
    # Calculate year totals
    
    # Get income and expenses for the year
    income_accounts = db.query(Account).filter(
        Account.account_type == AccountType.INCOME,
        Account.is_active == True
    )
    if temple_id is not None:
        income_accounts = income_accounts.filter(Account.temple_id == temple_id)
    income_accounts = income_accounts.all()
    
    expense_accounts = db.query(Account).filter(
        Account.account_type == AccountType.EXPENSE,
        Account.is_active == True
    )
    if temple_id is not None:
        expense_accounts = expense_accounts.filter(Account.temple_id == temple_id)
    expense_accounts = expense_accounts.all()
    
    income_ids = [acc.id for acc in income_accounts]
    expense_ids = [acc.id for acc in expense_accounts]
    
    # Calculate totals
    income_query = db.query(func.sum(JournalLine.credit_amount)).join(JournalLine.journal_entry).filter(
        JournalLine.account_id.in_(income_ids),
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) >= financial_year.start_date,
        func.date(JournalEntry.entry_date) <= financial_year.end_date
    )
    if temple_id is not None:
        income_query = income_query.filter(JournalEntry.temple_id == temple_id)
    total_income = float(income_query.first()[0] or 0)
    
    expense_query = db.query(func.sum(JournalLine.debit_amount)).join(JournalLine.journal_entry).filter(
        JournalLine.account_id.in_(expense_ids),
        JournalEntry.status == JournalEntryStatus.POSTED,
        func.date(JournalEntry.entry_date) >= financial_year.start_date,
        func.date(JournalEntry.entry_date) <= financial_year.end_date
    )
    if temple_id is not None:
        expense_query = expense_query.filter(JournalEntry.temple_id == temple_id)
    total_expenses = float(expense_query.first()[0] or 0)
    net_surplus = total_income - total_expenses
    
    # Create year-end closing entry
    year = financial_year.end_date.year
    prefix = f"YEAR-END/{year}/"
    last_entry = db.query(JournalEntry).filter(
        JournalEntry.entry_number.like(f"{prefix}%")
    ).order_by(JournalEntry.id.desc()).first()
    
    entry_number = f"{prefix}00001" if not last_entry else f"{prefix}{int(last_entry.entry_number.split('/')[-1]) + 1:05d}"
    
    closing_entry = JournalEntry(
        temple_id=temple_id,
        entry_number=entry_number,
        entry_date=closing_data.closing_date,
        reference_type="year_end_closing",
        narration=f"Year-end closing for {financial_year.year_code}",
        status=JournalEntryStatus.POSTED,
        created_by=current_user.id
    )
    db.add(closing_entry)
    db.flush()
    
    # Transfer surplus/deficit to General Fund
    general_fund = db.query(Account).filter(Account.account_code == '3101')
    if temple_id is not None:
        general_fund = general_fund.filter(Account.temple_id == temple_id)
    general_fund = general_fund.first()
    
    if general_fund:
        if net_surplus > 0:
            db.add(JournalLine(
                journal_entry_id=closing_entry.id,
                account_id=general_fund.id,
                debit_amount=0.0,
                credit_amount=net_surplus,
                description=f"Year-end surplus {financial_year.year_code}"
            ))
        else:
            db.add(JournalLine(
                journal_entry_id=closing_entry.id,
                account_id=general_fund.id,
                debit_amount=abs(net_surplus),
                credit_amount=0.0,
                description=f"Year-end deficit {financial_year.year_code}"
            ))
    
    # Create closing record
    period_closing = PeriodClosing(
        financial_year_id=financial_year.id,
        temple_id=temple_id,
        closing_type=ClosingType.YEAR_END,
        closing_date=closing_data.closing_date,
        period_start=financial_year.start_date,
        period_end=financial_year.end_date,
        total_income=total_income,
        total_expenses=total_expenses,
        net_surplus=net_surplus,
        closing_journal_entry_id=closing_entry.id,
        is_completed=True,
        completed_at=datetime.utcnow(),
        completed_by=current_user.id,
        notes=closing_data.notes
    )
    db.add(period_closing)
    
    # Close financial year
    financial_year.is_closed = True
    financial_year.is_active = False
    financial_year.closed_at = datetime.utcnow()
    financial_year.closed_by = current_user.id
    financial_year.closing_date = closing_data.closing_date
    
    db.commit()
    db.refresh(period_closing)
    
    return period_closing


@router.get("/period-closings", response_model=List[PeriodClosingResponse])
def get_period_closings(
    financial_year_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all period closings"""
    query = db.query(PeriodClosing)
    
    if current_user.temple_id:
        query = query.filter(PeriodClosing.temple_id == current_user.temple_id)
    
    if financial_year_id:
        query = query.filter(PeriodClosing.financial_year_id == financial_year_id)
    
    return query.order_by(PeriodClosing.closing_date.desc()).all()


@router.get("/closings/{closing_id}/summary", response_model=ClosingSummaryResponse)
def get_closing_summary_by_id(
    closing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get closing summary by closing ID"""
    closing = db.query(PeriodClosing).filter(PeriodClosing.id == closing_id).first()
    if not closing:
        raise HTTPException(status_code=404, detail="Closing not found")
    
    # Get period dates
    period_start = closing.period_start if hasattr(closing, 'period_start') and closing.period_start else None
    period_end = closing.period_end if hasattr(closing, 'period_end') and closing.period_end else None
    
    if not period_start or not period_end:
        # Calculate from closing date
        if closing.closing_type == ClosingType.MONTH_END:
            period_start = closing.closing_date.replace(day=1)
            next_month = period_start.replace(month=period_start.month % 12 + 1) if period_start.month < 12 else period_start.replace(year=period_start.year + 1, month=1)
            period_end = (next_month - timedelta(days=1))
        else:
            # Year end - get from financial year
            financial_year = db.query(FinancialYear).filter(FinancialYear.id == closing.financial_year_id).first()
            if financial_year:
                period_start = financial_year.start_date
                period_end = financial_year.end_date
            else:
                period_start = closing.closing_date.replace(month=1, day=1)
                period_end = closing.closing_date.replace(month=12, day=31)
    
    # Get journal entry number
    journal_entry_number = None
    if closing.closing_journal_entry_id:
        journal_entry = db.query(JournalEntry).filter(JournalEntry.id == closing.closing_journal_entry_id).first()
        if journal_entry:
            journal_entry_number = journal_entry.entry_number
    
    return ClosingSummaryResponse(
        period_start=period_start,
        period_end=period_end,
        total_income=closing.total_income or 0.0,
        total_expenses=closing.total_expenses or 0.0,
        net_surplus=closing.net_surplus or 0.0,
        transaction_count=0,
        journal_entry_number=journal_entry_number
    )


@router.get("/closing-summary", response_model=ClosingSummaryResponse)
def get_closing_summary(
    period_start: date,
    period_end: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary for period closing"""
    temple_id = current_user.temple_id
    
    # Calculate income and expenses
    income_accounts = db.query(Account).filter(
        Account.account_type == AccountType.INCOME,
        Account.is_active == True
    )
    if temple_id is not None:
        income_accounts = income_accounts.filter(Account.temple_id == temple_id)
    income_ids = [acc.id for acc in income_accounts.all()]
    
    expense_accounts = db.query(Account).filter(
        Account.account_type == AccountType.EXPENSE,
        Account.is_active == True
    )
    if temple_id is not None:
        expense_accounts = expense_accounts.filter(Account.temple_id == temple_id)
    expense_ids = [acc.id for acc in expense_accounts.all()]
    
    income_total = 0.0
    if income_ids:
        income_query = db.query(func.sum(JournalLine.credit_amount)).join(JournalLine.journal_entry).filter(
            JournalLine.account_id.in_(income_ids),
            JournalEntry.status == JournalEntryStatus.POSTED,
            func.date(JournalEntry.entry_date) >= period_start,
            func.date(JournalEntry.entry_date) <= period_end
        )
        if temple_id is not None:
            income_query = income_query.filter(JournalEntry.temple_id == temple_id)
        income_total = float(income_query.first()[0] or 0)
    
    expense_total = 0.0
    if expense_ids:
        expense_query = db.query(func.sum(JournalLine.debit_amount)).join(JournalLine.journal_entry).filter(
            JournalLine.account_id.in_(expense_ids),
            JournalEntry.status == JournalEntryStatus.POSTED,
            func.date(JournalEntry.entry_date) >= period_start,
            func.date(JournalEntry.entry_date) <= period_end
        )
        if temple_id is not None:
            expense_query = expense_query.filter(JournalEntry.temple_id == temple_id)
        expense_total = float(expense_query.first()[0] or 0)
    
    return ClosingSummaryResponse(
        period_start=period_start,
        period_end=period_end,
        total_income=income_total,
        total_expenses=expense_total,
        net_surplus=income_total - expense_total,
        transaction_count=0  # Can be calculated if needed
    )

