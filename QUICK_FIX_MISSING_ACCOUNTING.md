# Quick Fix: Missing ₹11,000 in Trial Balance

## Problem
Out of ₹12,000 in donations received, only ₹1,000 is showing in trial balance. ₹11,000 is missing.

## Root Cause
The missing donations don't have journal entries created. This happens when:
1. Donations were created before the accounting integration was fixed
2. Journal entry creation failed silently
3. Accounts weren't linked properly

## Solution: Run Backfill Script

### Step 1: Run the Diagnostic (Optional)
Check what's missing:
```bash
cd backend
python -m scripts.check_missing_journal_entries
```

### Step 2: Run Backfill Script
Create journal entries for all missing donations:

```bash
cd backend
python -m scripts.backfill_donation_journal_entries
```

This will:
- Find all donations without journal entries
- Create journal entries for them
- Post them automatically
- Show progress and any errors

### Step 3: Verify
After running the script:
1. Check trial balance - should now show ₹12,000
2. Verify journal entries were created:
   ```sql
   SELECT COUNT(*) FROM journal_entries WHERE reference_type = 'donation';
   ```
3. Check that entries are POSTED:
   ```sql
   SELECT COUNT(*) FROM journal_entries 
   WHERE reference_type = 'donation' AND status = 'posted';
   ```

## If Backfill Fails

### Error: "Account not found"
**Solution:** Link accounts to donation categories first:
```bash
python -m scripts.link_accounts_to_categories_sevas
```

### Error: "Category has no account"
**Solution:** 
1. Create the required accounts in Chart of Accounts (4101, 4102, etc.)
2. Link them to categories using the linking script
3. Re-run backfill

### Error: "Debit account not found"
**Solution:**
Create these accounts in Chart of Accounts:
- `1101` - Cash in Hand - Counter
- `1102` - Cash in Hand - Hundi  
- `1110` - Bank - SBI Current Account

## Expected Output

When backfill runs successfully, you should see:
```
Found X donations without journal entries
Processing donation TMP001-2025-00001...
  ✓ Created journal entry: JE/2025/0001
Processing donation TMP001-2025-00002...
  ✓ Created journal entry: JE/2025/0002
...
✓ Successfully created X journal entries
```

## After Backfill

1. **Check Trial Balance:**
   - Go to Accounting → Trial Balance
   - Select today's date
   - Should now show ₹12,000 in donation income accounts

2. **Check Reports:**
   - Profit & Loss report should show correct income
   - Category Income report should show donations by category

3. **Verify Journal Entries:**
   - Go to Accounting → Journal Entries
   - Should see entries for all donations

## Troubleshooting

### Still showing ₹1,000 after backfill?

**Check:**
1. Are journal entries POSTED? (not DRAFT)
2. Are accounts correctly linked?
3. Are entry dates within the report date range?
4. Check for errors in backfill script output

**Debug SQL:**
```sql
-- Check journal entries
SELECT 
    je.id,
    je.entry_number,
    je.status,
    je.total_amount,
    je.entry_date,
    d.receipt_number,
    d.amount
FROM journal_entries je
JOIN donations d ON je.reference_id = d.id
WHERE je.reference_type = 'donation'
ORDER BY je.id DESC;

-- Check journal lines
SELECT 
    a.account_code,
    a.account_name,
    SUM(jl.credit_amount) as total_credit
FROM journal_lines jl
JOIN journal_entries je ON jl.journal_entry_id = je.id
JOIN accounts a ON jl.account_id = a.id
WHERE je.reference_type = 'donation'
  AND je.status = 'posted'
  AND a.account_code LIKE '41%'
GROUP BY a.account_code, a.account_name;
```

---

**Quick Command:**
```bash
cd backend && python -m scripts.backfill_donation_journal_entries
```

This should fix the missing ₹11,000!

