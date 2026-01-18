# Account Code Migration - Ready to Execute

## Preview Results

Found **25 accounts** that need standardization:

| Old Code | New Code | Account Name |
|----------|----------|--------------|
| 1001 | 01001 | Cash in Hand |
| 1000 | 01000 | Assets |
| 4000 | 04000 | Income |
| 1110 | 01110 | Bank - SBI Current Account |
| 5101 | 05101 | Priest Salary |
| ... | ... | ... (25 total) |

## How to Run the Migration

The migration script is ready but requires **interactive confirmation** for safety.

### Step 1: Open Terminal/Command Prompt

Navigate to the backend directory:
```bash
cd d:\MandirMitra\backend
```

### Step 2: Run the Migration Script

```bash
python scripts\standardize_account_codes.py
```

### Step 3: Follow the Prompts

The script will:
1. Ask if you've backed up the database → Type **yes**
2. Show a dry run preview (what will change)
3. Check for code collisions
4. Create a backup mapping file
5. Ask for final confirmation → Type **yes** to proceed

### Step 4: Update Codebase (After Migration)

After the database migration completes, run:

```bash
python scripts\update_hardcoded_account_codes.py
```

This will update all hardcoded account codes in Python files.

## Safety Features

✅ **Dry Run First** - Shows what will change before applying
✅ **Backup File** - Creates `account_code_migration_backup.json` for rollback
✅ **Collision Detection** - Automatically resolves code conflicts
✅ **Transaction-Based** - All changes in one transaction, rollback on error
✅ **No Data Loss** - Uses foreign keys (account_id), not account_code

## Important Notes

1. **Backup First**: Always backup your database before running migrations
2. **Test First**: Consider testing on a copy of your database
3. **Review Changes**: The script shows exactly what will change
4. **Keep Backup File**: The backup mapping file allows rollback if needed

## Next Steps After Migration

1. Verify account codes are all 5 digits
2. Test the application (donations, sevas, expenses, reports)
3. Commit the changes if everything works
4. Delete the backup file once confirmed working (or keep for records)

---

**Ready to proceed?** Run the migration script in your terminal!




