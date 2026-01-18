"""
Check journal entry date for booking 7
"""

import sys
import os
from datetime import date

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.seva import SevaBooking
from app.models.accounting import JournalEntry, TransactionType

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

def check_entry_date():
    db = SessionLocal()
    try:
        booking = db.query(SevaBooking).filter(SevaBooking.id == 7).first()
        if not booking:
            print("Booking 7 not found")
            return
        
        print(f"Booking ID: {booking.id}")
        print(f"Booking Date: {booking.booking_date}")
        print(f"Created At: {booking.created_at}")
        if hasattr(booking.created_at, 'date'):
            print(f"Receipt Date (created_at.date()): {booking.created_at.date()}")
        else:
            print(f"Receipt Date (created_at): {booking.created_at}")
        
        # Find journal entry
        je = db.query(JournalEntry).filter(
            JournalEntry.reference_type == TransactionType.SEVA,
            JournalEntry.reference_id == booking.id,
            JournalEntry.status != 'cancelled'
        ).order_by(JournalEntry.id.desc()).first()
        
        if je:
            print(f"\nJournal Entry: {je.entry_number}")
            print(f"Entry Date: {je.entry_date}")
            print(f"Status: {je.status}")
            print(f"\nToday: {date.today()}")
            print(f"Trial Balance As Of Date: 2025-12-18")
            print(f"\nIssue: Entry date ({je.entry_date}) is AFTER Trial Balance date (2025-12-18)")
            print(f"  The entry will be excluded from Trial Balance because entry_date > as_of_date")
            print(f"\nReceipt Date (when money was received): {booking.created_at.date() if hasattr(booking.created_at, 'date') else booking.created_at}")
            print(f"  Entry date should be receipt date, not booking date!")
        else:
            print("No journal entry found")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_entry_date()

















