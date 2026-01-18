"""
Check why advance seva booking is not showing in report
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
from sqlalchemy.orm import load_only

# Import all models for proper SQLAlchemy initialization
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

def check_booking():
    db = SessionLocal()
    try:
        # Find booking with amount 25000
        booking = db.query(SevaBooking).filter(
            SevaBooking.amount_paid == 25000
        ).first()
        
        if not booking:
            print("Booking with ₹25,000 not found")
            return
        
        print(f"Found booking:")
        print(f"  ID: {booking.id}")
        print(f"  Receipt Number: {booking.receipt_number}")
        print(f"  Booking Date: {booking.booking_date}")
        print(f"  Amount: ₹{booking.amount_paid}")
        print(f"  Status: {booking.status}")
        print(f"  Seva: {booking.seva.name_english if booking.seva else 'N/A'}")
        print(f"  Devotee: {booking.devotee.name if booking.devotee else 'N/A'}")
        print(f"  Devotee Temple ID: {booking.devotee.temple_id if booking.devotee else 'N/A'}")
        
        today = date.today()
        print(f"\nToday: {today}")
        
        # Simulate report query with different date ranges
        print(f"\n=== Report Query Simulation ===")
        
        # Scenario 1: Report from 2025-12-18 to 2025-12-18 (single day)
        from_date_1 = date(2025, 12, 18)
        to_date_1 = date(2025, 12, 18)
        print(f"\nScenario 1: Report from {from_date_1} to {to_date_1}")
        print(f"  Booking date ({booking.booking_date}) >= from_date ({from_date_1}): {booking.booking_date >= from_date_1}")
        print(f"  Booking date ({booking.booking_date}) <= to_date ({to_date_1}): {booking.booking_date <= to_date_1}")
        print(f"  Would be included: {booking.booking_date >= from_date_1 and booking.booking_date <= to_date_1}")
        
        # Scenario 2: Report from 2025-12-01 to 2025-12-31 (full month)
        from_date_2 = date(2025, 12, 1)
        to_date_2 = date(2025, 12, 31)
        print(f"\nScenario 2: Report from {from_date_2} to {to_date_2}")
        print(f"  Booking date ({booking.booking_date}) >= from_date ({from_date_2}): {booking.booking_date >= from_date_2}")
        print(f"  Booking date ({booking.booking_date}) <= to_date ({to_date_2}): {booking.booking_date <= to_date_2}")
        print(f"  Would be included: {booking.booking_date >= from_date_2 and booking.booking_date <= to_date_2}")
        
        # Check status determination
        if booking.booking_date <= today:
            booking_status = "Completed"
        else:
            booking_status = "Pending"
        print(f"\n  Status would be: {booking_status} (booking_date {booking.booking_date} {'<=' if booking.booking_date <= today else '>'} today {today})")
        
        # Test actual query
        print(f"\n=== Testing Actual Query ===")
        temple_id = booking.devotee.temple_id if booking.devotee else None
        print(f"Temple ID: {temple_id}")
        
        query = db.query(SevaBooking).options(
            load_only(
                SevaBooking.id,
                SevaBooking.seva_id,
                SevaBooking.devotee_id,
                SevaBooking.booking_date,
                SevaBooking.booking_time,
                SevaBooking.status,
                SevaBooking.amount_paid,
                SevaBooking.receipt_number,
            )
        ).join(Seva).join(Devotee).filter(
            SevaBooking.booking_date >= from_date_2,
            SevaBooking.booking_date <= to_date_2,
            SevaBooking.status != SevaBookingStatus.CANCELLED
        )
        
        if temple_id is not None:
            query = query.filter(Devotee.temple_id == temple_id)
        
        bookings = query.all()
        print(f"Total bookings in range {from_date_2} to {to_date_2}: {len(bookings)}")
        for b in bookings:
            status = "Completed" if b.booking_date <= today else "Pending"
            print(f"  Booking {b.receipt_number}: Date={b.booking_date}, Amount=₹{b.amount_paid}, Status={status}")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_booking()

















