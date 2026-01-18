"""
Pre-calculate Sacred Events Cache
This script should be run daily (preferably at midnight) to maintain the cache

Usage:
    python scripts/pre_calculate_sacred_events.py [days_ahead]

Default: 30 days ahead
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure encoding for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from datetime import date, timedelta
from app.core.database import SessionLocal, init_db
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.temple import Temple
from app.services.ready_reckoner_service import ReadyReckonerService

# Import all models to ensure relationships are properly configured
# This is needed for SQLAlchemy to work correctly (same as in database.py)
from app.models.user import User
from app.models.temple import Temple
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine
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


def main():
    """Main function to pre-calculate sacred events"""
    
    # Get days ahead from command line or default to 30
    days_ahead = 30
    if len(sys.argv) > 1:
        try:
            days_ahead = int(sys.argv[1])
        except ValueError:
            print(f"Invalid days_ahead argument: {sys.argv[1]}. Using default: 30")
    
    print(f"Starting pre-calculation of sacred events for next {days_ahead} days...")
    
    db = SessionLocal()
    try:
        # Calculate date range
        start_date = date.today()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Get all temples (or handle standalone mode)
        temples = db.query(Temple).all()
        
        if not temples:
            # Standalone mode - no temples, use None for temple_id
            print("No temples found. Running in standalone mode...")
            run_pre_calculation(db, None, start_date, end_date)
        else:
            # Multi-tenant mode - process each temple
            print(f"Found {len(temples)} temple(s). Processing each...")
            for temple in temples:
                print(f"\nProcessing temple: {temple.name} (ID: {temple.id})")
                run_pre_calculation(db, temple.id, start_date, end_date)
        
        print("\n[OK] Pre-calculation completed successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Error during pre-calculation: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def run_pre_calculation(db, temple_id, start_date, end_date):
    """Run pre-calculation for a specific temple"""
    
    # Get temple's panchang settings for location
    lat = 12.9716  # Default: Bangalore
    lon = 77.5946
    city = "Bengaluru"
    
    if temple_id:
        panchang_settings = db.query(PanchangDisplaySettings).filter(
            PanchangDisplaySettings.temple_id == temple_id
        ).first()
        
        if panchang_settings and panchang_settings.latitude and panchang_settings.longitude:
            lat = float(panchang_settings.latitude)
            lon = float(panchang_settings.longitude)
            city = panchang_settings.city_name or "Bengaluru"
            print(f"  Using location: {city} ({lat}, {lon})")
        else:
            print(f"  No panchang settings found. Using default location: {city}")
    else:
        print(f"  Using default location: {city}")
    
    # Initialize service and pre-calculate
    service = ReadyReckonerService(db)
    result = service.pre_calculate_dates(
        temple_id=temple_id,
        start_date=start_date,
        end_date=end_date,
        lat=lat,
        lon=lon,
        city=city
    )
    
    print(f"  ✅ Created {result['events_created']} events")
    return result


if __name__ == "__main__":
    main()

