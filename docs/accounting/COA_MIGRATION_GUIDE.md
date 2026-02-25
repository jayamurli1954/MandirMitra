# COA Migration Guide - 5-Digit Account Code Structure

## Overview

This document tracks the migration from inconsistent account codes to a standardized 5-digit structure following industry best practices.

## Account Code Structure

```
A B C D E
│ │ │ │ └─ Sub-account (00-99)
│ │ │ └── Account group (00-99)
│ │ └──── Sub-category (00-99)
│ └────── Major category (0-9)
└──────── Account class (1-5)
```

### Account Classes (1st Digit):
- **1xxxx** = Assets
- **2xxxx** = Liabilities
- **3xxxx** = Equity
- **4xxxx** = Income
- **5xxxx** = Expenses

## Migration Status

### ✅ Completed:
1. Default COA structure created (`backend/app/data/default_coa.py`)
2. Migration script created (`backend/scripts/migrate_coa_codes.py`)
3. Initialization script created (`backend/scripts/initialize_default_coa.py`)
4. `backend/app/api/donations.py` - All account codes updated
5. `backend/app/api/sevas.py` - All account codes updated

### 🔄 In Progress:
6. Other API files (journal_entries, inventory, hr, bank_accounts, sponsorships, etc.)

### ⏳ Pending:
7. Account code validation
8. Testing and verification

## Key Account Code Mappings

### Assets:
- `1101` → `11001` (Cash in Hand - Counter)
- `1102` → `11002` (Cash in Hand - Hundi)
- `1110` → `12001` (Bank - Current Account)
- `1300` → `14003` (Pooja Materials Inventory)
- `1400` → `15002` (Building/Fixed Assets)
- `1500` → `15010` (Temple Gold & Silver)

### Liabilities:
- `3003` → `21003` (Advance Seva Booking)

### Income:
- `3001` → `44001` (General Donations)
- `3002` → `42002` (Seva Income - General)
- `4200` → `42002` (Seva Income - General)

### Expenses:
- Various old codes → New 5-digit codes

## Files to Update

### High Priority (Core Accounting):
- ✅ `backend/app/api/donations.py`
- ✅ `backend/app/api/sevas.py`
- ⏳ `backend/app/api/journal_entries.py`
- ⏳ `backend/app/api/bank_accounts.py`

### Medium Priority:
- ⏳ `backend/app/api/inventory.py`
- ⏳ `backend/app/api/sponsorships.py`
- ⏳ `backend/app/api/hr.py`
- ⏳ `backend/app/api/financial_closing.py`

### Lower Priority (Specialized):
- ⏳ `backend/app/api/payment_gateway.py`
- ⏳ `backend/app/api/hundi.py`
- ⏳ `backend/app/api/disposal.py`
- ⏳ `backend/app/api/revaluation.py`
- ⏳ `backend/app/api/cwip.py`

## Migration Steps

1. **Run migration script (dry-run first)**:
   ```bash
   python backend/scripts/migrate_coa_codes.py --dry-run
   python backend/scripts/migrate_coa_codes.py
   ```

2. **Initialize default COA for temples**:
   ```bash
   python backend/scripts/initialize_default_coa.py
   ```

3. **Update code references** (already done for donations.py and sevas.py)

4. **Test thoroughly**:
   - Create donations (cash, bank, in-kind)
   - Create seva bookings (current date, advance)
   - Verify journal entries
   - Check reports (Trial Balance, P&L, Balance Sheet)

## Notes

- **Journal entries are SAFE**: They use `account_id` (foreign key), not `account_code`, so existing entries will continue to work.
- **Migration is reversible**: Keep backups before running migration.
- **Test in dev/staging first**: Always test migration in a non-production environment first.

















