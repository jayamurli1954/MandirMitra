"""
Backfill script to create journal entries for existing seva bookings
that don't have accounting entries yet.

Usage:
    python -m scripts.backfill_seva_journal_entries
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
from app.models.accounting import (
    Account,
    JournalEntry,
    JournalLine,
    JournalEntryStatus,
    TransactionType,
)

from app.api.sevas import post_seva_to_accounting


def backfill_seva_bookings(db: Session, temple_id: int = None):
    """
    Backfill journal entries for seva bookings that don't have them
    """
    # Find seva bookings without journal entries
    # Note: Seva model doesn't have temple_id, so we'll get it from user or devotee
    query = db.query(SevaBooking)

    # Don't filter by temple_id here since Seva doesn't have it
    # We'll determine temple_id per booking from user or devotee
    bookings = query.all()

    print(f"Found {len(bookings)} total seva bookings")

    # Find bookings without journal entries
    bookings_without_entries = []
    for booking in bookings:
        existing_entry = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.reference_type == TransactionType.SEVA,
                JournalEntry.reference_id == booking.id,
            )
            .first()
        )

        if not existing_entry:
            bookings_without_entries.append(booking)

    print(f"Found {len(bookings_without_entries)} seva bookings without journal entries")

    if not bookings_without_entries:
        print("All seva bookings already have journal entries!")
        return

    # Process each booking
    success_count = 0
    error_count = 0

    for booking in bookings_without_entries:
        try:
            print(
                f"\nProcessing seva booking {booking.receipt_number or f'ID:{booking.id}'} (ID: {booking.id})..."
            )
            print(f"  Amount: ₹{booking.amount_paid}")
            print(f"  Date: {booking.booking_date}")
            print(f"  Payment method: {booking.payment_method or 'Unknown'}")
            print(f"  Seva: {booking.seva.name_english if booking.seva else 'Unknown'}")

            # Get temple_id from user who created the booking
            temple_id_for_booking = None
            if booking.user_id:
                from app.models.user import User

                user = db.query(User).filter(User.id == booking.user_id).first()
                if user and user.temple_id:
                    temple_id_for_booking = user.temple_id

            # Fallback: try to get from current_user context if available
            # For backfill, we'll use the first temple if we can't determine
            if not temple_id_for_booking:
                first_temple = db.query(Temple).first()
                if first_temple:
                    temple_id_for_booking = first_temple.id
                    print(f"  ⚠ Using default temple_id: {temple_id_for_booking}")

            if not temple_id_for_booking:
                print(f"  ✗ Cannot determine temple_id for booking")
                error_count += 1
                continue

            # Use the same function from the API
            journal_entry = post_seva_to_accounting(db, booking, temple_id_for_booking)

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
            import traceback

            traceback.print_exc()
            error_count += 1
            db.rollback()

    print(f"\n{'='*60}")
    print(f"Backfill Summary:")
    print(f"  Total bookings processed: {len(bookings_without_entries)}")
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

        print("Starting seva booking journal entry backfill...")
        print(f"{'='*60}\n")

        backfill_seva_bookings(db, temple_id)

    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
