"""
Inventory Management API
Handles item master, stores, stock movements (purchase, issue, adjustment)
with automatic accounting integration
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
from app.models.inventory import (
    Store, Item, StockBalance, StockMovement,
    StockMovementType, ItemCategory, Unit
)
from app.models.accounting import (
    Account, JournalEntry, JournalLine,
    JournalEntryStatus, TransactionType
)
from app.models.vendor import Vendor

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


# ===== INVENTORY ACCOUNT SETUP ENDPOINT =====

@router.post("/setup-accounts/")
def setup_inventory_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create inventory accounts (1400-1499 series) and link items/stores
    This should be run once after inventory module is set up
    """
    from app.models.accounting import Account, AccountType, AccountSubType
    from app.models.temple import Temple
    
    temple_id = current_user.temple_id
    
    # Get parent account (1000 - Assets)
    parent_account = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == "1000"
    ).first()
    
    if not parent_account:
        raise HTTPException(
            status_code=400,
            detail="Parent account 1000 (Assets) not found. Please run seed_chart_of_accounts.py first."
        )
    
    # Import the setup functions (inline to avoid import issues)
    import sys
    import os
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, backend_dir)
    
    try:
        from scripts.setup_inventory_accounts import (
            create_inventory_accounts,
            link_items_to_accounts,
            link_stores_to_accounts
        )
        
        # Create accounts
        if not create_inventory_accounts(db, temple_id):
            raise HTTPException(status_code=500, detail="Failed to create inventory accounts")
        
        # Link items
        link_items_to_accounts(db, temple_id)
        
        # Link stores
        link_stores_to_accounts(db, temple_id)
        
        return {
            "message": "Inventory accounts created and linked successfully",
            "accounts_created": True,
            "items_linked": True,
            "stores_linked": True,
            "account_codes": {
                "1400": "Inventory Assets (Parent)",
                "1401": "Inventory - Pooja Materials",
                "1402": "Inventory - Grocery & Annadanam",
                "1403": "Inventory - Cleaning Supplies",
                "1404": "Inventory - Maintenance Items",
                "1405": "Inventory - General"
            }
        }
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error setting up accounts: {str(e)}")


# ===== PYDANTIC SCHEMAS =====

class StoreBase(BaseModel):
    code: str
    name: str
    location: Optional[str] = None
    inventory_account_id: Optional[int] = None

class StoreCreate(StoreBase):
    pass

class StoreResponse(StoreBase):
    id: int
    temple_id: Optional[int]
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: ItemCategory
    unit: Unit
    reorder_level: float = 0.0
    reorder_quantity: float = 0.0
    standard_cost: float = 0.0
    hsn_code: Optional[str] = None
    gst_rate: float = 0.0
    inventory_account_id: Optional[int] = None
    expense_account_id: Optional[int] = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    temple_id: Optional[int]
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class StockBalanceResponse(BaseModel):
    id: int
    item_id: int
    item_code: str
    item_name: str
    store_id: int
    store_code: str
    store_name: str
    quantity: float
    value: float
    unit: str
    
    class Config:
        from_attributes = True


class StockMovementBase(BaseModel):
    movement_type: StockMovementType
    movement_date: date
    item_id: int
    store_id: int
    to_store_id: Optional[int] = None  # For transfers
    quantity: float
    unit_price: float = 0.0
    reference_number: Optional[str] = None
    vendor_id: Optional[int] = None  # For purchases
    issued_to: Optional[str] = None  # For issues
    purpose: Optional[str] = None  # For issues
    notes: Optional[str] = None

class StockMovementCreate(StockMovementBase):
    pass

class StockMovementResponse(StockMovementBase):
    id: int
    movement_number: str
    total_value: float
    journal_entry_id: Optional[int]
    created_at: str
    
    class Config:
        from_attributes = True


# ===== ACCOUNTING INTEGRATION =====

