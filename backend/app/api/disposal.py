"""
Asset Disposal API
Handles asset disposal (sale, scrap, donation, loss)
Following standard accounting practices
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
    Asset, AssetDisposal, AssetStatus, DisposalType
)
from app.models.accounting import (
    Account, JournalEntry, JournalLine,
    JournalEntryStatus, TransactionType
)

router = APIRouter(prefix="/api/v1/assets/disposal", tags=["disposal"])


# ===== PYDANTIC SCHEMAS =====

class DisposalBase(BaseModel):
    disposal_date: date
    disposal_type: DisposalType
    disposal_reason: Optional[str] = None
    disposal_proceeds: float = 0.0  # If sold
    buyer_name: Optional[str] = None
    disposal_document_number: Optional[str] = None

class DisposalCreate(DisposalBase):
    pass

class DisposalResponse(DisposalBase):
    id: int
    asset_id: int
    book_value_at_disposal: float
    accumulated_depreciation_at_disposal: float
    gain_loss_amount: float
    journal_entry_id: Optional[int]
    created_at: str
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


# ===== DISPOSAL ENDPOINTS =====

@router.post("/", response_model=DisposalResponse, status_code=status.HTTP_201_CREATED)
def dispose_asset(
    asset_id: int,
    disposal_data: DisposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record asset disposal
    Accounting entries:
    - Dr Accumulated Depreciation
    - Dr Cash (if sold) / Dr Loss on Disposal
    - Cr Asset Account
    - Cr Gain on Disposal (if gain)
    """
    temple_id = current_user.temple_id
    
    # Get asset
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.temple_id == temple_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    if asset.status in [AssetStatus.DISPOSED, AssetStatus.SOLD, AssetStatus.SCRAPPED]:
        raise HTTPException(status_code=400, detail="Asset already disposed")
    
    book_value = asset.current_book_value
    accumulated_depreciation = asset.accumulated_depreciation
    original_cost = asset.original_cost
    
    # Calculate gain/loss
    if disposal_data.disposal_type == DisposalType.SALE:
        gain_loss = disposal_data.disposal_proceeds - book_value
    else:
        gain_loss = -book_value  # Loss (no proceeds)
    
    # Get accounts
    asset_account = db.query(Account).filter(Account.id == asset.asset_account_id).first()
    if not asset_account:
        raise HTTPException(status_code=400, detail="Asset account not found")
    
    # Get accumulated depreciation account
    acc_dep_account_code = "1720"  # Default
    if asset.category:
        category_name = asset.category.name.lower()
        if "building" in category_name:
            acc_dep_account_code = "1701"
        elif "vehicle" in category_name:
            acc_dep_account_code = "1702"
        elif "equipment" in category_name or "computer" in category_name:
            acc_dep_account_code = "1703"
        elif "furniture" in category_name:
            acc_dep_account_code = "1710"
    
    acc_dep_account = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == acc_dep_account_code
    ).first()
    
    if not acc_dep_account:
        raise HTTPException(status_code=400, detail="Accumulated depreciation account not found")
    
    # Get gain/loss account
    gain_loss_account = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == "6001"  # Expense account (for loss) or can create gain account
    ).first()
    
    if not gain_loss_account:
        raise HTTPException(status_code=400, detail="Gain/Loss account not found")
    
    # Create disposal record
    disposal = AssetDisposal(
        asset_id=asset_id,
        disposal_date=disposal_data.disposal_date,
        disposal_type=disposal_data.disposal_type,
        disposal_reason=disposal_data.disposal_reason,
        book_value_at_disposal=book_value,
        accumulated_depreciation_at_disposal=accumulated_depreciation,
        disposal_proceeds=disposal_data.disposal_proceeds,
        gain_loss_amount=gain_loss,
        buyer_name=disposal_data.buyer_name,
        disposal_document_number=disposal_data.disposal_document_number,
        created_by=current_user.id
    )
    db.add(disposal)
    db.flush()
    
    # Create journal entry
    year = disposal_data.disposal_date.year
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
    entry_date = datetime.combine(disposal_data.disposal_date, datetime.min.time())
    
    total_amount = max(original_cost, disposal_data.disposal_proceeds + abs(gain_loss))
    
    journal_entry = JournalEntry(
        temple_id=temple_id,
        entry_date=entry_date,
        entry_number=entry_number,
        narration=f"Asset disposal - {asset.name} ({disposal_data.disposal_type.value})",
        reference_type=TransactionType.MANUAL,
        reference_id=disposal.id,
        total_amount=total_amount,
        status=JournalEntryStatus.POSTED,
        created_by=current_user.id,
        posted_by=current_user.id,
        posted_at=datetime.utcnow()
    )
    db.add(journal_entry)
    db.flush()
    
    # Create journal lines
    # Dr Accumulated Depreciation
    if accumulated_depreciation > 0:
        acc_dep_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=acc_dep_account.id,
            debit_amount=accumulated_depreciation,
            credit_amount=0,
            description=f"Remove accumulated depreciation - {asset.name}"
        )
        db.add(acc_dep_line)
    
    # If sold - Dr Cash
    if disposal_data.disposal_type == DisposalType.SALE and disposal_data.disposal_proceeds > 0:
        cash_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == "1101"  # Cash
        ).first()
        
        if cash_account:
            cash_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=cash_account.id,
                debit_amount=disposal_data.disposal_proceeds,
                credit_amount=0,
                description=f"Sale proceeds - {asset.name}"
            )
            db.add(cash_line)
    
    # Dr Loss or Cr Gain
    if gain_loss < 0:  # Loss
        loss_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=gain_loss_account.id,
            debit_amount=abs(gain_loss),
            credit_amount=0,
            description=f"Loss on disposal - {asset.name}"
        )
        db.add(loss_line)
    elif gain_loss > 0:  # Gain
        gain_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=gain_loss_account.id,
            debit_amount=0,
            credit_amount=gain_loss,
            description=f"Gain on disposal - {asset.name}"
        )
        db.add(gain_line)
    
    # Cr Asset Account
    asset_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=asset_account.id,
        debit_amount=0,
        credit_amount=original_cost,
        description=f"Remove asset - {asset.name}"
    )
    db.add(asset_line)
    
    disposal.journal_entry_id = journal_entry.id
    
    # Update asset status
    if disposal_data.disposal_type == DisposalType.SALE:
        asset.status = AssetStatus.SOLD
    elif disposal_data.disposal_type == DisposalType.SCRAP:
        asset.status = AssetStatus.SCRAPPED
    else:
        asset.status = AssetStatus.DISPOSED
    
    asset.current_book_value = 0.0
    asset.accumulated_depreciation = 0.0
    asset.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(disposal)
    return disposal


@router.get("/{asset_id}", response_model=List[DisposalResponse])
def get_disposal_history(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get disposal history for an asset"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.temple_id == current_user.temple_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    disposals = db.query(AssetDisposal).filter(
        AssetDisposal.asset_id == asset_id
    ).order_by(AssetDisposal.disposal_date.desc()).all()
    
    return disposals




