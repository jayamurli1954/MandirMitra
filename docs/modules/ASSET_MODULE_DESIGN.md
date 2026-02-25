# Asset Management Module - Design Document

## Overview

Comprehensive asset management system following **standard accounting practices** and **audit compliance requirements** for temple assets including land, buildings, vehicles, equipment, gold, silver, and precious metals.

---

## Accounting Standards Compliance

### Indian Accounting Standards (Ind AS) / AS
- **AS 10** - Accounting for Fixed Assets
- **AS 6** - Depreciation Accounting
- **Ind AS 16** - Property, Plant and Equipment
- **AS 28** - Impairment of Assets (if applicable)

### Key Principles
1. **Cost Basis** - Assets recorded at historical cost
2. **Capitalization** - Costs capitalized when asset ready for use
3. **Depreciation** - Systematic allocation over useful life
4. **Revaluation** - Optional, with proper accounting
5. **Disclosure** - Full disclosure in financial statements

---

## Asset Classification

### 1. Fixed Assets (1500-1599 Series)

#### 1500 - Fixed Assets (Parent)
- **1501** - Land
- **1502** - Buildings
- **1503** - Building Improvements
- **1510** - Vehicles
- **1520** - Furniture & Fixtures
- **1530** - Computer & Equipment
- **1540** - Electrical Installations
- **1550** - Plumbing & Sanitation
- **1560** - Temple Idols & Statues
- **1570** - Sound & Lighting Systems
- **1580** - Other Fixed Assets

### 2. Capital Work in Progress (1600-1699 Series)

#### 1600 - Capital Work in Progress (Parent)
- **1601** - Building Construction
- **1602** - Building Renovation
- **1603** - Infrastructure Development
- **1610** - Installation in Progress
- **1620** - Other CWIP

### 3. Accumulated Depreciation (1700-1799 Series)

#### 1700 - Accumulated Depreciation (Parent)
- **1701** - Accumulated Depreciation - Buildings
- **1702** - Accumulated Depreciation - Vehicles
- **1703** - Accumulated Depreciation - Equipment
- **1710** - Accumulated Depreciation - Furniture
- **1720** - Accumulated Depreciation - Other Assets

### 4. Revaluation Reserve (1800-1899 Series)

#### 1800 - Revaluation Reserve (Parent)
- **1801** - Revaluation Reserve - Land
- **1802** - Revaluation Reserve - Buildings
- **1803** - Revaluation Reserve - Gold
- **1804** - Revaluation Reserve - Silver
- **1805** - Revaluation Reserve - Other Assets

### 5. Precious Assets (1900-1999 Series)

#### 1900 - Precious Assets (Parent)
- **1901** - Gold Ornaments
- **1902** - Silver Articles
- **1903** - Precious Stones
- **1904** - Other Precious Items

---

## Database Models

### 1. AssetCategory
```python
- id
- temple_id
- code (e.g., "FIXED", "MOVABLE", "PRECIOUS")
- name
- parent_category_id
- default_depreciation_method (STRAIGHT_LINE, WDV, DOUBLE_DECLINING, etc.)
- default_useful_life_years
- default_depreciation_rate_percent (for WDV/Double Declining)
- is_depreciable
- account_id (for asset)
- accumulated_depreciation_account_id
- revaluation_reserve_account_id
```

### 2. Asset
```python
- id
- temple_id
- asset_number (unique identifier)
- name
- description
- category_id
- asset_type (FIXED, MOVABLE, PRECIOUS, INTANGIBLE)
  
# Identification
- location
- tag_number (physical tag)
- serial_number (if applicable)
- identification_mark
  
# Financial
- purchase_date
- original_cost
- current_book_value
- accumulated_depreciation
- revalued_amount
- revaluation_reserve
  
# Depreciation
- depreciation_method (STRAIGHT_LINE, WDV, DOUBLE_DECLINING, DECLINING_BALANCE, 
                       UNITS_OF_PRODUCTION, ANNUITY, DEPLETION, SINKING_FUND)
- useful_life_years
- depreciation_rate_percent (for WDV, Declining Balance, Double Declining)
- salvage_value (residual value)
- is_depreciable
- depreciation_start_date
  
# For Units of Production Method
- total_estimated_units (total production capacity/usage)
- units_used_this_period (for calculation)
  
# For Annuity Method
- interest_rate_percent (discount rate)
  
# For Sinking Fund Method
- sinking_fund_interest_rate
- sinking_fund_payments_per_year
  
# Status
- status (ACTIVE, UNDER_CONSTRUCTION, DISPOSED, SOLD)
- cwip_id (if under construction)
  
# Documents
- purchase_invoice_number
- purchase_invoice_date
- vendor_id
- warranty_expiry_date
  
# Timestamps
- created_at
- updated_at
```

