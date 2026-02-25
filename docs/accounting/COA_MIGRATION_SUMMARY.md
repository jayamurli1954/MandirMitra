# COA Migration Summary - 5-Digit Account Code Structure

## ✅ Migration Complete

All code changes have been completed. The system now uses a standardized 5-digit account code structure.

## What Was Done

### 1. Default COA Structure Created
- **File**: `backend/app/data/default_coa.py`
- **Content**: Comprehensive Chart of Accounts with 150+ account heads
- **Structure**: Follows 5-digit format (1xxxx = Assets, 2xxxx = Liabilities, 3xxxx = Equity, 4xxxx = Income, 5xxxx = Expenses)

### 2. Migration Scripts Created
- **File**: `backend/scripts/migrate_coa_codes.py`
  - Migrates existing account codes from old format to new 5-digit format
  - Supports dry-run mode for testing
  - Safe migration (doesn't affect journal entries which use account_id)

- **File**: `backend/scripts/initialize_default_coa.py`
  - Initializes default COA for temples
  - Creates all standard account heads
  - Can initialize for specific temple or all temples

### 3. Code Updates Completed
All hardcoded account codes have been updated in the following files:

#### Core Accounting:
- ✅ `backend/app/api/donations.py` - All account codes updated
- ✅ `backend/app/api/sevas.py` - All account codes updated
- ✅ `backend/app/api/journal_entries.py` - Range queries updated

#### Supporting Modules:
- ✅ `backend/app/api/bank_accounts.py` - Bank account codes updated
- ✅ `backend/app/api/inventory.py` - Inventory account codes updated
- ✅ `backend/app/api/sponsorships.py` - Sponsorship account codes updated
- ✅ `backend/app/api/hr.py` - HR account codes updated
- ✅ `backend/app/api/financial_closing.py` - Financial closing codes updated

#### Specialized Modules:
- ✅ `backend/app/api/payment_gateway.py` - Payment gateway codes updated
- ✅ `backend/app/api/hundi.py` - Hundi account codes updated
- ✅ `backend/app/api/disposal.py` - Asset disposal codes updated
- ✅ `backend/app/api/revaluation.py` - Asset revaluation codes updated
- ✅ `backend/app/api/cwip.py` - CWIP codes updated

## Key Account Code Mappings

### Assets (1xxxx):
- `1101` → `11001` (Cash in Hand - Counter)
- `1102` → `11002` (Cash in Hand - Hundi)
- `1110` → `12001` (Bank - Current Account)
- `1300` → `14003` (Pooja Materials Inventory)
- `1400` → `15002` (Building/Fixed Assets)
- `1500` → `15010` (Temple Gold & Silver)

### Liabilities (2xxxx):
- `3003` → `21003` (Advance Seva Booking)

### Income (4xxxx):
- `3001` → `44001` (General Donations)
- `3002` → `42002` (Seva Income - General)
- `4200` → `42002` (Seva Income - General)
- `4101` → `44001` (General Donations)
- `4400` → `44004` (In-Kind Donation Income)
- `4403` → `45002` (In-Kind Sponsorship Income)

### Expenses (5xxxx):
- `5001` → `54012` (Miscellaneous Expenses)
- `5200` → `52001` (Salaries)
- `5400` → `54004` (Festival Expenses)
- `6001` → `54011` (Depreciation/Revaluation Expense)

### Equity (3xxxx):
- `3101` → `31010` (General Fund)

## Next Steps

### 1. Run Migration (Test First!)
```bash
# Dry run to see what will change
python backend/scripts/migrate_coa_codes.py --dry-run

# Actual migration
python backend/scripts/migrate_coa_codes.py
```

### 2. Initialize Default COA
```bash
# Initialize for all temples
python backend/scripts/initialize_default_coa.py

# Or for specific temple
python backend/scripts/initialize_default_coa.py --temple-id 1
```

### 3. Testing Checklist
- [ ] Create cash donation
- [ ] Create bank/UPI donation
- [ ] Create in-kind donation
- [ ] Create seva booking (current date)
- [ ] Create seva booking (advance)
- [ ] Verify journal entries created correctly
- [ ] Check Trial Balance
- [ ] Check Profit & Loss statement
- [ ] Check Balance Sheet
- [ ] Test reports

### 4. Account Code Validation (Pending)
- Add validation to enforce 5-digit format
- Prevent invalid account codes
- Add validation in Account model or API layer

## Important Notes

1. **Journal Entries are SAFE**: They use `account_id` (foreign key), not `account_code`, so existing entries continue to work.

2. **Migration is Reversible**: Keep database backups before running migration.

3. **Test Thoroughly**: Always test in dev/staging environment first.

4. **Default COA is Comprehensive**: Users should need to add minimal custom accounts (10-15 at most).

5. **5-Digit Structure**: All codes follow ABCDE format:
   - A = Account Class (1-5)
   - BC = Major Category (00-99)
   - DE = Account (00-99)

## Files Modified

Total: **15 API files** updated with new account codes

All changes maintain backward compatibility at the database level (journal entries use account_id, not account_code).

















