"""
Backfill script to create journal entries for existing donations
that don't have accounting entries yet.

Usage:
    python -m scripts.backfill_donation_journal_entries
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import SessionLocal, engine

# Import all models to ensure relationships are properly configured
# This must be done before querying any models with relationships
from app.models.temple import Temple
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.user import User
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine, JournalEntryStatus, TransactionType

from app.api.donations import post_donation_to_accounting


def backfill_donations(db: Session, temple_id: int = None):
    """
    Backfill journal entries for donations that don't have them
    """
    # Find donations without journal entries
    query = db.query(Donation)
    
    if temple_id:
        query = query.filter(Donation.temple_id == temple_id)
    
    donations = query.all()
    
    print(f"Found {len(donations)} total donations")
    
    # Find donations without journal entries
    donations_without_entries = []
    for donation in donations:
        existing_entry = db.query(JournalEntry).filter(
            JournalEntry.reference_type == TransactionType.DONATION,
            JournalEntry.reference_id == donation.id
        ).first()
        
        if not existing_entry:
            donations_without_entries.append(donation)
    
    print(f"Found {len(donations_without_entries)} donations without journal entries")
    
    if not donations_without_entries:
        print("All donations already have journal entries!")
        return
    
    # Process each donation
    success_count = 0
    error_count = 0
    
    for donation in donations_without_entries:
        try:
            print(f"\nProcessing donation {donation.receipt_number} (ID: {donation.id})...")
            print(f"  Amount: ₹{donation.amount}")
            print(f"  Date: {donation.donation_date}")
            print(f"  Payment mode: {donation.payment_mode}")
            print(f"  Category: {donation.category.name if donation.category else 'Unknown'}")
            
            # Use the same function from the API
            journal_entry = post_donation_to_accounting(db, donation, donation.temple_id)
            
            if journal_entry:
                db.commit()
                print(f"  ✓ Created journal entry: {journal_entry.entry_number}")
                success_count += 1
            else:
                print(f"  ✗ Failed to create journal entry (check accounts)")
                error_count += 1
                db.rollback()
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            error_count += 1
            db.rollback()
    
    print(f"\n{'='*60}")
    print(f"Backfill Summary:")
    print(f"  Total donations processed: {len(donations_without_entries)}")
    print(f"  Successfully created: {success_count}")
    print(f"  Failed: {error_count}")
    print(f"{'='*60}")


def main():
    """Main entry point"""
    db = SessionLocal()
    
    try:
        # Auto-detect temple for standalone installation
        temples = db.query(Temple).all()
        
        temple_id = None
        if len(temples) == 1:
            # Standalone installation - use the single temple
            temple_id = temples[0].id
            print(f"Detected standalone installation - Temple: {temples[0].name} (ID: {temple_id})")
        elif len(temples) > 1:
            print(f"Multiple temples found ({len(temples)}). Processing all temples.")
        else:
            print("WARNING: No temples found in database!")
            return
        
        print("Starting donation journal entry backfill...")
        print(f"{'='*60}\n")
        
        backfill_donations(db, temple_id)
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

