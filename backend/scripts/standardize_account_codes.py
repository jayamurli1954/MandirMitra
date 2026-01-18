"""
Account Code Standardization Migration Script

This script standardizes all account codes to 5-digit format (with leading zeros).
Example: 1110 -> 01110, 5101 -> 05101

IMPORTANT: 
- This is a critical migration that affects all accounting data
- Backup your database before running this script
- Test on a copy of production data first
- Run during maintenance window
"""

import sys
import os
from pathlib import Path
import io

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # If already wrapped or not available, continue

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import text, update
from app.core.database import SessionLocal, engine
from datetime import datetime
import json


def standardize_account_code(code: str) -> str:
    """
    Convert account code to 5-digit format with leading zeros
    
    Args:
        code: Account code (can be string or number)
    
    Returns:
        5-digit account code string
    """
    if not code:
        return code
    
    # Convert to string and strip whitespace
    code_str = str(code).strip()
    
    # Remove any non-numeric characters (except if it's a valid format)
    # Keep only digits
    code_digits = ''.join(c for c in code_str if c.isdigit())
    
    if not code_digits:
        return code_str  # Return original if no digits found
    
    # Pad with leading zeros to make 5 digits
    return code_digits.zfill(5)


def get_all_accounts_to_migrate(db: Session) -> list:
    """
    Get all accounts that need migration (non-5-digit codes)
    
    Returns:
        List of (account_id, old_code, new_code) tuples
    """
    # Use raw SQL to avoid ORM relationship issues
    result = db.execute(text("SELECT id, account_code, account_name, temple_id FROM accounts"))
    migrations = []
    
    for row in result:
        account_id, old_code, account_name, temple_id = row
        new_code = standardize_account_code(old_code)
        
        if old_code != new_code:
            migrations.append({
                'id': account_id,
                'old_code': old_code,
                'new_code': new_code,
                'name': account_name,
                'temple_id': temple_id
            })
    
    return migrations


def check_code_collisions(db: Session, migrations: list) -> dict:
    """
    Check if any new codes would collide with existing codes
    
    Returns:
        Dictionary of collisions: {new_code: [account_ids]}
    """
    collisions = {}
    
    # Get all existing account codes using raw SQL
    result = db.execute(text("SELECT id, account_code FROM accounts"))
    existing_codes = {row.account_code: row.id for row in result}
    
    # Check each migration
    for mig in migrations:
        new_code = mig['new_code']
        account_id = mig['id']
        
        # If new code already exists and it's not the same account
        if new_code in existing_codes and existing_codes[new_code] != account_id:
            if new_code not in collisions:
                collisions[new_code] = []
            collisions[new_code].append({
                'migrating_account_id': account_id,
                'existing_account_id': existing_codes[new_code],
                'migrating_name': mig['name'],
                'old_code': mig['old_code']
            })
    
    return collisions


def resolve_collisions(db: Session, migrations: list, collisions: dict) -> list:
    """
    Resolve code collisions by finding alternative codes
    
    Returns:
        Updated migrations list with resolved collisions
    """
    resolved_migrations = []
    
    for mig in migrations:
        new_code = mig['new_code']
        
        if new_code in collisions:
            # Find alternative code (try next available)
            base_num = int(new_code)
            alternative = base_num + 1
            max_attempts = 100
            
            while alternative < 100000 and max_attempts > 0:
                alt_code = str(alternative).zfill(5)
                
                # Check if alternative is available
                result = db.execute(text("SELECT id FROM accounts WHERE account_code = :code"), {"code": alt_code})
                existing = result.first()
                if not existing:
                    mig['new_code'] = alt_code
                    mig['collision_resolved'] = True
                    mig['original_new_code'] = new_code
                    print(f"  [WARN] Resolved collision: {mig['old_code']} -> {alt_code} (original target: {new_code})")
                    break
                
                alternative += 1
                max_attempts -= 1
            
            if max_attempts == 0:
                print(f"  [ERROR] Could not resolve collision for {mig['old_code']}")
                return None
        
        resolved_migrations.append(mig)
    
    return resolved_migrations


def update_account_codes(db: Session, migrations: list, dry_run: bool = True) -> dict:
    """
    Update account codes in database
    
    Args:
        db: Database session
        migrations: List of migration dictionaries
        dry_run: If True, only show what would be changed
    
    Returns:
        Dictionary with results
    """
    results = {
        'total': len(migrations),
        'updated': 0,
        'errors': [],
        'changes': []
    }
    
    if dry_run:
        print("\n[DRY RUN] MODE - No changes will be made\n")
    
    for mig in migrations:
        try:
            # Get account using raw SQL
            result = db.execute(
                text("SELECT id, account_code, account_name, temple_id FROM accounts WHERE id = :id"),
                {"id": mig['id']}
            )
            row = result.first()
            if not row:
                results['errors'].append(f"Account {mig['id']} not found")
                continue
            
            account_id, old_code, account_name, temple_id = row
            new_code = mig['new_code']
            
            if old_code == new_code:
                continue  # Already correct
            
            change_info = {
                'account_id': account_id,
                'account_name': account_name,
                'old_code': old_code,
                'new_code': new_code,
                'temple_id': temple_id
            }
            
            if not dry_run:
                # Update account code using raw SQL
                db.execute(
                    text("UPDATE accounts SET account_code = :new_code WHERE id = :id"),
                    {"new_code": new_code, "id": account_id}
                )
                db.flush()
                
                # Note: JournalLines use account_id (foreign key), not account_code
                # So we don't need to update journal_lines
                # But we should check if any code references account_code directly
                
            results['changes'].append(change_info)
            results['updated'] += 1
            
            status = "[OK]" if not dry_run else "[DRY]"
            print(f"{status} {old_code:>6} -> {new_code:>6} | {account_name}")
            
        except Exception as e:
            error_msg = f"Error updating account {mig['id']}: {str(e)}"
            results['errors'].append(error_msg)
            print(f"  [ERROR] {error_msg}")
    
    if not dry_run:
        try:
            db.commit()
            print(f"\n[OK] Successfully updated {results['updated']} account codes")
        except Exception as e:
            db.rollback()
            print(f"\n[ERROR] Error committing changes: {str(e)}")
            results['errors'].append(f"Commit error: {str(e)}")
    
    return results


