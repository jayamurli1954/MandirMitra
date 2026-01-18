# Complete Accounting System Implementation Plan

**Version:** 1.0 - Audit-Ready Standalone  
**Date:** January 2025  
**Focus:** Donation, Seva, and Accounting Systems

---

## Executive Summary

Based on the comprehensive accounting specification provided, this document outlines the implementation plan to make MandirMitra a **complete, audit-ready, compliance-first accounting system** that eliminates the need for external tools like Tally.

**Goal:** Zero external dependency for accounting. CA can work directly in the system.

---

## Current Status Assessment

### ✅ **Already Implemented:**

1. **Chart of Accounts** - Fully functional
2. **Double-Entry Bookkeeping** - Journal entries with debit/credit validation
3. **Voucher Entry System** - Receipt, Payment, Journal, Contra vouchers
4. **Trial Balance** - Working
5. **Profit & Loss Statement** - Working
6. **Account Ledger** - Working
7. **Category Income Reports** - Working
8. **Top Donors Report** - Working
9. **Auto-posting from Donations** - Donations auto-create journal entries
10. **Auto-posting from Sevas** - Seva bookings auto-create journal entries
11. **Financial Year Management** - Basic implementation
12. **Audit Trail** - Complete audit log system
13. **80G Certificate Generation** - Basic implementation exists

### ❌ **Critical Missing Features:**

1. **Balance Sheet Report** - CRITICAL for audit
2. **Day Book Report** - Standard accounting book
3. **Cash Book Report** - Cash management
4. **Bank Book Report** - Bank transaction tracking
5. **Month-end Closing Process** - Period management
6. **Year-end Closing Process** - Financial year closure
7. **Bank Reconciliation UI** - Model exists, UI missing
8. **PDF Receipt Generation** - Professional receipts
9. **TDS Management** - Calculation, certificates, returns
10. **GST Support** - If applicable (optional)
11. **FCRA Reporting** - If applicable (optional)
12. **Budget vs Actual** - Budget management
13. **Tally Export** - Data export to Tally format
14. **Cash Flow Statement** - Financial statement
15. **Receipts & Payments Account** - Simple cash statement

---

## Implementation Priority

### **Phase 1: Critical Audit Reports (Week 1-2) - HIGHEST PRIORITY**

These are essential for audit compliance:

1. **Balance Sheet Report** ⚠️ CRITICAL
   - Assets (Fixed + Current)
   - Liabilities (Current + Long-term)
   - Equity/Funds
   - Format: Schedule III compliant
   - Comparative (current vs previous year)

2. **Day Book Report** ⚠️ CRITICAL
   - All transactions for a day
   - Receipts and payments
   - Opening and closing balance

3. **Cash Book Report** ⚠️ CRITICAL
   - All cash transactions
   - Counter-wise breakdown
   - Running balance

4. **Bank Book Report** ⚠️ CRITICAL
   - All bank transactions
   - Account-wise
   - Cheque tracking

5. **Bank Reconciliation UI** ⚠️ CRITICAL
   - Import bank statement
   - Auto-matching
   - Manual matching
   - Reconciliation statement

### **Phase 2: Period Management (Week 3) - HIGH PRIORITY**

6. **Month-end Closing Process**
   - Closing checklist
   - Lock period
   - Generate closing reports
   - Board approval workflow

7. **Year-end Closing Process**
   - Comprehensive checklist
   - Depreciation run
   - Final trial balance
   - Transfer surplus to funds
   - Lock year
   - Opening balance for next year

### **Phase 3: Compliance Features (Week 4-5) - HIGH PRIORITY**

8. **TDS Management**
   - TDS rate configuration
   - Auto-calculation on payments
   - TDS payment tracking
   - Form 16/16A generation
   - TDS return data export

9. **GST Support (Optional)**
   - GST registration details (in settings)
   - GST-compliant invoices
   - Input tax credit tracking
   - GSTR-1/GSTR-3B data export

10. **FCRA Reporting (Optional)**
    - FCRA registration details (in settings)
    - Foreign donation tracking
    - FC-4 format reports
    - Quarterly/annual returns

### **Phase 4: Professional Features (Week 6) - MEDIUM PRIORITY**

11. **PDF Receipt Generation**
    - Professional receipt format
    - 80G certificate PDF
    - Email attachment
    - Print-ready

