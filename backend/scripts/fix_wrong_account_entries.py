"""
Script to fix journal entries that are using wrong accounts (payment-mode accounts instead of category accounts)

This will:
1. Find journal entries for donations that are using payment-mode accounts (4102, 4103, 4104)
2. Update them to use category-linked accounts instead
3. Show what was fixed
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.donation import Donation, DonationCategory
from app.models.accounting import Account, JournalEntry, JournalLine, TransactionType

def fix_wrong_account_entries(db: Session, temple_id: int = None):
    """Fix journal entries using wrong accounts"""
    
    print("=" * 60)
    print("FIXING WRONG ACCOUNT ENTRIES")
    print("=" * 60)
    
    # Find journal entries for donations
    query = db.query(JournalEntry).filter(
        JournalEntry.reference_type == TransactionType.DONATION
    )
    
    if temple_id:
        query = query.filter(JournalEntry.temple_id == temple_id)
    
    entries = query.all()
    
    print(f"\nFound {len(entries)} donation journal entries")
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for entry in entries:
        try:
            # Get the donation
            donation = db.query(Donation).filter(Donation.id == entry.reference_id).first()
            if not donation or not donation.category:
                skipped_count += 1
                continue
            
            # Check if category has linked account
            if not donation.category.account_id:
                print(f"  ⚠ Entry {entry.entry_number}: Category '{donation.category.name}' not linked to account - SKIP")
                skipped_count += 1
                continue
            
            # Get the correct account
            correct_account = db.query(Account).filter(Account.id == donation.category.account_id).first()
            if not correct_account:
                print(f"  ✗ Entry {entry.entry_number}: Category account {donation.category.account_id} not found - SKIP")
                skipped_count += 1
                continue
            
            # Get journal lines for this entry
            credit_line = db.query(JournalLine).filter(
                JournalLine.journal_entry_id == entry.id,
                JournalLine.credit_amount > 0
            ).first()
            
            if not credit_line:
                skipped_count += 1
                continue
            
            # Check if it's using wrong account (payment-mode account)
            current_account = db.query(Account).filter(Account.id == credit_line.account_id).first()
            if not current_account:
                skipped_count += 1
                continue
            
            # Check if account code is in payment-mode accounts (4102, 4103, 4104)
            wrong_account_codes = ['4102', '4103', '4104']
            if current_account.account_code in wrong_account_codes:
                # Check if correct account is different
                if current_account.id != correct_account.id:
                    print(f"\n  Fixing entry {entry.entry_number}:")
                    print(f"    Donation: {donation.receipt_number} ({donation.category.name})")
                    print(f"    Current account: {current_account.account_code} - {current_account.account_name}")
                    print(f"    Correct account: {correct_account.account_code} - {correct_account.account_name}")
                    
                    # Update the credit line to use correct account
                    credit_line.account_id = correct_account.id
                    db.commit()
                    
                    fixed_count += 1
                    print(f"    ✓ Fixed!")
                else:
                    skipped_count += 1
            else:
                # Already using correct account or category account
                skipped_count += 1
                
        except Exception as e:
            print(f"  ✗ Error fixing entry {entry.entry_number}: {str(e)}")
            error_count += 1
            db.rollback()
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Fixed: {fixed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")
    print(f"{'='*60}")


def main():
    db = SessionLocal()
    try:
        # Auto-detect temple
        from app.models.temple import Temple
        temples = db.query(Temple).all()
        
        temple_id = None
        if len(temples) == 1:
            temple_id = temples[0].id
            print(f"Detected temple: {temples[0].name} (ID: {temple_id})")
        
        fix_wrong_account_entries(db, temple_id)
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()







