"""
Sync Script: Post Existing Seva Bookings to Accounting Ledger

This script creates journal entries for all existing seva bookings that haven't been posted to accounting yet.
Run this once to sync historical sevas, then the system will auto-post new bookings.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.seva import SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine
from app.models.temple import Temple

def get_account_by_code(db: Session, temple_id: int, account_code: str):
    """Get account by code"""
    return db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == account_code
    ).first()

def sync_sevas_to_accounting(db: Session, temple_id: int):
    """
    Sync all seva bookings to accounting system
    Creates journal entries for sevas that don't have accounting entries
    """

    # Get all seva bookings
    bookings = db.query(SevaBooking).all()

    print(f"\n📊 Found {len(bookings)} total seva bookings")

    # Check which bookings already have journal entries
    synced_count = 0
    skipped_count = 0
    error_count = 0

    for booking in bookings:
        # Check if journal entry already exists for this booking
        existing_entry = db.query(JournalEntry).filter(
            JournalEntry.temple_id == temple_id,
            JournalEntry.reference_type == 'SEVA',
            JournalEntry.reference_id == booking.id
        ).first()

        if existing_entry:
            skipped_count += 1
            continue

        try:
            # Determine debit account (payment method)
            payment_method = booking.payment_method or 'CASH'
            debit_account_code = None

            if payment_method.upper() in ['CASH', 'COUNTER']:
                debit_account_code = A101'  # Cash in Hand - Counter
            elif payment_method.upper() in ['UPI', 'ONLINE', 'CARD', 'NETBANKING']:
                debit_account_code = A110'  # Bank - SBI Current Account
            else:
                debit_account_code = A101'  # Default to cash counter

            # Determine credit account - prefer seva-linked account
            credit_account = None

            if booking.seva and hasattr(booking.seva, 'account_id') and booking.seva.account_id:
                credit_account = db.query(Account).filter(Account.id == booking.seva.account_id).first()

            # Fallback to default Special Pooja
            if not credit_account:
                credit_account_code = '4208'  # Special Pooja (default)
                credit_account = get_account_by_code(db, temple_id, credit_account_code)

            # Get debit account
            debit_account = get_account_by_code(db, temple_id, debit_account_code)

            if not debit_account or not credit_account:
                print(f"⚠️  Skipping booking {booking.receipt_number}: Accounts not found (Dr: {debit_account_code}, Cr: {credit_account.account_code if credit_account else 'N/A'})")
                error_count += 1
                continue

            # Create narration
            devotee_name = booking.devotee.name if booking.devotee else 'Unknown'
            seva_name = booking.seva.name_english if booking.seva else 'Seva'
            narration = f"Seva booking - {seva_name} by {devotee_name}"

            # Create journal entry
            journal_entry = JournalEntry(
                temple_id=temple_id,
                entry_date=booking.booking_date,
                entry_number=None,  # Will be auto-generated
                narration=narration,
                reference_type='SEVA',
                reference_id=booking.id,
                reference_number=booking.receipt_number,
                status='POSTED',
                created_by=booking.user_id
            )
            db.add(journal_entry)
            db.flush()  # Get journal_entry.id

            # Generate entry number
            year = booking.booking_date.year
            last_entry = db.query(JournalEntry).filter(
                JournalEntry.temple_id == temple_id,
                JournalEntry.id < journal_entry.id
            ).order_by(JournalEntry.id.desc()).first()

            seq = 1
            if last_entry and last_entry.entry_number:
                try:
                    seq = int(last_entry.entry_number.split('-')[-1]) + 1
                except:
                    seq = journal_entry.id

            journal_entry.entry_number = f"JE-{year}-{str(seq).zfill(5)}"

            # Create journal lines (Debit: Payment Account, Credit: Seva Income)
            debit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=debit_account.id,
                debit_amount=booking.amount_paid,
                credit_amount=0,
                description=f"Seva booking received via {payment_method}"
            )

            credit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=credit_account.id,
                debit_amount=0,
                credit_amount=booking.amount_paid,
                description=f"Seva income - {seva_name}"
            )

            db.add(debit_line)
            db.add(credit_line)

            synced_count += 1
            print(f"✅ Synced: {booking.receipt_number} - {seva_name} - ₹{booking.amount_paid:,.2f} (Entry: {journal_entry.entry_number})")

        except Exception as e:
            print(f"❌ Error syncing booking {booking.receipt_number}: {str(e)}")
            error_count += 1
            continue

    # Commit all changes
    db.commit()

    print(f"\n📈 Sync Summary:")
    print(f"   ✅ Successfully synced: {synced_count} seva bookings")
    print(f"   ⏭️  Already synced (skipped): {skipped_count} seva bookings")
    print(f"   ❌ Errors: {error_count} seva bookings")
    print(f"   📊 Total: {len(bookings)} seva bookings")

def main():
    """
    Main function to sync seva bookings
    """
    db = SessionLocal()

    try:
        # Get first temple
        temple = db.query(Temple).first()

        if not temple:
            print("⚠️  No temple found. Please create a temple first.")
            return

        print(f"\n🕉️  Temple: {temple.name}")
        print(f"   ID: {temple.id}")

        # Check if chart of accounts exists
        account_count = db.query(Account).filter(Account.temple_id == temple.id).count()

        if account_count == 0:
            print("\n⚠️  No chart of accounts found!")
            print("   Please run: python seed_chart_of_accounts.py")
            return

        print(f"   Accounts in chart: {account_count}")

        # Confirm
        response = input(f"\n🔄 Sync all seva bookings to accounting ledger for '{temple.name}'? (y/n): ")
        if response.lower() != 'y':
            print("❌ Aborted.")
            return

        # Sync sevas
        sync_sevas_to_accounting(db, temple.id)

        print("\n✅ Seva sync completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Check Trial Balance: http://localhost:3000/accounting/reports")
        print("   2. View Journal Entries: http://localhost:3000/accounting/journal-entries")
        print("   3. Future seva bookings will auto-post to accounting!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