12. **Cash Flow Statement**
    - Operating activities
    - Investing activities
    - Financing activities
    - Direct/Indirect method

13. **Receipts & Payments Account**
    - Simple cash-based statement
    - Left: Receipts, Right: Payments

### **Phase 5: Advanced Features (Week 7-8) - MEDIUM PRIORITY**

14. **Budget vs Actual**
    - Budget entry
    - Budget vs actual comparison
    - Variance analysis
    - Alerts

15. **Tally Export**
    - XML format export
    - Chart of accounts export
    - Voucher export
    - Opening balance export

---

## Detailed Implementation Specifications

### 1. Balance Sheet Report

**Backend API:**
```python
GET /api/v1/journal-entries/reports/balance-sheet
Query Params:
  - as_of_date: date (required)
  - previous_year: boolean (for comparison)
```

**Report Structure:**
```
ASSETS
├─ Fixed Assets
│  ├─ Gross Block
│  ├─ Less: Accumulated Depreciation
│  └─ Net Block
├─ Current Assets
│  ├─ Cash in Hand
│  ├─ Bank Balances
│  ├─ Fixed Deposits
│  ├─ Investments
│  ├─ Loans & Advances
│  └─ Other Current Assets
└─ Total Assets

LIABILITIES & FUNDS
├─ Corpus/Capital Fund
├─ Designated Funds
│  ├─ Education Fund
│  ├─ Medical Fund
│  └─ Building Fund
├─ Current Liabilities
│  ├─ Sundry Creditors
│  ├─ Expenses Payable
│  ├─ Advance from Devotees
│  └─ TDS Payable
└─ Total Liabilities & Funds
```

**Implementation:**
- Query accounts by type (Asset, Liability)
- Calculate balances as of date
- Group by account groups
- Format as per Schedule III
- Add comparative columns

### 2. Day Book Report

**Backend API:**
```python
GET /api/v1/journal-entries/reports/day-book
Query Params:
  - date: date (required)
```

**Report Structure:**
```
Day Book - [Date]

Opening Balance: ₹X,XXX

RECEIPTS
├─ Donations: ₹X,XXX
├─ Seva Bookings: ₹X,XXX
├─ Other Income: ₹X,XXX
└─ Total Receipts: ₹X,XXX

PAYMENTS
├─ Expenses: ₹X,XXX
├─ Vendor Payments: ₹X,XXX
└─ Total Payments: ₹X,XXX

Net Cash Flow: ₹X,XXX
Closing Balance: ₹X,XXX
```

### 3. Cash Book Report

**Backend API:**
```python
GET /api/v1/journal-entries/reports/cash-book
Query Params:
  - from_date: date
  - to_date: date
  - counter_id: integer (optional)
```

**Report Structure:**
```
Cash Book - [Date Range]

Date | Particulars | Receipts | Payments | Balance
-----|-------------|----------|----------|----------
```

### 4. Bank Book Report

**Backend API:**
```python
GET /api/v1/journal-entries/reports/bank-book
Query Params:
  - account_id: integer (bank account)
  - from_date: date
  - to_date: date
```

**Report Structure:**
```
Bank Book - [Bank Name] - [Account Number]

Date | Particulars | Cheque No | Deposits | Withdrawals | Balance
-----|-------------|-----------|----------|-------------|--------
```

### 5. Bank Reconciliation

**Backend API:**
```python
POST /api/v1/journal-entries/bank-reconciliation/start
Body: { account_id, statement_date, bank_balance }

POST /api/v1/journal-entries/bank-reconciliation/match
Body: { recon_id, voucher_id, bank_transaction_id }

GET /api/v1/journal-entries/bank-reconciliation/statement/{recon_id}
```

**UI Features:**
- Import bank statement (CSV)
- Auto-match transactions
- Manual matching interface
- Outstanding items list
- Reconciliation statement

### 6. Month-end Closing

**Backend API:**
```python
POST /api/v1/journal-entries/period/close
Body: { month, year, closing_date }
```

**Process:**
1. Verify all vouchers posted
2. Run depreciation (if monthly)
3. Generate closing reports
4. Lock period (no more transactions)
5. Board approval workflow

### 7. Year-end Closing

**Backend API:**
```python
POST /api/v1/journal-entries/financial-year/{fy_id}/close
```

