# Opening Balance Setup Guide

## Overview

When starting MandirMitra in the middle of a financial year, you need to enter opening balances for all balance sheet items (Assets, Liabilities, Equity) as of the beginning of the financial year.

## What are Opening Balances?

Opening balances represent the values of accounts at the start of the financial year. For example:
- **Cash Balance**: ₹50,000 (as of April 1st)
- **Bank Balance**: ₹5,00,000 (as of April 1st)
- **Fixed Assets**: ₹10,00,000 (as of April 1st)
- **Liabilities**: ₹2,00,000 (as of April 1st)
- **Equity/Corpus Fund**: ₹13,50,000 (as of April 1st)

## Methods to Set Opening Balances

### Method 1: Using the API (Recommended for Frontend UI)

**Get Balance Sheet Accounts:**
```
GET /api/v1/opening-balances/accounts
```
Returns all accounts (Assets, Liabilities, Equity) that can have opening balances.

**Update Single Account:**
```
PUT /api/v1/opening-balances/accounts/{account_id}
Body: {
    "opening_balance_debit": 50000.0,   // For Assets (positive value)
    "opening_balance_credit": 0.0
}
```

**For Liabilities/Equity:**
```
PUT /api/v1/opening-balances/accounts/{account_id}
Body: {
    "opening_balance_debit": 0.0,
    "opening_balance_credit": 100000.0  // For Liabilities/Equity (positive value)
}
```

**Bulk Update (Multiple Accounts):**
```
PUT /api/v1/opening-balances/bulk-update
Body: [
    {
        "account_id": 1,
        "opening_balance_debit": 50000.0,
        "opening_balance_credit": 0.0
    },
    {
        "account_id": 5,
        "opening_balance_debit": 0.0,
        "opening_balance_credit": 100000.0
    }
]
```

### Method 2: Using Python Script (Interactive)

Run the interactive script:

```bash
cd backend
python scripts/set_opening_balances.py
```

This will:
1. List all balance sheet accounts
2. Ask you to enter opening balance for each account
3. Update the accounts automatically

**Instructions:**
- For **Assets** (Cash, Bank, Fixed Assets): Enter positive balance
  - Example: `50000` for ₹50,000 cash
- For **Liabilities** (Loans, Payables): Enter positive balance
  - Example: `100000` for ₹1,00,000 loan
- For **Equity** (Corpus Fund, General Fund): Enter positive balance
  - Example: `1000000` for ₹10,00,000 fund
- Leave empty to skip an account

### Method 3: Direct Database Update (Advanced)

If you need to update many accounts programmatically:

```python
from app.core.database import SessionLocal
from app.models.accounting import Account

db = SessionLocal()

# Example: Set cash balance
cash_account = db.query(Account).filter(
    Account.account_code == "11001"  # Cash account code
).first()
cash_account.opening_balance_debit = 50000.0
cash_account.opening_balance_credit = 0.0

# Example: Set bank balance
bank_account = db.query(Account).filter(
    Account.account_code == "12001"  # Bank account code
).first()
bank_account.opening_balance_debit = 500000.0
bank_account.opening_balance_credit = 0.0

# Example: Set liability (loan)
loan_account = db.query(Account).filter(
    Account.account_code == "21001"  # Loan account code
).first()
loan_account.opening_balance_debit = 0.0
loan_account.opening_balance_credit = 200000.0

db.commit()
```

## Understanding Debit and Credit

### For Assets:
- **Debit Balance** = Positive value (Asset exists)
- **Credit Balance** = Negative value (Asset is overdrawn, rare)

Example:
- Cash ₹50,000 → `opening_balance_debit = 50000.0`, `opening_balance_credit = 0.0`

### For Liabilities:
- **Credit Balance** = Positive value (Owed to others)
- **Debit Balance** = Negative value (Prepaid, rare)

Example:
- Loan ₹2,00,000 → `opening_balance_debit = 0.0`, `opening_balance_credit = 200000.0`

### For Equity:
- **Credit Balance** = Positive value (Fund balance)
- **Debit Balance** = Negative value (Deficit, rare)

Example:
- Corpus Fund ₹10,00,000 → `opening_balance_debit = 0.0`, `opening_balance_credit = 1000000.0`

## Common Accounts to Update

### Assets (Debit Balance):
- **Cash Accounts**: `11001` (Cash in Hand - Counter), `11002` (Cash in Hand - Hundi)
- **Bank Accounts**: `12001` (Bank - Current Account), etc.
- **Fixed Assets**: `15002` (Building), `15003` (Land), etc.
- **Current Assets**: `13001` (Accounts Receivable), etc.

### Liabilities (Credit Balance):
- **Loans**: `21001` (Short-term Loans), `22001` (Long-term Loans)
- **Payables**: `21002` (Accounts Payable)
- **Advance Collections**: `21003` (Advance Seva Booking)

### Equity (Credit Balance):
- **Corpus Fund**: `31001` (Corpus Fund)
- **General Fund**: `31010` (General Fund)
- **Reserves**: `32001` (Various reserves)

## Verifying Opening Balances

After setting opening balances:

1. **Generate Trial Balance:**
   ```
   GET /api/v1/journal-entries/trial-balance?as_of_date=2025-04-01
   ```
   This should show all your opening balances.

2. **Generate Balance Sheet:**
   ```
   GET /api/v1/journal-entries/balance-sheet?as_of_date=2025-04-01
   ```
   Verify that:
   - Total Assets = Total Liabilities + Total Equity

3. **Check Individual Account Ledger:**
   ```
   GET /api/v1/journal-entries/accounts/{account_id}/ledger?from_date=2025-04-01
   ```
   The opening balance should appear at the top.

## Important Notes

1. **Financial Year Start Date**: Opening balances should be set as of your financial year start date (typically April 1st in India).

2. **Double-Entry Principle**: 
   - Total Assets = Total Liabilities + Total Equity
   - Make sure your opening balances balance out!

3. **Income/Expense Accounts**: 
   - These accounts should NOT have opening balances
   - They start at zero each financial year
   - Only balance sheet accounts (Assets, Liabilities, Equity) have opening balances

4. **After Setting Opening Balances**:
   - Start entering regular transactions from the current date
   - All new transactions will be added to the opening balances
   - Reports will automatically include opening balances

## Example Workflow

1. **Determine Financial Year Start**: April 1, 2025 (or your temple's financial year start)

2. **Gather Opening Balance Information**:
   - Bank statement as of March 31, 2025
   - Cash count as of March 31, 2025
   - Fixed asset register
   - Liability statements
   - Previous year's balance sheet

3. **Set Opening Balances**:
   - Use the API or script to enter all balances
   - Verify trial balance matches your records

4. **Verify Balance Sheet**:
   - Assets = Liabilities + Equity
   - All accounts match your records

5. **Start Regular Operations**:
   - Begin entering daily transactions
   - System will automatically calculate balances including opening balances

## Troubleshooting

**Balance Sheet doesn't balance:**
- Check that Total Assets = Total Liabilities + Total Equity
- Verify all opening balances are entered correctly
- Check for missing accounts

**Negative balances on Assets:**
- Assets should have debit (positive) balances
- If you see negative, check if credit was entered instead

**Opening balances not showing in reports:**
- Verify opening balance date is before the report date
- Check account is active
- Verify opening_balance_debit/credit fields are set correctly

---

**Need Help?** Contact your system administrator or refer to the Accounting documentation.

















