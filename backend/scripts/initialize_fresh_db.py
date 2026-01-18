"""
Initialize Fresh Database
Creates a default temple and admin user for a fresh SQLite database
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import all models first to ensure relationships are configured
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

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash


def initialize_fresh_database():
    """Initialize fresh database with temple and admin user"""
    db = SessionLocal()
    try:
        # Check if temple exists
        temple = db.query(Temple).first()
        
        if not temple:
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
        else:
            print(f"  Temple already exists: {temple.name}")
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@temple.com").first()
        
        if not admin_user:
            print("Creating admin user...")
            admin_user = User(
                email="admin@temple.com",
                password_hash=get_password_hash("admin123"),
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
        else:
            print("  Admin user already exists")
            # Update password to ensure it's correct
            admin_user.password_hash = get_password_hash("admin123")
            admin_user.is_active = True
            admin_user.temple_id = temple.id
            db.commit()
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
    print("Initializing fresh database...")
    print("-" * 60)
    success = initialize_fresh_database()
    if success:
        print("\nYou can now login to the application!")
    else:
        print("\nFailed to initialize database. Please check the errors above.")









