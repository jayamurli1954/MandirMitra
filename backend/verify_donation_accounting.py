from app.core.database import SessionLocal
# Import ALL models to ensure mappers are initialized correctly
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

def verify_5000_donation(temple_id=1):
    db = SessionLocal()
    try:
        print(f"--- Verifying 5000 Rs Donation for Temple {temple_id} ---")
        
        # 1. Find the donation
        donation = db.query(Donation).filter(
            Donation.temple_id == temple_id,
            Donation.amount == 5000
        ).order_by(Donation.id.desc()).first()
        
        if not donation:
            print("ERROR: No donation of Rs 5000 found!")
            return
            
        print(f"Found Donation ID: {donation.id}, Date: {donation.created_at}, Amount: {donation.amount}")
        print(f"Linked JE ID: {donation.journal_entry_id}")
        
        if not donation.journal_entry_id:
            print("ERROR: Donation has no Journal Entry linked!")
            return
            
        # 2. Check Journal Entry
        je = db.query(JournalEntry).filter(JournalEntry.id == donation.journal_entry_id).first()
        if not je:
            print(f"ERROR: Journal Entry {donation.journal_entry_id} not found in DB!")
            return
            
        print(f"JE Number: {je.entry_number}, Date: {je.entry_date}")
        
        # 3. Check Lines
        lines = db.query(JournalLine).filter(JournalLine.journal_entry_id == je.id).all()
        for line in lines:
            acc = line.account
            d_or_c = "DEBIT" if line.debit_amount > 0 else "CREDIT"
            amt = line.debit_amount if line.debit_amount > 0 else line.credit_amount
            print(f"  Line {line.id}: {d_or_c} ₹{amt} -> Account [{acc.account_code}] {acc.account_name}")
            
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_5000_donation()
