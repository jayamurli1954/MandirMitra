"""
Script to create accounting entries for existing seva bookings that don't have journal entries.
This script will find bookings without accounting entries and create them.
"""
import os
import sys
import inspect
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session

# Add the backend directory to the Python path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.core.config import settings
from app.models.seva import SevaBooking
from app.models.accounting import JournalEntry, JournalLine
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

def create_accounting_for_existing_bookings():
    """
    Find seva bookings without journal entries and create accounting entries for them.
    Specifically target receipts: SEV202512180951133 and SEV202512180953353
    """
    print("Creating accounting entries for existing seva bookings...")
    db: Session = next(get_db())
    
    try:
        # Find bookings that need accounting entries
        # First, get all bookings
        all_bookings = db.query(SevaBooking).all()
        
        bookings_to_account = []
        
        from app.models.accounting import TransactionType
        
        for booking in all_bookings:
            # Check if this booking has a journal entry
            journal_entry = db.query(JournalEntry).filter(
                JournalEntry.reference_type == TransactionType.SEVA,
                JournalEntry.reference_id == booking.id
            ).first()
            
            if not journal_entry:
                bookings_to_account.append(booking)
                print(f"Found booking without accounting entry: ID={booking.id}, Receipt={booking.receipt_number}, Amount=₹{booking.amount_paid}")
        
        if not bookings_to_account:
            print("No bookings found that need accounting entries.")
            return
        
        print(f"\nFound {len(bookings_to_account)} booking(s) that need accounting entries.")
        
        # Process each booking
        success_count = 0
        error_count = 0
        
        for booking in bookings_to_account:
            try:
                # Get temple_id from booking
                temple_id = None
                if booking.seva and booking.seva.temple_id:
                    temple_id = booking.seva.temple_id
                elif booking.devotee and booking.devotee.temple_id:
                    temple_id = booking.devotee.temple_id
                else:
                    print(f"  ⚠️  Skipping booking ID {booking.id}: No temple_id found")
                    error_count += 1
                    continue
                
                print(f"\n  Processing booking ID {booking.id} (Receipt: {booking.receipt_number})...")
                
                # Create accounting entry using the same function as new bookings
                journal_entry = post_seva_to_accounting(db, booking, temple_id)
                
                if journal_entry:
                    db.commit()
                    print(f"  ✅ Successfully created accounting entry for booking ID {booking.id}")
                    success_count += 1
                else:
                    print(f"  ❌ Failed to create accounting entry for booking ID {booking.id}")
                    error_count += 1
                    db.rollback()
                    
            except Exception as e:
                db.rollback()
                print(f"  ❌ Error processing booking ID {booking.id}: {str(e)}")
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
    
    print("Done!")

if __name__ == "__main__":
    create_accounting_for_existing_bookings()

