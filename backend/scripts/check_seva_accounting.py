"""
Check if seva booking SEV000008 is accounted
"""

import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.seva import SevaBooking
from app.models.accounting import JournalEntry, JournalLine, TransactionType, JournalEntryStatus

# Import all models
from app.models.temple import Temple
from app.models.user import User
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

def check_seva_accounting():
    db = SessionLocal()
    try:
        # Find booking by receipt number
        booking = db.query(SevaBooking).filter(
            SevaBooking.receipt_number == 'SEV000008'
        ).first()
        
        if not booking:
            print("Booking SEV000008 not found")
            # Try finding by other criteria
            booking = db.query(SevaBooking).filter(
                SevaBooking.seva.has(name_english='Mahapooja'),
                SevaBooking.devotee.has(name='Deepak Menon'),
                SevaBooking.amount_paid == 500
            ).first()
            if booking:
                print(f"Found booking by criteria: {booking.receipt_number}")
            else:
                print("No booking found matching the criteria")
                return
        else:
            print(f"Found booking: {booking.receipt_number}")
        
        print(f"\nBooking Details:")
        print(f"  ID: {booking.id}")
        print(f"  Receipt Number: {booking.receipt_number}")
        print(f"  Seva: {booking.seva.name_english if booking.seva else 'N/A'}")
        print(f"  Devotee: {booking.devotee.name if booking.devotee else 'N/A'}")
        print(f"  Amount: ₹{booking.amount_paid}")
        print(f"  Booking Date: {booking.booking_date}")
        print(f"  Created At: {booking.created_at}")
        print(f"  Payment Method: {booking.payment_method}")
        
        # Check if accounting entry exists
        je = db.query(JournalEntry).filter(
            JournalEntry.reference_type == TransactionType.SEVA,
            JournalEntry.reference_id == booking.id,
            JournalEntry.status == JournalEntryStatus.POSTED
        ).first()
        
        if je:
            print(f"\n✅ Accounting Entry Found:")
            print(f"  Journal Entry: {je.entry_number}")
            print(f"  Entry Date: {je.entry_date}")
            print(f"  Status: {je.status}")
            print(f"  Narration: {je.narration}")
            print(f"\n  Journal Lines:")
            for line in je.journal_lines:
                account = line.account
                print(f"    {account.account_code} - {account.account_name}:")
                print(f"      Debit: ₹{line.debit_amount:,.2f}")
                print(f"      Credit: ₹{line.credit_amount:,.2f}")
        else:
            print(f"\n❌ NO ACCOUNTING ENTRY FOUND")
            print(f"  This booking is NOT accounted!")
            print(f"  Use API endpoint to create accounting entry:")
            print(f"  POST /api/v1/sevas/bookings/{booking.id}/create-accounting")
            
            # Check if there's a cancelled entry
            cancelled_je = db.query(JournalEntry).filter(
                JournalEntry.reference_type == TransactionType.SEVA,
                JournalEntry.reference_id == booking.id
            ).first()
            if cancelled_je:
                print(f"\n  Note: Found cancelled entry: {cancelled_je.entry_number}")
                print(f"    Status: {cancelled_je.status}")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_seva_accounting()

















