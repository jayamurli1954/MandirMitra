"""
Inventory Alerts and Reports API
Handles low stock alerts, expiry tracking, reorder management, consumption analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.inventory import Item, Store, StockBalance, StockMovement, StockMovementType
from app.models.stock_audit import (
    StockAudit,
    StockAuditItem,
    StockWastage,
    AuditStatus,
    WastageReason,
)

router = APIRouter(prefix="/api/v1/inventory/alerts", tags=["inventory-alerts"])


# ===== SCHEMAS =====


class LowStockAlertResponse(BaseModel):
    item_id: int
    item_code: str
    item_name: str
    store_id: int
    store_name: str
    current_quantity: float
    reorder_level: float
    reorder_quantity: float
    unit: str
    shortage: float
    days_to_stockout: Optional[int] = None

    class Config:
        from_attributes = True


class ExpiryAlertResponse(BaseModel):
    item_id: int
    item_code: str
    item_name: str
    store_id: int
    store_name: str
    quantity: float
    expiry_date: date
    days_until_expiry: int
    batch_number: Optional[str] = None

    class Config:
        from_attributes = True


class ConsumptionAnalysisResponse(BaseModel):
    item_id: int
    item_code: str
    item_name: str
    category: str
    unit: str
    opening_balance: float
    purchases: float
    issues: float
    adjustments: float
    closing_balance: float
    consumption_rate: float  # Issues per day
    avg_daily_consumption: float

    class Config:
        from_attributes = True


# ===== LOW STOCK ALERTS =====


@router.get("/alerts/low-stock", response_model=List[LowStockAlertResponse])
def get_low_stock_alerts(
    store_id: Optional[int] = Query(None),
    include_zero: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get items with low stock (below reorder level)"""
    query = (
        db.query(StockBalance, Item, Store)
        .join(Item, StockBalance.item_id == Item.id)
        .join(Store, StockBalance.store_id == Store.id)
        .filter(
            StockBalance.temple_id == current_user.temple_id,
            Item.is_active == True,
            Store.is_active == True,
            Item.reorder_level > 0,  # Only items with reorder level set
        )
    )

    if store_id:
        query = query.filter(StockBalance.store_id == store_id)

    results = query.all()

    alerts = []
    for balance, item, store in results:
        if balance.quantity <= item.reorder_level or (include_zero and balance.quantity == 0):
            shortage = (
                item.reorder_level - balance.quantity
                if balance.quantity < item.reorder_level
                else 0
            )

            # Calculate days to stockout based on consumption rate
            days_to_stockout = None
            if balance.quantity > 0:
                # Get average daily consumption from last 30 days
                thirty_days_ago = date.today() - timedelta(days=30)
                consumption = (
                    db.query(func.sum(StockMovement.quantity))
                    .filter(
                        StockMovement.item_id == item.id,
                        StockMovement.store_id == store.id,
                        StockMovement.movement_type == StockMovementType.ISSUE,
                        StockMovement.movement_date >= thirty_days_ago,
                    )
                    .scalar()
                    or 0.0
                )

                avg_daily = consumption / 30.0 if consumption > 0 else 0
                if avg_daily > 0:
                    days_to_stockout = int(balance.quantity / avg_daily)

            alerts.append(
                LowStockAlertResponse(
                    item_id=item.id,
                    item_code=item.code,
                    item_name=item.name,
                    store_id=store.id,
                    store_name=store.name,
                    current_quantity=balance.quantity,
                    reorder_level=item.reorder_level,
                    reorder_quantity=item.reorder_quantity,
                    unit=item.unit.value,
                    shortage=shortage,
                    days_to_stockout=days_to_stockout,
                )
            )

    # Sort by shortage (highest first)
    alerts.sort(key=lambda x: x.shortage, reverse=True)
    return alerts


