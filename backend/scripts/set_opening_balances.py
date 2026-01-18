"""
Set Opening Balances for Balance Sheet Items
Used when starting the system mid-year

Usage:
    python scripts/set_opening_balances.py

This script will:
1. List all balance sheet accounts (Assets, Liabilities, Equity)
2. Allow you to enter opening balances interactively
3. Update the account opening_balance_debit/opening_balance_credit fields
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.accounting import Account, AccountType
from sqlalchemy import or_

def get_balance_sheet_accounts(db):
    """Get all balance sheet accounts (Assets, Liabilities, Equity)"""
    return db.query(Account).filter(
        or_(
            Account.account_type == AccountType.ASSET,
            Account.account_type == AccountType.LIABILITY,
            Account.account_type == AccountType.EQUITY
        )
    ).order_by(Account.account_code).all()


def display_account(account, index, total):
    """Display account information"""
    current_balance = account.opening_balance_debit - account.opening_balance_credit
    balance_str = f"₹{current_balance:,.2f}" if current_balance != 0 else "₹0.00"
    print(f"\n[{index}/{total}] {account.account_code} - {account.account_name}")
    print(f"     Type: {account.account_type.value.upper()}")
    print(f"     Current Opening Balance: {balance_str}")


def get_balance_input():
    """Get balance input from user"""
    while True:
        try:
            value = input("Enter opening balance (positive for debit/asset, negative for credit/liability): ").strip()
            if not value:
                return None  # Skip this account
            
            balance = float(value)
            return balance
        except ValueError:
            print("   [ERROR] Please enter a valid number. Leave empty to skip.")
        except KeyboardInterrupt:
            print("\n\nSetup cancelled.")
            return None


def update_account_balance(account, balance):
    """Update account opening balance"""
    if balance is None:
        return False
    
    if balance >= 0:
        # Debit balance (for Assets, or negative for Liabilities/Equity)
        if account.account_type == AccountType.ASSET:
            account.opening_balance_debit = abs(balance)
            account.opening_balance_credit = 0.0
        else:  # Liability or Equity (credit balance)
            account.opening_balance_credit = abs(balance)
            account.opening_balance_debit = 0.0
    else:
        # Negative balance (credit for Assets, debit for Liabilities/Equity)
        if account.account_type == AccountType.ASSET:
            account.opening_balance_credit = abs(balance)
            account.opening_balance_debit = 0.0
        else:  # Liability or Equity
            account.opening_balance_debit = abs(balance)
            account.opening_balance_credit = 0.0
    
    return True


def main():
    """Main function"""
    print("=" * 70)
    print("  MandirMitra - Opening Balance Setup")
    print("=" * 70)
    print()
    print("This script allows you to set opening balances for balance sheet")
    print("items (Assets, Liabilities, Equity) when starting mid-year.")
    print()
    print("Instructions:")
    print("  - For Assets: Enter positive balance (e.g., 50000 for ₹50,000 cash)")
    print("  - For Liabilities: Enter positive balance (e.g., 10000 for ₹10,000 loan)")
    print("  - For Equity: Enter positive balance (e.g., 1000000 for ₹10,00,000 fund)")
    print("  - Leave empty to skip an account")
    print("  - Press Ctrl+C to cancel")
    print()
    
    input("Press Enter to continue...")
    
    db = SessionLocal()
    try:
        accounts = get_balance_sheet_accounts(db)
        
        if not accounts:
            print("\n[ERROR] No balance sheet accounts found.")
            print("Please run initialize_default_coa.py first to create accounts.")
            return
        
        print(f"\nFound {len(accounts)} balance sheet accounts")
        print("=" * 70)
        
        updated_count = 0
        skipped_count = 0
        
        for i, account in enumerate(accounts, 1):
            display_account(account, i, len(accounts))
            
            balance = get_balance_input()
            if balance is None:
                skipped_count += 1
                print("   [SKIPPED]")
                continue
            
            if update_account_balance(account, balance):
                db.commit()
                updated_count += 1
                new_balance = account.opening_balance_debit - account.opening_balance_credit
                print(f"   [OK] Updated to ₹{new_balance:,.2f}")
        
        print("\n" + "=" * 70)
        print("  Setup Complete")
        print("=" * 70)
        print(f"Updated: {updated_count} accounts")
        print(f"Skipped: {skipped_count} accounts")
        print()
        print("Opening balances have been set. You can now:")
        print("  1. Generate Trial Balance to verify")
        print("  2. Generate Balance Sheet to view balances")
        print("  3. Start entering regular transactions")
        print()
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled. No changes saved.")
        db.rollback()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

















