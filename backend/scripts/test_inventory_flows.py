"""
Test Inventory Flows
Creates sample items, stores, and tests purchase/issue transactions with accounting
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal

# Import all models to ensure relationships are properly configured
# This must be done before querying (same as main.py)
from app.models.temple import Temple
from app.models.user import User
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine
from app.models.bank_reconciliation import BankStatement, BankStatementEntry, BankReconciliation, ReconciliationOutstandingItem
from app.models.financial_period import FinancialYear, FinancialPeriod, PeriodClosing
from app.models.vendor import Vendor
from app.models.token_seva import TokenInventory, TokenSale, TokenReconciliation
from app.models.inkind_sponsorship import (
    InKindDonation, InKindConsumption,
    Sponsorship, SponsorshipPayment
)
from app.models.upi_banking import (
    UpiPayment, BankAccount, BankTransaction
)
from app.models.inventory import (
    Store, Item, StockBalance, StockMovement,
    ItemCategory, Unit, StockMovementType
)
from datetime import date

def create_sample_stores(db: Session, temple_id: int):
    """Create sample stores"""
    stores_data = [
        {"code": "ST001", "name": "Main Store", "location": "Ground Floor"},
        {"code": "ST002", "name": "Kitchen Store", "location": "Kitchen Area"},
        {"code": "ST003", "name": "Pooja Room Store", "location": "Pooja Room"}
    ]
    
    created_stores = []
    for store_data in stores_data:
        existing = db.query(Store).filter(
            Store.temple_id == temple_id,
            Store.code == store_data["code"]
        ).first()
        
        if not existing:
            store = Store(
                **store_data,
                temple_id=temple_id
            )
            db.add(store)
            created_stores.append(store)
            print(f"✅ Created store: {store.code} - {store.name}")
        else:
            created_stores.append(existing)
            print(f"ℹ️  Store already exists: {existing.code} - {existing.name}")
    
    db.commit()
    return created_stores


def create_sample_items(db: Session, temple_id: int):
    """Create sample inventory items"""
    items_data = [
        {
            "code": "ITM001",
            "name": "Camphor",
            "category": ItemCategory.POOJA_MATERIAL,
            "unit": Unit.KG,
            "reorder_level": 5.0,
            "standard_cost": 500.0
        },
        {
            "code": "ITM002",
            "name": "Kumkum",
            "category": ItemCategory.POOJA_MATERIAL,
            "unit": Unit.KG,
            "reorder_level": 2.0,
            "standard_cost": 800.0
        },
        {
            "code": "ITM003",
            "name": "Rice",
            "category": ItemCategory.GROCERY,
            "unit": Unit.KG,
            "reorder_level": 50.0,
            "standard_cost": 50.0
        },
        {
            "code": "ITM004",
            "name": "Toor Dal",
            "category": ItemCategory.GROCERY,
            "unit": Unit.KG,
            "reorder_level": 20.0,
            "standard_cost": 120.0
        },
        {
            "code": "ITM005",
            "name": "Cooking Oil",
            "category": ItemCategory.GROCERY,
            "unit": Unit.LITRE,
            "reorder_level": 10.0,
            "standard_cost": 150.0
        },
        {
            "code": "ITM006",
            "name": "Detergent",
            "category": ItemCategory.CLEANING,
            "unit": Unit.KG,
            "reorder_level": 5.0,
            "standard_cost": 100.0
        }
    ]
    
    created_items = []
    for item_data in items_data:
        existing = db.query(Item).filter(
            Item.temple_id == temple_id,
            Item.code == item_data["code"]
        ).first()
        
        if not existing:
            item = Item(
                **item_data,
                temple_id=temple_id
            )
            db.add(item)
            created_items.append(item)
            print(f"✅ Created item: {item.code} - {item.name} ({item.category.value})")
        else:
            created_items.append(existing)
            print(f"ℹ️  Item already exists: {existing.code} - {existing.name}")
    
    db.commit()
    
    # Link items to accounts (if setup_inventory_accounts was run)
    from scripts.setup_inventory_accounts import link_items_to_accounts
    link_items_to_accounts(db, temple_id)
    
    return created_items


def post_inventory_purchase_to_accounting(db: Session, movement: StockMovement, temple_id: int):
    """Create journal entry for inventory purchase (copied from inventory.py)"""
    from app.models.accounting import Account, JournalEntry, JournalLine, TransactionType, JournalEntryStatus
    from datetime import datetime
    
    try:
        # Get item and store
        item = db.query(Item).filter(Item.id == movement.item_id).first()
        if not item:
            return None
        
        # Determine inventory account
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
            print(f"ERROR: Inventory account not found for purchase. Item: {item.name}")
            return None
        
        # Default to cash
        credit_account_code = '1101'
        credit_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == credit_account_code
        ).first()
        
        if not credit_account:
            print(f"ERROR: Credit account ({credit_account_code}) not found")
            return None
        
        # Generate entry number
        year = datetime.now().year
        prefix = f"JNL/{year}/"
        last_entry = db.query(JournalEntry).filter(
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
        
        # Create journal entry
        from datetime import datetime
        entry_date = datetime.combine(movement.movement_date, datetime.min.time())
        
        journal_entry = JournalEntry(
            entry_number=entry_number,
            entry_date=entry_date,
            narration=f"Inventory Purchase: {item.name} - {movement.movement_number}",
            total_amount=movement.total_value,
            reference_type="inventory_purchase",  # Use string value directly
            reference_id=movement.id,
            status="posted",  # Use string value directly
            temple_id=temple_id,
            created_by=1,
            posted_by=1,
            posted_at=datetime.utcnow()
        )
        db.add(journal_entry)
        db.flush()
        
        # Create journal lines
        # Dr: Inventory
        db.add(JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=inventory_account.id,
            debit_amount=movement.total_value,
            credit_amount=0.0,
            narration=f"Purchase: {item.name}"
        ))
        
        # Cr: Cash
        db.add(JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=credit_account.id,
            debit_amount=0.0,
            credit_amount=movement.total_value,
            narration=f"Payment for: {item.name}"
        ))
        
        db.commit()
        return journal_entry
    except Exception as e:
        print(f"ERROR creating journal entry: {e}")
        db.rollback()
        return None


def test_purchase(db: Session, temple_id: int, item: Item, store: Store, quantity: float, unit_price: float):
    """Test purchase transaction"""
    
    print(f"\n📦 Testing Purchase:")
    print(f"   Item: {item.name}")
    print(f"   Store: {store.name}")
    print(f"   Quantity: {quantity} {item.unit.value}")
    print(f"   Unit Price: ₹{unit_price}")
    
    # Generate movement number
    year = date.today().year
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
    total_value = quantity * unit_price
    
    # Create movement
    movement = StockMovement(
        movement_type=StockMovementType.PURCHASE,
        movement_number=movement_number,
        movement_date=date.today(),
        item_id=item.id,
        store_id=store.id,
        quantity=quantity,
        unit_price=unit_price,
        total_value=total_value,
        reference_number=f"BILL-{movement_number}",
        temple_id=temple_id,
        created_by=1  # System user
    )
    db.add(movement)
    db.flush()
    
    # Update stock balance
    stock_balance = db.query(StockBalance).filter(
        StockBalance.item_id == item.id,
        StockBalance.store_id == store.id
    ).first()
    
    if not stock_balance:
        stock_balance = StockBalance(
            item_id=item.id,
            store_id=store.id,
            quantity=0.0,
            value=0.0,
            temple_id=temple_id
        )
        db.add(stock_balance)
        db.flush()
    
    stock_balance.quantity += quantity
    stock_balance.value += total_value
    stock_balance.last_movement_date = date.today()
    stock_balance.last_movement_id = movement.id
    
    # Post to accounting
    journal_entry = post_inventory_purchase_to_accounting(db, movement, temple_id)
    if journal_entry:
        movement.journal_entry_id = journal_entry.id
        print(f"   ✅ Accounting entry created: {journal_entry.entry_number}")
        print(f"      Dr: Inventory Account")
        print(f"      Cr: Cash Account")
    else:
        print(f"   ⚠️  Accounting entry not created (check accounts)")
    
    db.commit()
    print(f"   ✅ Purchase recorded: {movement_number}")
    return movement


def post_inventory_issue_to_accounting(db: Session, movement: StockMovement, temple_id: int):
    """Create journal entry for inventory issue (copied from inventory.py)"""
    from app.models.accounting import Account, JournalEntry, JournalLine, TransactionType, JournalEntryStatus
    from datetime import datetime
    
    try:
        # Get item
        item = db.query(Item).filter(Item.id == movement.item_id).first()
        if not item:
            return None
        
        # Determine inventory account
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
        
        # Determine expense account based on item category
        expense_account_code = '5005'  # Default: General Operational Expense
        if item.category == ItemCategory.POOJA_MATERIAL:
            expense_account_code = '5001'  # Pooja Expense
        elif item.category == ItemCategory.GROCERY:
            expense_account_code = '5002'  # Annadanam Expense
        elif item.category == ItemCategory.CLEANING:
            expense_account_code = '5003'  # Cleaning & Maintenance Expense
        elif item.category == ItemCategory.MAINTENANCE:
            expense_account_code = '5004'  # Maintenance Expense
        
        expense_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == expense_account_code
        ).first()
        
        if not expense_account:
            print(f"ERROR: Expense account ({expense_account_code}) not found")
            return None
        
        # Generate entry number
        year = datetime.now().year
        prefix = f"JNL/{year}/"
        last_entry = db.query(JournalEntry).filter(
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
        
        # Create journal entry
        from datetime import datetime
        entry_date = datetime.combine(movement.movement_date, datetime.min.time())
        
        journal_entry = JournalEntry(
            entry_number=entry_number,
            entry_date=entry_date,
            narration=f"Inventory Issue: {item.name} - {movement.movement_number} ({movement.purpose})",
            total_amount=movement.total_value,
            reference_type="inventory_issue",  # Use string value directly
            reference_id=movement.id,
            status="posted",  # Use string value directly
            temple_id=temple_id,
            created_by=1,
            posted_by=1,
            posted_at=datetime.utcnow()
        )
        db.add(journal_entry)
        db.flush()
        
        # Create journal lines
        # Dr: Expense
        db.add(JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=expense_account.id,
            debit_amount=movement.total_value,
            credit_amount=0.0,
            narration=f"Issue: {item.name} - {movement.purpose}"
        ))
        
        # Cr: Inventory
        db.add(JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=inventory_account.id,
            debit_amount=0.0,
            credit_amount=movement.total_value,
            narration=f"Consumption: {item.name}"
        ))
        
        db.commit()
        return journal_entry
    except Exception as e:
        print(f"ERROR creating journal entry: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None


def test_issue(db: Session, temple_id: int, item: Item, store: Store, quantity: float, purpose: str):
    """Test issue/consumption transaction"""
    
    print(f"\n📤 Testing Issue:")
    print(f"   Item: {item.name}")
    print(f"   Store: {store.name}")
    print(f"   Quantity: {quantity} {item.unit.value}")
    print(f"   Purpose: {purpose}")
    
    # Check stock availability
    stock_balance = db.query(StockBalance).filter(
        StockBalance.item_id == item.id,
        StockBalance.store_id == store.id
    ).first()
    
    if not stock_balance or stock_balance.quantity < quantity:
        print(f"   ❌ Insufficient stock. Available: {stock_balance.quantity if stock_balance else 0.0}")
        return None
    
    # Calculate unit price (use average cost)
    unit_price = stock_balance.value / stock_balance.quantity if stock_balance.quantity > 0 else item.standard_cost
    total_value = quantity * unit_price
    
    # Generate movement number
    year = date.today().year
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
        movement_date=date.today(),
        item_id=item.id,
        store_id=store.id,
        quantity=quantity,
        unit_price=unit_price,
        total_value=total_value,
        issued_to="Priest/Kitchen Staff",
        purpose=purpose,
        temple_id=temple_id,
        created_by=1
    )
    db.add(movement)
    db.flush()
    
    # Update stock balance
    stock_balance.quantity -= quantity
    stock_balance.value -= total_value
    stock_balance.last_movement_date = date.today()
    stock_balance.last_movement_id = movement.id
    
    # Post to accounting
    journal_entry = post_inventory_issue_to_accounting(db, movement, temple_id)
    if journal_entry:
        movement.journal_entry_id = journal_entry.id
        print(f"   ✅ Accounting entry created: {journal_entry.entry_number}")
        print(f"      Dr: Expense Account")
        print(f"      Cr: Inventory Account")
    else:
        print(f"   ⚠️  Accounting entry not created (check accounts)")
    
    db.commit()
    print(f"   ✅ Issue recorded: {movement_number}")
    return movement


def main():
    """Main test function"""
    print("=" * 60)
    print("Inventory Flow Testing")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get temple_id
        sample_account = db.query(Account).filter(Account.account_code == "1000").first()
        temple_id = sample_account.temple_id if sample_account else None
        
        if not temple_id:
            print("⚠️  No temple found. Please ensure accounts are seeded first.")
            return
        
        print(f"\n🏛️  Temple ID: {temple_id}")
        print("-" * 60)
        
        # Step 1: Create stores
        print("\n📦 Step 1: Creating sample stores...")
        stores = create_sample_stores(db, temple_id)
        
        # Step 2: Create items
        print("\n📋 Step 2: Creating sample items...")
        items = create_sample_items(db, temple_id)
        
        # Step 3: Test purchase
        print("\n💰 Step 3: Testing purchase transactions...")
        if stores and items:
            # Purchase 1: Camphor (Pooja Material)
            purchase1 = test_purchase(db, temple_id, items[0], stores[0], 10.0, 500.0)
            
            # Purchase 2: Rice (Grocery)
            purchase2 = test_purchase(db, temple_id, items[2], stores[1], 100.0, 50.0)
            
            # Purchase 3: Cooking Oil (Grocery)
            purchase3 = test_purchase(db, temple_id, items[4], stores[1], 20.0, 150.0)
        
        # Step 4: Test issue
        print("\n📤 Step 4: Testing issue/consumption transactions...")
        if stores and items:
            # Issue 1: Camphor for Pooja
            issue1 = test_issue(db, temple_id, items[0], stores[0], 2.0, "Daily Pooja")
            
            # Issue 2: Rice for Annadanam
            issue2 = test_issue(db, temple_id, items[2], stores[1], 25.0, "Annadanam")
            
            # Issue 3: Cooking Oil for Annadanam
            issue3 = test_issue(db, temple_id, items[4], stores[1], 5.0, "Annadanam")
        
        # Step 5: Check stock balances
        print("\n📊 Step 5: Current Stock Balances...")
        balances = db.query(StockBalance).join(Item).join(Store).filter(
            StockBalance.temple_id == temple_id
        ).all()
        
        for balance in balances:
            print(f"   {balance.item.name} @ {balance.store.name}: {balance.quantity} {balance.item.unit.value} (Value: ₹{balance.value:.2f})")
        
        # Step 6: Check accounting entries
        print("\n📝 Step 6: Accounting Entries Created...")
        from app.models.accounting import JournalEntry
        # Query all entries and filter manually to avoid enum issues
        all_entries = db.query(JournalEntry).filter(
            JournalEntry.temple_id == temple_id
        ).order_by(JournalEntry.id.desc()).limit(20).all()
        
        entries = [e for e in all_entries if 'Inventory' in e.narration]
        
        for entry in entries:
            print(f"   {entry.entry_number}: {entry.narration} (₹{entry.total_amount})")
        
        print("\n" + "=" * 60)
        print("✅ Inventory flow testing completed!")
        print("\nNext: Create frontend pages for inventory management")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    main()

