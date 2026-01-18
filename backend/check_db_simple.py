#!/usr/bin/env python3

"""
Simple database check script
"""

import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal

def check_db():
    """Check database contents"""
    db = SessionLocal()
    try:
        print("Checking database...")

        # Import models after session is created to avoid circular imports
        from app.models.temple import Temple
        from app.models.accounting import Account, AccountType, AccountSubType
        from app.models.donation import Donation
        from app.models.seva import SevaBooking

        # Get the temple
        temple = db.query(Temple).first()
        if temple:
            print(f"✅ Temple: {temple.name} (ID: {temple.id})")
        else:
            print("❌ No temple found!")
            return

        # Check bank accounts in chart of accounts
        print("\n🏦 Bank Accounts in Chart of Accounts:")
        accounts = db.query(Account).filter(
            Account.account_type == AccountType.ASSET,
            Account.account_subtype == AccountSubType.CASH_BANK
        ).all()

        if accounts:
            for acc in accounts:
                print(f"  ✅ {acc.account_code}: {acc.account_name} (Active: {acc.is_active})")
        else:
            print("  ❌ No bank accounts found in chart of accounts!")

        # Check all accounts for debugging
        print("\n📊 All Accounts in Chart of Accounts:")
        all_accounts = db.query(Account).filter(Account.temple_id == temple.id).all()
        print(f"  Total accounts: {len(all_accounts)}")
        for acc in all_accounts:
            print(f"    - {acc.account_code}: {acc.account_name} (Type: {acc.account_type}, Subtype: {acc.account_subtype})")

        # Check donations
        print("\n💰 Donations:")
        donations = db.query(Donation).count()
        print(f"  Total donations: {donations}")

        # Check seva bookings
        print("\n🕉️ Seva Bookings:")
        sevas = db.query(SevaBooking).count()
        print(f"  Total seva bookings: {sevas}")

        print("\n" + "=" * 50)
        print("SUMMARY:")
        print(f"  - Temple: {'✅ Found' if temple else '❌ Not found'}")
        print(f"  - Bank accounts for reconciliation: {'✅ Found' if accounts else '❌ Not found'}")
        print(f"  - Donations: {donations}")
        print(f"  - Seva bookings: {sevas}")

        if not accounts:
            print("\n🔍 ISSUE IDENTIFIED:")
            print("   The bank reconciliation dropdown is empty because there are no")
            print("   bank accounts in the chart of accounts with the correct type/subtype.")
            print("   Bank reconciliation requires accounts with:")
            print("     - account_type = 'asset'")
            print("     - account_subtype = 'cash_bank'")

        return True

    except Exception as e:
        print(f"[ERROR] Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("CHECKING DATABASE CONTENTS")
    print("=" * 60)
    success = check_db()
    if success:
        print("\n[OK] Database check completed!")
    else:
        print("\n[ERROR] Failed to check database.")
