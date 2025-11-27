"""
Asset Reports API
Provides various asset reports for management and audit
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.asset import (
    Asset, AssetCategory, DepreciationSchedule, AssetRevaluation, AssetDisposal,
    CapitalWorkInProgress, AssetStatus
)
from app.models.accounting import Account

router = APIRouter(prefix="/api/v1/assets/reports", tags=["asset-reports"])


# ===== PYDANTIC SCHEMAS =====

class AssetRegisterItem(BaseModel):
    asset_id: int
    asset_number: str
    name: str
    category: str
    asset_type: str
    location: Optional[str]
    purchase_date: date
    original_cost: float
    current_book_value: float
    accumulated_depreciation: float
    depreciation_method: str
    status: str
    vendor_name: Optional[str] = None

class AssetRegisterResponse(BaseModel):
    total_assets: int
    total_cost: float
    total_book_value: float
    total_depreciation: float
    assets: List[AssetRegisterItem]


class DepreciationReportItem(BaseModel):
    asset_id: int
    asset_number: str
    asset_name: str
    category: str
    depreciation_method: str
    financial_year: str
    period: str
    opening_book_value: float
    depreciation_amount: float
    closing_book_value: float
    status: str

class DepreciationReportResponse(BaseModel):
    financial_year: str
    period: str
    total_depreciation: float
    schedules: List[DepreciationReportItem]


class CWIPReportItem(BaseModel):
    cwip_id: int
    cwip_number: str
    project_name: str
    category: str
    start_date: date
    expected_completion_date: Optional[date]
    total_budget: float
    total_expenditure: float
    status: str
    asset_id: Optional[int] = None

class CWIPReportResponse(BaseModel):
    total_projects: int
    total_budget: float
    total_expenditure: float
    projects: List[CWIPReportItem]


# ===== REPORT ENDPOINTS =====

@router.get("/register/", response_model=AssetRegisterResponse)
def get_asset_register(
    category_id: Optional[int] = Query(None),
    asset_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Asset Register Report
    Complete listing of all assets with financial details
    """
    temple_id = current_user.temple_id
    
    query = db.query(Asset).filter(Asset.temple_id == temple_id)
    
    if category_id:
        query = query.filter(Asset.category_id == category_id)
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if status:
        query = query.filter(Asset.status == status)
    
    assets = query.order_by(Asset.asset_number).all()
    
    items = []
    total_cost = 0.0
    total_book_value = 0.0
    total_depreciation = 0.0
    
    for asset in assets:
        items.append(AssetRegisterItem(
            asset_id=asset.id,
            asset_number=asset.asset_number,
            name=asset.name,
            category=asset.category.name if asset.category else "N/A",
            asset_type=asset.asset_type.value,
            location=asset.location,
            purchase_date=asset.purchase_date,
            original_cost=asset.original_cost,
            current_book_value=asset.current_book_value,
            accumulated_depreciation=asset.accumulated_depreciation,
            depreciation_method=asset.depreciation_method.value if asset.depreciation_method else "N/A",
            status=asset.status.value,
            vendor_name=asset.vendor.name if asset.vendor else None
        ))
        total_cost += asset.original_cost
        total_book_value += asset.current_book_value
        total_depreciation += asset.accumulated_depreciation
    
    return AssetRegisterResponse(
        total_assets=len(items),
        total_cost=total_cost,
        total_book_value=total_book_value,
        total_depreciation=total_depreciation,
        assets=items
    )


