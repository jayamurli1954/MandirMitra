"""
Script to delete accounts with 4-digit codes or codes starting with '0'
Only deletes accounts that:
1. Have no journal entries
2. Have no child accounts
3. Are not referenced by donation_categories
4. Are not referenced by bank_accounts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import os for environment variable check later
import os as os_module

from app.core.database import SessionLocal
from sqlalchemy import text

def check_account_dependencies(account_id):
    """Check if account has any dependencies using a fresh session"""
    from app.core.database import SessionLocal
    check_db = SessionLocal()
    try:
        # Check journal entries
        journal_check = text("""
            SELECT COUNT(*) FROM journal_lines WHERE account_id = :account_id
        """)
        journal_count = check_db.execute(journal_check, {"account_id": account_id}).fetchone()[0]
        
        # Check child accounts
        child_check = text("""
            SELECT COUNT(*) FROM accounts WHERE parent_account_id = :account_id
        """)
        child_count = check_db.execute(child_check, {"account_id": account_id}).fetchone()[0]
        
        # Check donation categories
        donation_check = text("""
            SELECT COUNT(*) FROM donation_categories WHERE account_id = :account_id
        """)
        donation_count = check_db.execute(donation_check, {"account_id": account_id}).fetchone()[0]
        
        # Check bank accounts (if account_id column exists)
        bank_count = 0
        try:
            bank_check = text("""
                SELECT COUNT(*) FROM bank_accounts WHERE account_id = :account_id
            """)
            bank_count = check_db.execute(bank_check, {"account_id": account_id}).fetchone()[0]
        except Exception:
            # Column might not exist, skip
            pass
        
        return {
            'journal_entries': journal_count,
            'child_accounts': child_count,
            'donation_categories': donation_count,
            'bank_accounts': bank_count,
            'has_dependencies': (journal_count > 0 or child_count > 0 or 
                                donation_count > 0 or bank_count > 0)
        }
    finally:
        check_db.close()

def main():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("DELETE ACCOUNTS WITH INVALID CODES (4-digit or 0-prefix)")
        print("=" * 70)
        print()
        
        # Find all accounts with 4-digit or 0-prefixed codes
        query = text("""
            SELECT id, account_code, account_name, is_active
            FROM accounts
            WHERE temple_id = 1
            AND (LENGTH(account_code) < 5 OR account_code LIKE '0%')
            ORDER BY account_code
        """)
        result = db.execute(query)
        accounts = result.fetchall()
        
        if not accounts:
            print("No accounts found with 4-digit or 0-prefixed codes.")
            return 0
        
        print(f"Found {len(accounts)} account(s) to check for deletion:")
        print()
        
        safe_to_delete = []
        has_dependencies = []
        
        for acc_id, acc_code, acc_name, is_active in accounts:
            try:
                deps = check_account_dependencies(acc_id)
            except Exception as e:
                print(f"  Error checking {acc_code}: {e}")
                continue
            
            if deps['has_dependencies']:
                has_dependencies.append({
                    'id': acc_id,
                    'code': acc_code,
                    'name': acc_name,
                    'is_active': is_active,
                    'dependencies': deps
                })
            else:
                safe_to_delete.append({
                    'id': acc_id,
                    'code': acc_code,
                    'name': acc_name,
                    'is_active': is_active
                })
        
        # Show accounts with dependencies
        if has_dependencies:
            print(f"Accounts with dependencies (will NOT be deleted): {len(has_dependencies)}")
            for acc in has_dependencies:
                print(f"  - {acc['code']} ({acc['name']})")
                deps = acc['dependencies']
                if deps['journal_entries'] > 0:
                    print(f"    -> {deps['journal_entries']} journal entries")
                if deps['child_accounts'] > 0:
                    print(f"    -> {deps['child_accounts']} child accounts")
                if deps['donation_categories'] > 0:
                    print(f"    -> {deps['donation_categories']} donation categories")
                if deps['bank_accounts'] > 0:
                    print(f"    -> {deps['bank_accounts']} bank accounts")
            print()
        
        # Delete safe accounts
        if not safe_to_delete:
            print("No accounts are safe to delete (all have dependencies or are already handled).")
            return 0
        
        print(f"Accounts safe to delete: {len(safe_to_delete)}")
        for acc in safe_to_delete:
            print(f"  - {acc['code']} ({acc['name']})")
        print()
        
        # Confirm deletion (non-interactive mode via command-line argument)
        non_interactive = '--yes' in sys.argv or os_module.getenv('MIGRATION_NON_INTERACTIVE', '').lower() == 'true'
        
        if non_interactive:
            response = 'yes'
            print(f"Non-interactive mode: Auto-confirming deletion of {len(safe_to_delete)} account(s)")
        else:
            response = input(f"Delete {len(safe_to_delete)} account(s)? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("Deletion cancelled.")
            return 0
        
        # Delete accounts
        deleted_count = 0
        for acc in safe_to_delete:
            delete_query = text("""
                DELETE FROM accounts WHERE id = :account_id
            """)
            db.execute(delete_query, {"account_id": acc['id']})
            print(f"  Deleted {acc['code']} ({acc['name']})")
            deleted_count += 1
        
        db.commit()
        print()
        print(f"Successfully deleted {deleted_count} account(s).")
        
        return 0
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        db.close()

if __name__ == "__main__":
    exit(main())

