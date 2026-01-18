"""
Seed Sample Data for Fresh Database
Creates sample data including accounts, sevas, donation categories, and sample transactions
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import all models (must import all to ensure relationships are configured)
# Same as init_db() function
from app.models.user import User
from app.models.temple import Temple
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking, SevaCategory, SevaAvailability
from app.models.accounting import Account, AccountType, AccountSubType, JournalEntry, JournalLine
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


def seed_sample_data():
    """Seed sample data for testing"""
    db = SessionLocal()
    try:
        # Get the temple
        temple = db.query(Temple).first()
        if not temple:
            print("[ERROR] No temple found. Please run initialize_fresh_db.py first.")
            return False
        
        print(f"Seeding data for temple: {temple.name}")
        
        # 1. Create Chart of Accounts
        print("\n1. Creating Chart of Accounts...")
        
        accounts = []
        
        # Cash Account
        cash_acc = db.query(Account).filter(
            Account.account_code == "1001",
            Account.temple_id == temple.id
        ).first()
        if not cash_acc:
            cash_acc = Account(
                temple_id=temple.id,
                account_code="1001",
                account_name="Cash in Hand",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubType.CASH_BANK,
                is_active=True
            )
            db.add(cash_acc)
            db.flush()
            accounts.append(cash_acc)
            print("  [OK] Created Cash Account (1001)")
        else:
            accounts.append(cash_acc)
            print("  [INFO] Cash Account already exists")
        
        # Bank Account
        bank_acc = db.query(Account).filter(
            Account.account_code == "1002",
            Account.temple_id == temple.id
        ).first()
        if not bank_acc:
            bank_acc = Account(
                temple_id=temple.id,
                account_code="1002",
                account_name="Bank Account",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubType.CASH_BANK,
                is_active=True
            )
            db.add(bank_acc)
            db.flush()
            accounts.append(bank_acc)
            print("  [OK] Created Bank Account (1002)")
        else:
            accounts.append(bank_acc)
            print("  [INFO] Bank Account already exists")
        
        # Donation Income
        don_inc = db.query(Account).filter(
            Account.account_code == "4001",
            Account.temple_id == temple.id
        ).first()
        if not don_inc:
            don_inc = Account(
                temple_id=temple.id,
                account_code="4001",
                account_name="Donation Income",
                account_type=AccountType.INCOME,
                account_subtype=AccountSubType.DONATION_INCOME,
                is_active=True
            )
            db.add(don_inc)
            db.flush()
            accounts.append(don_inc)
            print("  [OK] Created Donation Income Account (4001)")
        else:
            accounts.append(don_inc)
            print("  [INFO] Donation Income Account already exists")
        
        # Seva Income
        seva_inc = db.query(Account).filter(
            Account.account_code == "4002",
            Account.temple_id == temple.id
        ).first()
        if not seva_inc:
            seva_inc = Account(
                temple_id=temple.id,
                account_code="4002",
                account_name="Seva Income",
                account_type=AccountType.INCOME,
                account_subtype=AccountSubType.SEVA_INCOME,
                is_active=True
            )
            db.add(seva_inc)
            db.flush()
            accounts.append(seva_inc)
            print("  [OK] Created Seva Income Account (4002)")
        else:
            accounts.append(seva_inc)
            print("  [INFO] Seva Income Account already exists")
        
        # 2. Create Bank Account (skip if model doesn't support it easily)
        # Bank accounts can be created via the UI
        print("\n2. Bank Account (create via UI: Donations -> Bank Accounts)")
        print("  [INFO] You can add bank accounts through the web interface")
        
        # 3. Create Donation Categories
        print("\n3. Creating Donation Categories...")
        
        cat_gen = db.query(DonationCategory).filter(
            DonationCategory.name == "General Fund",
            DonationCategory.temple_id == temple.id
        ).first()
        if not cat_gen:
            cat_gen = DonationCategory(
                temple_id=temple.id,
                name="General Fund",
                description="General purpose donations",
                account_id=don_inc.id,
                is_active=True
            )
            db.add(cat_gen)
            print("  [OK] Created 'General Fund' category")
        
        cat_anna = db.query(DonationCategory).filter(
            DonationCategory.name == "Annadana",
            DonationCategory.temple_id == temple.id
        ).first()
        if not cat_anna:
            cat_anna = DonationCategory(
                temple_id=temple.id,
                name="Annadana",
                description="Food donation",
                account_id=don_inc.id,
                is_active=True
            )
            db.add(cat_anna)
            print("  [OK] Created 'Annadana' category")
        
        # 4. Create Sevas (using raw SQL to avoid column issues)
        print("\n4. Creating Sevas...")
        from sqlalchemy import text
        
        # Check if sevas exist using raw SQL
        existing_arch = db.execute(
            text("SELECT id FROM sevas WHERE name_english = :name"),
            {"name": "Daily Archana"}
        ).fetchone()
        
        if not existing_arch:
            seva_arch = Seva(
                name_english="Daily Archana",
                category=SevaCategory.ARCHANA,
                amount=50.0,
                availability=SevaAvailability.DAILY,
                account_id=seva_inc.id,
                description="Standard Daily Archana"
            )
            db.add(seva_arch)
            print("  [OK] Created 'Daily Archana' Seva (Rs 50)")
        else:
            print("  [INFO] 'Daily Archana' Seva already exists")
        
        existing_alan = db.execute(
            text("SELECT id FROM sevas WHERE name_english = :name"),
            {"name": "Alankara"}
        ).fetchone()
        
        if not existing_alan:
            seva_alan = Seva(
                name_english="Alankara",
                category=SevaCategory.ALANKARA,
                amount=500.0,
                availability=SevaAvailability.DAILY,
                account_id=seva_inc.id,
                description="Special Decoration"
            )
            db.add(seva_alan)
            print("  [OK] Created 'Alankara' Seva (Rs 500)")
        else:
            print("  [INFO] 'Alankara' Seva already exists")
        
        db.commit()
        print("\n[OK] Sample master data created successfully!")
        print("\nYou can now:")
        print("  1. Go to Donations -> Add New Donation")
        print("  2. Go to Sevas -> Book Seva")
        print("  3. The dashboard will show data after you add transactions")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("SEEDING SAMPLE DATA")
    print("=" * 60)
    success = seed_sample_data()
    if success:
        print("\n[OK] Done! Your database is ready to use.")
    else:
        print("\n[ERROR] Failed to seed data. Please check errors above.")

