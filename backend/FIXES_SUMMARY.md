# Bank Account Mapping & Account Code Fixes - Summary

## Issues Fixed

### 1. ✅ Integrity Hash Column Migration Error
**Problem:** Startup was failing because `integrity_hash` column doesn't exist yet.

**Solution:** Made integrity check gracefully handle missing column - shows info message instead of error.

**Files Changed:**
- `backend/app/core/integrity_check.py` - Added graceful column existence check

**Action Required:**
- Run migration script: `python scripts/add_integrity_hash_column.py`

---

### 2. ✅ Bank Account Mapping Issue
**Problem:** 
- Donations/sevas with bank payment mode were using hardcoded account codes (`12001`, `1110`)
- Different account codes for debit (12001) vs credit (1110)
- Not using bank accounts created through Bank Account Management module

**Solution:** 
- Created helper function `get_bank_account_for_payment()` to get bank account from `BankAccount` model
- Updated donations and sevas APIs to use bank accounts from `BankAccount` model
- Priority: Specific bank account → Primary bank account → Any active bank account → Fallback to hardcoded code

**Files Changed:**
- `backend/app/core/bank_account_helper.py` - NEW: Helper functions for bank account lookup
- `backend/app/api/donations.py` - Updated to use bank account helper
- `backend/app/api/sevas.py` - Updated to use bank account helper

**How It Works Now:**
1. When payment mode is bank-related (UPI, CARD, ONLINE, BANK, CHEQUE, etc.)
2. System looks up bank account from `BankAccount` model
3. Uses the `chart_account_id` from bank account
4. This ensures consistency - same bank account used for both debit and credit

---

### 3. ⚠️ Account Code Standardization (Documented, Not Yet Implemented)
**Problem:** Account codes are inconsistent - some 4 digits (1110, 5101), some 5 digits (11001, 12001).

**Status:** Documented in `ACCOUNT_CODE_STANDARDIZATION_PLAN.md`

**Recommendation:** 
- This requires a comprehensive migration script
- Should be done separately as it affects all accounting data
- For now, ensure new accounts use 5-digit codes

---

## Testing Checklist

1. **Integrity Hash Migration:**
   - [ ] Run `python scripts/add_integrity_hash_column.py`
   - [ ] Restart application
   - [ ] Verify no errors on startup
   - [ ] Create a transaction and verify hash is generated

2. **Bank Account Mapping:**
   - [ ] Create a bank account through "Bank Account Management"
   - [ ] Mark it as Primary
   - [ ] Record a donation with payment mode = UPI/CARD/BANK
   - [ ] Verify journal entry uses the bank account from BankAccount model
   - [ ] Record a seva booking with bank payment
   - [ ] Verify journal entry uses the same bank account
   - [ ] Check trial balance - debit and credit should use same bank account

3. **Account Codes:**
   - [ ] Review existing account codes
   - [ ] Note which ones are non-standard (4 digits)
   - [ ] Plan migration for account code standardization (separate task)

---

## Files Created/Modified

### New Files:
- `backend/app/core/bank_account_helper.py` - Bank account lookup helpers
- `backend/ACCOUNT_CODE_STANDARDIZATION_PLAN.md` - Documentation for account code standardization
- `backend/FIXES_SUMMARY.md` - This file

### Modified Files:
- `backend/app/core/integrity_check.py` - Graceful column existence check
- `backend/app/api/donations.py` - Use bank account helper
- `backend/app/api/sevas.py` - Use bank account helper

---

## Next Steps

1. **Immediate:**
   - Run integrity hash migration script
   - Test bank account mapping with donations and sevas

2. **Short-term:**
   - Review account code standardization plan
   - Create migration script for account code standardization (if needed)
   - Update account creation to enforce 5-digit codes

3. **Long-term:**
   - Consider adding validation for account codes
   - Add account code format check in Account model

---

## Notes

- Bank account mapping now uses `BankAccount.chart_account_id` which links to the `Account` table
- This ensures that bank accounts created through the UI are used consistently
- The system falls back to hardcoded codes only if no bank account is found (should show warning)
- Account code standardization is a separate concern and requires careful migration planning