### 3. CapitalWorkInProgress (CWIP)
```python
- id
- temple_id
- cwip_number
- project_name
- description
- asset_category_id (target asset category)
- start_date
- expected_completion_date
- actual_completion_date
  
# Financial
- total_budget
- total_expenditure
- account_id (CWIP account)
  
# Status
- status (IN_PROGRESS, COMPLETED, SUSPENDED)
- asset_id (when capitalized)
  
# Timestamps
- created_at
- updated_at
```

### 4. AssetExpense (for CWIP)
```python
- id
- cwip_id
- expense_date
- description
- amount
- expense_category (MATERIAL, LABOR, OVERHEAD, OTHER)
- vendor_id
- reference_number
- journal_entry_id
```

### 5. DepreciationSchedule
```python
- id
- asset_id
- financial_year
- period (MONTHLY, YEARLY)
- period_start_date
- period_end_date
  
# Depreciation Details
- depreciation_method_used
- opening_book_value
- depreciation_amount
- closing_book_value
- depreciation_rate (if applicable)
  
# For Units of Production
- units_produced_this_period
- total_units_produced_to_date
  
# For Annuity Method
- interest_component
- principal_component
  
# Accounting
- journal_entry_id
- posted_date
- status (CALCULATED, POSTED, CANCELLED)
  
# Timestamps
- created_at
- updated_at
```

### 6. AssetRevaluation
```python
- id
- asset_id
- revaluation_date
- revaluation_type (INCREASE, DECREASE)
  
# Valuation
- previous_book_value
- revalued_amount
- revaluation_amount (difference)
- valuation_method (MARKET_VALUE, PROFESSIONAL_VALUER, INDEX_BASED)
- valuer_name
- valuation_report_number
  
# Accounting
- revaluation_reserve_account_id
- journal_entry_id
  
# Timestamps
- created_at
- created_by
```

### 7. AssetDisposal
```python
- id
- asset_id
- disposal_date
- disposal_type (SALE, SCRAP, DONATION, LOSS)
- disposal_reason
  
# Financial
- book_value_at_disposal
- accumulated_depreciation_at_disposal
- disposal_proceeds (if sold)
- gain_loss_amount
  
# Accounting
- journal_entry_id
  
# Details
- buyer_name (if sold)
- disposal_document_number
  
# Timestamps
- created_at
- created_by
```

### 8. AssetMaintenance
```python
- id
- asset_id
- maintenance_date
- maintenance_type (PREVENTIVE, CORRECTIVE, ROUTINE)
- description
- cost
- vendor_id
- next_maintenance_date
- journal_entry_id (if capitalized)
```

---

## Accounting Entries

### 1. Asset Purchase (Direct)
```
Dr: Asset Account (1501-1580)          ₹X
    Cr: Cash/Bank/Payables              ₹X
```

### 2. Construction Expense (CWIP)
```
Dr: CWIP Account (1601-1620)            ₹X
    Cr: Cash/Bank/Payables              ₹X
```

### 3. Capitalization (CWIP → Asset)
```
Dr: Asset Account (1501-1580)           ₹X
    Cr: CWIP Account (1601-1620)        ₹X
```

### 4. Depreciation (Monthly/Yearly)
```
Dr: Depreciation Expense (6001-6099)    ₹X
    Cr: Accumulated Depreciation (1701-1720)  ₹X
```

### 5. Revaluation (Increase)
```
Dr: Asset Account                       ₹X
    Cr: Revaluation Reserve (1801-1805) ₹X
```

### 6. Revaluation (Decrease - if reserve exists)
```
Dr: Revaluation Reserve (1801-1805)     ₹X
    Cr: Asset Account                   ₹X
```

### 7. Revaluation (Decrease - excess)
```
Dr: Revaluation Reserve (1801-1805)     ₹Y (available)
Dr: Revaluation Expense (6001)          ₹Z (excess)
    Cr: Asset Account                   ₹X (total)
```

### 8. Asset Disposal (Sale)
```
Dr: Cash/Bank                           ₹X (proceeds)
Dr: Accumulated Depreciation            ₹Y
Dr/Cr: Gain/Loss on Disposal           ₹Z
    Cr: Asset Account                   ₹W (book value)
```

