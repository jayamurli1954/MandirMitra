#!/usr/bin/env python3

"""
Fix Bank Accounts for Reconciliation
This script ensures that proper bank accounts exist in the chart of accounts
for bank reconciliation to work correctly.
"""

import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal

def fix_bank_accounts():
    """Ensure proper bank accounts exist for reconciliation"""
    db = SessionLocal()
    try:
        print("Fixing bank accounts for reconciliation...")
        print("=" * 50)

        # Import models after session is created to avoid circular imports
        from app.models.temple import Temple
        from app.models.accounting import Account, AccountType, AccountSubType

        # Get the temple
        temple = db.query(Temple).first()
        if not temple:
            print("[ERROR] No temple found. Please run initialize_fresh_db.py first.")
            return False

        print(f"Working with temple: {temple.name} (ID: {temple.id})")

        # Check if the required bank account exists
        bank_account = db.query(Account).filter(
            Account.account_code == "12001",
            Account.temple_id == temple.id
        ).first()

        if bank_account:
            print("✅ Bank account 12001 already exists:")
            print(f"   - Name: {bank_account.account_name}")
            print(f"   - Type: {bank_account.account_type}")
            print(f"   - Subtype: {bank_account.account_subtype}")
            print(f"   - Active: {bank_account.is_active}")
            return True

        # If not, create it
        print("🔧 Creating bank account 12001 for reconciliation...")

        bank_account = Account(
            temple_id=temple.id,
            account_code="12001",
            account_name="Bank - Current Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.CASH_BANK,
            is_active=True,
            opening_balance_debit=0.0,
            opening_balance_credit=0.0
        )

        db.add(bank_account)
        db.commit()
        db.refresh(bank_account)

        print("✅ Successfully created bank account 12001:")
        print(f"   - Name: {bank_account.account_name}")
        print(f"   - Type: {bank_account.account_type}")
        print(f"   - Subtype: {bank_account.account_subtype}")
        print(f"   - Active: {bank_account.is_active}")

        # Also check if account 1002 exists and update it if needed
        old_bank_account = db.query(Account).filter(
            Account.account_code == "1002",
            Account.temple_id == temple.id
        ).first()

        if old_bank_account:
            print("\n📝 Found existing bank account 1002:")
            print(f"   - Name: {old_bank_account.account_name}")
            print(f"   - Type: {old_bank_account.account_type}")
            print(f"   - Subtype: {old_bank_account.account_subtype}")

            # Update it to match the expected format if needed
            if old_bank_account.account_type != AccountType.ASSET or old_bank_account.account_subtype != AccountSubType.CASH_BANK:
                print("   Updating account type/subtype to match reconciliation requirements...")
                old_bank_account.account_type = AccountType.ASSET
                old_bank_account.account_subtype = AccountSubType.CASH_BANK
                db.commit()
                print("   ✅ Updated account 1002")

        print("\n🎉 Bank accounts are now properly configured for reconciliation!")
        print("\nYou should now be able to:")
        print("  1. Go to Accounting -> Bank Reconciliation")
        print("  2. Select a bank account from the dropdown")
        print("  3. Import bank statements and perform reconciliation")

        return True

    except Exception as e:
        print(f"[ERROR] Error fixing bank accounts: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("FIXING BANK ACCOUNTS FOR RECONCILIATION")
    print("=" * 60)
    success = fix_bank_accounts()
    if success:
        print("\n[OK] Bank accounts are ready for reconciliation!")
    else:
        print("\n[ERROR] Failed to fix bank accounts. Please check errors above.")
