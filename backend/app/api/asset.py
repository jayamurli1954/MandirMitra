"""
Asset Management API
Handles asset procurement, CWIP, depreciation, revaluation, and disposal
Following standard accounting practices and audit compliance
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.asset import (
    Asset, AssetCategory, CapitalWorkInProgress, AssetExpense,
    DepreciationSchedule, AssetRevaluation, AssetDisposal, AssetMaintenance,
    AssetType, AssetStatus, DepreciationMethod, DisposalType, MaintenanceType
)
from app.models.accounting import (
    Account, JournalEntry, JournalLine,
    JournalEntryStatus, TransactionType
)
from app.models.vendor import Vendor
from app.models.depreciation_methods import DepreciationCalculator

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


# ===== PYDANTIC SCHEMAS =====

class AssetCategoryBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    default_depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE
    default_useful_life_years: float = 0.0
    default_depreciation_rate_percent: float = 0.0
    is_depreciable: bool = True

class AssetCategoryCreate(AssetCategoryBase):
    pass

class AssetCategoryResponse(AssetCategoryBase):
    id: int
    temple_id: Optional[int]
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class AssetBase(BaseModel):
    asset_number: str
    name: str
    description: Optional[str] = None
    category_id: int
    asset_type: AssetType
    location: Optional[str] = None
    tag_number: Optional[str] = None
    serial_number: Optional[str] = None
    identification_mark: Optional[str] = None
    purchase_date: date
    original_cost: float
    purchase_invoice_number: Optional[str] = None
    purchase_invoice_date: Optional[date] = None
    vendor_id: Optional[int] = None
    warranty_expiry_date: Optional[date] = None
    # Depreciation
    depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE
    useful_life_years: float = 0.0
    depreciation_rate_percent: float = 0.0
    salvage_value: float = 0.0
    is_depreciable: bool = True
    depreciation_start_date: Optional[date] = None
    # For Units of Production
    total_estimated_units: Optional[float] = None
    # For Annuity
    interest_rate_percent: Optional[float] = None
    # For Sinking Fund
    sinking_fund_interest_rate: Optional[float] = None
    sinking_fund_payments_per_year: int = 1
    # Optional tender
    tender_id: Optional[int] = None

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int
    temple_id: Optional[int]
    current_book_value: float
    accumulated_depreciation: float
    revalued_amount: float
    revaluation_reserve: float
    status: AssetStatus
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class AssetPurchaseRequest(BaseModel):
    """Request for asset purchase/procurement"""
    asset_data: AssetCreate
    payment_method: str = "cash"  # cash, bank, payables
    payment_account_code: Optional[str] = None  # If not cash
    reference_number: Optional[str] = None
    notes: Optional[str] = None


# ===== ASSET CATEGORY ENDPOINTS =====

@router.post("/categories/", response_model=AssetCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_asset_category(
    category_data: AssetCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new asset category"""
    # Check if code already exists
    existing = db.query(AssetCategory).filter(
        AssetCategory.temple_id == current_user.temple_id,
        AssetCategory.code == category_data.code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category code already exists")
    
    category = AssetCategory(
        **category_data.dict(),
        temple_id=current_user.temple_id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories/", response_model=List[AssetCategoryResponse])
def list_asset_categories(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all asset categories"""
    query = db.query(AssetCategory).filter(AssetCategory.temple_id == current_user.temple_id)
    if is_active is not None:
        query = query.filter(AssetCategory.is_active == is_active)
    return query.order_by(AssetCategory.name).all()


# ===== ASSET PROCUREMENT ENDPOINT =====

@router.post("/purchase/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def purchase_asset(
    purchase_request: AssetPurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record asset purchase/procurement
    Creates asset record and accounting entry
    Dr: Asset Account, Cr: Cash/Bank/Payables
    """
    temple_id = current_user.temple_id
    
    # Validate category
    category = db.query(AssetCategory).filter(
        AssetCategory.id == purchase_request.asset_data.category_id,
        AssetCategory.temple_id == temple_id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Asset category not found")
    
    # Check if asset number already exists
    existing = db.query(Asset).filter(
        Asset.temple_id == temple_id,
        Asset.asset_number == purchase_request.asset_data.asset_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Asset number already exists")
    
    # Determine asset account
    asset_account = None
    if category.account_id:
        asset_account = db.query(Account).filter(Account.id == category.account_id).first()
    
    # Fallback to category-based account
    if not asset_account:
        # Map category to account code
        account_code = "1580"  # Default: Other Fixed Assets
        if "land" in category.name.lower():
            account_code = "1501"
        elif "building" in category.name.lower():
            account_code = "1502"
        elif "vehicle" in category.name.lower():
            account_code = "1510"
        elif "furniture" in category.name.lower():
            account_code = "1520"
        elif "computer" in category.name.lower() or "equipment" in category.name.lower():
            account_code = "1530"
        
        asset_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == account_code
        ).first()
    
    if not asset_account:
        raise HTTPException(status_code=400, detail="Asset account not found. Please setup asset accounts first.")
    
    # Create asset
    asset = Asset(
        **purchase_request.asset_data.dict(),
        temple_id=temple_id,
        current_book_value=purchase_request.asset_data.original_cost,
        accumulated_depreciation=0.0,
        status=AssetStatus.ACTIVE,
        asset_account_id=asset_account.id,
        created_by=current_user.id
    )
    db.add(asset)
    db.flush()
    
    # Determine credit account (payment method)
    credit_account = None
    if purchase_request.payment_method.lower() == "cash":
        credit_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == A101"  # Cash in Hand
        ).first()
    elif purchase_request.payment_method.lower() == "bank":
        if purchase_request.payment_account_code:
            credit_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == purchase_request.payment_account_code
            ).first()
        else:
            # Default bank account
            credit_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code.like("111%")  # Bank accounts
            ).first()
    elif purchase_request.payment_method.lower() == "payables":
        credit_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == "2101"  # Vendor Payables
        ).first()
    
    if not credit_account:
        raise HTTPException(status_code=400, detail="Credit account not found for payment method")
    
    # Create journal entry
    year = purchase_request.asset_data.purchase_date.year
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
    entry_date = datetime.combine(purchase_request.asset_data.purchase_date, datetime.min.time())
    
    journal_entry = JournalEntry(
        temple_id=temple_id,
        entry_date=entry_date,
        entry_number=entry_number,
        narration=f"Asset purchase - {purchase_request.asset_data.name}",
        reference_type=TransactionType.MANUAL,  # Can add ASSET_PURCHASE to enum later
        reference_id=asset.id,
        total_amount=purchase_request.asset_data.original_cost,
        status=JournalEntryStatus.POSTED,
        created_by=current_user.id,
        posted_by=current_user.id,
        posted_at=datetime.utcnow()
    )
    db.add(journal_entry)
    db.flush()
    
    # Create journal lines
    debit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=asset_account.id,
        debit_amount=purchase_request.asset_data.original_cost,
        credit_amount=0,
        description=f"Asset purchase - {purchase_request.asset_data.name}"
    )
    
    credit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=credit_account.id,
        debit_amount=0,
        credit_amount=purchase_request.asset_data.original_cost,
        description=f"Payment for {purchase_request.asset_data.name}"
    )
    
    db.add(debit_line)
    db.add(credit_line)
    
    db.commit()
    db.refresh(asset)
    
    return asset


