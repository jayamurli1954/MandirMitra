"""
Diagnostic script to check why journal entries aren't showing in reports
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.donation import Donation
from app.models.seva import SevaBooking
from app.models.accounting import JournalEntry, JournalLine, TransactionType, JournalEntryStatus
from app.models.accounting import Account

def diagnose_issues(db: Session):
    """Diagnose accounting issues"""
    
    print("=" * 60)
    print("ACCOUNTING DIAGNOSTIC REPORT")
    print("=" * 60)
    
    # 1. Check donations
    print("\n1. DONATIONS CHECK")
    print("-" * 60)
    donations = db.query(Donation).all()
    print(f"Total donations: {len(donations)}")
    
    if donations:
        total_donation_amount = sum(d.amount for d in donations)
        print(f"Total donation amount: ₹{total_donation_amount:,.2f}")
        
        # Check journal entries for donations
        donation_entries = db.query(JournalEntry).filter(
            JournalEntry.reference_type == TransactionType.DONATION
        ).all()
        print(f"Journal entries for donations: {len(donation_entries)}")
        
        donations_with_entries = 0
        donations_without_entries = []
        
        for donation in donations:
            entry = db.query(JournalEntry).filter(
                JournalEntry.reference_type == TransactionType.DONATION,
                JournalEntry.reference_id == donation.id
            ).first()
            
            if entry:
                donations_with_entries += 1
                # Check if entry is posted
                if entry.status != JournalEntryStatus.POSTED:
                    print(f"  ⚠ Donation {donation.receipt_number} has entry but status is {entry.status}")
            else:
                donations_without_entries.append(donation)
        
        print(f"Donations with journal entries: {donations_with_entries}")
        print(f"Donations WITHOUT journal entries: {len(donations_without_entries)}")
        
        if donations_without_entries:
            print("\n  Missing journal entries for:")
            for d in donations_without_entries[:10]:  # Show first 10
                print(f"    - {d.receipt_number}: ₹{d.amount} on {d.donation_date}")
    
    # 2. Check seva bookings
    print("\n2. SEVA BOOKINGS CHECK")
    print("-" * 60)
    bookings = db.query(SevaBooking).all()
    print(f"Total seva bookings: {len(bookings)}")
    
    if bookings:
        total_booking_amount = sum(b.amount_paid for b in bookings)
        print(f"Total booking amount: ₹{total_booking_amount:,.2f}")
        
        # Check journal entries for bookings
        booking_entries = db.query(JournalEntry).filter(
            JournalEntry.reference_type == TransactionType.SEVA
        ).all()
        print(f"Journal entries for bookings: {len(booking_entries)}")
        
        bookings_with_entries = 0
        bookings_without_entries = []
        
        for booking in bookings:
            entry = db.query(JournalEntry).filter(
                JournalEntry.reference_type == TransactionType.SEVA,
                JournalEntry.reference_id == booking.id
            ).first()
            
            if entry:
                bookings_with_entries += 1
                if entry.status != JournalEntryStatus.POSTED:
                    print(f"  ⚠ Booking {booking.receipt_number} has entry but status is {entry.status}")
            else:
                bookings_without_entries.append(booking)
        
        print(f"Bookings with journal entries: {bookings_with_entries}")
        print(f"Bookings WITHOUT journal entries: {len(bookings_without_entries)}")
    
    # 3. Check journal entries status
    print("\n3. JOURNAL ENTRIES STATUS")
    print("-" * 60)
    all_entries = db.query(JournalEntry).all()
    print(f"Total journal entries: {len(all_entries)}")
    
    posted_entries = db.query(JournalEntry).filter(
        JournalEntry.status == JournalEntryStatus.POSTED
    ).all()
    print(f"Posted entries: {len(posted_entries)}")
    
    draft_entries = db.query(JournalEntry).filter(
        JournalEntry.status == JournalEntryStatus.DRAFT
    ).all()
    print(f"Draft entries: {len(draft_entries)}")
    
    if draft_entries:
        print("\n  ⚠ WARNING: Found draft entries that won't appear in reports!")
        for e in draft_entries[:5]:
            print(f"    - {e.entry_number}: {e.narration} (Status: {e.status})")
    
    # 4. Check accounts
    print("\n4. ACCOUNTS CHECK")
    print("-" * 60)
    accounts = db.query(Account).all()
    print(f"Total accounts: {len(accounts)}")
    
    # Check required accounts
    required_accounts = {
        '1101': 'Cash in Hand - Counter',
        '1102': 'Cash in Hand - Hundi',
        '1110': 'Bank - SBI Current Account',
        '4101': 'General Donation Income',
        '4102': 'Cash Donation Income',
        '4103': 'Online/UPI Donation Income',
        '4104': 'Hundi Collection Income',
        '4208': 'Special Pooja Income',
    }
    
    missing_accounts = []
    for code, name in required_accounts.items():
        account = db.query(Account).filter(Account.account_code == code).first()
        if account:
            # Check if account has any journal lines
            lines = db.query(JournalLine).filter(JournalLine.account_id == account.id).count()
            print(f"  ✓ {code}: {name} ({lines} transactions)")
        else:
            missing_accounts.append((code, name))
            print(f"  ✗ {code}: {name} - MISSING")
    
    if missing_accounts:
        print(f"\n  ⚠ WARNING: {len(missing_accounts)} required accounts are missing!")
        print("  These accounts need to be created for donations/sevas to work.")
    
    # 5. Check journal lines
    print("\n5. JOURNAL LINES CHECK")
    print("-" * 60)
    all_lines = db.query(JournalLine).all()
    print(f"Total journal lines: {len(all_lines)}")
    
    if all_lines:
        total_debit = sum(l.debit_amount for l in all_lines)
        total_credit = sum(l.credit_amount for l in all_lines)
        print(f"Total debits: ₹{total_debit:,.2f}")
        print(f"Total credits: ₹{total_credit:,.2f}")
        print(f"Balance: ₹{abs(total_debit - total_credit):,.2f}")
    
    # 6. Summary
    print("\n" + "=" * 60)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 60)
    
    if donations_without_entries or bookings_without_entries:
        print("\n⚠ ACTION REQUIRED:")
        if donations_without_entries:
            print(f"  - Run backfill script for {len(donations_without_entries)} donations:")
            print("    python -m scripts.backfill_donation_journal_entries")
        if bookings_without_entries:
            print(f"  - Run backfill script for {len(bookings_without_entries)} bookings:")
            print("    python -m scripts.backfill_seva_journal_entries")
    
    if draft_entries:
        print(f"\n⚠ ACTION REQUIRED:")
        print(f"  - {len(draft_entries)} journal entries are in DRAFT status")
        print("  - These need to be POSTED to appear in reports")
        print("  - Check why entries are being created as DRAFT instead of POSTED")
    
    if missing_accounts:
        print(f"\n⚠ ACTION REQUIRED:")
        print(f"  - Create {len(missing_accounts)} missing accounts")
        print("  - Use Chart of Accounts page or seed script")
    
    if not donations_without_entries and not bookings_without_entries and not draft_entries and not missing_accounts:
        print("\n✓ All checks passed! Journal entries should be working correctly.")
        print("  If reports still show 0, check:")
        print("  - Date filters in reports")
        print("  - Account codes match between donations and chart of accounts")
        print("  - Journal entry dates are within report date range")


def main():
    """Main entry point"""
    db = SessionLocal()
    
    try:
        diagnose_issues(db)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()








