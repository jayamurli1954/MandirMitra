"""
Migration Script: Update existing account codes from old format to new 5-digit format
This script updates account codes in the database without affecting journal entries
(since they use account_id foreign keys, not account codes)
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


def migrate_account_codes(db: Session, dry_run: bool = False):
    """
    Migrate existing account codes to new 5-digit format
    
    Args:
        db: Database session
        dry_run: If True, only shows what would be changed without actually changing
    """
    code_mapping = DefaultCOA.get_code_mapping()
    
    print(f"\n{'=' * 80}")
    print(f"COA Code Migration {'(DRY RUN - No Changes)' if dry_run else '(LIVE - Will Update Database)'}")
    print(f"{'=' * 80}\n")
    
    changes = []
    errors = []
    
    # Find all accounts that need migration
    for old_code, new_code in code_mapping.items():
        accounts = db.query(Account).filter(Account.account_code == old_code).all()
        
        if accounts:
            for account in accounts:
                # Check if new code already exists
                existing = db.query(Account).filter(
                    Account.account_code == new_code,
                    Account.temple_id == account.temple_id
                ).first()
                
                if existing and existing.id != account.id:
                    error_msg = f"WARNING: Cannot migrate {old_code} -> {new_code}: Code {new_code} already exists for temple {account.temple_id}"
                    errors.append(error_msg)
                    print(error_msg)
                else:
                    changes.append({
                        'account_id': account.id,
                        'account_name': account.account_name,
                        'temple_id': account.temple_id,
                        'old_code': old_code,
                        'new_code': new_code
                    })
    
    # Show changes
    if changes:
        print(f"Found {len(changes)} account(s) to migrate:\n")
        for change in changes:
            print(f"  [{change['temple_id']}] {change['account_name']}")
            print(f"    {change['old_code']} -> {change['new_code']}\n")
    else:
        print("No accounts found that need migration.\n")
    
    # Show errors
    if errors:
        print(f"\n⚠️  {len(errors)} error(s) found:")
        for error in errors:
            print(f"  {error}\n")
    
    # Apply changes - update one at a time to avoid unique constraint violations
    if not dry_run and changes:
        print(f"\nApplying {len(changes)} migration(s)...")
        successful = 0
        failed = 0
        
        for change in changes:
            account = db.query(Account).filter(Account.id == change['account_id']).first()
            if account:
                # Check if new code already exists (for a different account)
                existing = db.query(Account).filter(
                    Account.account_code == change['new_code'],
                    Account.temple_id == account.temple_id,
                    Account.id != account.id
                ).first()
                
                if existing:
                    print(f"  SKIP: {change['account_name']} ({change['old_code']} -> {change['new_code']}) - Code {change['new_code']} already exists as '{existing.account_name}'")
                    failed += 1
                else:
                    # Temporarily set to a unique code to avoid conflicts during batch update
                    # Use a temporary code format: old_code + '_temp'
                    temp_code = f"{change['old_code']}_temp_{account.id}"
                    account.account_code = temp_code
                    db.flush()  # Flush to apply temp code
                    
                    # Now set to final code
                    account.account_code = change['new_code']
                    print(f"  + Updated {change['account_name']} ({change['old_code']} -> {change['new_code']})")
                    successful += 1
                    db.flush()  # Flush each change
        
        try:
            db.commit()
            print(f"\nSUCCESS: Successfully migrated {successful} account(s)")
            if failed > 0:
                print(f"WARNING: Skipped {failed} account(s) due to duplicate codes")
        except Exception as e:
            db.rollback()
            print(f"\nERROR: Error during migration: {str(e)}")
            raise
    elif dry_run:
        if changes:
            print(f"\nNOTE: This is a DRY RUN. To apply changes, run without --dry-run flag")
    
    return len(changes), len(errors)


def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate COA account codes to 5-digit format')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without actually changing')
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        changes, errors = migrate_account_codes(db, dry_run=args.dry_run)
        
        if args.dry_run:
            print(f"\n{'=' * 80}")
            print(f"DRY RUN COMPLETE: {changes} account(s) would be migrated, {errors} error(s) found")
            print(f"{'=' * 80}\n")
            print("To apply changes, run: python scripts/migrate_coa_codes.py")
        else:
            print(f"\n{'=' * 80}")
            print(f"MIGRATION COMPLETE: {changes} account(s) migrated, {errors} error(s) found")
            print(f"{'=' * 80}\n")
            
    except Exception as e:
        print(f"\nERROR: Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

