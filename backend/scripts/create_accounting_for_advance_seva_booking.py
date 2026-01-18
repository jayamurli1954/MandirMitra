"""
Script to create accounting entry for an existing advance seva booking
Use this if an advance booking was created before account 3003 existed
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import date
from app.core.database import SessionLocal, init_db
from app.models.seva import SevaBooking
from app.models.accounting import Account, JournalEntry, TransactionType
from app.api.sevas import post_seva_to_accounting

# Import all models
from app.models.user import User
from app.models.devotee import Devotee
from app.models.temple import Temple
from app.models.accounting import JournalLine

def create_accounting_for_booking(booking_id=None, receipt_number=None):
    db = SessionLocal()
    try:
        # Find the booking
        if booking_id:
            booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
        elif receipt_number:
            booking = db.query(SevaBooking).filter(SevaBooking.receipt_number == receipt_number).first()
        else:
            print("Please provide either booking_id or receipt_number")
            return
        
        if not booking:
            print(f"Booking not found (ID: {booking_id}, Receipt: {receipt_number})")
            return
        
        # Check if accounting entry already exists
        existing_entry = db.query(JournalEntry).filter(
            JournalEntry.reference_type == TransactionType.SEVA,
            JournalEntry.reference_id == booking.id
        ).first()
        
        if existing_entry:
            print(f"Accounting entry already exists for booking {booking.receipt_number}")
            print(f"  Entry Number: {existing_entry.entry_number}")
            print(f"  Entry Date: {existing_entry.entry_date}")
            return
        
        # Get temple_id
        temple_id = None
        if booking.devotee and hasattr(booking.devotee, 'temple_id'):
            temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, 'temple_id'):
            temple_id = booking.user.temple_id
        
        if not temple_id:
            print(f"Could not determine temple_id for booking {booking.receipt_number}")
            return
        
        # Check if account 3003 exists
        account_3003 = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == '3003'
        ).first()
        
        if not account_3003:
            print(f"Account 3003 (Advance Seva Booking) not found for temple {temple_id}")
            print("Please run create_advance_seva_account.py first")
            return
        
        print(f"Creating accounting entry for booking {booking.receipt_number}")
        print(f"  Booking Date: {booking.booking_date}")
        print(f"  Amount: Rs. {booking.amount_paid}")
        print(f"  Is Advance: {booking.booking_date > date.today()}")
        
        # Create accounting entry
        journal_entry = post_seva_to_accounting(db, booking, temple_id)
        db.commit()
        
        print(f"\n[OK] Accounting entry created successfully!")
        print(f"  Entry Number: {journal_entry.entry_number}")
        print(f"  Entry Date: {journal_entry.entry_date}")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # You can specify booking ID or receipt number
    # For the user's booking: receipt_number should be something like SEV0000XX
    # Let's find the booking for 22-12-2025 with Rathotsava Seve
    
    import sys
    if len(sys.argv) > 1:
        # Try to parse as booking ID
        try:
            booking_id = int(sys.argv[1])
            create_accounting_for_booking(booking_id=booking_id)
        except ValueError:
            # Treat as receipt number
            receipt_number = sys.argv[1]
            create_accounting_for_booking(receipt_number=receipt_number)
    else:
        # Find the most recent advance booking for Rathotsava
        db = SessionLocal()
        from app.models.seva import Seva
        try:
            # Find Rathotsava seva
            rathotsava = db.query(Seva).filter(
                Seva.name_english.ilike('%rathotsava%')
            ).first()
            
            if rathotsava:
                # Find booking for 22-12-2025
                booking = db.query(SevaBooking).filter(
                    SevaBooking.seva_id == rathotsava.id,
                    SevaBooking.booking_date == date(2025, 12, 22)
                ).order_by(SevaBooking.id.desc()).first()
                
                if booking:
                    db.close()
                    create_accounting_for_booking(booking_id=booking.id)
                else:
                    print("No booking found for Rathotsava on 22-12-2025")
            else:
                print("Rathotsava Seva not found")
        finally:
            db.close()



















