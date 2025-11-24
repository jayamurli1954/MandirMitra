# Fix Accounting Issues - Step by Step Guide

## Problem
Donations and seva collections are not reflecting in accounts/reports. All reports show '0'.

## Root Causes
1. **Existing donations/sevas don't have journal entries** - Need to run backfill
2. **Missing accounts** - Required accounts may not exist
3. **Journal entries in DRAFT status** - Need to be POSTED
4. **Date field error** - Fixed (Donation.date → Donation.donation_date)

---

## Step 1: Run Diagnostic Script

First, check what's wrong:

```bash
cd backend
python -m scripts.diagnose_accounting_issues
```

This will show:
- How many donations/bookings exist
- How many have journal entries
- Which accounts are missing
- Status of journal entries

---

## Step 2: Check Required Accounts

Run the account checker:

```bash
cd backend
python -m scripts.check_accounts
```

**Required accounts:**
- `1101`: Cash in Hand - Counter
- `1102`: Cash in Hand - Hundi
- `1110`: Bank - SBI Current Account
- `4101`: General Donation Income
- `4102`: Cash Donation Income
- `4103`: Online/UPI Donation Income
- `4104`: Hundi Collection Income
- `4208`: Special Pooja Income (for sevas)

**If accounts are missing:**
1. Go to Chart of Accounts page in UI
2. Create the missing accounts
3. Or use the seed script: `python seed_chart_of_accounts.py`

---

## Step 3: Backfill Existing Donations

If you have existing donations without journal entries:

```bash
cd backend
python -m scripts.backfill_donation_journal_entries
```

This will:
- Find all donations without journal entries
- Create journal entries for them
- Post them automatically

**Expected output:**
```
Found X donations without journal entries
Processing donation TMP001-2025-00001...
  ✓ Created journal entry: JE/2025/0001
```

---

## Step 4: Backfill Existing Seva Bookings

If you have existing seva bookings without journal entries:

```bash
cd backend
python -m scripts.backfill_seva_journal_entries
```

---

## Step 5: Verify Journal Entries

Check if journal entries were created:

```sql
-- In PostgreSQL
SELECT COUNT(*) FROM journal_entries WHERE status = 'posted';
SELECT COUNT(*) FROM journal_entries WHERE reference_type = 'donation';
SELECT COUNT(*) FROM journal_entries WHERE reference_type = 'seva';
```

Or use the diagnostic script again to verify.

---

## Step 6: Check Trial Balance

After backfilling, check the trial balance:

1. Go to Accounting → Trial Balance
2. Select a date (e.g., today)
3. You should see accounts with balances

**If still showing 0:**
- Check if journal entries are POSTED (not DRAFT)
- Check if account codes match
- Check if entry dates are within the date range

---

## Common Issues & Solutions

### Issue 1: "Accounts not found" error
**Solution:** Create the required accounts (see Step 2)

### Issue 2: Journal entries created as DRAFT
**Solution:** The code should create them as POSTED. If not, check:
- `post_donation_to_accounting()` function
- `post_seva_to_accounting()` function
- Both should set `status=JournalEntryStatus.POSTED`

### Issue 3: Reports show 0 even after backfill
**Possible causes:**
- Date filter is wrong (check report date range)
- Journal entries have wrong dates
- Accounts don't match (check account codes)

### Issue 4: Backfill script fails
**Check:**
- Database connection
- Required accounts exist
- Donation/seva data is valid
- Error messages in console

---

## Quick Test

After fixing, test with a new donation:

1. Create a new donation (₹100)
2. Check if journal entry is created
3. Check trial balance - should show:
   - Cash account: ₹100 debit
   - Donation income account: ₹100 credit

---

## Verification Checklist

- [ ] Diagnostic script runs without errors
- [ ] All required accounts exist
- [ ] Backfill script completed successfully
- [ ] Journal entries are POSTED (not DRAFT)
- [ ] Trial balance shows non-zero balances
- [ ] Reports show correct amounts
- [ ] New donations create journal entries automatically

---

## Still Having Issues?

1. **Check backend logs** for errors
2. **Run diagnostic script** to see what's wrong
3. **Check database directly**:
   ```sql
   SELECT * FROM journal_entries ORDER BY id DESC LIMIT 10;
   SELECT * FROM journal_lines ORDER BY id DESC LIMIT 10;
   ```
4. **Verify account codes** match between donations and accounts

---

## Fixed Issues

✅ **Donation.date error** - Changed to `Donation.donation_date` in top donors report
✅ **Error handling** - Added global error handlers
✅ **Journal entry creation** - Fixed status and enum usage

---

**Last Updated:** November 2025


