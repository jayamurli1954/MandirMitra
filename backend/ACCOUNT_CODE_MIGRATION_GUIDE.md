# Account Code Standardization Migration Guide

## Overview

This migration standardizes all account codes to a uniform 5-digit format with leading zeros.

**Standard Format:** All account codes must be exactly 5 digits (e.g., `01110`, `05101`, `11001`)

## Migration Scripts

### 1. `standardize_account_codes.py` - Database Migration

This script:
- Finds all accounts with non-5-digit codes
- Updates them to 5-digit format (pads with leading zeros)
- Handles code collisions automatically
- Creates a backup mapping file for rollback
- Safe: Uses foreign keys (account_id), so journal_lines don't need updating

**Usage:**
```bash
cd backend
python scripts/standardize_account_codes.py
```

**What it does:**
- `1110` → `01110`
- `5101` → `05101`
- `11001` → `11001` (already correct)
- `12001` → `12001` (already correct)

**Safety Features:**
- ✅ Dry run mode (shows changes before applying)
- ✅ Collision detection and resolution
- ✅ Backup mapping file created
- ✅ Transaction-based (rollback on error)
- ✅ JournalLines use account_id (foreign key), so no data loss

### 2. `update_hardcoded_account_codes.py` - Codebase Update

This script:
- Reads the migration backup file
- Finds all hardcoded account codes in Python files
- Updates them to the new 5-digit format
- Shows preview before making changes

**Usage:**
```bash
cd backend
python scripts/update_hardcoded_account_codes.py
```

**What it updates:**
- String literals: `'1110'` → `'01110'`
- Comparisons: `account_code == "1110"` → `account_code == "01110"`
- Model queries: `Account.account_code == "1110"` → `Account.account_code == "01110"`

## Migration Steps

### Step 1: Backup Database
```bash
# PostgreSQL
pg_dump -U postgres temple_db > backup_before_migration.sql

# SQLite (if using)
cp temple.db temple.db.backup
```

### Step 2: Run Database Migration
```bash
cd backend
python scripts/standardize_account_codes.py
```

Follow the prompts:
1. Confirm you've backed up the database
2. Review the dry run output
3. Confirm to proceed with actual migration

### Step 3: Verify Database Changes
```sql
-- Check account codes are all 5 digits
SELECT account_code, account_name 
FROM accounts 
WHERE LENGTH(account_code) != 5;

-- Should return no rows
```

### Step 4: Update Codebase
```bash
cd backend
python scripts/update_hardcoded_account_codes.py
```

Review the changes:
```bash
git diff
```

### Step 5: Test Application
1. Start the application
2. Test key functionality:
   - Record a donation
   - Record a seva booking
   - Create an expense
   - View trial balance
   - Generate reports

### Step 6: Commit Changes
```bash
git add .
git commit -m "Standardize account codes to 5-digit format"
```

## Rollback (If Needed)

If something goes wrong, you can rollback using the backup mapping:

```python
# Rollback script (create if needed)
import json
from app.core.database import SessionLocal
from app.models.accounting import Account

backup_file = "account_code_migration_backup.json"
with open(backup_file, 'r') as f:
    backup = json.load(f)

db = SessionLocal()
try:
    for mig in backup['migrations']:
        account = db.query(Account).filter(Account.id == mig['id']).first()
        if account:
            account.account_code = mig['old_code']
    db.commit()
    print("✅ Rollback complete")
except Exception as e:
    db.rollback()
    print(f"❌ Rollback failed: {e}")
finally:
    db.close()
```

## Impact on Existing Modules

### ✅ Safe (No Changes Needed)
- **Journal Entries**: Use `account_id` (foreign key), not `account_code`
- **Journal Lines**: Use `account_id` (foreign key)
- **Bank Accounts**: Use `chart_account_id` (foreign key)
- **Donation Categories**: Use `account_id` (foreign key)

### ⚠️ Needs Update (Handled by Script)
- Hardcoded account codes in:
  - `backend/app/api/donations.py`
  - `backend/app/api/sevas.py`
  - `backend/app/api/bank_accounts.py`
  - `backend/app/core/bank_account_helper.py`
  - Other API files with hardcoded codes

## Common Account Codes

After migration, common codes will be:

| Old Code | New Code | Account Name |
|----------|----------|--------------|
| 1110 | 01110 | Bank - SBI Current Account |
| 1101 | 01101 | Cash in Hand - Counter |
| 5101 | 05101 | Priest Salary |
| 11001 | 11001 | Cash in Hand - Counter (already correct) |
| 12001 | 12001 | Bank - Current Account (already correct) |
| 21003 | 21003 | Advance Seva Booking (already correct) |
| 42002 | 42002 | Seva Income (already correct) |
| 44001 | 44001 | Donation Income (already correct) |

## Notes

1. **Foreign Keys**: The migration is safe because:
   - `JournalLine.account_id` → `Account.id` (not account_code)
   - `BankAccount.chart_account_id` → `Account.id` (not account_code)
   - All relationships use IDs, not codes

2. **Unique Constraint**: Account codes have a unique constraint, so collisions are detected and resolved automatically.

3. **Backup File**: The migration creates `account_code_migration_backup.json` in the backend root directory. Keep this for rollback if needed.

4. **Testing**: Always test on a copy of production data first!

## Troubleshooting

### Error: "Account code already exists"
- The migration script handles collisions automatically
- It will find the next available code if collision occurs

### Error: "Foreign key constraint violation"
- This shouldn't happen (we use account_id, not account_code)
- If it does, check for any custom code that references account_code directly

### Some codes not updated
- Check if the account code has non-numeric characters
- The script only updates numeric codes
- Manual review may be needed for special cases

## Support

If you encounter issues:
1. Check the backup file: `account_code_migration_backup.json`
2. Review the migration logs
3. Test on a copy of production data first
4. Contact support if needed




