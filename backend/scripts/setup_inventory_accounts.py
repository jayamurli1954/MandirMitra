"""
Setup Inventory Accounts in Chart of Accounts
Creates inventory asset accounts (1400-1499 series) and links them to inventory items
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings

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
from app.models.inventory import Item, ItemCategory, Store, StockMovement
from app.models.accounting import AccountType, AccountSubType

# Inventory Account Code Series: 1400-1499
INVENTORY_ACCOUNT_STRUCTURE = {
    "1400": {
        "account_name": "Inventory Assets",
        "account_name_kannada": "ದಾಸ್ತಾನು ಆಸ್ತಿಗಳು",
        "description": "All inventory items (1400-1499 block)",
        "is_parent": True
    },
    "1401": {
        "account_name": "Inventory - Pooja Materials",
        "account_name_kannada": "ದಾಸ್ತಾನು - ಪೂಜಾ ಸಾಮಗ್ರಿಗಳು",
        "description": "Flowers, oil, camphor, incense, kumkum, etc.",
        "category": ItemCategory.POOJA_MATERIAL,
        "parent_code": "1400"
    },
    "1402": {
        "account_name": "Inventory - Grocery & Annadanam",
        "account_name_kannada": "ದಾಸ್ತಾನು - ಅನ್ನದಾನ ಸಾಮಗ್ರಿಗಳು",
        "description": "Rice, dal, oil, spices, vegetables for annadanam",
        "category": ItemCategory.GROCERY,
        "parent_code": "1400"
    },
    "1403": {
        "account_name": "Inventory - Cleaning Supplies",
        "account_name_kannada": "ದಾಸ್ತಾನು - ಸ್ವಚ್ಛತೆ ಸಾಮಗ್ರಿಗಳು",
        "description": "Soap, detergent, cleaning supplies",
        "category": ItemCategory.CLEANING,
        "parent_code": "1400"
    },
    "1404": {
        "account_name": "Inventory - Maintenance Items",
        "account_name_kannada": "ದಾಸ್ತಾನು - ನಿರ್ವಹಣೆ ಸಾಮಗ್ರಿಗಳು",
        "description": "Electrical items, plumbing, maintenance supplies",
        "category": ItemCategory.MAINTENANCE,
        "parent_code": "1400"
    },
    "1405": {
        "account_name": "Inventory - General",
        "account_name_kannada": "ದಾಸ್ತಾನು - ಸಾಮಾನ್ಯ",
        "description": "General inventory items",
        "category": ItemCategory.GENERAL,
        "parent_code": "1400"
    }
    # 1406-1499 reserved for future inventory categories
}

# Expense Accounts for Consumption (5000-5999 series)
# These are used when inventory is issued/consumed
EXPENSE_ACCOUNT_MAPPING = {
    ItemCategory.POOJA_MATERIAL: {
        "account_code": "5001",
        "account_name": "Pooja Expense",
        "account_name_kannada": "ಪೂಜಾ ವೆಚ್ಚ"
    },
    ItemCategory.GROCERY: {
        "account_code": "5002",
        "account_name": "Annadanam Expense",
        "account_name_kannada": "ಅನ್ನದಾನ ವೆಚ್ಚ"
    },
    ItemCategory.CLEANING: {
        "account_code": "5003",
        "account_name": "Cleaning & Maintenance Expense",
        "account_name_kannada": "ಸ್ವಚ್ಛತೆ ವೆಚ್ಚ"
    },
    ItemCategory.MAINTENANCE: {
        "account_code": "5004",
        "account_name": "Maintenance Expense",
        "account_name_kannada": "ನಿರ್ವಹಣೆ ವೆಚ್ಚ"
    },
    ItemCategory.GENERAL: {
        "account_code": "5005",
        "account_name": "General Operational Expense",
        "account_name_kannada": "ಸಾಮಾನ್ಯ ಕಾರ್ಯಾಚರಣಾ ವೆಚ್ಚ"
    }
}


def get_or_create_parent_account(db: Session, temple_id: int, account_code: str, account_data: dict):
    """Get or create parent account (1000 - Assets)"""
    parent_account = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == A000"
    ).first()
    
    if not parent_account:
        print(f"⚠️  Parent account 1000 (Assets) not found. Please run seed_chart_of_accounts.py first.")
        return None
    
    return parent_account


def create_inventory_accounts(db: Session, temple_id: int):
    """Create inventory accounts (1400-1499 series)"""
    parent_account = get_or_create_parent_account(db, temple_id, A000", {})
    if not parent_account:
        return False
    
    created_count = 0
    updated_count = 0
    
    # First, create parent account 1400
    parent_inv_account = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == "1400"
    ).first()
    
    if not parent_inv_account:
        parent_inv_account = Account(
            temple_id=temple_id,
            account_code="1400",
            account_name=INVENTORY_ACCOUNT_STRUCTURE["1400"]["account_name"],
            account_name_kannada=INVENTORY_ACCOUNT_STRUCTURE["1400"]["account_name_kannada"],
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.INVENTORY,
            parent_account_id=parent_account.id,
            is_system_account=True,
            allow_manual_entry=False,
            description=INVENTORY_ACCOUNT_STRUCTURE["1400"]["description"]
        )
        db.add(parent_inv_account)
        db.flush()
        created_count += 1
        print(f"✅ Created parent account: 1400 - {parent_inv_account.account_name}")
    else:
        print(f"ℹ️  Parent account 1400 already exists")
    
    # Create category-wise inventory accounts
    for code, data in INVENTORY_ACCOUNT_STRUCTURE.items():
        if code == "1400":  # Skip parent, already created
            continue
        
        account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == code
        ).first()
        
        if not account:
            account = Account(
                temple_id=temple_id,
                account_code=code,
                account_name=data["account_name"],
                account_name_kannada=data.get("account_name_kannada", ""),
                account_type=AccountType.ASSET,
                account_subtype=AccountSubType.INVENTORY,
                parent_account_id=parent_inv_account.id,
                is_system_account=True,
                allow_manual_entry=False,
                description=data["description"]
            )
            db.add(account)
            db.flush()
            created_count += 1
            print(f"✅ Created account: {code} - {account.account_name}")
        else:
            updated_count += 1
            print(f"ℹ️  Account {code} already exists")
    
    db.commit()
    print(f"\n📊 Summary: Created {created_count} accounts, {updated_count} already existed")
    return True


def link_items_to_accounts(db: Session, temple_id: int):
    """Link inventory items to their category-specific accounts"""
    items = db.query(Item).filter(Item.temple_id == temple_id).all()
    
    linked_count = 0
    not_found_count = 0
    
    for item in items:
        # Find account for this item's category
        account_code = None
        for code, data in INVENTORY_ACCOUNT_STRUCTURE.items():
            if code != "1400" and data.get("category") == item.category:
                account_code = code
                break
        
        if account_code:
            account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == account_code
            ).first()
            
            if account:
                if item.inventory_account_id != account.id:
                    item.inventory_account_id = account.id
                    linked_count += 1
                    print(f"✅ Linked item '{item.name}' to account {account_code}")
            else:
                not_found_count += 1
                print(f"⚠️  Account {account_code} not found for item '{item.name}'")
        else:
            # Use default inventory account (1405 - General)
            default_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == "1405"
            ).first()
            if default_account and item.inventory_account_id != default_account.id:
                item.inventory_account_id = default_account.id
                linked_count += 1
                print(f"✅ Linked item '{item.name}' to default account 1405")
    
    # Link expense accounts
    for item in items:
        expense_mapping = EXPENSE_ACCOUNT_MAPPING.get(item.category)
        if expense_mapping:
            expense_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == expense_mapping["account_code"]
            ).first()
            
            if expense_account:
                if item.expense_account_id != expense_account.id:
                    item.expense_account_id = expense_account.id
                    print(f"✅ Linked expense account for item '{item.name}'")
    
    db.commit()
    print(f"\n📊 Linked {linked_count} items to accounts")
    return True


def link_stores_to_accounts(db: Session, temple_id: int):
    """Link stores to default inventory account (1400) or category-specific accounts"""
    stores = db.query(Store).filter(Store.temple_id == temple_id).all()
    
    # Get default inventory account (1400 - parent)
    default_account = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == "1400"
    ).first()
    
    if not default_account:
        print("⚠️  Default inventory account 1400 not found. Run create_inventory_accounts first.")
        return False
    
    linked_count = 0
    for store in stores:
        if not store.inventory_account_id:
            store.inventory_account_id = default_account.id
            linked_count += 1
            print(f"✅ Linked store '{store.name}' to account 1400")
    
    db.commit()
    print(f"\n📊 Linked {linked_count} stores to accounts")
    return True


def main():
    """Main function to setup inventory accounts"""
    print("=" * 60)
    print("Inventory Accounts Setup")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get temple_id from accounts (find any account to get temple_id)
        sample_account = db.query(Account).filter(Account.account_code == A000").first()
        temple_id = sample_account.temple_id if sample_account else None
        
        if temple_id:
            print(f"🏛️  Processing temple ID: {temple_id}")
        else:
            print("🏛️  Processing in standalone mode (temple_id=None)")
        
        print("-" * 60)
        
        # Step 1: Create inventory accounts
        print("\n📝 Step 1: Creating inventory accounts (1400-1499)...")
        if create_inventory_accounts(db, temple_id):
            print("✅ Inventory accounts created successfully")
        else:
            print("❌ Failed to create inventory accounts")
            return
        
        # Step 2: Link items to accounts
        print("\n🔗 Step 2: Linking items to accounts...")
        link_items_to_accounts(db, temple_id)
        
        # Step 3: Link stores to accounts
        print("\n🏪 Step 3: Linking stores to accounts...")
        link_stores_to_accounts(db, temple_id)
        
        print("\n" + "=" * 60)
        print("✅ Inventory accounts setup completed!")
        print("\nAccount Code Series:")
        print("  1400 - Inventory Assets (Parent)")
        print("  1401 - Inventory - Pooja Materials")
        print("  1402 - Inventory - Grocery & Annadanam")
        print("  1403 - Inventory - Cleaning Supplies")
        print("  1404 - Inventory - Maintenance Items")
        print("  1405 - Inventory - General")
        print("  1406-1499 - Reserved for future categories")
        print("\nExpense Accounts (for consumption):")
        print("  5001 - Pooja Expense")
        print("  5002 - Annadanam Expense")
        print("  5003 - Cleaning & Maintenance Expense")
        print("  5004 - Maintenance Expense")
        print("  5005 - General Operational Expense")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    main()