**Process:**
1. Comprehensive checklist
2. Final depreciation run
3. Transfer surplus to funds
4. Generate final reports
5. Lock financial year
6. Create opening balances for next year

### 8. TDS Management

**Database Schema:**
```sql
CREATE TABLE tds_entries (
    tds_id SERIAL PRIMARY KEY,
    voucher_id INTEGER REFERENCES vouchers(voucher_id),
    deductee_name VARCHAR(200),
    deductee_pan VARCHAR(10),
    tds_section VARCHAR(10), -- '194J', '194C', etc.
    gross_amount DECIMAL(15,2),
    tds_rate DECIMAL(5,2),
    tds_amount DECIMAL(15,2),
    tds_payment_date DATE,
    challan_number VARCHAR(50),
    certificate_issued BOOLEAN DEFAULT FALSE,
    certificate_number VARCHAR(50),
    quarter INTEGER,
    financial_year VARCHAR(10),
    temple_id INTEGER
);
```

**Features:**
- TDS rate configuration by section
- Auto-calculation on payment vouchers
- TDS payment tracking
- Form 16/16A generation
- TDS return export (24Q, 26Q)

### 9. GST Support (Optional)

**Settings Fields:**
- `gst_applicable: boolean`
- `gstin: string` (if applicable)
- `gst_registration_date: date`
- `gst_tax_rates: json` (HSN codes and rates)

**Features:**
- GST-compliant invoices
- Input tax credit tracking
- GSTR-1/GSTR-3B export

### 10. FCRA Reporting (Optional)

**Settings Fields:**
- `fcra_applicable: boolean`
- `fcra_registration_number: string` (if applicable)
- `fcra_valid_from: date`
- `fcra_valid_to: date`
- `fcra_bank_account_id: integer`

**Features:**
- Foreign donation tracking
- FCRA account separation
- FC-4 format reports
- Quarterly/annual returns

### 11. PDF Receipt Generation

**Technology:** ReportLab or WeasyPrint

**Features:**
- Professional receipt template
- 80G certificate PDF
- Email attachment
- Print-ready format
- Digital signature support

### 12. Budget vs Actual

**Database Schema:**
```sql
CREATE TABLE budget (
    budget_id SERIAL PRIMARY KEY,
    financial_year VARCHAR(10),
    account_id INTEGER REFERENCES accounts(account_id),
    month INTEGER, -- 1-12, or 0 for annual
    budgeted_amount DECIMAL(15,2),
    approved_by INTEGER,
    approved_at TIMESTAMP,
    version INTEGER DEFAULT 1,
    temple_id INTEGER
);
```

**Features:**
- Annual/monthly budget entry
- Budget vs actual comparison
- Variance analysis
- Alerts on over-budget

### 13. Tally Export

**Format:** Tally XML format

**Export Options:**
- Chart of Accounts
- Opening Balances
- Vouchers (all types)
- Masters (parties, items)

---

## Settings Page Updates

### Add GST/FCRA Optional Fields

**Temple Model Updates:**
```python
# GST Fields (Optional)
gst_applicable = Column(Boolean, default=False)
gstin = Column(String(15))  # 15-character GSTIN
gst_registration_date = Column(Date)
gst_tax_rates = Column(JSON)  # HSN codes and rates

# FCRA Fields (Optional - already exists but need to make conditional)
# fcra_registration_number (exists)
# fcra_valid_from (exists)
# fcra_valid_to (exists)
# Add: fcra_applicable boolean
fcra_applicable = Column(Boolean, default=False)
fcra_bank_account_id = Column(Integer)  # Link to bank account
```

**Settings UI Updates:**
- Add "GST Applicable" toggle
- Show GST fields only if enabled
- Add "FCRA Applicable" toggle
- Show FCRA fields only if enabled
- Validation: GSTIN format, FCRA dates

---

## Database Migrations Required

1. **Add GST fields to temples table**
2. **Add fcra_applicable to temples table**
3. **Create tds_entries table**
4. **Create budget table**
5. **Create financial_years table** (if not exists)
6. **Create bank_reconciliation table** (if not exists)
7. **Create bank_recon_items table** (if not exists)

---

## API Endpoints to Create

### Reports
- `GET /api/v1/journal-entries/reports/balance-sheet`
- `GET /api/v1/journal-entries/reports/day-book`
- `GET /api/v1/journal-entries/reports/cash-book`
- `GET /api/v1/journal-entries/reports/bank-book`
- `GET /api/v1/journal-entries/reports/cash-flow`
- `GET /api/v1/journal-entries/reports/receipts-payments`

