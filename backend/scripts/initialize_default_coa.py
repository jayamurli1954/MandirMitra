"""
Initialize Default Chart of Accounts for a Temple
Creates all default accounts from the comprehensive COA structure
"""

import sys
import os

# Fix Windows encoding for emoji characters
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.accounting import Account

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

from app.data.default_coa import DefaultCOA


def initialize_coa_for_temple(db: Session, temple_id: int, overwrite_existing: bool = False):
    """
    Initialize default COA for a temple
    
    Args:
        db: Database session
        temple_id: Temple ID to initialize COA for
        overwrite_existing: If True, update existing accounts. If False, skip existing codes.
    
    Returns:
        tuple: (created_count, updated_count, skipped_count, errors)
    """
    default_accounts = DefaultCOA.get_default_accounts()
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    errors = []
    
    print(f"\n{'=' * 80}")
    print(f"Initializing Default COA for Temple ID: {temple_id}")
    print(f"{'=' * 80}\n")
    
    for account_data in default_accounts:
        account_code = account_data['account_code']
        account_name = account_data['account_name']
        
        # Check if account already exists
        existing_account = db.query(Account).filter(
            Account.account_code == account_code,
            Account.temple_id == temple_id
        ).first()
        
        if existing_account:
            if overwrite_existing:
                # Update existing account
                for key, value in account_data.items():
                    if key != 'temple_id':  # Don't update temple_id
                        setattr(existing_account, key, value)
                updated_count += 1
                print(f"  ✓ Updated: {account_code} - {account_name}")
            else:
                # Skip existing account
                skipped_count += 1
                print(f"  ⊘ Skipped (exists): {account_code} - {account_name}")
        else:
            # Create new account
            try:
                new_account = Account(
                    temple_id=temple_id,
                    **account_data
                )
                db.add(new_account)
                created_count += 1
                print(f"  + Created: {account_code} - {account_name}")
            except Exception as e:
                error_msg = f"  ✗ Error creating {account_code} - {account_name}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
    
    # Commit all changes
    try:
        db.commit()
        print(f"\nSUCCESS: COA Initialization Complete:")
        print(f"   Created: {created_count}")
        print(f"   Updated: {updated_count}")
        print(f"   Skipped: {skipped_count}")
        if errors:
            print(f"   Errors: {len(errors)}")
        print()
    except Exception as e:
        db.rollback()
        print(f"\nERROR: Error during initialization: {str(e)}")
        raise
    
    return created_count, updated_count, skipped_count, errors


def initialize_all_temples(db: Session, overwrite_existing: bool = False):
    """
    Initialize COA for all temples in the database
    
    Args:
        db: Database session
        overwrite_existing: If True, update existing accounts. If False, skip existing codes.
    """
    from app.models.temple import Temple
    
    temples = db.query(Temple).all()
    
    if not temples:
        print("No temples found in database.")
        return
    
    print(f"\n{'=' * 80}")
    print(f"Initializing Default COA for {len(temples)} Temple(s)")
    print(f"{'=' * 80}\n")
    
    total_created = 0
    total_updated = 0
    total_skipped = 0
    
    for temple in temples:
        print(f"\n--- Temple: {temple.name} (ID: {temple.id}) ---")
        created, updated, skipped, errors = initialize_coa_for_temple(
            db, temple.id, overwrite_existing
        )
        total_created += created
        total_updated += updated
        total_skipped += skipped
    
    print(f"\n{'=' * 80}")
    print(f"TOTAL SUMMARY:")
    print(f"   Created: {total_created}")
    print(f"   Updated: {total_updated}")
    print(f"   Skipped: {total_skipped}")
    print(f"{'=' * 80}\n")


def main():
    """Main initialization function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize default Chart of Accounts')
    parser.add_argument('--temple-id', type=int, help='Initialize for specific temple ID (if not provided, initializes for all temples)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing accounts if they exist')
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        if args.temple_id:
            initialize_coa_for_temple(db, args.temple_id, args.overwrite)
        else:
            initialize_all_temples(db, args.overwrite)
            
    except Exception as e:
        print(f"\nERROR: Initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

