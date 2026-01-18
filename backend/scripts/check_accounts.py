"""
Script to check if required accounts exist for donations to work properly.

Usage:
    python -m scripts.check_accounts [temple_id]
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal

# Import all models to ensure relationships are properly configured
from app.models.temple import Temple
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.user import User
from app.models.accounting import Account, JournalEntry, JournalLine


def check_required_accounts(db: Session, temple_id: int = None):
    """
    Check if required accounts exist for donations
    """
    required_accounts = {
        A101': 'Cash in Hand - Counter',
        A102': 'Cash in Hand - Hundi',
        A110': 'Bank - SBI Current Account',
        '4101': 'General Donation Income',
        '4102': 'Cash Donation Income',
        '4103': 'Online/UPI Donation Income',
        '4104': 'Hundi Collection Income',
        '4208': 'Special Pooja Income (Default Seva Income)',
    }
    
    if temple_id:
        temples = [db.query(Temple).filter(Temple.id == temple_id).first()]
    else:
        temples = db.query(Temple).all()
    
    if not temples:
        print("No temples found!")
        return
    
    for temple in temples:
        print(f"\n{'='*60}")
        print(f"Temple: {temple.name} (ID: {temple.id})")
        print(f"{'='*60}")
        
        missing_accounts = []
        existing_accounts = []
        
        for account_code, account_name in required_accounts.items():
            account = db.query(Account).filter(
                Account.temple_id == temple.id,
                Account.account_code == account_code
            ).first()
            
            if account:
                status = "✓ EXISTS"
                existing_accounts.append((account_code, account_name, account))
            else:
                status = "✗ MISSING"
                missing_accounts.append((account_code, account_name))
            
            print(f"  {status} - {account_code}: {account_name}")
        
        if missing_accounts:
            print(f"\n⚠️  Missing {len(missing_accounts)} required accounts:")
            for code, name in missing_accounts:
                print(f"    - {code}: {name}")
            print("\n  Please create these accounts in the Chart of Accounts.")
        else:
            print(f"\n✓ All required accounts exist!")
        
        # Check donation categories and their linked accounts
        print(f"\n  Checking donation categories...")
        from app.models.donation import DonationCategory
        categories = db.query(DonationCategory).filter(
            DonationCategory.temple_id == temple.id
        ).all()
        
        if categories:
            for cat in categories:
                if cat.account_id:
                    account = db.query(Account).filter(Account.id == cat.account_id).first()
                    if account:
                        print(f"    ✓ {cat.name} -> {account.account_code}: {account.account_name}")
                    else:
                        print(f"    ✗ {cat.name} -> Linked account (ID: {cat.account_id}) NOT FOUND")
                else:
                    print(f"    ⚠ {cat.name} -> No account linked (will use default)")
        else:
            print(f"    No donation categories found")
        
        # Check sevas and their linked accounts
        print(f"\n  Checking sevas...")
        from app.models.seva import Seva
        sevas = db.query(Seva).all()  # Sevas might not have temple_id, so get all
        
        if sevas:
            for seva in sevas:
                if seva.account_id:
                    account = db.query(Account).filter(Account.id == seva.account_id).first()
                    if account:
                        print(f"    ✓ {seva.name_english} -> {account.account_code}: {account.account_name}")
                    else:
                        print(f"    ✗ {seva.name_english} -> Linked account (ID: {seva.account_id}) NOT FOUND")
                else:
                    print(f"    ⚠ {seva.name_english} -> No account linked (will use default 4208)")
        else:
            print(f"    No sevas found")


def main():
    """Main entry point"""
    db = SessionLocal()
    
    try:
        temple_id = None
        if len(sys.argv) > 1:
            try:
                temple_id = int(sys.argv[1])
            except ValueError:
                print(f"Invalid temple_id: {sys.argv[1]}")
                return
        else:
            # Auto-detect temple for standalone installation
            temples = db.query(Temple).all()
            if len(temples) == 1:
                temple_id = temples[0].id
                print(f"Detected standalone installation - Temple: {temples[0].name} (ID: {temple_id})")
            elif len(temples) > 1:
                print(f"Multiple temples found ({len(temples)}). Checking all temples.")
            else:
                print("WARNING: No temples found in database!")
                return
        
        print("Checking required accounts for donations and sevas...")
        print(f"{'='*60}\n")
        check_required_accounts(db, temple_id)
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

