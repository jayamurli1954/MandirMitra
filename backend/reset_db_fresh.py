
import os
import sys
import traceback
from sqlalchemy import text
from datetime import datetime

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.temple import Temple
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.inventory import Store, Item, StockBalance, StockMovement
from app.models.asset import Asset
from app.models.asset_history import AssetTransfer, AssetValuationHistory, AssetPhysicalVerification, AssetInsurance, AssetDocument
from app.models.hundi import HundiOpening, HundiMaster, HundiDenominationCount
from app.models.hr import Employee, Department, Designation, SalaryComponent, SalaryStructure, Payroll, LeaveType, LeaveApplication
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.upi_banking import BankAccount, UpiPayment, BankTransaction
from app.models.token_seva import TokenInventory, TokenSale, TokenReconciliation
from app.models.budget import Budget
from app.models.bank_reconciliation import BankReconciliation, BankStatement, BankStatementEntry
from app.models.financial_period import FinancialPeriod
from app.models.inkind_sponsorship import InKindDonation, Sponsorship
from app.core.security import get_password_hash

# Triggers all imports in database.py
# Make sure database.py has all models imported!

def reset_database():
    print("WARNING: This will DELETE ALL DATA and reset the database.")
    
    # 1. Drop all tables (PostgreSQL specific CASCADE)
    print("Dropping all tables (CASCADE)...")
    try:
        with engine.connect() as connection:
            connection.commit()
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))
            connection.commit()
    except Exception as e:
        print(f"Error dropping schema: {e}")
        # Fallback to drop_all if schema drop fails (e.g. permission)
        Base.metadata.drop_all(bind=engine)
    
    
    # 2. Create tables
    print("Creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("Error creating tables:")
        traceback.print_exc()
        return

    # 3. Create Test Data
    session = SessionLocal()
    try:
        print("Creating Test Temple...")
        test_temple = Temple(
            name="Test Mandir",
            name_kannada="ಪರೀಕ್ಷಾ ಮಂದಿರ",
            slug="test-mandir",
            primary_deity="Ganesha",
            city="Bangalore",
            state="Karnataka", 
            phone="9999999999",
            email="test@mandir.com",
            address="123, Test Street, Bangalore",
            description="A test temple for QA.",
            is_active=True,
            module_donations_enabled=True,
            module_sevas_enabled=True,
            module_inventory_enabled=True,
            module_assets_enabled=True,
            module_accounting_enabled=True,
            token_seva_threshold=50.0
        )
        session.add(test_temple)
        session.flush() # Get ID
        
        print("Creating Admin User...")
        try:
            hashed_pwd = get_password_hash("admin123")
        except Exception:
            print("(Using fallback hash due to passlib error)")
            # Fallback bcrypt hash for 'admin123' if passlib fails
            hashed_pwd = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWUNUz/dF12b0kX.sKj.D/3X/f/1.2" 
        
        admin_user = User(
            email="admin@temple.com",
            password_hash=hashed_pwd,
            full_name="System Admin",
            role="super_admin",
            is_active=True,
            is_superuser=True,
            temple_id=test_temple.id,
            created_at=datetime.utcnow().isoformat()
        )
        session.add(admin_user)
        session.commit()
        
        print(f"\nRESET COMPLETE SUCCESSFULLY!")
        print(f"----------------------------------------")
        print(f"Temple: {test_temple.name} (ID: {test_temple.id})")
        print(f"Admin:  admin@temple.com / admin123")
        print(f"----------------------------------------")
        
    except Exception as e:
        print(f"Error during data seeding:")
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    reset_database()