@router.get("/alerts/expiring", response_model=List[ExpiryAlertResponse])
def get_expiring_items(
    days_ahead: int = Query(30, ge=1, le=365),
    store_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get items expiring within specified days"""
    today = date.today()
    expiry_threshold = today + timedelta(days=days_ahead)

    query = (
        db.query(StockBalance, Item, Store)
        .join(Item, StockBalance.item_id == Item.id)
        .join(Store, StockBalance.store_id == Store.id)
        .filter(
            StockBalance.temple_id == current_user.temple_id,
            Item.is_active == True,
            Item.has_expiry == True,
            Store.is_active == True,
            StockBalance.earliest_expiry_date.isnot(None),
            StockBalance.earliest_expiry_date <= expiry_threshold,
            StockBalance.quantity > 0,
        )
    )

    if store_id:
        query = query.filter(StockBalance.store_id == store_id)

    results = query.all()

    alerts = []
    for balance, item, store in results:
        if balance.earliest_expiry_date:
            days_until = (balance.earliest_expiry_date - today).days

            alerts.append(
                ExpiryAlertResponse(
                    item_id=item.id,
                    item_code=item.code,
                    item_name=item.name,
                    store_id=store.id,
                    store_name=store.name,
                    quantity=balance.quantity,
                    expiry_date=balance.earliest_expiry_date,
                    days_until_expiry=days_until,
                    batch_number=None,  # Can be enhanced to get from batch_numbers JSON
                )
            )

    # Sort by expiry date (earliest first)
    alerts.sort(key=lambda x: x.expiry_date)
    return alerts


@router.get("/reorder-suggestions", response_model=List[dict])
def get_reorder_suggestions(
    store_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get reorder suggestions based on low stock alerts"""
    low_stock_items = get_low_stock_alerts(store_id=store_id, db=db, current_user=current_user)

    suggestions = []
    for alert in low_stock_items:
        # Suggest reorder quantity (reorder_quantity or shortage + buffer)
        suggested_qty = (
            alert.reorder_quantity if alert.reorder_quantity > 0 else alert.shortage * 1.5
        )

        suggestions.append(
            {
                "item_id": alert.item_id,
                "item_code": alert.item_code,
                "item_name": alert.item_name,
                "store_id": alert.store_id,
                "store_name": alert.store_name,
                "current_quantity": alert.current_quantity,
                "reorder_level": alert.reorder_level,
                "suggested_quantity": round(suggested_qty, 2),
                "unit": alert.unit,
                "urgency": "critical"
                if alert.current_quantity == 0
                else "high"
                if alert.days_to_stockout and alert.days_to_stockout < 7
                else "medium",
            }
        )

    return suggestions


# ===== CONSUMPTION ANALYSIS =====


@router.get("/consumption-analysis", response_model=List[ConsumptionAnalysisResponse])
def get_consumption_analysis(
    from_date: date = Query(...),
    to_date: date = Query(...),
    item_id: Optional[int] = Query(None),
    store_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get consumption analysis for items"""
    # Get items
    item_query = db.query(Item).filter(
        Item.temple_id == current_user.temple_id, Item.is_active == True
    )

    if item_id:
        item_query = item_query.filter(Item.id == item_id)
    if category:
        item_query = item_query.filter(Item.category == category)

    items = item_query.all()

    analysis = []
    days = (to_date - from_date).days + 1

    for item in items:
        # Get opening balance (balance at start of period)
        opening_balance_query = db.query(StockBalance).filter(
            StockBalance.item_id == item.id, StockBalance.temple_id == current_user.temple_id
        )
        if store_id:
            opening_balance_query = opening_balance_query.filter(StockBalance.store_id == store_id)

        opening_balances = opening_balance_query.all()
        opening_qty = sum(b.quantity for b in opening_balances)

        # Get purchases
        purchase_query = db.query(func.sum(StockMovement.quantity)).filter(
            StockMovement.item_id == item.id,
            StockMovement.movement_type == StockMovementType.PURCHASE,
            StockMovement.movement_date >= from_date,
            StockMovement.movement_date <= to_date,
        )
        if store_id:
            purchase_query = purchase_query.filter(StockMovement.store_id == store_id)
        if current_user.temple_id:
            purchase_query = purchase_query.filter(
                StockMovement.temple_id == current_user.temple_id
            )

        purchases = purchase_query.scalar() or 0.0

        # Get issues
        issue_query = db.query(func.sum(StockMovement.quantity)).filter(
            StockMovement.item_id == item.id,
            StockMovement.movement_type == StockMovementType.ISSUE,
            StockMovement.movement_date >= from_date,
            StockMovement.movement_date <= to_date,
        )
        if store_id:
            issue_query = issue_query.filter(StockMovement.store_id == store_id)
        if current_user.temple_id:
            issue_query = issue_query.filter(StockMovement.temple_id == current_user.temple_id)

        issues = issue_query.scalar() or 0.0

        # Get adjustments
        adjustment_query = db.query(func.sum(StockMovement.quantity)).filter(
            StockMovement.item_id == item.id,
            StockMovement.movement_type == StockMovementType.ADJUSTMENT,
            StockMovement.movement_date >= from_date,
            StockMovement.movement_date <= to_date,
        )
        if store_id:
            adjustment_query = adjustment_query.filter(StockMovement.store_id == store_id)
        if current_user.temple_id:
            adjustment_query = adjustment_query.filter(
                StockMovement.temple_id == current_user.temple_id
            )

        adjustments = adjustment_query.scalar() or 0.0

        # Calculate closing balance
        closing_balance = opening_qty + purchases - issues + adjustments

        # Calculate consumption rate
        consumption_rate = issues / days if days > 0 else 0.0
        avg_daily_consumption = consumption_rate

        analysis.append(
            ConsumptionAnalysisResponse(
                item_id=item.id,
                item_code=item.code,
                item_name=item.name,
                category=item.category.value,
                unit=item.unit.value,
                opening_balance=opening_qty,
                purchases=purchases,
                issues=issues,
                adjustments=adjustments,
                closing_balance=closing_balance,
                consumption_rate=consumption_rate,
                avg_daily_consumption=avg_daily_consumption,
            )
        )

    # Sort by consumption rate (highest first)
    analysis.sort(key=lambda x: x.consumption_rate, reverse=True)
    return analysis