def post_inventory_purchase_to_accounting(
    db: Session,
    movement: StockMovement,
    temple_id: int
):
    """
    Create journal entry for inventory purchase
    Dr: Inventory Account (Asset increases)
    Cr: Cash/Bank/Creditors (based on payment)
    """
    try:
        # Get item and store
        item = db.query(Item).filter(Item.id == movement.item_id).first()
        if not item:
            return None
        
        # Determine inventory account
        # Priority: Store inventory account > Item inventory account > Default inventory account
        inventory_account = None
        
        if movement.store_id:
            store = db.query(Store).filter(Store.id == movement.store_id).first()
            if store and store.inventory_account_id:
                inventory_account = db.query(Account).filter(Account.id == store.inventory_account_id).first()
        
        if not inventory_account and item.inventory_account_id:
            inventory_account = db.query(Account).filter(Account.id == item.inventory_account_id).first()
        
        # Fallback to default inventory account (1400 - Inventory Assets)
        if not inventory_account:
            inventory_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == '1400'
            ).first()
        
        if not inventory_account:
            print(f"ERROR: Inventory account not found for purchase. Item: {item.name}")
            return None
        
        # Determine credit account (payment method - assume cash for now, can be enhanced)
        # For now, default to cash
        credit_account_code = '1101'  # Cash in Hand - Counter
        credit_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == credit_account_code
        ).first()
        
        if not credit_account:
            print(f"ERROR: Credit account ({credit_account_code}) not found")
            return None
        
        # Generate entry number
        year = movement.movement_date.year
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
        entry_date = datetime.combine(movement.movement_date, datetime.min.time())
        
        # Create journal entry
        journal_entry = JournalEntry(
            temple_id=temple_id,
            entry_date=entry_date,
            entry_number=entry_number,
            narration=f"Inventory purchase - {item.name}",
            reference_type=TransactionType.INVENTORY_PURCHASE,
            reference_id=movement.id,
            total_amount=movement.total_value,
            status=JournalEntryStatus.POSTED,
            created_by=movement.created_by or 1,
            posted_by=movement.created_by or 1,
            posted_at=datetime.utcnow()
        )
        db.add(journal_entry)
        db.flush()
        
        # Create journal lines
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=inventory_account.id,
            debit_amount=movement.total_value,
            credit_amount=0,
            description=f"Purchase - {item.name} ({movement.quantity} {item.unit.value})"
        )
        
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=credit_account.id,
            debit_amount=0,
            credit_amount=movement.total_value,
            description=f"Payment for {item.name}"
        )
        
        db.add(debit_line)
        db.add(credit_line)
        
        return journal_entry
        
    except Exception as e:
        print(f"Error posting inventory purchase to accounting: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def post_inventory_issue_to_accounting(
    db: Session,
    movement: StockMovement,
    temple_id: int
):
    """
    Create journal entry for inventory issue (consumption)
    Dr: Expense Account (Expense increases)
    Cr: Inventory Account (Asset decreases)
    """
    try:
        # Get item
        item = db.query(Item).filter(Item.id == movement.item_id).first()
        if not item:
            return None
        
        # Determine expense account
        # Priority: Item expense account > Purpose-based account > Default expense
        expense_account = None
        
        if item.expense_account_id:
            expense_account = db.query(Account).filter(Account.id == item.expense_account_id).first()
        
        # If purpose is specified, try to map to expense account
        if not expense_account and movement.purpose:
            purpose_lower = movement.purpose.lower()
            if 'annadanam' in purpose_lower or 'food' in purpose_lower:
                expense_account = db.query(Account).filter(
                    Account.temple_id == temple_id,
                    Account.account_name.ilike('%annadanam%')
                ).first()
            elif 'pooja' in purpose_lower:
                expense_account = db.query(Account).filter(
                    Account.temple_id == temple_id,
                    Account.account_name.ilike('%pooja%')
                ).first()
        
        # Fallback to default operational expense
        if not expense_account:
            expense_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == '5001'  # Default operational expense
            ).first()
        
        if not expense_account:
            print(f"ERROR: Expense account not found for issue. Item: {item.name}")
            return None
        
        # Determine inventory account (same logic as purchase)
        inventory_account = None
        if movement.store_id:
            store = db.query(Store).filter(Store.id == movement.store_id).first()
            if store and store.inventory_account_id:
                inventory_account = db.query(Account).filter(Account.id == store.inventory_account_id).first()
        
        if not inventory_account and item.inventory_account_id:
            inventory_account = db.query(Account).filter(Account.id == item.inventory_account_id).first()
        
        if not inventory_account:
            inventory_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == '1400'
            ).first()
        
        if not inventory_account:
            print(f"ERROR: Inventory account not found for issue")
            return None
        
        # Generate entry number
        year = movement.movement_date.year
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
        entry_date = datetime.combine(movement.movement_date, datetime.min.time())
        
        # Create journal entry
        journal_entry = JournalEntry(
            temple_id=temple_id,
            entry_date=entry_date,
            entry_number=entry_number,
            narration=f"Inventory issue - {item.name} for {movement.purpose or 'temple use'}",
            reference_type=TransactionType.INVENTORY_ISSUE,
            reference_id=movement.id,
            total_amount=movement.total_value,
            status=JournalEntryStatus.POSTED,
            created_by=movement.created_by or 1,
            posted_by=movement.created_by or 1,
            posted_at=datetime.utcnow()
        )
        db.add(journal_entry)
        db.flush()
        
        # Create journal lines
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=expense_account.id,
            debit_amount=movement.total_value,
            credit_amount=0,
            description=f"Issue - {item.name} ({movement.quantity} {item.unit.value})"
        )
        
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=inventory_account.id,
            debit_amount=0,
            credit_amount=movement.total_value,
            description=f"Stock out - {item.name}"
        )
        
        db.add(debit_line)
        db.add(credit_line)
        
        return journal_entry
        
    except Exception as e:
        print(f"Error posting inventory issue to accounting: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# ===== STORE ENDPOINTS =====

@router.post("/stores/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
def create_store(
    store_data: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new store/location"""
    # Check if code already exists
    existing = db.query(Store).filter(
        Store.temple_id == current_user.temple_id,
        Store.code == store_data.code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Store code already exists")
    
    store = Store(
        **store_data.dict(),
        temple_id=current_user.temple_id
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@router.get("/stores/", response_model=List[StoreResponse])
def list_stores(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all stores"""
    query = db.query(Store).filter(Store.temple_id == current_user.temple_id)
    if is_active is not None:
        query = query.filter(Store.is_active == is_active)
    return query.all()


@router.put("/stores/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    store_data: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a store"""
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.temple_id == current_user.temple_id
    ).first()
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    for key, value in store_data.dict(exclude_unset=True).items():
        setattr(store, key, value)
    
    db.commit()
    db.refresh(store)
    return store


# ===== ITEM ENDPOINTS =====

@router.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new inventory item"""
    # Check if code already exists
    existing = db.query(Item).filter(
        Item.temple_id == current_user.temple_id,
        Item.code == item_data.code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item code already exists")
    
    item = Item(
        **item_data.dict(),
        temple_id=current_user.temple_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/items/", response_model=List[ItemResponse])
def list_items(
    category: Optional[ItemCategory] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all items"""
    query = db.query(Item).filter(Item.temple_id == current_user.temple_id)
    if category:
        query = query.filter(Item.category == category)
    if is_active is not None:
        query = query.filter(Item.is_active == is_active)
    return query.order_by(Item.name).all()


@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an item"""
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.temple_id == current_user.temple_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item_data.dict(exclude_unset=True).items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete (deactivate) an item"""
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.temple_id == current_user.temple_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Soft delete - set is_active to False
    item.is_active = False
    db.commit()
    return None


# ===== STOCK BALANCE ENDPOINTS =====

@router.get("/stock-balances/", response_model=List[StockBalanceResponse])
def list_stock_balances(
    store_id: Optional[int] = Query(None),
    item_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current stock balances"""
    query = db.query(StockBalance).join(Item).join(Store).filter(
        StockBalance.temple_id == current_user.temple_id
    )
    
    if store_id:
        query = query.filter(StockBalance.store_id == store_id)
    if item_id:
        query = query.filter(StockBalance.item_id == item_id)
    
    balances = query.all()
    
    # Convert to response format
    result = []
    for balance in balances:
        result.append(StockBalanceResponse(
            id=balance.id,
            item_id=balance.item_id,
            item_code=balance.item.code,
            item_name=balance.item.name,
            store_id=balance.store_id,
            store_code=balance.store.code,
            store_name=balance.store.name,
            quantity=balance.quantity,
            value=balance.value,
            unit=balance.item.unit.value
        ))
    
    return result


# ===== STOCK MOVEMENT ENDPOINTS =====

@router.post("/movements/purchase/", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def create_purchase(
    movement_data: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record inventory purchase"""
    # Validate item and store
    item = db.query(Item).filter(Item.id == movement_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    store = db.query(Store).filter(Store.id == movement_data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Calculate total value
    total_value = movement_data.quantity * movement_data.unit_price
    
    # Generate movement number
    year = movement_data.movement_date.year
    prefix = f"PUR/{year}/"
    last_movement = db.query(StockMovement).filter(
        StockMovement.movement_number.like(f"{prefix}%")
    ).order_by(StockMovement.id.desc()).first()
    
    new_num = 1
    if last_movement:
        try:
            last_num = int(last_movement.movement_number.split('/')[-1])
            new_num = last_num + 1
        except:
            pass
    
    movement_number = f"{prefix}{new_num:04d}"
    
    # Create movement
    movement = StockMovement(
        movement_type=StockMovementType.PURCHASE,
        movement_number=movement_number,
        movement_date=movement_data.movement_date,
        item_id=movement_data.item_id,
        store_id=movement_data.store_id,
        quantity=movement_data.quantity,
        unit_price=movement_data.unit_price,
        total_value=total_value,
        reference_number=movement_data.reference_number,
        vendor_id=movement_data.vendor_id,
        notes=movement_data.notes,
        temple_id=current_user.temple_id,
        created_by=current_user.id
    )
    db.add(movement)
    db.flush()
    
    # Update stock balance
    stock_balance = db.query(StockBalance).filter(
        StockBalance.item_id == movement_data.item_id,
        StockBalance.store_id == movement_data.store_id
    ).first()
    
    if not stock_balance:
        stock_balance = StockBalance(
            item_id=movement_data.item_id,
            store_id=movement_data.store_id,
            quantity=0.0,
            value=0.0,
            temple_id=current_user.temple_id
        )
        db.add(stock_balance)
        db.flush()
    
    # Update balance
    stock_balance.quantity += movement_data.quantity
    stock_balance.value += total_value
    stock_balance.last_movement_date = movement_data.movement_date
    stock_balance.last_movement_id = movement.id
    
    # Post to accounting
    journal_entry = post_inventory_purchase_to_accounting(db, movement, current_user.temple_id)
    if journal_entry:
        movement.journal_entry_id = journal_entry.id
        db.commit()
    else:
        db.commit()  # Still commit movement even if accounting fails
    
    db.refresh(movement)
    return movement


@router.post("/movements/issue/", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def create_issue(
    movement_data: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record inventory issue (consumption)"""
    # Validate item and store
    item = db.query(Item).filter(Item.id == movement_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    store = db.query(Store).filter(Store.id == movement_data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Check stock availability
    stock_balance = db.query(StockBalance).filter(
        StockBalance.item_id == movement_data.item_id,
        StockBalance.store_id == movement_data.store_id
    ).first()
    
    if not stock_balance or stock_balance.quantity < movement_data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {stock_balance.quantity if stock_balance else 0.0} {item.unit.value}"
        )
    
    # Calculate total value (use standard cost or last purchase price)
    unit_price = movement_data.unit_price if movement_data.unit_price > 0 else item.standard_cost
    if unit_price == 0:
        # Use average cost from stock balance
        if stock_balance.quantity > 0:
            unit_price = stock_balance.value / stock_balance.quantity
        else:
            unit_price = 0.0
    
    total_value = movement_data.quantity * unit_price
    
    # Generate movement number
    year = movement_data.movement_date.year
    prefix = f"ISS/{year}/"
    last_movement = db.query(StockMovement).filter(
        StockMovement.movement_number.like(f"{prefix}%")
    ).order_by(StockMovement.id.desc()).first()
    
    new_num = 1
    if last_movement:
        try:
            last_num = int(last_movement.movement_number.split('/')[-1])
            new_num = last_num + 1
        except:
            pass
    
    movement_number = f"{prefix}{new_num:04d}"
    
    # Create movement
    movement = StockMovement(
        movement_type=StockMovementType.ISSUE,
        movement_number=movement_number,
        movement_date=movement_data.movement_date,
        item_id=movement_data.item_id,
        store_id=movement_data.store_id,
        quantity=movement_data.quantity,
        unit_price=unit_price,
        total_value=total_value,
        issued_to=movement_data.issued_to,
        purpose=movement_data.purpose,
        notes=movement_data.notes,
        temple_id=current_user.temple_id,
        created_by=current_user.id
    )
    db.add(movement)
    db.flush()
    
    # Update stock balance
    stock_balance.quantity -= movement_data.quantity
    stock_balance.value -= total_value
    stock_balance.last_movement_date = movement_data.movement_date
    stock_balance.last_movement_id = movement.id
    
    # Post to accounting
    journal_entry = post_inventory_issue_to_accounting(db, movement, current_user.temple_id)
    if journal_entry:
        movement.journal_entry_id = journal_entry.id
        db.commit()
    else:
        db.commit()  # Still commit movement even if accounting fails
    
    db.refresh(movement)
    return movement

