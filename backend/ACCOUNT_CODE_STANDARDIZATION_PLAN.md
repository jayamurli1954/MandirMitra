# Account Code Standardization Plan

## Current Issue

Account codes are inconsistent - some are 4 digits, some are 5 digits:
- `11001` (5 digits) - Cash in Hand - Counter
- `1110` (4 digits) - Bank - SBI Current Account (should be `01110`)
- `12001` (5 digits) - Main Bank Account
- `5101` (4 digits) - Priest Salary (should be `05101`)
- `42002` (5 digits) - Seva Income
- `44001` (5 digits) - Donation Income

## Standard: 5-Digit Account Codes

**All account codes should be 5 digits with leading zeros if needed.**

Examples:
- `11001` → `11001` (already correct)
- `1110` → `01110` (needs padding)
- `5101` → `05101` (needs padding)

## Migration Strategy

### Phase 1: Preparation
1. Create utility function to standardize account codes (pad to 5 digits)
2. Create migration script to:
   - Find all accounts with non-standard codes
   - Update account codes to 5-digit format
   - Update all journal_lines that reference old codes
   - Update all references in other tables

### Phase 2: Migration Script

```python
# backend/scripts/standardize_account_codes.py

def standardize_account_code(code: str) -> str:
    """Convert account code to 5-digit format with leading zeros"""
    if not code:
        return code
    # Remove any whitespace
    code = str(code).strip()
    # Pad with leading zeros to make 5 digits
    return code.zfill(5)
```

**Steps:**
1. Get all accounts with codes that are not 5 digits
2. For each account:
   - Generate new 5-digit code
   - Check if new code already exists (collision detection)
   - If collision, use alternative (e.g., 01110 -> 01111)
   - Update account.account_code
   - Update all journal_lines.account_id references (if using account_code in journal_lines)
   - Update all other references

**Important:** This is a critical migration that affects all accounting data. Must be:
- Tested thoroughly on a backup
- Run during maintenance window
- Backed up before execution
- Verified after execution

### Phase 3: Update Account Creation
- Ensure all new accounts use 5-digit codes
- Add validation in Account model to enforce 5-digit format

## Current Status

**This migration is NOT yet implemented** - it requires careful testing.

**Recommendation:** 
- For now, fix the bank account mapping issue (use BankAccount model)
- Account code standardization can be done as a separate migration later
- Document existing account codes and ensure new ones follow 5-digit standard

## Notes

The bank account mapping issue is separate from account code standardization:
- Bank accounts should use `chart_account_id` from `BankAccount` model
- Account code format is a separate concern about consistency





