"""
Initialize default accounts for Quick Expense module
Creates expense accounts and payment method accounts that Quick Expense expects
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure stdout encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Import app.main to ensure all models are registered
# This ensures all SQLAlchemy relationships are properly initialized
import app.main

# Now import what we need
from app.models.temple import Temple
from app.models.accounting import Account, AccountType, AccountSubType

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from datetime import datetime

def create_default_accounts(db: Session, temple_id: int = 1):
    """
    Create default accounts for Quick Expense module
    """
    
    # Check if accounts already exist
    existing_codes = {acc.account_code for acc in db.query(Account).filter(Account.temple_id == temple_id).all()}
    
    # Expense Accounts (Debit accounts - Expenses)
    # Note: Using None for subtype if the enum values don't match - can be set later
    expense_accounts = [
        # Operational Expenses (51xx)
        {'code': E101', 'name': 'Priest Salary', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E102', 'name': 'Staff Salary', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E110', 'name': 'Electricity Bill', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E111', 'name': 'Water Bill', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E120', 'name': 'Maintenance & Repairs', 'type': AccountType.EXPENSE, 'subtype': None},
        
        # Pooja & Ritual Expenses (52xx)
        {'code': E201', 'name': 'Flower Decoration', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E202', 'name': 'Pooja Materials', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E203', 'name': 'Prasadam Expense', 'type': AccountType.EXPENSE, 'subtype': None},
        
        # Annadana Expenses (53xx)
        {'code': E301', 'name': 'Vegetables & Groceries', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E302', 'name': 'Cooking Gas', 'type': AccountType.EXPENSE, 'subtype': None},
        
        # Festival Expenses (54xx)
        {'code': E401', 'name': 'Tent Hiring', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E402', 'name': 'Sound System', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E403', 'name': 'Lighting Expense', 'type': AccountType.EXPENSE, 'subtype': None},
        
        # Administrative Expenses (55xx)
        {'code': E501', 'name': 'Audit Fees', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E502', 'name': 'Bank Charges', 'type': AccountType.EXPENSE, 'subtype': None},
        {'code': E503', 'name': 'Printing & Stationery', 'type': AccountType.EXPENSE, 'subtype': None},
    ]
    
    # Payment Method Accounts (Credit accounts - Assets)
    payment_accounts = [
        {'code': A101', 'name': 'Cash - Counter', 'type': AccountType.ASSET, 'subtype': None},
        {'code': A102', 'name': 'Cash - Hundi', 'type': AccountType.ASSET, 'subtype': None},
        {'code': A110', 'name': 'Bank - SBI Current Account', 'type': AccountType.ASSET, 'subtype': None},
        {'code': A111', 'name': 'Bank - HDFC Savings Account', 'type': AccountType.ASSET, 'subtype': None},
    ]
    
    all_accounts = expense_accounts + payment_accounts
    created_count = 0
    skipped_count = 0
    
    for acc_data in all_accounts:
        if acc_data['code'] in existing_codes:
            print(f"[SKIP] Account {acc_data['code']} ({acc_data['name']}) already exists. Skipping.")
            skipped_count += 1
            continue
        
        account = Account(
            account_code=acc_data['code'],
            account_name=acc_data['name'],
            account_type=acc_data['type'],
            account_subtype=acc_data['subtype'],
            temple_id=temple_id,
            is_active=True,
            is_system_account=False,
            allow_manual_entry=True,
            description=f"Default account for {acc_data['name']}",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        
        db.add(account)
        created_count += 1
        print(f"[OK] Created account {acc_data['code']} - {acc_data['name']}")
    
    try:
        db.commit()
        print(f"\n[SUCCESS] Successfully created {created_count} accounts")
        print(f"[INFO] Skipped {skipped_count} existing accounts")
        return True
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error creating accounts: {e}")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("Initializing Default Accounts for Quick Expense Module")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Get temple ID (default to 1, or get from first temple)
        temple = db.query(Temple).first()
        if not temple:
            print("[ERROR] No temple found in database. Please create a temple first.")
            return
        
        temple_id = temple.id
        print(f"[INFO] Using Temple ID: {temple_id} ({temple.name})")
        print()
        
        # Create accounts
        success = create_default_accounts(db, temple_id)
        
        if success:
            print("\n[SUCCESS] Default accounts initialized successfully!")
            print("\nYou can now use Quick Expense module with these accounts:")
            print("  - Expense Types: 5101-5503")
            print("  - Payment Methods: 1101, 1102, 1110, 1111")
        else:
            print("\n[ERROR] Failed to initialize accounts. Please check the error above.")
    
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

