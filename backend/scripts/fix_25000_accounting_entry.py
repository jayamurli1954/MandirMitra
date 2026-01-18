"""
Fix the incorrect accounting entry for booking 7 (₹25,000 advance booking)
The entry incorrectly credited 42002 (Seva Income) instead of 21003 (Advance Seva Booking)

We'll cancel the incorrect entry and create a new correct one.
"""

import sys
import os
from datetime import date, datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.seva import SevaBooking
from app.models.accounting import JournalEntry, JournalLine, Account, TransactionType, JournalEntryStatus
from app.models.user import User

# Import all models
from app.models.temple import Temple
from app.models.devotee import Devotee
from app.models.donation import Donation, DonationCategory
from app.models.seva import Seva
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

def fix_accounting_entry():
    db = SessionLocal()
    try:
        # Find booking 7
        booking = db.query(SevaBooking).filter(SevaBooking.id == 7).first()
        if not booking:
            print("Booking 7 not found")
            return
        
        print(f"Booking ID: {booking.id}")
        print(f"Amount: ₹{booking.amount_paid}")
        print(f"Booking Date: {booking.booking_date}")
        print(f"Today: {date.today()}")
        print(f"Is Advance Booking: {booking.booking_date > date.today()}")
        
        # Find the incorrect journal entry
        je = db.query(JournalEntry).filter(
            JournalEntry.reference_type == TransactionType.SEVA,
            JournalEntry.reference_id == booking.id
        ).first()
        
        if not je:
            print("No journal entry found")
            return
        
        print(f"\nFound Journal Entry: {je.entry_number}")
        print(f"Status: {je.status}")
        
        # Check current journal lines
        print("\nCurrent Journal Lines:")
        for line in je.journal_lines:
            account = line.account
            print(f"  {account.account_code} - {account.account_name}:")
            print(f"    Debit: ₹{line.debit_amount:,.2f}, Credit: ₹{line.credit_amount:,.2f}")
        
        # Check if it's wrong
        seva_income_line = next((line for line in je.journal_lines if line.account.account_code == '42002'), None)
        advance_seva_line = next((line for line in je.journal_lines if line.account.account_code == '21003'), None)
        
        if seva_income_line and seva_income_line.credit_amount > 0 and not advance_seva_line:
            print("\n❌ ERROR: Entry incorrectly credits 42002 (Seva Income) instead of 21003 (Advance Seva Booking)")
            print("\nCancelling incorrect entry and creating new one...")
            
            # Get admin user for cancellation
            admin_user = db.query(User).filter(User.email == "admin@temple.com").first()
            if not admin_user:
                admin_user = db.query(User).filter(User.is_superuser == True).first()
            
            if not admin_user:
                print("ERROR: No admin user found to cancel entry")
                return
            
            # Cancel the incorrect entry
            je.status = JournalEntryStatus.CANCELLED
            je.cancelled_by = admin_user.id
            je.cancelled_at = datetime.utcnow()
            je.cancellation_reason = "Incorrect account - should credit 21003 (Advance Seva Booking) instead of 42002 (Seva Income) for advance booking"
            
            db.flush()
            
            # Now create correct entry using the API function
            from app.api.sevas import post_seva_to_accounting
            # Get temple_id from booking (via seva or devotee)
            temple_id = booking.seva.temple_id if booking.seva and hasattr(booking.seva, 'temple_id') else None
            if not temple_id and booking.devotee and hasattr(booking.devotee, 'temple_id'):
                temple_id = booking.devotee.temple_id
            
            if not temple_id:
                print("ERROR: Could not determine temple_id")
                db.rollback()
                return
            
            new_je = post_seva_to_accounting(db, booking, temple_id)
            
            if new_je:
                print(f"\n✅ Created new correct journal entry: {new_je.entry_number}")
                print("\nNew Journal Lines:")
                for line in new_je.journal_lines:
                    account = line.account
                    print(f"  {account.account_code} - {account.account_name}:")
                    print(f"    Debit: ₹{line.debit_amount:,.2f}, Credit: ₹{line.credit_amount:,.2f}")
                
                db.commit()
                print("\n✅ Accounting entry corrected successfully!")
            else:
                print("ERROR: Failed to create new entry")
                db.rollback()
        else:
            print("\n✅ Entry appears correct")
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fix_accounting_entry()

