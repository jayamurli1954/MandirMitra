"""
Capital Work in Progress (CWIP) API
Handles construction/installation projects, expenses, and capitalization
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.asset import CapitalWorkInProgress, AssetExpense, Asset, AssetCategory, AssetStatus
from app.models.accounting import (
    Account,
    JournalEntry,
    JournalLine,
    JournalEntryStatus,
    TransactionType,
)
from app.models.vendor import Vendor
from .asset import AssetResponse

router = APIRouter(prefix="/api/v1/assets/cwip", tags=["cwip"])


# ===== PYDANTIC SCHEMAS =====


class CWIPBase(BaseModel):
    cwip_number: str
    project_name: str
    description: Optional[str] = None
    asset_category_id: int
    start_date: date
    expected_completion_date: Optional[date] = None
    total_budget: float = 0.0
    tender_id: Optional[int] = None


class CWIPCreate(CWIPBase):
    pass


class CWIPResponse(CWIPBase):
    id: int
    temple_id: Optional[int]
    total_expenditure: float
    status: str
    asset_id: Optional[int]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CWIPExpenseBase(BaseModel):
    expense_date: date
    description: str
    amount: float
    expense_category: Optional[str] = None  # MATERIAL, LABOR, OVERHEAD, OTHER
    vendor_id: Optional[int] = None
    reference_number: Optional[str] = None


class CWIPExpenseCreate(CWIPExpenseBase):
    pass


class CWIPExpenseResponse(CWIPExpenseBase):
    id: int
    cwip_id: int
    journal_entry_id: Optional[int]
    created_at: str

    class Config:
        from_attributes = True


class CapitalizeRequest(BaseModel):
    """Request to capitalize CWIP to Asset"""

    asset_number: str
    asset_name: str
    description: Optional[str] = None
    location: Optional[str] = None
    tag_number: Optional[str] = None
    serial_number: Optional[str] = None
    capitalization_date: date
    # Depreciation details
    depreciation_method: str = "straight_line"
    useful_life_years: float = 0.0
    depreciation_rate_percent: float = 0.0
    salvage_value: float = 0.0
    is_depreciable: bool = True


# ===== CWIP ENDPOINTS =====


@router.post("/", response_model=CWIPResponse, status_code=status.HTTP_201_CREATED)
def create_cwip(
    cwip_data: CWIPCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new CWIP project"""
    temple_id = current_user.temple_id

    # Validate category
    category = (
        db.query(AssetCategory)
        .filter(
            AssetCategory.id == cwip_data.asset_category_id, AssetCategory.temple_id == temple_id
        )
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Asset category not found")

    # Check if CWIP number already exists
    existing = (
        db.query(CapitalWorkInProgress)
        .filter(
            CapitalWorkInProgress.temple_id == temple_id,
            CapitalWorkInProgress.cwip_number == cwip_data.cwip_number,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="CWIP number already exists")

    # Determine CWIP account
    cwip_account = None
    # Map to CWIP account based on project type
    account_code = "15020"  # Capital Work in Progress (default)
    # All CWIP goes to single account

    cwip_account = (
        db.query(Account)
        .filter(Account.temple_id == temple_id, Account.account_code == account_code)
        .first()
    )

    if not cwip_account:
        raise HTTPException(
            status_code=400, detail="CWIP account not found. Please setup asset accounts first."
        )

    # Create CWIP
    cwip = CapitalWorkInProgress(
        **cwip_data.dict(),
        temple_id=temple_id,
        total_expenditure=0.0,
        status="in_progress",
        account_id=cwip_account.id,
        created_by=current_user.id,
    )
    db.add(cwip)
    db.commit()
    db.refresh(cwip)
    return cwip


@router.get("/", response_model=List[CWIPResponse])
def list_cwip(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all CWIP projects"""
    query = db.query(CapitalWorkInProgress).filter(
        CapitalWorkInProgress.temple_id == current_user.temple_id
    )
    if status:
        query = query.filter(CapitalWorkInProgress.status == status)
    return query.order_by(CapitalWorkInProgress.cwip_number).all()


@router.get("/{cwip_id}", response_model=CWIPResponse)
def get_cwip(
    cwip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get CWIP project details"""
    cwip = (
        db.query(CapitalWorkInProgress)
        .filter(
            CapitalWorkInProgress.id == cwip_id,
            CapitalWorkInProgress.temple_id == current_user.temple_id,
        )
        .first()
    )

    if not cwip:
        raise HTTPException(status_code=404, detail="CWIP project not found")

    return cwip


@router.post(
    "/{cwip_id}/expenses/", response_model=CWIPExpenseResponse, status_code=status.HTTP_201_CREATED
)
def add_cwip_expense(
    cwip_id: int,
    expense_data: CWIPExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add expense to CWIP project
    Creates accounting entry: Dr CWIP, Cr Cash/Bank/Payables
    """
    temple_id = current_user.temple_id

    # Get CWIP
    cwip = (
        db.query(CapitalWorkInProgress)
        .filter(CapitalWorkInProgress.id == cwip_id, CapitalWorkInProgress.temple_id == temple_id)
        .first()
    )

    if not cwip:
        raise HTTPException(status_code=404, detail="CWIP project not found")

    if cwip.status != "in_progress":
        raise HTTPException(
            status_code=400, detail="Cannot add expenses to completed/suspended CWIP"
        )

    # Get CWIP account
    cwip_account = db.query(Account).filter(Account.id == cwip.account_id).first()
    if not cwip_account:
        raise HTTPException(status_code=400, detail="CWIP account not found")

    # Determine credit account (payment method)
    credit_account = (
        db.query(Account)
        .filter(
            Account.temple_id == temple_id,
            Account.account_code == "11001",  # Cash in Hand - Counter
        )
        .first()
    )

    if not credit_account:
        raise HTTPException(status_code=400, detail="Credit account not found")

    # Create expense
    expense = AssetExpense(cwip_id=cwip_id, **expense_data.dict(), created_by=current_user.id)
    db.add(expense)
    db.flush()

    # Update CWIP expenditure
    cwip.total_expenditure += expense_data.amount
    cwip.updated_at = datetime.utcnow()

    # Create journal entry
    year = expense_data.expense_date.year
    prefix = f"JE/{year}/"
    last_entry = (
        db.query(JournalEntry)
        .filter(JournalEntry.temple_id == temple_id, JournalEntry.entry_number.like(f"{prefix}%"))
        .order_by(JournalEntry.id.desc())
        .first()
    )

    new_num = 1
    if last_entry:
        try:
            last_num = int(last_entry.entry_number.split("/")[-1])
            new_num = last_num + 1
        except:
            pass

    entry_number = f"{prefix}{new_num:04d}"
    entry_date = datetime.combine(expense_data.expense_date, datetime.min.time())

    journal_entry = JournalEntry(
        temple_id=temple_id,
        entry_date=entry_date,
        entry_number=entry_number,
        narration=f"CWIP expense - {cwip.project_name}: {expense_data.description}",
        reference_type=TransactionType.MANUAL,
        reference_id=expense.id,
        total_amount=expense_data.amount,
        status=JournalEntryStatus.POSTED,
        created_by=current_user.id,
        posted_by=current_user.id,
        posted_at=datetime.utcnow(),
    )
    db.add(journal_entry)
    db.flush()

    # Create journal lines
    debit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=cwip_account.id,
        debit_amount=expense_data.amount,
        credit_amount=0,
        description=f"CWIP expense - {expense_data.description}",
    )

    credit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=credit_account.id,
        debit_amount=0,
        credit_amount=expense_data.amount,
        description=f"Payment for {expense_data.description}",
    )

    db.add(debit_line)
    db.add(credit_line)

    expense.journal_entry_id = journal_entry.id

    db.commit()
    db.refresh(expense)
    return expense


@router.get("/{cwip_id}/expenses/", response_model=List[CWIPExpenseResponse])
def list_cwip_expenses(
    cwip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """List all expenses for a CWIP project"""
    cwip = (
        db.query(CapitalWorkInProgress)
        .filter(
            CapitalWorkInProgress.id == cwip_id,
            CapitalWorkInProgress.temple_id == current_user.temple_id,
        )
        .first()
    )

    if not cwip:
        raise HTTPException(status_code=404, detail="CWIP project not found")

    expenses = (
        db.query(AssetExpense)
        .filter(AssetExpense.cwip_id == cwip_id)
        .order_by(AssetExpense.expense_date.desc())
        .all()
    )

    return expenses


@router.post(
    "/{cwip_id}/capitalize/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED
)
def capitalize_cwip(
    cwip_id: int,
    capitalize_request: CapitalizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Capitalize CWIP to Fixed Asset
    Creates asset and transfers CWIP balance to asset account
    Dr: Asset Account, Cr: CWIP Account
    """
    temple_id = current_user.temple_id

    # Get CWIP
    cwip = (
        db.query(CapitalWorkInProgress)
        .filter(CapitalWorkInProgress.id == cwip_id, CapitalWorkInProgress.temple_id == temple_id)
        .first()
    )

    if not cwip:
        raise HTTPException(status_code=404, detail="CWIP project not found")

    if cwip.status == "completed":
        raise HTTPException(status_code=400, detail="CWIP already capitalized")

    if cwip.total_expenditure == 0:
        raise HTTPException(status_code=400, detail="Cannot capitalize CWIP with zero expenditure")

    # Get category
    category = db.query(AssetCategory).filter(AssetCategory.id == cwip.asset_category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Asset category not found")

    # Check if asset number already exists
    existing = (
        db.query(Asset)
        .filter(Asset.temple_id == temple_id, Asset.asset_number == capitalize_request.asset_number)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Asset number already exists")

    # Determine asset account (same logic as purchase)
    asset_account = None
    if category.account_id:
        asset_account = db.query(Account).filter(Account.id == category.account_id).first()

    if not asset_account:
        account_code = "15002"  # Building (Fixed Assets)
        # All fixed assets under building
        asset_account = (
            db.query(Account)
            .filter(Account.temple_id == temple_id, Account.account_code == account_code)
            .first()
        )

    if not asset_account:
        raise HTTPException(status_code=400, detail="Asset account not found")

    # Get CWIP account
    cwip_account = db.query(Account).filter(Account.id == cwip.account_id).first()
    if not cwip_account:
        raise HTTPException(status_code=400, detail="CWIP account not found")

    # Create asset
    from app.models.depreciation_methods import DepreciationMethod

    asset = Asset(
        asset_number=capitalize_request.asset_number,
        name=capitalize_request.asset_name,
        description=capitalize_request.description,
        category_id=cwip.asset_category_id,
        asset_type=AssetType.FIXED,
        location=capitalize_request.location,
        tag_number=capitalize_request.tag_number,
        serial_number=capitalize_request.serial_number,
        purchase_date=capitalize_request.capitalization_date,
        original_cost=cwip.total_expenditure,
        current_book_value=cwip.total_expenditure,
        accumulated_depreciation=0.0,
        depreciation_method=DepreciationMethod(capitalize_request.depreciation_method),
        useful_life_years=capitalize_request.useful_life_years,
        depreciation_rate_percent=capitalize_request.depreciation_rate_percent,
        salvage_value=capitalize_request.salvage_value,
        is_depreciable=capitalize_request.is_depreciable,
        depreciation_start_date=capitalize_request.capitalization_date
        if capitalize_request.is_depreciable
        else None,
        status=AssetStatus.ACTIVE,
        cwip_id=cwip_id,
        asset_account_id=asset_account.id,
        temple_id=temple_id,
        created_by=current_user.id,
    )
    db.add(asset)
    db.flush()

    # Create journal entry for capitalization
    year = capitalize_request.capitalization_date.year
    prefix = f"JE/{year}/"
    last_entry = (
        db.query(JournalEntry)
        .filter(JournalEntry.temple_id == temple_id, JournalEntry.entry_number.like(f"{prefix}%"))
        .order_by(JournalEntry.id.desc())
        .first()
    )

    new_num = 1
    if last_entry:
        try:
            last_num = int(last_entry.entry_number.split("/")[-1])
            new_num = last_num + 1
        except:
            pass

    entry_number = f"{prefix}{new_num:04d}"
    entry_date = datetime.combine(capitalize_request.capitalization_date, datetime.min.time())

    journal_entry = JournalEntry(
        temple_id=temple_id,
        entry_date=entry_date,
        entry_number=entry_number,
        narration=f"Capitalization - {cwip.project_name} to {capitalize_request.asset_name}",
        reference_type=TransactionType.MANUAL,
        reference_id=asset.id,
        total_amount=cwip.total_expenditure,
        status=JournalEntryStatus.POSTED,
        created_by=current_user.id,
        posted_by=current_user.id,
        posted_at=datetime.utcnow(),
    )
    db.add(journal_entry)
    db.flush()

    # Create journal lines
    debit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=asset_account.id,
        debit_amount=cwip.total_expenditure,
        credit_amount=0,
        description=f"Capitalization - {capitalize_request.asset_name}",
    )

    credit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=cwip_account.id,
        debit_amount=0,
        credit_amount=cwip.total_expenditure,
        description=f"Transfer from CWIP - {cwip.project_name}",
    )

    db.add(debit_line)
    db.add(credit_line)

    # Update CWIP status
    cwip.status = "completed"
    cwip.actual_completion_date = capitalize_request.capitalization_date
    cwip.asset_id = asset.id
    cwip.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(asset)
    return asset
