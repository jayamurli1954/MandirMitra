
import os
import sys
from datetime import datetime

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app.core.database import SessionLocal
from app.models.user import User
from app.models.temple import Temple
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.accounting import Account, AccountType, AccountSubType
from app.models.seva import Seva, SevaCategory, SevaAvailability, SevaBooking
from app.models.inventory import Store, Item, StockBalance
from app.models.asset import Asset
from app.models.hundi import HundiOpening
from app.models.hr import Employee
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.upi_banking import BankAccount
from app.models.token_seva import TokenInventory
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.asset_history import AssetTransfer, AssetValuationHistory, AssetPhysicalVerification, AssetInsurance, AssetDocument
from app.models.budget import Budget
from app.models.bank_reconciliation import BankReconciliation, BankStatement, BankStatementEntry
from app.models.financial_period import FinancialPeriod
from app.models.inkind_sponsorship import InKindDonation, Sponsorship

def seed_data():
    session = SessionLocal()
    try:
        # 1. Get Test Temple
        temple = session.query(Temple).filter(Temple.slug == "test-mandir").first()
        if not temple:
            print("❌ 'Test Mandir' not found. Please run reset_db_fresh.py first.")
            return
        
        print(f"Seeding data for Temple: {temple.name} (ID: {temple.id})")
        
        # 2. Seed Accounts
        print("Creating Accounts...")
        
        # Cash Account (Asset)
        cash_acc = session.query(Account).filter(Account.account_code == A001", Account.temple_id == temple.id).first()
        if not cash_acc:
            cash_acc = Account(
                temple_id=temple.id,
                account_code=A001",
                account_name="Cash in Hand",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubType.CASH_BANK,
                description="Main cash account",
                is_active=True
            )
            session.add(cash_acc)
            session.flush()
            print(f"  - Created Account: 1001 - Cash in Hand")
        
        # Bank Account (Asset)
        bank_acc = session.query(Account).filter(Account.account_code == A002", Account.temple_id == temple.id).first()
        if not bank_acc:
            bank_acc = Account(
                temple_id=temple.id,
                account_code=A002",
                account_name="Primary Bank Account",  # Generic Name
                account_type=AccountType.ASSET,
                account_subtype=AccountSubType.CASH_BANK,
                description="Primary Bank Account for Main Operations",
                is_active=True
            )
            session.add(bank_acc)
            session.flush()
            print(f"  - Created Account: 1002 - Primary Bank Account")
            
        # Donation Income (Income)
        don_inc = session.query(Account).filter(Account.account_code == "3001", Account.temple_id == temple.id).first()
        if not don_inc:
            don_inc = Account(
                temple_id=temple.id,
                account_code="3001",
                account_name="Donation Income",
                account_type=AccountType.INCOME,
                account_subtype=AccountSubType.DONATION_INCOME,
                description="General donations",
                is_active=True
            )
            session.add(don_inc)
            session.flush()
            print(f"  - Created Account: 3001 - Donation Income")

        # Seva Income (Income)
        seva_inc = session.query(Account).filter(Account.account_code == "3002", Account.temple_id == temple.id).first()
        if not seva_inc:
            seva_inc = Account(
                temple_id=temple.id,
                account_code="3002",
                account_name="Seva Income",
                account_type=AccountType.INCOME,
                account_subtype=AccountSubType.SEVA_INCOME,
                description="Income from sevas",
                is_active=True
            )
            session.add(seva_inc)
            session.flush()
            print(f"  - Created Account: 3002 - Seva Income")

        # 3. Seed Donation Categories
        print("Creating Donation Categories...")
        cat_gen = session.query(DonationCategory).filter(DonationCategory.name == "General Fund", DonationCategory.temple_id == temple.id).first()
        if not cat_gen:
            cat_gen = DonationCategory(
                temple_id=temple.id,
                name="General Fund",
                description="General purpose donations",
                account_id=don_inc.id,
                is_active=True
            )
            session.add(cat_gen)
            print("  - Created Category: General Fund")
            
        cat_anna = session.query(DonationCategory).filter(DonationCategory.name == "Annadana", DonationCategory.temple_id == temple.id).first()
        if not cat_anna:
            cat_anna = DonationCategory(
                temple_id=temple.id,
                name="Annadana",
                description="Food donation",
                account_id=don_inc.id,
                is_active=True
            )
            session.add(cat_anna)
            print("  - Created Category: Annadana")

        # 4. Seed Sevas (Examples)
        print("Creating Sevas...")
        
        # Example 1: Daily Archana
        seva_arch = session.query(Seva).filter(Seva.name_english == "Daily Archana").first()
        if not seva_arch:
            seva_arch = Seva(
                name_english="Daily Archana",
                category=SevaCategory.ARCHANA,
                amount=20.0,
                availability=SevaAvailability.DAILY,
                account_id=seva_inc.id,
                description="Standard Daily Archana"
            )
            session.add(seva_arch)
            print("  - Created Seva: Daily Archana (₹20)")

        seva_alan = session.query(Seva).filter(Seva.name_english == "Alankara").first()
        if not seva_alan:
            seva_alan = Seva(
                name_english="Alankara",
                category=SevaCategory.ALANKARA,
                amount=500.0,
                availability=SevaAvailability.DAILY,
                account_id=seva_inc.id,
                description="Special Decoration"
            )
            session.add(seva_alan)
            print("  - Created Seva: Alankara (₹500)")

        session.commit()
        print("\n✅ Seed Data Created Successfully!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()