def create_backup_mapping(migrations: list, backup_file: str = "account_code_migration_backup.json"):
    """
    Create backup mapping file for rollback
    
    Args:
        migrations: List of migration dictionaries
        backup_file: Path to backup file
    """
    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'migrations': migrations,
        'description': 'Account code standardization migration - old_code to new_code mapping'
    }
    
    backup_path = Path(__file__).parent.parent / backup_file
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[INFO] Backup mapping saved to: {backup_path}")
    return backup_path


def main():
    """Main migration function"""
    import sys
    
    # Check for non-interactive mode
    non_interactive = '--yes' in sys.argv or '--non-interactive' in sys.argv
    
    print("=" * 70)
    print("ACCOUNT CODE STANDARDIZATION MIGRATION")
    print("=" * 70)
    print("\nThis script will standardize all account codes to 5-digit format.")
    print("Example: 1110 -> 01110, 5101 -> 05101\n")
    
    # Ask for confirmation (unless non-interactive)
    if not non_interactive:
        print("\n[WARNING] This migration will modify account codes in the database.")
        print("[WARNING] Please ensure you have backed up your database!")
        response = input("Have you backed up your database? (yes/no): ").strip().lower()
        if response != 'yes':
            print("[ERROR] Please backup your database before running this migration!")
            return
    else:
        print("\n[INFO] Non-interactive mode enabled. Proceeding with migration...")
        print("[WARNING] Ensure you have backed up your database!")
    
    # Dry run first
    print("\n" + "=" * 70)
    print("STEP 1: DRY RUN - Checking what will be changed")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Get all accounts to migrate
        migrations = get_all_accounts_to_migrate(db)
        
        if not migrations:
            print("\n[OK] All account codes are already in 5-digit format!")
            return
        
        print(f"\n[INFO] Found {len(migrations)} accounts that need migration:\n")
        
        # Show what will be changed
        for mig in migrations[:20]:  # Show first 20
            print(f"  {mig['old_code']:>6} -> {mig['new_code']:>6} | {mig['name']}")
        
        if len(migrations) > 20:
            print(f"  ... and {len(migrations) - 20} more")
        
        # Check for collisions
        print("\n" + "=" * 70)
        print("STEP 2: Checking for code collisions")
        print("=" * 70)
        
        collisions = check_code_collisions(db, migrations)
        
        if collisions:
            print(f"\n[WARN] Found {len(collisions)} potential collisions:")
            for new_code, coll_list in collisions.items():
                print(f"\n  Code {new_code} would collide:")
                for coll in coll_list:
                    print(f"    - Account {coll['migrating_account_id']} ({coll['old_code']} -> {new_code})")
                    print(f"      conflicts with existing account {coll['existing_account_id']}")
            
            # Resolve collisions
            print("\n" + "=" * 70)
            print("STEP 3: Resolving collisions")
            print("=" * 70)
            
            migrations = resolve_collisions(db, migrations, collisions)
            if not migrations:
                print("[ERROR] Could not resolve all collisions. Migration aborted.")
                return
        else:
            print("\n[OK] No collisions found!")
        
        # Create backup mapping
        backup_path = create_backup_mapping(migrations)
        
        # Dry run update
        print("\n" + "=" * 70)
        print("STEP 4: DRY RUN - Simulating updates")
        print("=" * 70)
        
        dry_results = update_account_codes(db, migrations, dry_run=True)
        
        # Ask for confirmation
        print("\n" + "=" * 70)
        print("CONFIRMATION")
        print("=" * 70)
        print(f"\n[INFO] Summary:")
        print(f"  - Total accounts to update: {dry_results['total']}")
        print(f"  - Accounts that will be updated: {dry_results['updated']}")
        if dry_results['errors']:
            print(f"  - Errors: {len(dry_results['errors'])}")
        
        if not non_interactive:
            response = input("\n[WARN] Proceed with actual migration? (yes/no): ").strip().lower()
            if response != 'yes':
                print("[ERROR] Migration cancelled.")
                return
        else:
            print("\n[INFO] Non-interactive mode: Proceeding with migration...")
        
        # Actual update
        print("\n" + "=" * 70)
        print("STEP 5: APPLYING MIGRATION")
        print("=" * 70)
        
        results = update_account_codes(db, migrations, dry_run=False)
        
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETE")
        print("=" * 70)
        print(f"\n[OK] Successfully updated {results['updated']} account codes")
        print(f"[INFO] Backup mapping saved to: {backup_path}")
        
        if results['errors']:
            print(f"\n[WARN] {len(results['errors'])} errors occurred:")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("\n[INFO] Next steps:")
        print("  1. Verify account codes in database")
        print("  2. Test accounting functionality")
        print("  3. Update any hardcoded account codes in code (if needed)")
        print("  4. Keep backup file for rollback if needed")
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