### Period Management
- `POST /api/v1/journal-entries/period/close`
- `GET /api/v1/journal-entries/period/status`
- `POST /api/v1/journal-entries/financial-year/{fy_id}/close`
- `GET /api/v1/journal-entries/financial-years`

### Bank Reconciliation
- `POST /api/v1/journal-entries/bank-reconciliation/start`
- `POST /api/v1/journal-entries/bank-reconciliation/match`
- `GET /api/v1/journal-entries/bank-reconciliation/statement/{recon_id}`
- `GET /api/v1/journal-entries/bank-reconciliation/outstanding`

### TDS Management
- `GET /api/v1/journal-entries/tds/summary`
- `POST /api/v1/journal-entries/tds/calculate`
- `POST /api/v1/journal-entries/tds/generate-certificates`
- `GET /api/v1/journal-entries/tds/returns/{quarter}`

### Budget
- `POST /api/v1/journal-entries/budget`
- `GET /api/v1/journal-entries/budget/{fy_id}`
- `GET /api/v1/journal-entries/budget/vs-actual`

### Export
- `GET /api/v1/journal-entries/export/tally-xml`
- `GET /api/v1/journal-entries/export/excel`
- `GET /api/v1/journal-entries/export/pdf`

---

## Frontend Pages to Create/Update

### New Pages:
1. `BalanceSheet.js` - Balance Sheet report
2. `DayBook.js` - Day Book report
3. `CashBook.js` - Cash Book report
4. `BankBook.js` - Bank Book report
5. `BankReconciliation.js` - Bank reconciliation UI
6. `PeriodClosing.js` - Month/Year-end closing
7. `TDSManagement.js` - TDS management
8. `BudgetManagement.js` - Budget entry and reports
9. `CashFlowStatement.js` - Cash flow report

### Update Existing:
1. `Settings.js` - Add GST/FCRA toggles
2. `AccountingReports.js` - Add new reports to menu

---

## Testing Checklist

### Functional Testing:
- [ ] Balance Sheet generates correctly
- [ ] Day Book shows all transactions
- [ ] Cash Book balances correctly
- [ ] Bank Book matches bank statements
- [ ] Bank reconciliation matches correctly
- [ ] Month-end closing locks period
- [ ] Year-end closing creates next year
- [ ] TDS calculates correctly
- [ ] Budget vs actual shows variance
- [ ] Tally export imports correctly

### Compliance Testing:
- [ ] Balance Sheet format matches Schedule III
- [ ] TDS returns match IT department format
- [ ] FCRA reports match MHA format
- [ ] GST returns match GST portal format
- [ ] 80G certificates match IT requirements

### Integration Testing:
- [ ] Donations auto-post to accounting
- [ ] Sevas auto-post to accounting
- [ ] Reports reflect all transactions
- [ ] Audit trail captures all changes

---

## Timeline Estimate

**Total Duration:** 8 weeks

- **Week 1-2:** Critical Reports (Balance Sheet, Day Book, Cash Book, Bank Book, Bank Reconciliation)
- **Week 3:** Period Management (Month-end, Year-end closing)
- **Week 4-5:** Compliance (TDS, GST, FCRA)
- **Week 6:** Professional Features (PDF, Cash Flow, Receipts & Payments)
- **Week 7:** Advanced Features (Budget, Tally Export)
- **Week 8:** Testing, Bug Fixes, Documentation

---

## Success Criteria

✅ **System is audit-ready when:**
1. CA can generate all required reports
2. All transactions are traceable
3. Periods can be locked
4. Bank reconciliation works
5. TDS/GST/FCRA compliance reports available
6. Tally export works
7. No external tool needed

✅ **System is compliance-ready when:**
1. All statutory reports available
2. Returns can be generated
3. Certificates auto-generated
4. Due dates tracked
5. Alerts configured

---

## Next Steps

1. **Immediate:** Update Temple model and Settings page with GST/FCRA toggles
2. **Week 1:** Implement Balance Sheet, Day Book, Cash Book, Bank Book
3. **Week 2:** Complete Bank Reconciliation UI
4. **Week 3:** Implement Period Closing
5. **Continue:** Follow priority order above

---

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Status:** Ready for Implementation









