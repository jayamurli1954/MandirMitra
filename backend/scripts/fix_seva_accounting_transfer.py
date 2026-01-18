"""
Script to transfer seva income from account 4000 to 3002
This will:
1. Find journal entries that credited account 4000 for seva bookings
2. Update them to credit account 3002 instead
3. Create accounting entries for bookings that don't have journal entries yet
"""
import os
import sys
import inspect
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Add the backend directory to the Python path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.core.config import settings
# Import main app to ensure all models are registered
import app.main
from app.models.seva import SevaBooking
from app.models.accounting import JournalEntry, JournalLine, TransactionType, Account
from app.api.sevas import post_seva_to_accounting

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def fix_seva_accounting():
    """
    Fix seva accounting:
    1. Transfer entries from account 4000 to 3002
    2. Create missing accounting entries for bookings
    """
    print("Fixing seva accounting entries...")
    db: Session = next(get_db())
    
    try:
        # Step 1: Find and update journal entries that credited account 4000 for seva bookings
        account_4000 = db.query(Account).filter(Account.account_code == D000').first()
        account_3002 = db.query(Account).filter(Account.account_code == '3002').first()
        
        if not account_3002:
            print("ERROR: Account 3002 (Seva Income) not found in Chart of Accounts!")
            print("Please create account 3002 - Seva Income before running this script.")
            return
        
        if account_4000:
            # Find journal lines that credited account 4000 for seva bookings
            journal_entries = db.query(JournalEntry).filter(
                JournalEntry.reference_type == TransactionType.SEVA
            ).all()
            
            updated_count = 0
            for je in journal_entries:
                # Check if this journal entry has a credit line to account 4000
                credit_line = db.query(JournalLine).filter(
                    JournalLine.journal_entry_id == je.id,
                    JournalLine.account_id == account_4000.id,
                    JournalLine.credit_amount > 0
                ).first()
                
                if credit_line:
                    print(f"Found journal entry {je.entry_number} crediting account 4000 (Rs.{credit_line.credit_amount})")
                    # Update to credit account 3002 instead
                    credit_line.account_id = account_3002.id
                    updated_count += 1
                    print(f"  Updated to credit account 3002 instead")
            
            if updated_count > 0:
                db.commit()
                print(f"\nUpdated {updated_count} journal entry/entries from account 4000 to 3002")
            else:
                print("\nNo journal entries found crediting account 4000 for seva bookings")
        else:
            print("Account 4000 not found - skipping transfer step")
        
        # Step 2: Create accounting entries for bookings without journal entries
        print("\n" + "="*60)
        print("Creating accounting entries for bookings without journal entries...")
        
        all_bookings = db.query(SevaBooking).all()
        bookings_to_account = []
        
        for booking in all_bookings:
            # Check if this booking has a journal entry
            journal_entry = db.query(JournalEntry).filter(
                JournalEntry.reference_type == TransactionType.SEVA,
                JournalEntry.reference_id == booking.id
            ).first()
            
            if not journal_entry:
                bookings_to_account.append(booking)
                print(f"Found booking without accounting entry: ID={booking.id}, Receipt={booking.receipt_number}, Amount=Rs.{booking.amount_paid}")
        
        if not bookings_to_account:
            print("No bookings found that need accounting entries.")
        else:
            print(f"\nFound {len(bookings_to_account)} booking(s) that need accounting entries.")
            
            # Process each booking
            success_count = 0
            error_count = 0
            
            for booking in bookings_to_account:
                try:
                    # Get temple_id from booking
                    temple_id = None
                    if booking.seva and hasattr(booking.seva, 'temple_id'):
                        temple_id = booking.seva.temple_id
                    elif booking.devotee and hasattr(booking.devotee, 'temple_id'):
                        temple_id = booking.devotee.temple_id
                    elif booking.user and hasattr(booking.user, 'temple_id'):
                        temple_id = booking.user.temple_id
                    else:
                        print(f"  Skipping booking ID {booking.id}: No temple_id found")
                        error_count += 1
                        continue
                    
                    print(f"\n  Processing booking ID {booking.id} (Receipt: {booking.receipt_number})...")
                    
                    # Create accounting entry using the same function as new bookings
                    journal_entry = post_seva_to_accounting(db, booking, temple_id)
                    
                    if journal_entry:
                        db.commit()
                        print(f"  Successfully created accounting entry for booking ID {booking.id}")
                        success_count += 1
                    else:
                        print(f"  Failed to create accounting entry for booking ID {booking.id}")
                        error_count += 1
                        db.rollback()
                        
                except Exception as e:
                    db.rollback()
                    print(f"  Error processing booking ID {booking.id}: {str(e)}")
                    error_count += 1
                    import traceback
                    traceback.print_exc()
            
            print(f"\n{'='*60}")
            print(f"Summary:")
            print(f"  Successfully processed: {success_count}")
            print(f"  Errors: {error_count}")
            print(f"{'='*60}")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    print("\nDone!")

if __name__ == "__main__":
    fix_seva_accounting()