### 9. Asset Disposal (Scrap/Loss)
```
Dr: Accumulated Depreciation            ₹Y
Dr: Loss on Disposal (6001)             ₹Z
    Cr: Asset Account                   ₹W
```

---

## Depreciation Calculation

### Straight-Line Method
```python
annual_depreciation = (original_cost - salvage_value) / useful_life_years
monthly_depreciation = annual_depreciation / 12
```

### Written Down Value (WDV)
```python
# First year
depreciation = (opening_wdv × rate) / 100

# Subsequent years
opening_wdv = previous_closing_wdv
depreciation = (opening_wdv × rate) / 100
closing_wdv = opening_wdv - depreciation
```

### Depreciation Rates (As per Income Tax Act - Reference)
**Note:** Temple admins should consult their auditor for appropriate rates

- **Buildings:**
  - Residential: 5%
  - Non-residential: 10%
- **Vehicles:**
  - Motor cars: 15%
  - Motorcycles: 20%
  - Other vehicles: 15%
- **Furniture & Fixtures:** 10%
- **Computer & Equipment:** 40%
- **Machinery:** 15%
- **Electrical Installations:** 10%
- **Plumbing & Sanitation:** 10%
- **Sound & Lighting Systems:** 15%

**System Feature:**
- Default rates provided as reference
- Fully customizable per asset
- Temple admin can set rates based on auditor advice

---

## API Endpoints Design

### Asset Master
- `GET /api/v1/assets/` - List assets
- `POST /api/v1/assets/` - Create asset
- `GET /api/v1/assets/{id}` - Get asset details
- `PUT /api/v1/assets/{id}` - Update asset
- `DELETE /api/v1/assets/{id}` - Delete asset

### Asset Purchase
- `POST /api/v1/assets/purchase/` - Record asset purchase
- **Auto-creates:** Journal entry, Asset record

### CWIP Management
- `GET /api/v1/assets/cwip/` - List CWIP projects
- `POST /api/v1/assets/cwip/` - Create CWIP project
- `POST /api/v1/assets/cwip/{id}/expense/` - Add expense to CWIP
- `POST /api/v1/assets/cwip/{id}/capitalize/` - Capitalize CWIP to asset

### Depreciation
- `POST /api/v1/assets/depreciation/calculate/` - Calculate depreciation
- `POST /api/v1/assets/depreciation/post/` - Post depreciation entries
- `GET /api/v1/assets/depreciation/schedule/{asset_id}` - Get depreciation schedule

### Revaluation
- `POST /api/v1/assets/revaluation/` - Record revaluation
- `GET /api/v1/assets/revaluation/{asset_id}` - Get revaluation history

### Disposal
- `POST /api/v1/assets/disposal/` - Record asset disposal
- **Auto-creates:** Journal entry, updates asset status

### Reports
- `GET /api/v1/assets/reports/register/` - Asset register
- `GET /api/v1/assets/reports/depreciation/` - Depreciation report
- `GET /api/v1/assets/reports/cwip/` - CWIP report

---

## Frontend Pages

1. **Asset Master** - Create/edit assets
2. **Asset Purchase** - Record purchases
3. **CWIP Management** - Track construction projects
4. **Depreciation** - Calculate and post depreciation
5. **Revaluation** - Record revaluations
6. **Asset Disposal** - Record disposals
7. **Asset Register** - Comprehensive report
8. **Depreciation Schedule** - Depreciation report

---

## Audit Compliance Features

1. **Asset Register** - Complete listing with all details
2. **Physical Verification** - Track verification status
3. **Document Management** - Link invoices, contracts, valuations
4. **Audit Trail** - Complete history of all transactions
5. **Reconciliation** - Book vs Physical verification
6. **Disclosure Reports** - For financial statements

---

## Implementation Phases

### Phase 1: Foundation
- Asset models and database
- Asset master CRUD
- Basic purchase accounting
- Account setup

### Phase 2: CWIP & Capitalization
- CWIP tracking
- Expense recording
- Capitalization workflow

### Phase 3: Depreciation
- Depreciation calculation
- Depreciation posting
- Depreciation schedule

### Phase 4: Advanced Features
- Revaluation
- Asset disposal
- Maintenance tracking
- Reports

---

**Status:** Design complete, ready for implementation following standard accounting practices and audit compliance.

