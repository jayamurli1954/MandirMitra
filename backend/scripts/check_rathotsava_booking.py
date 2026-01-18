"""
Check if Rathotsava booking exists and would appear in report
"""

import sys
import os
from datetime import date

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.seva import SevaBooking, SevaBookingStatus, Seva
from app.models.devotee import Devotee

# Import all models
from app.models.temple import Temple
from app.models.user import User
from app.models.donation import Donation, DonationCategory
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

def check_rathotsava():
    db = SessionLocal()
    try:
        # Find Rathotsava booking
        booking = db.query(SevaBooking).join(Seva).filter(
            Seva.name_english.ilike('%rathotsava%'),
            SevaBooking.booking_date == date(2025, 12, 22)
        ).first()
        
        if not booking:
            print("Rathotsava booking on 22-12-2025 not found")
            return
        
        print(f"Found Rathotsava booking:")
        print(f"  ID: {booking.id}")
        print(f"  Receipt Number: {booking.receipt_number}")
        print(f"  Booking Date: {booking.booking_date}")
        print(f"  Amount: ₹{booking.amount_paid}")
        print(f"  Status: {booking.status}")
        print(f"  Is Cancelled: {booking.is_cancelled if hasattr(booking, 'is_cancelled') else 'N/A'}")
        print(f"  Temple ID: {booking.seva.temple_id if booking.seva else 'N/A'}")
        
        # Check if it would appear in report (from 18-12-2025 to 31-12-2025)
        from_date = date(2025, 12, 18)
        to_date = date(2025, 12, 31)
        today = date.today()
        
        print(f"\nReport Date Range: {from_date} to {to_date}")
        print(f"Today: {today}")
        
        # Check filters
        print(f"\nQuery Filters Check:")
        print(f"  booking_date >= from_date: {booking.booking_date >= from_date} ({booking.booking_date} >= {from_date})")
        print(f"  booking_date <= to_date: {booking.booking_date <= to_date} ({booking.booking_date} <= {to_date})")
        print(f"  status != CANCELLED: {booking.status != SevaBookingStatus.CANCELLED} ({booking.status} != {SevaBookingStatus.CANCELLED})")
        
        # Determine status for report
        if booking.booking_date <= today:
            booking_status = "Completed"
        else:
            booking_status = "Pending"
        
        print(f"\n  Would show as: {booking_status}")
        
        # Check if it would be included
        if (booking.booking_date >= from_date and 
            booking.booking_date <= to_date and 
            booking.status != SevaBookingStatus.CANCELLED):
            print(f"\n✅ Booking SHOULD appear in report")
        else:
            print(f"\n❌ Booking would NOT appear in report")
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_rathotsava()

















