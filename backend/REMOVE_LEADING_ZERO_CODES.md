# Remove Leading Zero Account Codes

## Problem
Account codes starting with '0' (01101, 01102, 01110) are being used alongside non-0-prefixed codes (11001, 11002, 12001), causing:
- Expenses crediting to 01101/01110
- Donations/receipts debiting to 11001/12001
- Duplicate accounts in trial balance

## Solution Applied

### 1. Updated Backend Code
- ✅ `backend/app/core/bank_account_helper.py` - Changed from 01101/01102 to 11001/11002
- ✅ `backend/app/api/donations.py` - Updated fallback codes from 01101/01102 to 11001/11002
- ✅ Error messages updated to reflect correct codes

### 2. Updated Frontend Code
- ✅ `frontend/src/pages/accounting/QuickExpense.js` - Updated cash account lookups from 01101/01102 to 11001/11002

### 3. Current State
**Accounts in Database:**
- 01101 - Cash - Counter (OLD - should not be used)
- 01102 - Cash - Hundi (OLD - should not be used)
- 01110 - Bank - SBI Current Account (OLD - should not be used)
- 11001 - Cash in Hand - Counter (CORRECT - use this)
- 11002 - Cash in Hand - Hundi (CORRECT - use this)
- 12001 - Bank - SBI Current Account (CORRECT - use this)

### 4. What Changed
All new transactions will now use:
- Cash payments: 11001 (Counter) or 11002 (Hundi)
- Bank payments: 12001 (via BankAccount model's chart_account_id)

### 5. Existing Data
Existing journal entries that reference 01101, 01102, or 01110 will still appear in reports. These are historical transactions and should remain for audit purposes.

**Note:** If you want to migrate existing journal entries from old codes to new codes, this requires a database migration script. Consult with your accountant before doing this.

## Next Steps
1. ✅ Restart backend server
2. ✅ Test new expenses - should credit to 11001/12001
3. ✅ Test new donations - should debit to 11001/12001
4. ✅ Verify trial balance shows correct accounts for new transactions

## Future Cleanup (Optional)
If you want to remove the old 0-prefixed accounts from the database:
1. Ensure no active transactions reference them
2. Update any remaining journal entries (requires migration)
3. Delete or mark inactive the old accounts (01101, 01102, 01110)

**Warning:** Do not delete accounts if they have journal entry references, as this will break foreign key relationships.




