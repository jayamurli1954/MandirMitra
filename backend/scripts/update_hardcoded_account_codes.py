"""
Update Hardcoded Account Codes in Codebase

This script updates hardcoded account codes in Python files after migration.
It reads the migration backup file and updates all references.

IMPORTANT: Review all changes before committing!
"""

import re
import json
import sys
import io
from pathlib import Path
from typing import Dict, List, Tuple

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # If already wrapped or not available, continue


def load_migration_backup(backup_file: str = "account_code_migration_backup.json") -> Dict:
    """Load migration backup file"""
    backup_path = Path(__file__).parent.parent / backup_file
    
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    with open(backup_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_account_code_references(file_path: Path, old_code: str) -> List[Tuple[int, str]]:
    """
    Find all references to an account code in a file
    
    Returns:
        List of (line_number, line_content) tuples
    """
    matches = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Pattern to match account code references
        # Matches: A110', A110", account_code == A110", etc.
        patterns = [
            rf"['\"]{re.escape(old_code)}['\"]",  # String literals
            rf"account_code\s*==\s*['\"]{re.escape(old_code)}['\"]",  # Comparisons
            rf"account_code\s*=\s*['\"]{re.escape(old_code)}['\"]",  # Assignments
            rf"Account\.account_code\s*==\s*['\"]{re.escape(old_code)}['\"]",  # Model queries
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                if re.search(pattern, line):
                    matches.append((line_num, line.rstrip()))
                    break  # Only add once per line
    
    except Exception as e:
        print(f"  [WARN] Error reading {file_path}: {e}")
    
    return matches


def update_file_account_codes(file_path: Path, code_mapping: Dict[str, str], dry_run: bool = True) -> Dict:
    """
    Update account codes in a file
    
    Args:
        file_path: Path to file
        code_mapping: Dictionary mapping old_code -> new_code
        dry_run: If True, only show what would be changed
    
    Returns:
        Dictionary with results
    """
    results = {
        'file': str(file_path),
        'changes': [],
        'updated': False
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            original_content = content
        
        # Update each code mapping
        for old_code, new_code in code_mapping.items():
            # Pattern 1: String literals in quotes
            content = re.sub(
                rf"(['\"]){re.escape(old_code)}\1",
                rf"\1{new_code}\1",
                content
            )
            
            # Pattern 2: In account_code assignments/comparisons
            # This is more specific to avoid false positives
            patterns_replacements = [
                (rf"account_code\s*==\s*['\"]{re.escape(old_code)}['\"]", f"account_code == '{new_code}'"),
                (rf"account_code\s*=\s*['\"]{re.escape(old_code)}['\"]", f"account_code = '{new_code}'"),
                (rf"Account\.account_code\s*==\s*['\"]{re.escape(old_code)}['\"]", f"Account.account_code == '{new_code}'"),
            ]
            
            for pattern, replacement in patterns_replacements:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    results['changes'].append(f"{old_code} -> {new_code}")
        
        if content != original_content:
            results['updated'] = True
            
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  [OK] Updated: {file_path}")
            else:
                print(f"  [DRY] Would update: {file_path}")
                for change in results['changes']:
                    print(f"      {change}")
    
    except Exception as e:
        print(f"  [ERROR] Error updating {file_path}: {e}")
        results['error'] = str(e)
    
    return results


def main():
    """Main function"""
    import sys
    
    # Check for non-interactive mode
    non_interactive = '--yes' in sys.argv or '--non-interactive' in sys.argv
    
    print("=" * 70)
    print("UPDATE HARDCODED ACCOUNT CODES IN CODEBASE")
    print("=" * 70)
    print("\nThis script updates hardcoded account codes in Python files")
    print("based on the migration backup file.\n")
    
    # Load migration backup
    try:
        backup_data = load_migration_backup()
        migrations = backup_data.get('migrations', [])
        
        if not migrations:
            print("❌ No migrations found in backup file!")
            return
        
        # Create code mapping
        code_mapping = {mig['old_code']: mig['new_code'] for mig in migrations}
        
        print(f"📊 Found {len(code_mapping)} account codes to update:\n")
        for old_code, new_code in sorted(code_mapping.items()):
            print(f"  {old_code:>6} -> {new_code:>6}")
        
        # Find all Python files in backend
        backend_path = Path(__file__).parent.parent
        python_files = list(backend_path.rglob("*.py"))
        
        # Exclude certain directories
        exclude_dirs = {'__pycache__', '.git', 'venv', 'env', '.venv', 'node_modules'}
        python_files = [
            f for f in python_files 
            if not any(excluded in f.parts for excluded in exclude_dirs)
        ]
        
        print(f"\n[INFO] Scanning {len(python_files)} Python files...\n")
        
        # Find files with references
        files_to_update = []
        for file_path in python_files:
            for old_code in code_mapping.keys():
                matches = find_account_code_references(file_path, old_code)
                if matches:
                    files_to_update.append((file_path, old_code, matches))
        
        if not files_to_update:
            print("[OK] No hardcoded account codes found in codebase!")
            return
        
        # Group by file
        files_dict = {}
        for file_path, old_code, matches in files_to_update:
            if file_path not in files_dict:
                files_dict[file_path] = []
            files_dict[file_path].extend([(old_code, matches)])
        
        print(f"[INFO] Found references in {len(files_dict)} files:\n")
        for file_path, codes in files_dict.items():
            print(f"  {file_path.relative_to(backend_path)}")
            for old_code, matches in codes:
                print(f"    - {old_code} ({len(matches)} references)")
        
        # Dry run
        print("\n" + "=" * 70)
        print("DRY RUN - Preview of changes")
        print("=" * 70 + "\n")
        
        dry_results = []
        for file_path in files_dict.keys():
            result = update_file_account_codes(file_path, code_mapping, dry_run=True)
            if result['updated']:
                dry_results.append(result)
        
        if not dry_results:
            print("[OK] No files need updating!")
            return
        
        # Ask for confirmation
        print("\n" + "=" * 70)
        print("CONFIRMATION")
        print("=" * 70)
        print(f"\n[INFO] {len(dry_results)} files will be updated")
        
        if not non_interactive:
            response = input("\n[WARN] Proceed with updating files? (yes/no): ").strip().lower()
            if response != 'yes':
                print("[ERROR] Update cancelled.")
                return
        else:
            print("\n[INFO] Non-interactive mode: Proceeding with file updates...")
        
        # Actual update
        print("\n" + "=" * 70)
        print("UPDATING FILES")
        print("=" * 70 + "\n")
        
        results = []
        for file_path in files_dict.keys():
            result = update_file_account_codes(file_path, code_mapping, dry_run=False)
            if result['updated']:
                results.append(result)
        
        print("\n" + "=" * 70)
        print("UPDATE COMPLETE")
        print("=" * 70)
        print(f"\n[OK] Successfully updated {len(results)} files")
        print("\n[INFO] Next steps:")
        print("  1. Review all changes with: git diff")
        print("  2. Test the application")
        print("  3. Commit changes if everything works")
        
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        print("\n[INFO] Run the migration script first to create the backup file.")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

