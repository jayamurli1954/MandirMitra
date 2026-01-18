# Bank Account Mapping Fix

## Problem
- Expenses were crediting to account code `01110` (Bank - SBI Current Account)
- Donations were debiting to account code `12001` (Main Bank Account)
- User wants both to use account code `12001` (Bank - SBI Current Account)
- User doesn't want account codes starting with '0'

## Solution Applied

### 1. Database Updates
- ✅ Updated account code `12001` name from "Main Bank Account" to "Bank - SBI Current Account"
- ✅ Verified `bank_accounts` table points to account ID 9 (code 12001)
- ✅ Removed fallback references to account code `01110`

### 2. Code Updates
- ✅ Updated `bank_accounts.py` to only use account code `12001` (removed `01110` fallback)
- ✅ Bank account helper functions already use `chart_account_id` from BankAccount model, which now points to 12001

### 3. Current State
- **Bank Account Record**: Points to Chart Account ID 9 (code 12001)
- **Account 12001**: Name = "Bank - SBI Current Account"
- **Future Transactions**: Will use account code 12001 via BankAccount model's `chart_account_id`

### 4. Existing Data
- Existing journal entries that reference account `01110` will still show in reports
- New transactions (donations, expenses) will use account `12001`
- The account `01110` still exists in the database but won't be used for new transactions

### 5. Next Steps (If Needed)
If you want to migrate existing journal entries from `01110` to `12001`:
1. Create a migration script to update journal_lines.account_id
2. This requires careful consideration of existing transactions
3. Consult with accountant before merging accounts

## Verification
- Bank Account: SBI Current Account (ID: 1)
- Chart Account ID: 9
- Chart Account Code: 12001
- Chart Account Name: Bank - SBI Current Account

## Notes
- Account code `01110` still exists in the database but is no longer referenced in code
- Both donations and expenses now use the bank account's `chart_account_id` which points to 12001
- The QuickExpense frontend uses bank accounts from the API, so it will automatically use 12001




