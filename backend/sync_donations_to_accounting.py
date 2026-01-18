"""
Sync Script: Post Existing Donations to Accounting Ledger

This script creates journal entries for all existing donations that haven't been posted to accounting yet.
Run this once to sync historical donations, then the system will auto-post new donations.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import SessionLocal
from app.models.donation import Donation
from app.models.accounting import Account, JournalEntry, JournalLine, AccountType
from app.models.temple import Temple

def get_account_by_code(db: Session, temple_id: int, account_code: str):
    """Get account by code"""
    return db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == account_code
    ).first()

def sync_donations_to_accounting(db: Session, temple_id: int):
    """
    Sync all donations to accounting system
    Creates journal entries for donations that don't have accounting entries
    """

    # Get all donations for this temple
    donations = db.query(Donation).filter(
        Donation.temple_id == temple_id
    ).all()

    print(f"\n📊 Found {len(donations)} total donations for temple_id {temple_id}")

    # Check which donations already have journal entries
    synced_count = 0
    skipped_count = 0
    error_count = 0

    for donation in donations:
        # Check if journal entry already exists for this donation
        existing_entry = db.query(JournalEntry).filter(
            JournalEntry.temple_id == temple_id,
            JournalEntry.reference_type == 'DONATION',
            JournalEntry.reference_id == donation.id
        ).first()

        if existing_entry:
            skipped_count += 1
            continue

        try:
            # Determine debit account (payment method)
            debit_account_code = None
            if donation.payment_mode.upper() in ['CASH', 'COUNTER']:
                debit_account_code = A101'  # Cash in Hand - Counter
            elif donation.payment_mode.upper() in ['UPI', 'ONLINE', 'CARD', 'NETBANKING']:
                debit_account_code = A110'  # Bank - SBI Current Account (or HDFC based on preference)
            elif 'HUNDI' in donation.payment_mode.upper():
                debit_account_code = A102'  # Cash in Hand - Hundi
            else:
                # Default to cash counter
                debit_account_code = A101'

            # Determine credit account (donation income type)
            credit_account_code = None
            if donation.payment_mode.upper() in ['CASH', 'COUNTER']:
                credit_account_code = '4101'  # Donation - Cash
            elif donation.payment_mode.upper() in ['UPI', 'ONLINE', 'CARD', 'NETBANKING']:
                credit_account_code = '4102'  # Donation - Online/UPI
            elif 'HUNDI' in donation.payment_mode.upper():
                credit_account_code = '4103'  # Hundi Collection
            else:
                credit_account_code = '4101'  # Default to cash donation

            # Get accounts
            debit_account = get_account_by_code(db, temple_id, debit_account_code)
            credit_account = get_account_by_code(db, temple_id, credit_account_code)

            if not debit_account or not credit_account:
                print(f"⚠️  Skipping donation {donation.receipt_number}: Accounts not found (Dr: {debit_account_code}, Cr: {credit_account_code})")
                error_count += 1
                continue

            # Create journal entry
            narration = f"Donation from {donation.devotee.name if donation.devotee else 'Anonymous'}"
            if donation.category:
                narration += f" - {donation.category.name}"

            journal_entry = JournalEntry(
                temple_id=temple_id,
                entry_date=donation.donation_date,
                entry_number=None,  # Will be auto-generated
                narration=narration,
                reference_type='DONATION',
                reference_id=donation.id,
                reference_number=donation.receipt_number,
                status='POSTED',
                created_by=donation.created_by
            )
            db.add(journal_entry)
            db.flush()  # Get journal_entry.id

            # Generate entry number
            year = donation.donation_date.year
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

            # Create journal lines (Debit: Payment Account, Credit: Donation Income)
            debit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=debit_account.id,
                debit_amount=donation.amount,
                credit_amount=0,
                description=f"Donation received via {donation.payment_mode}"
            )

            credit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=credit_account.id,
                debit_amount=0,
                credit_amount=donation.amount,
                description=f"Donation income - {donation.category.name if donation.category else 'General'}"
            )

            db.add(debit_line)
            db.add(credit_line)

            synced_count += 1
            print(f"✅ Synced: {donation.receipt_number} - ₹{donation.amount:,.2f} (Entry: {journal_entry.entry_number})")

        except Exception as e:
            print(f"❌ Error syncing donation {donation.receipt_number}: {str(e)}")
            error_count += 1
            continue

    # Commit all changes
    db.commit()

    print(f"\n📈 Sync Summary:")
    print(f"   ✅ Successfully synced: {synced_count} donations")
    print(f"   ⏭️  Already synced (skipped): {skipped_count} donations")
    print(f"   ❌ Errors: {error_count} donations")
    print(f"   📊 Total: {len(donations)} donations")

def main():
    """
    Main function to sync donations
    """
    db = SessionLocal()

    try:
        # Get first temple (or create demo temple if none exists)
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
        response = input(f"\n🔄 Sync all donations to accounting ledger for '{temple.name}'? (y/n): ")
        if response.lower() != 'y':
            print("❌ Aborted.")
            return

        # Sync donations
        sync_donations_to_accounting(db, temple.id)

        print("\n✅ Donation sync completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Check Trial Balance: http://localhost:3000/accounting/reports")
        print("   2. View Journal Entries: http://localhost:3000/accounting/journal-entries")
        print("   3. Future donations will auto-post to accounting!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
