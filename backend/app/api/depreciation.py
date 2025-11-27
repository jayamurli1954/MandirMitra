"""
Depreciation API
Handles depreciation calculation and posting for assets
Supports all 8 depreciation methods
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.asset import (
    Asset, DepreciationSchedule, AssetCategory
)
from app.models.accounting import (
    Account, JournalEntry, JournalLine,
    JournalEntryStatus, TransactionType
)
from app.models.depreciation_methods import DepreciationCalculator, DepreciationMethod

router = APIRouter(prefix="/api/v1/assets/depreciation", tags=["depreciation"])


# ===== PYDANTIC SCHEMAS =====

class DepreciationScheduleResponse(BaseModel):
    id: int
    asset_id: int
    financial_year: str
    period: str
    period_start_date: date
    period_end_date: date
    depreciation_method_used: str
    opening_book_value: float
    depreciation_amount: float
    closing_book_value: float
    depreciation_rate: Optional[float]
    units_produced_this_period: Optional[float]
    total_units_produced_to_date: Optional[float]
    interest_component: Optional[float]
    principal_component: Optional[float]
    journal_entry_id: Optional[int]
    posted_date: Optional[date]
    status: str
    created_at: str
    
    class Config:
        from_attributes = True


class CalculateDepreciationRequest(BaseModel):
    """Request to calculate depreciation"""
    asset_id: int
    financial_year: str  # e.g., "2024-25"
    period: str = "yearly"  # monthly, yearly
    period_start_date: date
    period_end_date: date
    # For Units of Production
    units_produced_this_period: Optional[float] = None
    # For Annuity/Sinking Fund
    interest_rate_override: Optional[float] = None


class PostDepreciationRequest(BaseModel):
    """Request to post depreciation to accounting"""
    schedule_id: int
    post_date: date


# ===== DEPRECIATION ENDPOINTS =====

@router.post("/calculate/", response_model=DepreciationScheduleResponse, status_code=status.HTTP_201_CREATED)
def calculate_depreciation(
    request: CalculateDepreciationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate depreciation for an asset
    Uses the asset's configured depreciation method
    """
    temple_id = current_user.temple_id
    
    # Get asset
    asset = db.query(Asset).filter(
        Asset.id == request.asset_id,
        Asset.temple_id == temple_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    if not asset.is_depreciable:
        raise HTTPException(status_code=400, detail="Asset is not depreciable")
    
    if asset.status != AssetStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Can only calculate depreciation for active assets")
    
    # Check if schedule already exists for this period
    existing = db.query(DepreciationSchedule).filter(
        DepreciationSchedule.asset_id == request.asset_id,
        DepreciationSchedule.financial_year == request.financial_year,
        DepreciationSchedule.period == request.period,
        DepreciationSchedule.period_start_date == request.period_start_date
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Depreciation already calculated for this period")
    
    # Get opening book value (from last schedule or asset's current book value)
    last_schedule = db.query(DepreciationSchedule).filter(
        DepreciationSchedule.asset_id == request.asset_id,
        DepreciationSchedule.status == "posted"
    ).order_by(DepreciationSchedule.period_end_date.desc()).first()
    
    opening_book_value = asset.current_book_value
    if last_schedule:
        opening_book_value = last_schedule.closing_book_value
    
    # Calculate period in years
    period_days = (request.period_end_date - request.period_start_date).days
    period_years = period_days / 365.25
    
    # Calculate depreciation based on method
    depreciation_amount = 0.0
    depreciation_rate = None
    units_produced = None
    total_units = None
    interest_component = None
    principal_component = None
    
    try:
        if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            depreciation_amount = DepreciationCalculator.calculate_straight_line(
                cost=asset.original_cost,
                salvage_value=asset.salvage_value,
                useful_life_years=asset.useful_life_years,
                period_years=period_years
            )
            depreciation_rate = (depreciation_amount / asset.original_cost * 100) if asset.original_cost > 0 else 0
        
        elif asset.depreciation_method == DepreciationMethod.WDV:
            depreciation_amount = DepreciationCalculator.calculate_wdv(
                opening_book_value=opening_book_value,
                depreciation_rate_percent=asset.depreciation_rate_percent,
                period_years=period_years
            )
            depreciation_rate = asset.depreciation_rate_percent
        
        elif asset.depreciation_method == DepreciationMethod.DOUBLE_DECLINING:
            depreciation_amount = DepreciationCalculator.calculate_double_declining(
                opening_book_value=opening_book_value,
                useful_life_years=asset.useful_life_years,
                period_years=period_years
            )
            depreciation_rate = (200.0 / asset.useful_life_years) if asset.useful_life_years > 0 else 0
        
        elif asset.depreciation_method == DepreciationMethod.DECLINING_BALANCE:
            depreciation_amount = DepreciationCalculator.calculate_declining_balance(
                opening_book_value=opening_book_value,
                depreciation_rate_percent=asset.depreciation_rate_percent,
                period_years=period_years
            )
            depreciation_rate = asset.depreciation_rate_percent
        
        elif asset.depreciation_method == DepreciationMethod.UNITS_OF_PRODUCTION:
            if request.units_produced_this_period is None:
                raise HTTPException(status_code=400, detail="Units of production method requires units_produced_this_period")
            if asset.total_estimated_units is None:
                raise HTTPException(status_code=400, detail="Asset missing total_estimated_units")
            
            depreciation_amount = DepreciationCalculator.calculate_units_of_production(
                cost=asset.original_cost,
                salvage_value=asset.salvage_value,
                total_estimated_units=asset.total_estimated_units,
                units_produced_this_period=request.units_produced_this_period
            )
            units_produced = request.units_produced_this_period
            total_units = (asset.units_used_to_date or 0.0) + request.units_produced_this_period
        
        elif asset.depreciation_method == DepreciationMethod.ANNUITY:
            interest_rate = request.interest_rate_override or asset.interest_rate_percent
            if interest_rate is None:
                raise HTTPException(status_code=400, detail="Annuity method requires interest_rate_percent")
            
            depreciation_amount = DepreciationCalculator.calculate_annuity(
                cost=asset.original_cost,
                salvage_value=asset.salvage_value,
                useful_life_years=asset.useful_life_years,
                interest_rate_percent=interest_rate,
                opening_book_value=opening_book_value,
                period_years=period_years
            )
            # For annuity, interest component = opening_book_value * interest_rate
            interest_component = opening_book_value * (interest_rate / 100.0) * period_years
            principal_component = depreciation_amount - interest_component
        
        elif asset.depreciation_method == DepreciationMethod.DEPLETION:
            if request.units_produced_this_period is None:
                raise HTTPException(status_code=400, detail="Depletion method requires units_produced_this_period")
            if asset.total_estimated_units is None:
                raise HTTPException(status_code=400, detail="Asset missing total_estimated_units")
            
            depreciation_amount = DepreciationCalculator.calculate_depletion(
                cost=asset.original_cost,
                salvage_value=asset.salvage_value,
                total_units_of_resource=asset.total_estimated_units,
                units_extracted_this_period=request.units_produced_this_period
            )
            units_produced = request.units_produced_this_period
            total_units = (asset.units_used_to_date or 0.0) + request.units_produced_this_period
        
        elif asset.depreciation_method == DepreciationMethod.SINKING_FUND:
            interest_rate = request.interest_rate_override or asset.sinking_fund_interest_rate
            if interest_rate is None:
                raise HTTPException(status_code=400, detail="Sinking fund method requires sinking_fund_interest_rate")
            
            # Sinking fund calculates annual contribution
            annual_contribution = DepreciationCalculator.calculate_sinking_fund(
                cost=asset.original_cost,
                salvage_value=asset.salvage_value,
                useful_life_years=asset.useful_life_years,
                interest_rate_percent=interest_rate,
                payments_per_year=asset.sinking_fund_payments_per_year
            )
            depreciation_amount = annual_contribution * period_years
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown depreciation method: {asset.depreciation_method}")
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Ensure depreciation doesn't exceed remaining book value (for WDV/Double Declining)
    if asset.depreciation_method in [DepreciationMethod.WDV, DepreciationMethod.DOUBLE_DECLINING, DepreciationMethod.DECLINING_BALANCE]:
        max_depreciation = opening_book_value - asset.salvage_value
        depreciation_amount = min(depreciation_amount, max_depreciation)
    
    closing_book_value = opening_book_value - depreciation_amount
    
    # Ensure closing book value doesn't go below salvage value
    if closing_book_value < asset.salvage_value:
        depreciation_amount = opening_book_value - asset.salvage_value
        closing_book_value = asset.salvage_value
    
    # Create depreciation schedule
    schedule = DepreciationSchedule(
        asset_id=request.asset_id,
        financial_year=request.financial_year,
        period=request.period,
        period_start_date=request.period_start_date,
        period_end_date=request.period_end_date,
        depreciation_method_used=asset.depreciation_method,
        opening_book_value=opening_book_value,
        depreciation_amount=depreciation_amount,
        closing_book_value=closing_book_value,
        depreciation_rate=depreciation_rate,
        units_produced_this_period=units_produced,
        total_units_produced_to_date=total_units,
        interest_component=interest_component,
        principal_component=principal_component,
        status="calculated",
        created_by=current_user.id
    )
    db.add(schedule)
    db.flush()
    
    # Update asset units if applicable
    if units_produced is not None and total_units is not None:
        asset.units_used_to_date = total_units
    
    db.commit()
    db.refresh(schedule)
    return schedule


@router.post("/post/", response_model=DepreciationScheduleResponse)
def post_depreciation(
    request: PostDepreciationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Post depreciation to accounting
    Creates journal entry: Dr Depreciation Expense, Cr Accumulated Depreciation
    """
    temple_id = current_user.temple_id
    
    # Get schedule
    schedule = db.query(DepreciationSchedule).filter(
        DepreciationSchedule.id == request.schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Depreciation schedule not found")
    
    if schedule.status == "posted":
        raise HTTPException(status_code=400, detail="Depreciation already posted")
    
    # Get asset
    asset = db.query(Asset).filter(
        Asset.id == schedule.asset_id,
        Asset.temple_id == temple_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Get depreciation expense account
    expense_account = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == "6001"  # Depreciation Expense
    ).first()
    
    if not expense_account:
        raise HTTPException(status_code=400, detail="Depreciation expense account (6001) not found")
    
    # Get accumulated depreciation account
    # Map based on asset category
    acc_dep_account_code = "1720"  # Default: Accumulated Depreciation - Other
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
    
    # Create journal entry
    year = request.post_date.year
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
    entry_date = datetime.combine(request.post_date, datetime.min.time())
    
    journal_entry = JournalEntry(
        temple_id=temple_id,
        entry_date=entry_date,
        entry_number=entry_number,
        narration=f"Depreciation - {asset.name} ({schedule.financial_year}, {schedule.period})",
        reference_type=TransactionType.MANUAL,
        reference_id=schedule.id,
        total_amount=schedule.depreciation_amount,
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
        account_id=expense_account.id,
        debit_amount=schedule.depreciation_amount,
        credit_amount=0,
        description=f"Depreciation - {asset.name}"
    )
    
    credit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=acc_dep_account.id,
        debit_amount=0,
        credit_amount=schedule.depreciation_amount,
        description=f"Accumulated depreciation - {asset.name}"
    )
    
    db.add(debit_line)
    db.add(credit_line)
    
    # Update schedule
    schedule.journal_entry_id = journal_entry.id
    schedule.posted_date = request.post_date
    schedule.status = "posted"
    schedule.updated_at = datetime.utcnow()
    
    # Update asset
    asset.accumulated_depreciation += schedule.depreciation_amount
    asset.current_book_value = schedule.closing_book_value
    asset.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/schedule/{asset_id}", response_model=List[DepreciationScheduleResponse])
def get_depreciation_schedule(
    asset_id: int,
    financial_year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get depreciation schedule for an asset"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.temple_id == current_user.temple_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    query = db.query(DepreciationSchedule).filter(
        DepreciationSchedule.asset_id == asset_id
    )
    
    if financial_year:
        query = query.filter(DepreciationSchedule.financial_year == financial_year)
    
    return query.order_by(DepreciationSchedule.period_start_date).all()


@router.post("/calculate-batch/")
def calculate_depreciation_batch(
    financial_year: str,
    period: str = "yearly",
    period_start_date: date = None,
    period_end_date: date = None,
    asset_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate depreciation for multiple assets at once
    Useful for monthly/yearly depreciation runs
    """
    temple_id = current_user.temple_id
    
    if not period_start_date or not period_end_date:
        # Default to current period
        today = date.today()
        if period == "yearly":
            period_start_date = date(today.year, 4, 1)  # Financial year start (April)
            period_end_date = date(today.year + 1, 3, 31)  # Financial year end (March)
        else:  # monthly
            period_start_date = date(today.year, today.month, 1)
            # Last day of month
            if today.month == 12:
                period_end_date = date(today.year + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                period_end_date = date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
    
    # Get assets
    query = db.query(Asset).filter(
        Asset.temple_id == temple_id,
        Asset.is_depreciable == True,
        Asset.status == AssetStatus.ACTIVE
    )
    
    if asset_ids:
        query = query.filter(Asset.id.in_(asset_ids))
    
    assets = query.all()
    
    results = []
    errors = []
    
    for asset in assets:
        try:
            request = CalculateDepreciationRequest(
                asset_id=asset.id,
                financial_year=financial_year,
                period=period,
                period_start_date=period_start_date,
                period_end_date=period_end_date
            )
            schedule = calculate_depreciation(request, db, current_user)
            results.append({
                "asset_id": asset.id,
                "asset_name": asset.name,
                "status": "success",
                "schedule_id": schedule.id,
                "depreciation_amount": schedule.depreciation_amount
            })
        except Exception as e:
            errors.append({
                "asset_id": asset.id,
                "asset_name": asset.name,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "financial_year": financial_year,
        "period": period,
        "period_start_date": period_start_date,
        "period_end_date": period_end_date,
        "total_assets": len(assets),
        "successful": len(results),
        "errors": len(errors),
        "results": results,
        "error_details": errors
    }

