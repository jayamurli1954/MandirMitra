# Bank Account Management Guide

## Overview

MandirMitra supports **multiple bank accounts** for a temple. This allows you to:
- Track payments received in different bank accounts
- Link donations to specific bank accounts when recording non-cash payments (Card, UPI, Online, Cheque)
- Set one account as "Primary" for default use
- Manage bank account details centrally

## Where to Add Bank Accounts

**Location:** Accounting → Bank Accounts

**Path:** `/accounting/bank-accounts`

**Access:** Available in the Accounting menu in the sidebar

## Details Collected When Adding a Bank Account

### Required Fields (*)

1. **Account Name** *
   - Descriptive name for the account
   - Example: "SBI Current Account", "HDFC Savings", "Main Operating Account"
   - Used to identify the account in dropdowns

2. **Bank Name** *
   - Name of the bank
   - Example: "State Bank of India", "HDFC Bank", "ICICI Bank"

3. **Account Number** *
   - Full bank account number
   - Must be unique per temple
   - Displayed as masked (****1234) in the list for security

4. **IFSC Code** *
   - 11-character IFSC code
   - Format: 4 letters + 0 + 6 alphanumeric
   - Example: "SBIN0001234", "HDFC0001234"
   - Automatically converted to uppercase

### Optional Fields

5. **Branch Name**
   - Branch location where account is held
   - Example: "Main Branch, Bangalore", "MG Road Branch"

6. **Account Type**
   - Dropdown selection:
     - Savings
     - Current
     - Fixed Deposit
     - Recurring Deposit
   - Default: "Savings"

7. **Set as Primary Account**
   - Checkbox to mark account as primary
   - Only one account can be primary at a time
   - Primary account is used as default for online payments
   - Setting a new primary automatically unsets the current primary

8. **Active Status**
   - Checkbox to mark account as active/inactive
   - Inactive accounts won't appear in payment dropdowns
   - Default: Active

## Multiple Bank Accounts

### How It Works

- **Unlimited Accounts:** You can add as many bank accounts as needed
- **One Primary:** Only one account can be marked as "Primary" at a time
- **All Active:** All active accounts are available for selection when recording payments

### Use Cases

1. **Different Payment Methods:**
   - One account for UPI payments
   - Another for card payments
   - Separate account for cheque deposits

2. **Different Purposes:**
   - Operating account for daily transactions
   - Savings account for corpus funds
   - Fixed deposit accounts

3. **Multiple Banks:**
   - Accounts with different banks
   - Regional branch accounts

## How Bank Accounts Are Used

### 1. Donation Recording

When recording a donation with payment mode:
- **Cash:** No bank account needed
- **Card/UPI/Online/Cheque:** Bank account selection is **required**

The system will:
- Show a dropdown of all active bank accounts
- Display: "Account Name - Bank Name (****1234) (Primary)"
- Allow you to select which account received the payment

### 2. Dashboard Quick Donation

On the Dashboard, when selecting non-cash payment mode:
- If no bank accounts are configured: Shows warning message
- If bank accounts exist: Shows dropdown to select account

### 3. Accounting Integration

Each bank account is linked to:
- **Chart of Accounts:** Automatically linked to account code "1110" (Bank Accounts)
- **Journal Entries:** Donations are posted to the selected bank account
- **Bank Reconciliation:** Used for matching bank statements

## API Endpoints

### Get All Bank Accounts
```
GET /api/v1/bank-accounts
```

### Create Bank Account
```
POST /api/v1/bank-accounts
Body: {
  "account_name": "SBI Current Account",
  "bank_name": "State Bank of India",
  "branch_name": "Main Branch",
  "account_number": "1234567890",
  "ifsc_code": "SBIN0001234",
  "account_type": "Current",
  "is_primary": true,
  "is_active": true
}
```

### Update Bank Account
```
PUT /api/v1/bank-accounts/{id}
Body: (same as create)
```

### Delete Bank Account (Soft Delete)
```
DELETE /api/v1/bank-accounts/{id}
```
Note: This sets `is_active = false` instead of deleting

## Best Practices

1. **Naming Convention:**
   - Use descriptive account names
   - Include bank name in account name for clarity
   - Example: "SBI Current - Main Account"

2. **Primary Account:**
   - Set the most frequently used account as primary
   - Primary account is used as default fallback

3. **Account Number Security:**
   - Account numbers are masked in the UI (****1234)
   - Full account number is stored securely in database

4. **Inactive Accounts:**
   - Don't delete old accounts, mark them as inactive
   - This preserves historical data integrity

5. **IFSC Code:**
   - Always use uppercase
   - Verify IFSC code before saving
   - Format: 4 letters + 0 + 6 alphanumeric

## Troubleshooting

### "No bank accounts configured" Warning

**Problem:** When trying to record a non-cash donation, you see a warning.

**Solution:**
1. Go to Accounting → Bank Accounts
2. Click "Add Bank Account"
3. Fill in required details
4. Save the account

### Can't Select Bank Account in Donation Form

**Problem:** Bank account dropdown is empty or disabled.

**Solutions:**
1. Check if bank accounts are marked as "Active"
2. Verify you're logged in with correct temple_id
3. Check browser console for API errors

### Primary Account Not Working

**Problem:** Primary account not showing as default.

**Solution:**
1. Go to Bank Accounts page
2. Edit the account you want as primary
3. Check "Set as Primary Account"
4. Save - this will automatically unset other primary accounts

## Database Schema

### Bank Accounts Table

```sql
CREATE TABLE bank_accounts (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id),
    account_name VARCHAR(200) NOT NULL,
    bank_name VARCHAR(200) NOT NULL,
    branch_name VARCHAR(200),
    account_number VARCHAR(50) NOT NULL,
    ifsc_code VARCHAR(20) NOT NULL,
    account_type VARCHAR(50),
    chart_account_id INTEGER REFERENCES accounts(id),
    is_active BOOLEAN DEFAULT TRUE,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Summary

- **Location:** Accounting → Bank Accounts (`/accounting/bank-accounts`)
- **Multiple Accounts:** Yes, unlimited
- **Primary Account:** One can be set as primary
- **Required Fields:** Account Name, Bank Name, Account Number, IFSC Code
- **Optional Fields:** Branch Name, Account Type, Primary Status, Active Status
- **Usage:** Required for non-cash donation payments (Card, UPI, Online, Cheque)
- **Security:** Account numbers are masked in UI


