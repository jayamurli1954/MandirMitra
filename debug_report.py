import sys
import os
from datetime import date

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.core.database import SessionLocal
# Import ALL models to ensure mappers are initialized correctly
from app.models.user import User
from app.models.temple import Temple
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.accounting import JournalEntry, Account, JournalLine
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.inventory import Store, Item, StockBalance, StockMovement
from app.models.asset import Asset
from app.models.asset_history import AssetTransfer
from app.models.hundi import HundiOpening
from app.models.hr import Employee
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.upi_banking import BankAccount
from app.models.token_seva import TokenInventory
from app.models.budget import Budget
from app.models.bank_reconciliation import BankReconciliation
from app.models.financial_period import FinancialPeriod
from app.models.inkind_sponsorship import InKindDonation
from app.api.journal_entries import get_trial_balance

# Mock User
class MockUser:
    def __init__(self, temple_id):
        self.temple_id = temple_id

def debug_trial_balance():
    print("--- Debugging Trial Balance Logic ---")
    db = SessionLocal()
    try:
        # Get admin user
        user = db.query(User).filter(User.role == "admin").first()
        if not user:
             user = db.query(User).first()
             if not user: 
                 print("No user found.")
                 return
        
        print(f"Using Temple ID: {user.temple_id}")
        
        # Call the function directly
        try:
            # We mock the dependency injection
            response = get_trial_balance(
                as_of_date=date.today(),
                db=db,
                current_user=user
            )
            
            print(f"Report Date: {response.as_of_date}")
            print(f"Total Debits: {response.total_debits}")
            print(f"Total Credits: {response.total_credits}")
            print(f"Is Balanced: {response.is_balanced}")
            print(f"Account Count: {len(response.accounts)}")
            
            for acc in response.accounts:
                print(f" - {acc.account_code} {acc.account_name}: Dr {acc.debit_balance} / Cr {acc.credit_balance}")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"FAILURE: Report generation failed: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    debug_trial_balance()
