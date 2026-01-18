"""
Fix and Initialize Database
Removes existing users/temples and creates fresh ones with correct password hashes
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import all models first
from app.models.user import User
from app.models.temple import Temple
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.inventory import Store, Item, StockBalance, StockMovement
from app.models.asset import Asset
from app.models.asset_history import (
    AssetTransfer,
    AssetValuationHistory,
    AssetPhysicalVerification,
    AssetInsurance,
    AssetDocument,
)
from app.models.hundi import HundiOpening, HundiMaster, HundiDenominationCount
from app.models.hr import (
    Employee,
    Department,
    Designation,
    SalaryComponent,
    SalaryStructure,
    Payroll,
    LeaveType,
    LeaveApplication,
)
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.upi_banking import BankAccount, UpiPayment, BankTransaction
from app.models.token_seva import TokenInventory, TokenSale, TokenReconciliation
from app.models.bank_reconciliation import BankReconciliation, BankStatement, BankStatementEntry
from app.models.financial_period import FinancialPeriod
from app.models.inkind_sponsorship import InKindDonation, Sponsorship

from app.core.database import SessionLocal
import bcrypt


def fix_and_initialize():
    """Fix database and create temple/admin user"""
    db = SessionLocal()
    try:
        # Delete existing users (they might have corrupted password hashes)
        existing_users = db.query(User).all()
        if existing_users:
            print(f"Removing {len(existing_users)} existing user(s)...")
            for user in existing_users:
                db.delete(user)
            db.flush()
        
        # Delete existing temples
        existing_temples = db.query(Temple).all()
        if existing_temples:
            print(f"Removing {len(existing_temples)} existing temple(s)...")
            for temple in existing_temples:
                db.delete(temple)
            db.flush()
        
        # Create new temple
        print("Creating default temple...")
        temple = Temple(
            name="My Temple",
            slug="my-temple",
            address="",
            city="",
            state="",
            primary_deity="Lord Ganesha",
            is_active=True
        )
        db.add(temple)
        db.flush()
        print(f"  Created temple: {temple.name}")
        
        # Create admin user with proper password hash
        print("Creating admin user...")
        password = "admin123"
        # Use bcrypt directly to avoid passlib version issues
        password_bytes = password.encode('utf-8')
        # Truncate to 72 bytes if needed (bcrypt limit)
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        admin_user = User(
            email="admin@temple.com",
            password_hash=password_hash,
            full_name="Admin User",
            role="temple_manager",
            is_active=True,
            is_superuser=True,
            temple_id=temple.id
        )
        db.add(admin_user)
        db.commit()
        
        print("  Created admin user")
        print("\n" + "=" * 60)
        print("LOGIN CREDENTIALS:")
        print("=" * 60)
        print("  Email:    admin@temple.com")
        print("  Password: admin123")
        print("=" * 60)
        print("\nDatabase initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("Fixing and initializing database...")
    print("-" * 60)
    success = fix_and_initialize()
    if success:
        print("\nYou can now login to the application!")
    else:
        print("\nFailed to initialize database. Please check the errors above.")

