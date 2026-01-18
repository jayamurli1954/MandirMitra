
from app.core.database import SessionLocal
# Import ALL models
from app.models.user import User
from app.models.temple import Temple
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine, AccountType
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
from app.api.donations import post_donation_to_accounting

db = SessionLocal()

def fix_5000_donation():
    try:
        print("Finding Donation ID 1 (5000 Rs)...")
        donation = db.query(Donation).filter(Donation.id == 1).first()
        if not donation:
            print("Donation 1 not found!")
            return

        if donation.amount != 5000:
            print(f"Warning: Donation 1 amount is {donation.amount}, not 5000. Proceeding anyway.")

        if donation.journal_entry_id:
            print(f"Donation already has JE: {donation.journal_entry_id}")
        else:
            print("Posting to accounting...")
            # Create helper context for user if needed? post_donation_to_accounting usually doesn't need current_user unless it logs it.
            # It uses donation.created_by_id for logging.
            # Signature: post_donation_to_accounting(db, donation_obj, temple_id)
            je = post_donation_to_accounting(db, donation, 1)
            if je:
                print(f"Successfully created Journal Entry: {je.entry_number}")
                donation.journal_entry_id = je.id
                db.commit()
            else:
                print("Failed to create JE.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_5000_donation()
