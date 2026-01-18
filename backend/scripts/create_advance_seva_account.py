"""
Script to create Advance Seva Booking account (3003) if it doesn't exist
This account is needed for advance seva bookings accounting
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, init_db
from app.models.accounting import Account, AccountType
from app.models.temple import Temple

# Import all models to ensure relationships are properly configured
from app.models.user import User
from app.models.devotee import Devotee
from app.models.donation import Donation, DonationCategory
from app.models.seva import Seva, SevaBooking
from app.models.accounting import JournalEntry, JournalLine
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
from app.models.sacred_events_cache import SacredEventsCache

def create_advance_seva_account():
    db = SessionLocal()
    try:
        # Get all temples
        temples = db.query(Temple).all()
        
        if not temples:
            print("No temples found in database.")
            return
        
        for temple in temples:
            # Check if account 3003 exists for this temple
            existing = db.query(Account).filter(
                Account.temple_id == temple.id,
                Account.account_code == '3003'
            ).first()
            
            if existing:
                print(f"Temple {temple.id} ({temple.name}): Account 3003 already exists: {existing.account_name}")
                continue
            
            # Create the account
            account = Account(
                temple_id=temple.id,
                account_code='3003',
                account_name='Advance Seva Booking',
                account_type=AccountType.LIABILITY,
                description='Liability account for advance seva bookings. Amounts are credited here when seva is booked in advance, and transferred to Seva Income (3002) on the actual seva date.',
                is_active=True,
                parent_account_id=None  # You can link to a parent liability account if needed
            )
            
            db.add(account)
            db.commit()
            print(f"Temple {temple.id} ({temple.name}): Created account 3003 - Advance Seva Booking")
        
        print("\n[OK] Advance Seva Booking account check/creation completed!")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_advance_seva_account()

