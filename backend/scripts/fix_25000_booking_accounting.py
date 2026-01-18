"""
Script to find and create accounting entry for the ₹25,000 advance seva booking
"""

import sys
import os
from datetime import date

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.accounting import Account, TransactionType

# Import all models to ensure relationships are properly configured
from app.models.temple import Temple
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

def find_and_fix_booking():
    db = SessionLocal()
    try:
        # Find booking with amount 25000
        bookings = db.query(SevaBooking).filter(
            SevaBooking.amount_paid == 25000
        ).order_by(SevaBooking.id.desc()).all()
        
        print(f"\nFound {len(bookings)} booking(s) with amount ₹25,000:\n")
        
        for booking in bookings:
            print(f"Booking ID: {booking.id}")
            print(f"  Seva: {booking.seva.name_english if booking.seva else 'N/A'}")
            print(f"  Amount: ₹{booking.amount_paid}")
            print(f"  Booking Date: {booking.booking_date}")
            print(f"  Created: {booking.created_at}")
            print(f"  Payment Method: {booking.payment_method}")
            
            # Check if accounting entry exists
            je = db.query(JournalEntry).filter(
                JournalEntry.reference_type == TransactionType.SEVA,
                JournalEntry.reference_id == booking.id
            ).first()
            
            if je:
                print(f"  ✓ Accounting entry exists: {je.entry_number}")
            else:
                print(f"  ✗ NO ACCOUNTING ENTRY FOUND")
                print(f"  → Need to create accounting entry for this booking")
                print(f"  → Use API endpoint: POST /api/v1/sevas/bookings/{booking.id}/create-accounting")
            print()
        
        # Check account 21003 balance
        account_21003 = db.query(Account).filter(
            Account.account_code == '21003',
            Account.temple_id == 1  # Assuming temple_id 1
        ).first()
        
        if account_21003:
            # Get balance from journal lines
            from sqlalchemy import func
            credit_balance = db.query(func.coalesce(func.sum(JournalLine.credit_amount), 0)).join(JournalEntry).filter(
                JournalLine.account_id == account_21003.id,
                JournalEntry.status == 'posted'
            ).scalar()
            
            debit_balance = db.query(func.coalesce(func.sum(JournalLine.debit_amount), 0)).join(JournalEntry).filter(
                JournalLine.account_id == account_21003.id,
                JournalEntry.status == 'posted'
            ).scalar()
            
            net_balance = credit_balance - debit_balance
            print(f"Account 21003 (Advance Seva Booking) Balance: ₹{net_balance:,.2f}")
            print(f"  Credits: ₹{credit_balance:,.2f}")
            print(f"  Debits: ₹{debit_balance:,.2f}")
        else:
            print("Account 21003 not found!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    find_and_fix_booking()

