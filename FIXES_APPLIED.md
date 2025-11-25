# Fixes Applied - Multiple Issues

## Issues Fixed

### 1. ✅ Added Donation Categories API Endpoint
**Problem:** `/api/v1/donations/categories/` was returning 404

**Fix:** Added new endpoint in `backend/app/api/donations.py`:
```python
@router.get("/categories/", response_model=List[dict])
def get_donation_categories(...)
```

**Result:** Frontend can now fetch donation categories for dropdowns

---

### 2. ✅ Fixed Panchang Sunrise/Sunset Calculation Error
**Problem:** `TypeError: 'float' object cannot be interpreted as an integer`

**Root Cause:** `swe.julday()` was receiving float values for year/month/day

**Fix:** Changed in `backend/app/services/panchang_service.py`:
- `swe.julday(dt.year, dt.month, dt.day, 0.0)` → `swe.julday(int(dt.year), int(dt.month), int(dt.day), 0.0)`
- Applied to both `get_sun_rise_set()` and `get_moon_rise_set()` functions

**Result:** Panchang calculations will no longer throw errors

---

### 3. ✅ Fixed Dashboard Layout - Side by Side
**Problem:** Quick donation entry and Panchang were stacked vertically, Panchang not visible

**Fix:** Changed layout in `frontend/src/pages/Dashboard.js`:
- Donation form: `xs={12} md={6}` (left side)
- Panchang display: `xs={12} md={6}` (right side)
- Both now display side by side on medium+ screens

**Result:** Both donation form and Panchang are visible side by side

---

### 4. ✅ Created Database Migration Script
**Problem:** `column seva_bookings.original_booking_date does not exist` - reschedule fields missing

**Fix:** Created `backend/scripts/run_reschedule_migration.py` to add:
- `original_booking_date`
- `reschedule_requested_date`
- `reschedule_reason`
- `reschedule_approved`
- `reschedule_approved_by`
- `reschedule_approved_at`

**Action Required:** Run the migration script:
```bash
cd backend
python scripts/run_reschedule_migration.py
```

---

### 5. ⚠️ Donation Accounting Logic Review
**Status:** The code in `post_donation_to_accounting()` already prioritizes category-linked accounts:
- First tries to use `donation.category.account_id` (category-linked account)
- Only falls back to default account (4101) if category not linked
- Does NOT use payment-mode accounts (4102, 4103) anymore

**Issue:** If trial balance still shows wrong accounts, it means:
1. Existing journal entries were created with wrong accounts (before fix)
2. Categories are not linked to accounts
3. Need to run `link_accounts_to_categories_sevas.py` script

**Action Required:**
1. Link donation categories to accounts (run linking script)
2. Fix existing wrong entries (run `fix_wrong_account_entries.py`)

---

## Remaining Issues

### 1. Dashboard vs Reports Discrepancy
**Problem:** Dashboard shows ₹12,000 but reports show ₹10,000

**Possible Causes:**
- Different date filters
- Reports filtering by different criteria
- Cached data

**Action:** Check date ranges in reports match dashboard period

---

### 2. Trial Balance - No Seva Collection
**Problem:** Trial balance shows ₹12,000 donation but no seva collection (₹4,800)

**Possible Causes:**
- Seva bookings not posting to accounting
- Seva accounts not linked
- Seva journal entries missing

**Action:** 
1. Check if seva bookings have journal entries
2. Run `backfill_seva_journal_entries.py` if missing
3. Verify seva accounts are linked

---

### 3. Trial Balance - Wrong Credit Accounts
**Problem:** Credits going to "Donation - Cash" and "Donation - Online/UPI" instead of category accounts

**Root Cause:** Old journal entries created before the fix

**Action Required:**
1. **Link categories to accounts:**
   ```bash
   cd backend
   python scripts/link_accounts_to_categories_sevas.py
   ```

2. **Fix existing wrong entries:**
   ```bash
   python scripts/fix_wrong_account_entries.py
   ```

3. **Verify categories are linked:**
   - Check `donation_categories` table has `account_id` set
   - Check `sevas` table has `account_id` set

---

## Next Steps

### Immediate Actions:

1. **Run database migration:**
   ```bash
   cd backend
   python scripts/run_reschedule_migration.py
   ```

2. **Link accounts to categories:**
   ```bash
   python scripts/link_accounts_to_categories_sevas.py
   ```

3. **Fix existing wrong accounting entries:**
   ```bash
   python scripts/fix_wrong_account_entries.py
   ```

4. **Backfill missing seva journal entries:**
   ```bash
   python scripts/backfill_seva_journal_entries.py
   ```

5. **Restart backend** to apply code fixes:
   ```bash
   # Stop current server (Ctrl+C)
   uvicorn app.main:app --reload --port 8000
   ```

6. **Refresh frontend** to see layout changes

---

## Files Modified

1. `backend/app/api/donations.py` - Added `/categories/` endpoint
2. `backend/app/services/panchang_service.py` - Fixed float to int conversion
3. `frontend/src/pages/Dashboard.js` - Fixed layout (side by side)
4. `backend/scripts/run_reschedule_migration.py` - New migration script

---

## Testing Checklist

After applying fixes:

- [ ] Donation categories endpoint works (no 404)
- [ ] Panchang loads without errors (no float/int errors)
- [ ] Dashboard shows donation form and Panchang side by side
- [ ] Seva reports work (after running migration)
- [ ] Trial balance shows correct accounts (after linking and fixing)
- [ ] Seva collection appears in trial balance (after backfilling)

---

## Notes

- The donation accounting logic is correct - it prioritizes category accounts
- The issue is likely old entries created before the fix
- Need to run linking and fixing scripts to correct historical data
- New donations will automatically use correct accounts if categories are linked



