"""
Additional Inventory API Endpoints
Stock Adjustment, Transfer, Low Stock Alerts, etc.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.inventory import (
    Store,
    Item,
    StockBalance,
    StockMovement,
    StockMovementType,
    ItemCategory,
    Unit,
)
from app.models.accounting import (
    Account,
    JournalEntry,
    JournalLine,
    JournalEntryStatus,
    TransactionType,
)

# Import from main inventory router
from app.api.inventory import StockMovementCreate, StockMovementResponse

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


@router.post(
    "/movements/adjustment/",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_adjustment(
    movement_data: StockMovementCreate,
    adjustment_reason: str = Query(
        ..., description="Reason for adjustment (shortage, excess, write-off, etc.)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record stock adjustment (shortage, excess, write-off)"""
    # Validate item and store
    item = db.query(Item).filter(Item.id == movement_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    store = db.query(Store).filter(Store.id == movement_data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Get current stock balance
    stock_balance = (
        db.query(StockBalance)
        .filter(
            StockBalance.item_id == movement_data.item_id,
            StockBalance.store_id == movement_data.store_id,
        )
        .first()
    )

    if not stock_balance:
        stock_balance = StockBalance(
            item_id=movement_data.item_id,
            store_id=movement_data.store_id,
            quantity=0.0,
            value=0.0,
            temple_id=current_user.temple_id,
        )
        db.add(stock_balance)
        db.flush()

    # Calculate adjustment value
    unit_price = movement_data.unit_price if movement_data.unit_price > 0 else item.standard_cost
    if unit_price == 0 and stock_balance.quantity > 0:
        unit_price = stock_balance.value / stock_balance.quantity

    total_value = movement_data.quantity * unit_price

    # Generate movement number
    year = movement_data.movement_date.year
    prefix = f"ADJ/{year}/"
    last_movement = (
        db.query(StockMovement)
        .filter(StockMovement.movement_number.like(f"{prefix}%"))
        .order_by(StockMovement.id.desc())
        .first()
    )

    new_num = 1
    if last_movement:
        try:
            last_num = int(last_movement.movement_number.split("/")[-1])
            new_num = last_num + 1
        except:
            pass

    movement_number = f"{prefix}{new_num:04d}"

    # Create movement
    movement = StockMovement(
        movement_type=StockMovementType.ADJUSTMENT,
        movement_number=movement_number,
        movement_date=movement_data.movement_date,
        item_id=movement_data.item_id,
        store_id=movement_data.store_id,
        quantity=movement_data.quantity,
        unit_price=unit_price,
        total_value=total_value,
        notes=f"{adjustment_reason}. {movement_data.notes or ''}",
        temple_id=current_user.temple_id,
        created_by=current_user.id,
    )
    db.add(movement)
    db.flush()

    # Update stock balance (adjustment can be positive or negative)
    stock_balance.quantity += movement_data.quantity
    stock_balance.value += total_value
    stock_balance.last_movement_date = movement_data.movement_date
    stock_balance.last_movement_id = movement.id

    # Create accounting entry for adjustment
    try:
        inventory_account = None
        if item.inventory_account_id:
            inventory_account = (
                db.query(Account).filter(Account.id == item.inventory_account_id).first()
            )
        if not inventory_account and store.inventory_account_id:
            inventory_account = (
                db.query(Account).filter(Account.id == store.inventory_account_id).first()
            )
        if not inventory_account:
            inventory_account = (
                db.query(Account)
                .filter(Account.temple_id == current_user.temple_id, Account.account_code == "1400")
                .first()
            )

        if inventory_account:
            year = movement_data.movement_date.year
            prefix = f"JE/{year}/"
            last_entry = (
                db.query(JournalEntry)
                .filter(
                    JournalEntry.temple_id == current_user.temple_id,
                    JournalEntry.entry_number.like(f"{prefix}%"),
                )
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
            entry_date = datetime.combine(movement_data.movement_date, datetime.min.time())

            journal_entry = JournalEntry(
                temple_id=current_user.temple_id,
                entry_date=entry_date,
                entry_number=entry_number,
                narration=f"Stock adjustment - {item.name} ({adjustment_reason})",
                reference_type=TransactionType.INVENTORY_ADJUSTMENT,
                reference_id=movement.id,
                total_amount=abs(total_value),
                status=JournalEntryStatus.POSTED,
                created_by=current_user.id,
                posted_by=current_user.id,
                posted_at=datetime.utcnow(),
            )
            db.add(journal_entry)
            db.flush()

            if total_value > 0:  # Increase in stock
                db.add(
                    JournalLine(
                        journal_entry_id=journal_entry.id,
                        account_id=inventory_account.id,
                        debit_amount=abs(total_value),
                        credit_amount=0,
                        description=f"Adjustment - {item.name} ({adjustment_reason})",
                    )
                )
            else:  # Decrease in stock
                db.add(
                    JournalLine(
                        journal_entry_id=journal_entry.id,
                        account_id=inventory_account.id,
                        debit_amount=0,
                        credit_amount=abs(total_value),
                        description=f"Adjustment - {item.name} ({adjustment_reason})",
                    )
                )

            movement.journal_entry_id = journal_entry.id
    except Exception as e:
        print(f"Error creating accounting entry for adjustment: {str(e)}")

    db.commit()
    db.refresh(movement)
    return movement


@router.post(
    "/movements/transfer/",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transfer(
    movement_data: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Transfer stock between stores"""
    if not movement_data.to_store_id:
        raise HTTPException(status_code=400, detail="to_store_id is required for transfers")

    # Validate item and stores
    item = db.query(Item).filter(Item.id == movement_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    from_store = db.query(Store).filter(Store.id == movement_data.store_id).first()
    if not from_store:
        raise HTTPException(status_code=404, detail="Source store not found")

    to_store = db.query(Store).filter(Store.id == movement_data.to_store_id).first()
    if not to_store:
        raise HTTPException(status_code=404, detail="Destination store not found")

    # Check stock availability in source store
    from_balance = (
        db.query(StockBalance)
        .filter(
            StockBalance.item_id == movement_data.item_id,
            StockBalance.store_id == movement_data.store_id,
        )
        .first()
    )

    if not from_balance or from_balance.quantity < movement_data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock in source store. Available: {from_balance.quantity if from_balance else 0.0} {item.unit.value}",
        )

    # Calculate transfer value
    unit_price = movement_data.unit_price if movement_data.unit_price > 0 else item.standard_cost
    if unit_price == 0 and from_balance.quantity > 0:
        unit_price = from_balance.value / from_balance.quantity

    total_value = movement_data.quantity * unit_price

    # Generate movement number
    year = movement_data.movement_date.year
    prefix = f"TRF/{year}/"
    last_movement = (
        db.query(StockMovement)
        .filter(StockMovement.movement_number.like(f"{prefix}%"))
        .order_by(StockMovement.id.desc())
        .first()
    )

    new_num = 1
    if last_movement:
        try:
            last_num = int(last_movement.movement_number.split("/")[-1])
            new_num = last_num + 1
        except:
            pass

    movement_number = f"{prefix}{new_num:04d}"

    # Create movement
    movement = StockMovement(
        movement_type=StockMovementType.TRANSFER,
        movement_number=movement_number,
        movement_date=movement_data.movement_date,
        item_id=movement_data.item_id,
        store_id=movement_data.store_id,
        to_store_id=movement_data.to_store_id,
        quantity=movement_data.quantity,
        unit_price=unit_price,
        total_value=total_value,
        notes=movement_data.notes,
        temple_id=current_user.temple_id,
        created_by=current_user.id,
    )
    db.add(movement)
    db.flush()

    # Update source store balance
    from_balance.quantity -= movement_data.quantity
    from_balance.value -= total_value
    from_balance.last_movement_date = movement_data.movement_date
    from_balance.last_movement_id = movement.id

    # Update destination store balance
    to_balance = (
        db.query(StockBalance)
        .filter(
            StockBalance.item_id == movement_data.item_id,
            StockBalance.store_id == movement_data.to_store_id,
        )
        .first()
    )

    if not to_balance:
        to_balance = StockBalance(
            item_id=movement_data.item_id,
            store_id=movement_data.to_store_id,
            quantity=0.0,
            value=0.0,
            temple_id=current_user.temple_id,
        )
        db.add(to_balance)
        db.flush()

    to_balance.quantity += movement_data.quantity
    to_balance.value += total_value
    to_balance.last_movement_date = movement_data.movement_date

    db.commit()
    db.refresh(movement)
    return movement


@router.get("/alerts/low-stock", response_model=List[dict])
def get_low_stock_alerts(
    store_id: Optional[int] = Query(None),
    acknowledged: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get low stock alerts"""
    # Get all items with stock below reorder level
    query = (
        db.query(Item, StockBalance, Store)
        .join(StockBalance, Item.id == StockBalance.item_id)
        .join(Store, StockBalance.store_id == Store.id)
        .filter(
            Item.temple_id == current_user.temple_id,
            Item.is_active == True,
            Item.reorder_level > 0,
            StockBalance.quantity <= Item.reorder_level,
        )
    )

    if store_id:
        query = query.filter(StockBalance.store_id == store_id)

    results = query.all()

    alerts = []
    for item, balance, store in results:
        alerts.append(
            {
                "item_id": item.id,
                "item_code": item.code,
                "item_name": item.name,
                "store_id": store.id,
                "store_code": store.code,
                "store_name": store.name,
                "current_quantity": balance.quantity,
                "reorder_level": item.reorder_level,
                "reorder_quantity": item.reorder_quantity,
                "unit": item.unit.value,
                "shortage": item.reorder_level - balance.quantity,
                "last_movement_date": balance.last_movement_date.isoformat()
                if balance.last_movement_date
                else None,
            }
        )

    return alerts


@router.get("/alerts/expiring-soon", response_model=List[dict])
def get_expiring_soon_alerts(
    days_ahead: int = Query(30, description="Number of days ahead to check"),
    store_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get items expiring soon"""
    expiry_date_limit = date.today() + timedelta(days=days_ahead)

    query = (
        db.query(StockBalance, Item, Store)
        .join(Item, StockBalance.item_id == Item.id)
        .join(Store, StockBalance.store_id == Store.id)
        .filter(
            StockBalance.temple_id == current_user.temple_id,
            StockBalance.earliest_expiry_date.isnot(None),
            StockBalance.earliest_expiry_date <= expiry_date_limit,
            StockBalance.quantity > 0,
        )
    )

    if store_id:
        query = query.filter(StockBalance.store_id == store_id)

    results = query.all()

    alerts = []
    for balance, item, store in results:
        days_until_expiry = (balance.earliest_expiry_date - date.today()).days
        alerts.append(
            {
                "item_id": item.id,
                "item_code": item.code,
                "item_name": item.name,
                "store_id": store.id,
                "store_code": store.code,
                "store_name": store.name,
                "quantity": balance.quantity,
                "expiry_date": balance.earliest_expiry_date.isoformat(),
                "days_until_expiry": days_until_expiry,
                "is_expired": days_until_expiry < 0,
                "unit": item.unit.value,
            }
        )

    return sorted(alerts, key=lambda x: x["days_until_expiry"])
