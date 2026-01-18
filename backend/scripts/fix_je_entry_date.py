"""
Fix journal entry date for booking 7 - should be receipt date (2025-12-18), not booking date (2025-12-22)
"""

import sys
import os
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.seva import SevaBooking
from app.models.accounting import JournalEntry, TransactionType, JournalEntryStatus

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

def fix_entry_date():
    db = SessionLocal()
    try:
        booking = db.query(SevaBooking).filter(SevaBooking.id == 7).first()
        if not booking:
            print("Booking 7 not found")
            return
        
        print(f"Booking ID: {booking.id}")
        print(f"Booking Date: {booking.booking_date}")
        print(f"Created At: {booking.created_at}")
        
        receipt_date = booking.created_at.date() if hasattr(booking.created_at, 'date') else booking.created_at
        print(f"Receipt Date: {receipt_date}")
        
        # Find journal entry
        je = db.query(JournalEntry).filter(
            JournalEntry.reference_type == TransactionType.SEVA,
            JournalEntry.reference_id == booking.id,
            JournalEntry.status == JournalEntryStatus.POSTED
        ).order_by(JournalEntry.id.desc()).first()
        
        if je:
            print(f"\nJournal Entry: {je.entry_number}")
            print(f"Current Entry Date: {je.entry_date}")
            print(f"Should be Receipt Date: {receipt_date}")
            
            if je.entry_date.date() != receipt_date:
                print(f"\nUpdating entry date from {je.entry_date.date()} to {receipt_date}...")
                
                # Update entry date to receipt date
                new_entry_date = datetime.combine(receipt_date, datetime.min.time())
                je.entry_date = new_entry_date
                
                db.commit()
                print(f"✅ Entry date updated successfully!")
                print(f"New Entry Date: {je.entry_date}")
            else:
                print("\n✅ Entry date is already correct")
        else:
            print("No posted journal entry found")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fix_entry_date()

















