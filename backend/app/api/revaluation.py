"""
Asset Revaluation API
Handles revaluation of assets (land, gold, silver, buildings)
Following standard accounting practices for revaluation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.asset import (
    Asset, AssetRevaluation, AssetCategory, AssetStatus
)
from app.models.accounting import (
    Account, JournalEntry, JournalLine,
    JournalEntryStatus, TransactionType
)

router = APIRouter(prefix="/api/v1/assets/revaluation", tags=["revaluation"])


# ===== PYDANTIC SCHEMAS =====

class RevaluationBase(BaseModel):
    revaluation_date: date
    revaluation_type: str  # INCREASE, DECREASE
    revalued_amount: float
    valuation_method: Optional[str] = None  # MARKET_VALUE, PROFESSIONAL_VALUER, INDEX_BASED
    valuer_name: Optional[str] = None
    valuation_report_number: Optional[str] = None
    valuation_report_date: Optional[date] = None

class RevaluationCreate(RevaluationBase):
    pass

class RevaluationResponse(RevaluationBase):
    id: int
    asset_id: int
    previous_book_value: float
    revaluation_amount: float
    revaluation_reserve_account_id: Optional[int]
    journal_entry_id: Optional[int]
    created_at: str
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


# ===== REVALUATION ENDPOINTS =====

@router.post("/", response_model=RevaluationResponse, status_code=status.HTTP_201_CREATED)
def create_revaluation(
    asset_id: int,
    revaluation_data: RevaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record asset revaluation
    For INCREASE: Dr Asset, Cr Revaluation Reserve
    For DECREASE: Dr Revaluation Reserve, Cr Asset (if reserve exists)
                  Dr Revaluation Expense, Cr Asset (if reserve insufficient)
    """
    temple_id = current_user.temple_id
    
    # Get asset
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.temple_id == temple_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    if asset.status != AssetStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Can only revalue active assets")
    
    previous_book_value = asset.current_book_value
    revaluation_amount = revaluation_data.revalued_amount - previous_book_value
    
    if abs(revaluation_amount) < 0.01:  # No significant change
        raise HTTPException(status_code=400, detail="Revaluation amount is negligible")
    
    # Determine revaluation type
    if revaluation_amount > 0:
        revaluation_type = "INCREASE"
    else:
        revaluation_type = "DECREASE"
        revaluation_amount = abs(revaluation_amount)
    
    # Get revaluation reserve account
    revaluation_reserve_account = None
    account_code = "1805"  # Default: Revaluation Reserve - Other
    
    if asset.category:
        category_name = asset.category.name.lower()
        if "land" in category_name:
            account_code = "1801"
        elif "building" in category_name:
            account_code = "1802"
        elif "gold" in category_name:
            account_code = "1803"
        elif "silver" in category_name:
            account_code = "1804"
    
    revaluation_reserve_account = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == account_code
    ).first()
    
    if not revaluation_reserve_account:
        raise HTTPException(status_code=400, detail="Revaluation reserve account not found")
    
    # Get asset account
    asset_account = db.query(Account).filter(Account.id == asset.asset_account_id).first()
    if not asset_account:
        raise HTTPException(status_code=400, detail="Asset account not found")
    
    # Create revaluation record
    revaluation = AssetRevaluation(
        asset_id=asset_id,
        revaluation_date=revaluation_data.revaluation_date,
        revaluation_type=revaluation_type,
        previous_book_value=previous_book_value,
        revalued_amount=revaluation_data.revalued_amount,
        revaluation_amount=revaluation_amount,
        valuation_method=revaluation_data.valuation_method,
        valuer_name=revaluation_data.valuer_name,
        valuation_report_number=revaluation_data.valuation_report_number,
        valuation_report_date=revaluation_data.valuation_report_date,
        revaluation_reserve_account_id=revaluation_reserve_account.id,
        created_by=current_user.id
    )
    db.add(revaluation)
    db.flush()
    
    # Create journal entry
    year = revaluation_data.revaluation_date.year
    prefix = f"JE/{year}/"
    last_entry = db.query(JournalEntry).filter(
        JournalEntry.temple_id == temple_id,
        JournalEntry.entry_number.like(f"{prefix}%")
    ).order_by(JournalEntry.id.desc()).first()
    
    new_num = 1
    if last_entry:
        try:
            last_num = int(last_entry.entry_number.split('/')[-1])
            new_num = last_num + 1
        except:
            pass
    
    entry_number = f"{prefix}{new_num:04d}"
    entry_date = datetime.combine(revaluation_data.revaluation_date, datetime.min.time())
    
    # Get current revaluation reserve balance
    current_reserve = asset.revaluation_reserve or 0.0
    
    if revaluation_type == "INCREASE":
        # Dr Asset, Cr Revaluation Reserve
        journal_entry = JournalEntry(
            temple_id=temple_id,
            entry_date=entry_date,
            entry_number=entry_number,
            narration=f"Asset revaluation (increase) - {asset.name}",
            reference_type=TransactionType.MANUAL,
            reference_id=revaluation.id,
            total_amount=revaluation_amount,
            status=JournalEntryStatus.POSTED,
            created_by=current_user.id,
            posted_by=current_user.id,
            posted_at=datetime.utcnow()
        )
        db.add(journal_entry)
        db.flush()
        
        # Dr Asset
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=asset_account.id,
            debit_amount=revaluation_amount,
            credit_amount=0,
            description=f"Revaluation increase - {asset.name}"
        )
        
        # Cr Revaluation Reserve
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=revaluation_reserve_account.id,
            debit_amount=0,
            credit_amount=revaluation_amount,
            description=f"Revaluation reserve - {asset.name}"
        )
        
        db.add(debit_line)
        db.add(credit_line)
        
        # Update asset
        asset.current_book_value = revaluation_data.revalued_amount
        asset.revalued_amount = revaluation_data.revalued_amount
        asset.revaluation_reserve += revaluation_amount
    
    else:  # DECREASE
        # Check if reserve is sufficient
        if current_reserve >= revaluation_amount:
            # Dr Revaluation Reserve, Cr Asset
            journal_entry = JournalEntry(
                temple_id=temple_id,
                entry_date=entry_date,
                entry_number=entry_number,
                narration=f"Asset revaluation (decrease) - {asset.name}",
                reference_type=TransactionType.MANUAL,
                reference_id=revaluation.id,
                total_amount=revaluation_amount,
                status=JournalEntryStatus.POSTED,
                created_by=current_user.id,
                posted_by=current_user.id,
                posted_at=datetime.utcnow()
            )
            db.add(journal_entry)
            db.flush()
            
            # Dr Revaluation Reserve
            debit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=revaluation_reserve_account.id,
                debit_amount=revaluation_amount,
                credit_amount=0,
                description=f"Revaluation reserve decrease - {asset.name}"
            )
            
            # Cr Asset
            credit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=asset_account.id,
                debit_amount=0,
                credit_amount=revaluation_amount,
                description=f"Revaluation decrease - {asset.name}"
            )
            
            db.add(debit_line)
            db.add(credit_line)
            
            # Update asset
            asset.current_book_value = revaluation_data.revalued_amount
            asset.revalued_amount = revaluation_data.revalued_amount
            asset.revaluation_reserve -= revaluation_amount
        
        else:
            # Partial from reserve, rest as expense
            reserve_used = current_reserve
            expense_amount = revaluation_amount - reserve_used
            
            # Get revaluation expense account (or use general expense)
            expense_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == "6001"  # Depreciation/Revaluation Expense
            ).first()
            
            if not expense_account:
                raise HTTPException(status_code=400, detail="Expense account not found")
            
            journal_entry = JournalEntry(
                temple_id=temple_id,
                entry_date=entry_date,
                entry_number=entry_number,
                narration=f"Asset revaluation (decrease) - {asset.name}",
                reference_type=TransactionType.MANUAL,
                reference_id=revaluation.id,
                total_amount=revaluation_amount,
                status=JournalEntryStatus.POSTED,
                created_by=current_user.id,
                posted_by=current_user.id,
                posted_at=datetime.utcnow()
            )
            db.add(journal_entry)
            db.flush()
            
            # Dr Revaluation Reserve (if any)
            if reserve_used > 0:
                reserve_line = JournalLine(
                    journal_entry_id=journal_entry.id,
                    account_id=revaluation_reserve_account.id,
                    debit_amount=reserve_used,
                    credit_amount=0,
                    description=f"Revaluation reserve decrease - {asset.name}"
                )
                db.add(reserve_line)
            
            # Dr Revaluation Expense (excess)
            if expense_amount > 0:
                expense_line = JournalLine(
                    journal_entry_id=journal_entry.id,
                    account_id=expense_account.id,
                    debit_amount=expense_amount,
                    credit_amount=0,
                    description=f"Revaluation expense - {asset.name}"
                )
                db.add(expense_line)
            
            # Cr Asset
            credit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=asset_account.id,
                debit_amount=0,
                credit_amount=revaluation_amount,
                description=f"Revaluation decrease - {asset.name}"
            )
            db.add(credit_line)
            
            # Update asset
            asset.current_book_value = revaluation_data.revalued_amount
            asset.revalued_amount = revaluation_data.revalued_amount
            asset.revaluation_reserve = 0.0  # Reserve exhausted
    
    revaluation.journal_entry_id = journal_entry.id
    asset.updated_at = datetime.utcnow()
    
    # Add to valuation history
    from app.models.asset_history import AssetValuationHistory
    valuation_history = AssetValuationHistory(
        asset_id=asset_id,
        valuation_date=revaluation_data.revaluation_date,
        valuation_type="REVALUATION",
        valuation_amount=revaluation_data.revalued_amount,
        valuation_method=revaluation_data.valuation_method,
        valuer_name=revaluation_data.valuer_name,
        valuation_report_number=revaluation_data.valuation_report_number,
        valuation_report_date=revaluation_data.valuation_report_date,
        reference_id=revaluation.id,
        reference_type="revaluation",
        notes=None,
        created_by=current_user.id
    )
    db.add(valuation_history)
    
    db.commit()
    db.refresh(revaluation)
    return revaluation


@router.get("/{asset_id}", response_model=List[RevaluationResponse])
def get_revaluation_history(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get revaluation history for an asset"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.temple_id == current_user.temple_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    revaluations = db.query(AssetRevaluation).filter(
        AssetRevaluation.asset_id == asset_id
    ).order_by(AssetRevaluation.revaluation_date.desc()).all()
    
    return revaluations

