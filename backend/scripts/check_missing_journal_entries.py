"""
Diagnostic script to find donations/sevas without journal entries
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.donation import Donation
from app.models.seva import SevaBooking
from app.models.accounting import JournalEntry, TransactionType, JournalEntryStatus


def check_missing_entries(db: Session):
    """Check for donations/sevas without journal entries"""

    print("=" * 60)
    print("CHECKING MISSING JOURNAL ENTRIES")
    print("=" * 60)

    # Check donations
    print("\n1. DONATIONS CHECK")
    print("-" * 60)
    donations = db.query(Donation).filter(Donation.is_cancelled == False).all()
    print(f"Total donations: {len(donations)}")

    total_donation_amount = sum(d.amount for d in donations)
    print(f"Total donation amount: ₹{total_donation_amount:,.2f}")

    donations_with_entries = []
    donations_without_entries = []

    for donation in donations:
        entry = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.reference_type == TransactionType.DONATION,
                JournalEntry.reference_id == donation.id,
            )
            .first()
        )

        if entry:
            donations_with_entries.append(donation)
            if entry.status != JournalEntryStatus.POSTED:
                print(
                    f"  ⚠ Donation {donation.receipt_number} has entry but status is {entry.status}"
                )
        else:
            donations_without_entries.append(donation)

    accounted_amount = sum(d.amount for d in donations_with_entries)
    missing_amount = sum(d.amount for d in donations_without_entries)

    print(f"\nDonations WITH journal entries: {len(donations_with_entries)}")
    print(f"  Accounted amount: ₹{accounted_amount:,.2f}")
    print(f"\nDonations WITHOUT journal entries: {len(donations_without_entries)}")
    print(f"  Missing amount: ₹{missing_amount:,.2f}")

    if donations_without_entries:
        print(f"\nMissing journal entries for:")
        for d in donations_without_entries[:20]:  # Show first 20
            print(
                f"  - {d.receipt_number}: ₹{d.amount} on {d.donation_date} (Category: {d.category.name if d.category else 'Unknown'})"
            )
        if len(donations_without_entries) > 20:
            print(f"  ... and {len(donations_without_entries) - 20} more")

    # Check seva bookings
    print("\n2. SEVA BOOKINGS CHECK")
    print("-" * 60)
    bookings = db.query(SevaBooking).filter(SevaBooking.status != "cancelled").all()
    print(f"Total seva bookings: {len(bookings)}")

    if bookings:
        total_booking_amount = sum(b.amount_paid for b in bookings)
        print(f"Total booking amount: ₹{total_booking_amount:,.2f}")

        bookings_with_entries = []
        bookings_without_entries = []

        for booking in bookings:
            entry = (
                db.query(JournalEntry)
                .filter(
                    JournalEntry.reference_type == TransactionType.SEVA,
                    JournalEntry.reference_id == booking.id,
                )
                .first()
            )

            if entry:
                bookings_with_entries.append(booking)
            else:
                bookings_without_entries.append(booking)

        accounted_booking_amount = sum(b.amount_paid for b in bookings_with_entries)
        missing_booking_amount = sum(b.amount_paid for b in bookings_without_entries)

        print(f"\nBookings WITH journal entries: {len(bookings_with_entries)}")
        print(f"  Accounted amount: ₹{accounted_booking_amount:,.2f}")
        print(f"\nBookings WITHOUT journal entries: {len(bookings_without_entries)}")
        print(f"  Missing amount: ₹{missing_booking_amount:,.2f}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total donations: ₹{total_donation_amount:,.2f}")
    print(f"Accounted: ₹{accounted_amount:,.2f}")
    print(f"Missing: ₹{missing_amount:,.2f}")
    print(f"\nMissing percentage: {(missing_amount/total_donation_amount*100):.1f}%")

    if missing_amount > 0:
        print("\n⚠ ACTION REQUIRED:")
        print(
            f"  Run backfill script to create {len(donations_without_entries)} missing journal entries:"
        )
        print("  python -m scripts.backfill_donation_journal_entries")

    return {
        "donations_without_entries": donations_without_entries,
        "missing_amount": missing_amount,
    }


def main():
    db = SessionLocal()
    try:
        result = check_missing_entries(db)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
