"""
Script to find donations and seva bookings without journal entries
This helps identify the ₹8,800 gap between dashboard and trial balance
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.donation import Donation
from app.models.seva import SevaBooking
from app.models.temple import Temple

def find_missing_entries(db: Session, temple_id: int = None):
    """
    Find donations and seva bookings without journal entries
    """
    print("=" * 80)
    print("MISSING JOURNAL ENTRIES REPORT")
    print("=" * 80)
    
    # Filter by temple if provided
    donation_filter = [Donation.is_cancelled == False]
    seva_filter = [SevaBooking.status != "cancelled"]
    
    if temple_id:
        donation_filter.append(Donation.temple_id == temple_id)
        seva_filter.append(SevaBooking.temple_id == temple_id)
    
    # Find donations without journal entries
    donations_without_je = db.query(Donation).filter(
        *donation_filter,
        Donation.journal_entry_id.is_(None)
    ).all()
    
    # Find seva bookings without journal entries
    # Seva bookings don't have journal_entry_id field directly
    # We need to check via journal entries table
    from app.models.accounting import JournalEntry, TransactionType
    
    # Get all seva booking IDs that have journal entries
    seva_je_query = db.query(JournalEntry.reference_id).filter(
        JournalEntry.reference_type == TransactionType.SEVA
    )
    if temple_id:
        seva_je_query = seva_je_query.filter(JournalEntry.temple_id == temple_id)
    
    seva_ids_with_je = [row[0] for row in seva_je_query.all() if row[0] is not None]
    
    seva_bookings_without_je = db.query(SevaBooking).filter(
        *seva_filter
    ).all()
    
    # Filter out bookings that have journal entries
    seva_bookings_without_je = [s for s in seva_bookings_without_je if s.id not in seva_ids_with_je]
    
    # Calculate totals
    donation_total = sum(d.amount for d in donations_without_je)
    seva_total = sum(s.amount_paid for s in seva_bookings_without_je)
    total_missing = donation_total + seva_total
    
    print(f"\n📊 DONATIONS WITHOUT JOURNAL ENTRIES: {len(donations_without_je)}")
    print(f"   Total Amount: ₹{donation_total:,.2f}")
    if donations_without_je:
        print("\n   Details:")
        for d in donations_without_je[:10]:  # Show first 10
            print(f"   - {d.receipt_number}: ₹{d.amount:,.2f} on {d.donation_date} ({d.payment_mode})")
        if len(donations_without_je) > 10:
            print(f"   ... and {len(donations_without_je) - 10} more")
    
    print(f"\n📊 SEVA BOOKINGS WITHOUT JOURNAL ENTRIES: {len(seva_bookings_without_je)}")
    print(f"   Total Amount: ₹{seva_total:,.2f}")
    if seva_bookings_without_je:
        print("\n   Details:")
        for s in seva_bookings_without_je[:10]:  # Show first 10
            seva_name = s.seva.name_english if s.seva else "Unknown"
            print(f"   - {s.receipt_number}: ₹{s.amount_paid:,.2f} on {s.booking_date} ({seva_name})")
        if len(seva_bookings_without_je) > 10:
            print(f"   ... and {len(seva_bookings_without_je) - 10} more")
    
    print(f"\n💰 TOTAL MISSING FROM TRIAL BALANCE: ₹{total_missing:,.2f}")
    print(f"   (This explains the gap between dashboard and trial balance)")
    
    return {
        "donations": donations_without_je,
        "sevas": seva_bookings_without_je,
        "donation_total": donation_total,
        "seva_total": seva_total,
        "total_missing": total_missing
    }


def main():
    db = SessionLocal()
    try:
        # Get all temples
        temples = db.query(Temple).all()
        
        if not temples:
            print("❌ No temples found.")
            return
        
        for temple in temples:
            print(f"\n🏛️  TEMPLE: {temple.name} (ID: {temple.id})")
            find_missing_entries(db, temple.id)
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

