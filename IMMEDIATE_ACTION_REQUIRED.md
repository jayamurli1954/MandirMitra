# Immediate Action Required - Fix Trial Balance

## Problem Summary

Your trial balance shows:
- **1101 Cash**: ₹12,000 (debit) ✓ CORRECT
- **4101 Donation - Cash**: ₹6,500 (credit) ✓ CORRECT  
- **4102 Donation - Online/UPI**: ₹5,500 (credit) ✗ **WRONG** - Should be 0

**All donations are cash**, but ₹5,500 is being credited to the wrong account (4102 - Online/UPI).

## Root Cause

Donations are being credited to **payment-mode accounts** (4102, 4103) instead of **category-linked accounts** (4101, 4111, 4112, etc.).

## Solution - 3 Steps

### Step 1: Link Categories to Accounts

Run the linking script to connect donation categories to your accounts:

```bash
cd backend
python -m scripts.link_accounts_to_categories_sevas
```

**Before running**, edit the script and add your category names:

```python
CATEGORY_ACCOUNT_MAPPING = {
    "General Donation": "4101",
    "Construction Fund": "4111",  # Your actual category name
    "Annadanam": "4112",           # Your actual category name
    "Festival Donation": "4113",   # Your actual category name
    "Maintenance": "4114",         # Your actual category name
    # Add all your categories here
}
```

### Step 2: Fix Existing Journal Entries

After linking, fix the existing wrong entries:

```bash
python -m scripts.fix_wrong_account_entries
```

This will:
- Find entries using wrong accounts (4102, 4103, 4104)
- Update them to use category-linked accounts
- Show what was fixed

### Step 3: Verify

1. Check trial balance again
2. Should now show:
   - 1101 Cash: ₹12,000 (debit)
   - 4101 General Donation: ₹X (credit)
   - 4111 Construction Fund: ₹X (credit)
   - 4112 Annadanam: ₹X (credit)
   - etc. (by category)
   - **4102 should be ₹0**

## For New Donations

After Step 1, all **new donations** will automatically use category-linked accounts. The code has been fixed to prioritize category accounts.

## Seva Accounting Fix

For "Sarva Seva" booking that didn't create accounting entry:

1. **Link the seva to an account:**
   ```bash
   # Edit backend/scripts/link_accounts_to_categories_sevas.py
   # Add to SEVA_ACCOUNT_MAPPING:
   "Sarva Seva": "4203"  # or appropriate account code
   ```

2. **Run linking script:**
   ```bash
   python -m scripts.link_accounts_to_categories_sevas
   ```

3. **Re-run seva backfill:**
   ```bash
   python -m scripts.backfill_seva_journal_entries
   ```

## Quick Test

After fixing, create a test donation:
1. Create a new donation (₹100, Cash, any category)
2. Check journal entry - should use category-linked account
3. Check trial balance - should show in correct category account

---

**Priority:** Do Step 1 and Step 2 immediately to fix the trial balance!