@router.get("/depreciation/", response_model=DepreciationReportResponse)
def get_depreciation_report(
    financial_year: str = Query(..., description="Financial year e.g., 2024-25"),
    period: Optional[str] = Query(None, description="monthly or yearly"),
    asset_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Depreciation Report
    Shows depreciation schedules for specified period
    """
    temple_id = current_user.temple_id
    
    query = db.query(DepreciationSchedule).join(Asset).filter(
        Asset.temple_id == temple_id,
        DepreciationSchedule.financial_year == financial_year
    )
    
    if period:
        query = query.filter(DepreciationSchedule.period == period)
    if asset_id:
        query = query.filter(DepreciationSchedule.asset_id == asset_id)
    
    schedules = query.order_by(DepreciationSchedule.period_start_date).all()
    
    items = []
    total_depreciation = 0.0
    
    for schedule in schedules:
        asset = schedule.asset
        items.append(DepreciationReportItem(
            asset_id=asset.id,
            asset_number=asset.asset_number,
            asset_name=asset.name,
            category=asset.category.name if asset.category else "N/A",
            depreciation_method=schedule.depreciation_method_used.value,
            financial_year=schedule.financial_year,
            period=schedule.period,
            opening_book_value=schedule.opening_book_value,
            depreciation_amount=schedule.depreciation_amount,
            closing_book_value=schedule.closing_book_value,
            status=schedule.status
        ))
        total_depreciation += schedule.depreciation_amount
    
    return DepreciationReportResponse(
        financial_year=financial_year,
        period=period or "all",
        total_depreciation=total_depreciation,
        schedules=items
    )


@router.get("/cwip/", response_model=CWIPReportResponse)
def get_cwip_report(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CWIP Report
    Shows all capital work in progress projects
    """
    temple_id = current_user.temple_id
    
    query = db.query(CapitalWorkInProgress).filter(
        CapitalWorkInProgress.temple_id == temple_id
    )
    
    if status:
        query = query.filter(CapitalWorkInProgress.status == status)
    
    cwip_projects = query.order_by(CapitalWorkInProgress.cwip_number).all()
    
    items = []
    total_budget = 0.0
    total_expenditure = 0.0
    
    for cwip in cwip_projects:
        items.append(CWIPReportItem(
            cwip_id=cwip.id,
            cwip_number=cwip.cwip_number,
            project_name=cwip.project_name,
            category=cwip.category.name if cwip.category else "N/A",
            start_date=cwip.start_date,
            expected_completion_date=cwip.expected_completion_date,
            total_budget=cwip.total_budget,
            total_expenditure=cwip.total_expenditure,
            status=cwip.status,
            asset_id=cwip.asset_id
        ))
        total_budget += cwip.total_budget
        total_expenditure += cwip.total_expenditure
    
    return CWIPReportResponse(
        total_projects=len(items),
        total_budget=total_budget,
        total_expenditure=total_expenditure,
        projects=items
    )


@router.get("/summary/")
def get_asset_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Asset Summary Dashboard
    Quick overview of asset statistics
    """
    temple_id = current_user.temple_id
    
    # Total assets
    total_assets = db.query(Asset).filter(Asset.temple_id == temple_id).count()
    
    # Active assets
    active_assets = db.query(Asset).filter(
        Asset.temple_id == temple_id,
        Asset.status == AssetStatus.ACTIVE
    ).count()
    
    # Total cost
    total_cost_result = db.query(func.sum(Asset.original_cost)).filter(
        Asset.temple_id == temple_id
    ).scalar() or 0.0
    
    # Total book value
    total_book_value_result = db.query(func.sum(Asset.current_book_value)).filter(
        Asset.temple_id == temple_id
    ).scalar() or 0.0
    
    # Total depreciation
    total_depreciation_result = db.query(func.sum(Asset.accumulated_depreciation)).filter(
        Asset.temple_id == temple_id
    ).scalar() or 0.0
    
    # Active CWIP projects
    active_cwip = db.query(CapitalWorkInProgress).filter(
        CapitalWorkInProgress.temple_id == temple_id,
        CapitalWorkInProgress.status == "in_progress"
    ).count()
    
    # CWIP expenditure
    cwip_expenditure = db.query(func.sum(CapitalWorkInProgress.total_expenditure)).filter(
        CapitalWorkInProgress.temple_id == temple_id,
        CapitalWorkInProgress.status == "in_progress"
    ).scalar() or 0.0
    
    return {
        "total_assets": total_assets,
        "active_assets": active_assets,
        "total_cost": float(total_cost_result),
        "total_book_value": float(total_book_value_result),
        "total_depreciation": float(total_depreciation_result),
        "active_cwip_projects": active_cwip,
        "cwip_expenditure": float(cwip_expenditure),
        "net_asset_value": float(total_book_value_result)
    }

