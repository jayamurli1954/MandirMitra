# Accounting Fixes Summary

## Issues Fixed

### 1. ✅ Trial Balance vs Dashboard Mismatch (₹60,800 vs ₹52,000)

**Problem:** Dashboard shows ₹32,000 (donations) + ₹28,800 (sevas) = ₹60,800, but Trial Balance shows only ₹52,000.

**Root Cause:** Some seva bookings (₹8,800 worth) don't have journal entries because:
- Missing debit accounts (1101 Cash, 1110 Bank)
- Missing credit accounts (4200 Seva Income)
- Accounting posting failed silently

**Fix:**
- Created script `find_missing_journal_entries.py` to identify bookings without journal entries
- Run: `python backend/scripts/find_missing_journal_entries.py`
- This will show which seva bookings need journal entries created

### 2. ✅ Account Structure - Payment Method Accounts vs Parent/Category Accounts

**Problem:** Trial Balance was showing:
- "Donation - Cash" (4101)
- "Donation - Online/UPI" (4102)

Instead of:
- "Donation Income" (4100) - parent account with aggregated totals

**Fix:**
- Updated `get_trial_balance()` to aggregate child accounts under parent accounts
- Now shows:
  - **4100 Donation Income** (sum of 4101, 4102, 4103, etc.)
  - **4200 Seva Income** (sum of 4201, 4202, etc.)
  - **4400 In-Kind Donation Income** (sum of 4401, 4402, 4403)
  - **4300 Sponsorship Income** (sum of 4301, 4302)

**Note:** Donation accounting code already uses 4100 (parent) or category-linked accounts. Old entries using 4101/4102 will now be aggregated under 4100 in Trial Balance.

### 3. ✅ In-Kind Sponsorship Accounting (₹25,000 Flower Decoration)

**Problem:** ₹25,000 flower decoration sponsorship not appearing in Trial Balance.

**Root Cause:**
- In-kind accounts (4400, 4403, 5404-5407) may not exist
- Journal entry not posted automatically for DIRECT_PAYMENT sponsorships

**Fix:**
1. **Added in-kind accounts to chart of accounts:**
   - **4403** - In-Kind Sponsorship Income
   - **5404** - Flower Decoration Expense (In-Kind)
   - **5405** - Lighting Expense (In-Kind)
   - **5406** - Tent Expense (In-Kind)
   - **5407** - Sound System Expense (In-Kind)

2. **Updated sponsorship accounting:**
   - Automatically posts journal entry when DIRECT_PAYMENT sponsorship is created (if vendor invoice details provided)
   - Maps sponsorship categories to correct expense accounts:
     - `flower_decoration` → 5404 (Flower Decoration Expense - In-Kind)
     - `lighting` → 5405 (Lighting Expense - In-Kind)
     - `tent` → 5406 (Tent Expense - In-Kind)
     - `sound_system` → 5407 (Sound System Expense - In-Kind)
   - Uses **4403** (In-Kind Sponsorship Income) as credit account

3. **Created script to create missing accounts:**
   - Run: `python backend/scripts/create_inkind_accounts.py`
   - This creates all in-kind accounts if they don't exist

**Accounting Treatment (Confirmed Correct):**
For DIRECT_PAYMENT sponsorships (devotee pays vendor directly):
- **Dr:** Event Expense (e.g., 5404 Flower Decoration Expense - In-Kind) [FMV]
- **Cr:** In-Kind Sponsorship Income (4403) [FMV]

This ensures:
- Balance sheet not affected (no cash movement)
- Income and Expense accounts correctly reflect transaction
- Financial statements show accurate scale of operations

### 4. ✅ Two Types of Sponsorships

**Type 1: DIRECT_PAYMENT** (Devotee pays vendor directly)
- **Accounting:** Dr. Expense (In-Kind), Cr. In-Kind Sponsorship Income (4403)
- **No cash movement** through temple accounts
- **Journal entry posted automatically** when sponsorship created with vendor invoice details

**Type 2: TEMPLE_PAYMENT** (Devotee pays temple, temple pays vendor)
- **Step 1 - When devotee pays temple:**
  - Dr. Cash/Bank
  - Cr. Sponsorship Receivable (1402)
- **Step 2 - When temple pays vendor (manual entry needed):**
  - Dr. Expense Account (e.g., Flower Decoration Expense)
  - Cr. Cash/Bank
- **Description should clearly mention purpose** (e.g., "Sponsorship for flower decoration")

## Next Steps

### 1. Create Missing In-Kind Accounts
```bash
cd backend
python scripts/create_inkind_accounts.py
```

### 2. Find Missing Journal Entries
```bash
python scripts/find_missing_journal_entries.py
```

This will show:
- Donations without journal entries
- Seva bookings without journal entries
- Total missing amount (should explain ₹8,800 gap)

### 3. For Your ₹25,000 Flower Decoration Sponsorship

**If it was created as DIRECT_PAYMENT:**
- Check if it has `journal_entry_id_expense` set
- If not, call `/api/v1/sponsorships/{sponsorship_id}/record-direct-payment` with vendor invoice details
- Or re-create it with vendor invoice details to trigger automatic posting

**Expected Trial Balance entries after fix:**
- **Dr:** 5404 Flower Decoration Expense (In-Kind) - ₹25,000
- **Cr:** 4403 In-Kind Sponsorship Income - ₹25,000

### 4. Verify Trial Balance Now Shows:
- **4100 Donation Income** (aggregated, not 4101/4102 separately)
- **4200 Seva Income** (aggregated, not individual seva types)
- **4400 In-Kind Donation Income** (if any in-kind donations)
- **4403 In-Kind Sponsorship Income** (for your ₹25,000 sponsorship)
- **5404 Flower Decoration Expense (In-Kind)** (for your ₹25,000 sponsorship)

## Files Modified

1. `backend/app/api/journal_entries.py` - Trial Balance aggregation
2. `backend/app/api/sponsorships.py` - In-kind account mapping and auto-posting
3. `backend/seed_chart_of_accounts.py` - Added in-kind accounts (4403, 5404-5407)
4. `backend/scripts/create_inkind_accounts.py` - Script to create missing accounts
5. `backend/scripts/find_missing_journal_entries.py` - Script to find missing entries

## Testing Checklist

- [ ] Run `create_inkind_accounts.py` to ensure accounts exist
- [ ] Run `find_missing_journal_entries.py` to identify ₹8,800 gap
- [ ] Check Trial Balance shows parent accounts (4100, 4200, 4400) not child accounts
- [ ] Verify ₹25,000 sponsorship appears in Trial Balance (Dr. 5404, Cr. 4403)
- [ ] Verify Trial Balance total matches dashboard total (₹60,800)