@router.get("/", response_model=List[AssetResponse])
def list_assets(
    category_id: Optional[int] = Query(None),
    asset_type: Optional[AssetType] = Query(None),
    status: Optional[AssetStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all assets"""
    temple_id = current_user.temple_id
    
    # Handle standalone mode where temple_id might be None
    query = db.query(Asset)
    if temple_id is not None:
        query = query.filter(Asset.temple_id == temple_id)
    
    if category_id:
        query = query.filter(Asset.category_id == category_id)
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if status:
        query = query.filter(Asset.status == status)
    
    return query.order_by(Asset.asset_number).all()


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get asset details"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.temple_id == current_user.temple_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an asset"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.temple_id == current_user.temple_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Don't allow changing asset number if it's already set
    if asset_data.asset_number != asset.asset_number:
        existing = db.query(Asset).filter(
            Asset.temple_id == current_user.temple_id,
            Asset.asset_number == asset_data.asset_number,
            Asset.id != asset_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Asset number already exists")
    
    # Update fields
    for key, value in asset_data.dict(exclude_unset=True).items():
        setattr(asset, key, value)
    
    asset.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete (deactivate) an asset - Soft delete by changing status"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.temple_id == current_user.temple_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Soft delete - change status to disposed
    asset.status = AssetStatus.DISPOSED
    asset.updated_at = datetime.utcnow()
    db.commit()
    return None


# ===== TENDER PROCESS INFO ENDPOINT =====

@router.get("/tender-process/info/")
def get_tender_process_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Information about optional tender process feature
    Informs users that tender process is available on-demand
    """
    return {
        "available": True,
        "description": "Tender process is available as an optional feature for transparent procurement. This is especially useful for large temples requiring formal procurement procedures and competitive bidding.",
        "benefits": [
            "Transparent procurement process",
            "Competitive bidding from multiple vendors",
            "Formal documentation for audit compliance",
            "Regulatory compliance for large purchases",
            "Public accountability and trust"
        ],
        "when_to_use": [
            "Large value purchases (as per temple policy)",
            "Regulatory or trust requirements",
            "Need for competitive bidding",
            "Public transparency requirements",
            "Multiple vendor evaluation needed"
        ],
        "status": "designed_ready",
        "implementation": "Can be implemented on-demand when requested",
        "contact": "Contact support to enable tender process feature",
        "note": "Small temples typically don't need this feature. Direct procurement works fine for most cases."
    }

