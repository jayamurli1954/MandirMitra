"""
Migration script to replace 4-digit expense account codes with 5-digit codes
and remove all 4-digit and 0-prefixed account codes.

Mapping:
- 5101 (Priest Salary) -> 52003 (Priest Fees)
- 5102 (Staff Salary) -> 52001 (Salaries)
- 5110 (Electricity Bill) -> 53002 (Electricity)

Also removes all accounts with:
- 4-digit codes (length < 5)
- Codes starting with '0'
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from sqlalchemy import text
import json
from datetime import datetime

# Mapping of old codes to new codes
MIGRATION_MAP = {
    '5101': ('52003', 'Priest Fees'),  # Priest Salary -> Priest Fees
    '5102': ('52001', 'Salaries'),     # Staff Salary -> Salaries
    '5110': ('53002', 'Electricity'),  # Electricity Bill -> Electricity
}

def check_accounts_to_remove(db):
    """Find all accounts with 4-digit codes or codes starting with '0'"""
    query = text("""
        SELECT id, account_code, account_name, account_type, is_active
        FROM accounts
        WHERE temple_id = 1
        AND (LENGTH(account_code) < 5 OR account_code LIKE '0%')
        ORDER BY account_code
    """)
    result = db.execute(query)
    return result.fetchall()

def get_new_account(db, new_code):
    """Get new account ID by code using raw SQL"""
    query = text("""
        SELECT id FROM accounts
        WHERE temple_id = 1 AND account_code = :code
    """)
    result = db.execute(query, {"code": new_code})
    row = result.fetchone()
    return row[0] if row else None

def migrate_journal_entries(db, old_account_id, new_account_id, old_code, new_code):
    """Migrate journal entries from old account to new account using raw SQL"""
    # Count existing journal lines
    count_query = text("""
        SELECT COUNT(*) FROM journal_lines WHERE account_id = :account_id
    """)
    count_result = db.execute(count_query, {"account_id": old_account_id})
    count = count_result.fetchone()[0]
    
    if count > 0:
        # Update journal lines
        update_query = text("""
            UPDATE journal_lines
            SET account_id = :new_account_id
            WHERE account_id = :old_account_id
        """)
        db.execute(update_query, {
            "new_account_id": new_account_id,
            "old_account_id": old_account_id
        })
        db.commit()
        print(f"  Migrated {count} journal line(s) from {old_code} to {new_code}")
    
    return count

def deactivate_account(db, account_id, account_code):
    """Deactivate an account (set is_active = False)"""
    query = text("""
        UPDATE accounts
        SET is_active = FALSE
        WHERE id = :account_id
    """)
    db.execute(query, {"account_id": account_id})
    print(f"  Deactivated account {account_code} (ID: {account_id})")

def main():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("EXPENSE ACCOUNT CODE MIGRATION")
        print("=" * 70)
        print()
        
        # Step 1: Check accounts to migrate/remove
        print("Step 1: Checking accounts with 4-digit or 0-prefixed codes...")
        accounts_to_check = check_accounts_to_remove(db)
        
        if not accounts_to_check:
            print("  No accounts found with 4-digit or 0-prefixed codes.")
            return
        
        print(f"  Found {len(accounts_to_check)} account(s) to process:")
        for acc in accounts_to_check:
            print(f"    - {acc[1]} ({acc[2]}) - Type: {acc[3]}, Active: {acc[4]}")
        print()
        
        # Step 2: Migrate specific expense accounts
        print("Step 2: Migrating expense accounts...")
        migration_results = {}
        
        for old_code, (new_code, new_name) in MIGRATION_MAP.items():
            # Find old account using raw SQL
            old_acc_query = text("""
                SELECT id, account_name FROM accounts
                WHERE temple_id = 1 AND account_code = :code
            """)
            old_acc_result = db.execute(old_acc_query, {"code": old_code})
            old_acc_row = old_acc_result.fetchone()
            
            if not old_acc_row:
                print(f"  Old account {old_code} not found, skipping...")
                continue
            
            old_account_id, old_account_name = old_acc_row
            
            # Get or check new account exists
            new_account_id = get_new_account(db, new_code)
            
            if not new_account_id:
                print(f"  ERROR: New account {new_code} ({new_name}) does not exist!")
                print(f"  Please create this account first.")
                continue
            
            print(f"  Migrating {old_code} ({old_account_name}) -> {new_code} ({new_name})...")
            
            # Migrate journal entries
            migrated = migrate_journal_entries(
                db, old_account_id, new_account_id, old_code, new_code
            )
            
            # Deactivate old account
            deactivate_account(db, old_account_id, old_code)
            
            migration_results[old_code] = {
                'new_code': new_code,
                'new_name': new_name,
                'journal_lines_migrated': migrated
            }
        
        print()
        
        # Step 3: Deactivate remaining 4-digit and 0-prefixed accounts
        print("Step 3: Deactivating remaining accounts with 4-digit or 0-prefixed codes...")
        
        # Re-check after migrations
        remaining_accounts = check_accounts_to_remove(db)
        
        deactivated_count = 0
        for acc in remaining_accounts:
            acc_id, acc_code, acc_name, acc_type, is_active = acc
            
            # Skip if already deactivated
            if not is_active:
                continue
            
            # Skip accounts we just migrated
            if acc_code in MIGRATION_MAP:
                continue
            
            print(f"  Deactivating {acc_code} ({acc_name})...")
            deactivate_account(db, acc_id, acc_code)
            deactivated_count += 1
        
        print(f"  Deactivated {deactivated_count} additional account(s).")
        print()
        
        # Step 4: Summary
        print("=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        print(f"Migrated accounts: {len(migration_results)}")
        for old_code, info in migration_results.items():
            print(f"  {old_code} -> {info['new_code']} ({info['new_name']})")
            print(f"    Journal lines migrated: {info['journal_lines_migrated']}")
        print(f"Additional accounts deactivated: {deactivated_count}")
        print()
        print("Next steps:")
        print("1. Update frontend QuickExpense.js to use new codes")
        print("2. Verify all accounts have 5-digit codes (no 4-digit, no 0-prefix)")
        print("3. Test expense entry with new account codes")
        
        db.commit()
        print()
        print("Migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    exit(main())

