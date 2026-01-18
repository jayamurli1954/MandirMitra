# Quick Start: Setting Opening Balances

## Problem
You're starting MandirMitra in the middle of a financial year and need to enter opening balances for Cash, Bank, Assets, Liabilities, etc.

## Quick Solution

### Option 1: Use the Interactive Script (Easiest)

```bash
cd backend
python scripts/set_opening_balances.py
```

Follow the prompts to enter opening balances for each account.

### Option 2: Use the API (For Frontend Integration)

**Step 1: Get all balance sheet accounts**
```
GET /api/v1/opening-balances/accounts
Authorization: Bearer <your-token>
```

**Step 2: Update opening balance for each account**

For Cash (Asset):
```
PUT /api/v1/opening-balances/accounts/{cash_account_id}
Body: {
    "opening_balance_debit": 50000.0,
    "opening_balance_credit": 0.0
}
```

For Bank (Asset):
```
PUT /api/v1/opening-balances/accounts/{bank_account_id}
Body: {
    "opening_balance_debit": 500000.0,
    "opening_balance_credit": 0.0
}
```

For Loan (Liability):
```
PUT /api/v1/opening-balances/accounts/{loan_account_id}
Body: {
    "opening_balance_debit": 0.0,
    "opening_balance_credit": 200000.0
}
```

For Corpus Fund (Equity):
```
PUT /api/v1/opening-balances/accounts/{corpus_account_id}
Body: {
    "opening_balance_debit": 0.0,
    "opening_balance_credit": 1000000.0
}
```

### Option 3: Bulk Update (Multiple Accounts at Once)

```
PUT /api/v1/opening-balances/bulk-update
Body: [
    {"account_id": 1, "opening_balance_debit": 50000.0, "opening_balance_credit": 0.0},
    {"account_id": 2, "opening_balance_debit": 500000.0, "opening_balance_credit": 0.0},
    {"account_id": 5, "opening_balance_debit": 0.0, "opening_balance_credit": 200000.0}
]
```

## Rules

- **Assets** (Cash, Bank, Fixed Assets): Use `opening_balance_debit` (positive value)
- **Liabilities** (Loans, Payables): Use `opening_balance_credit` (positive value)
- **Equity** (Corpus Fund, General Fund): Use `opening_balance_credit` (positive value)
- **Income/Expense accounts**: Do NOT set opening balances (they start at zero)

## Verify

After setting opening balances:

1. Generate Trial Balance:
   ```
   GET /api/v1/journal-entries/trial-balance?as_of_date=2025-04-01
   ```

2. Generate Balance Sheet:
   ```
   GET /api/v1/journal-entries/balance-sheet?as_of_date=2025-04-01
   ```
   
   Verify: Total Assets = Total Liabilities + Total Equity

## Common Account Codes

- `11001` - Cash in Hand - Counter
- `11002` - Cash in Hand - Hundi
- `12001` - Bank - Current Account
- `15002` - Building
- `15003` - Land
- `21001` - Short-term Loans
- `21003` - Advance Seva Booking
- `31001` - Corpus Fund
- `31010` - General Fund

---

**Full Documentation**: See `backend/OPENING_BALANCE_GUIDE.md`

















