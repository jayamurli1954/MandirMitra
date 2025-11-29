# Depreciation Methods - Implementation Guide

## Overview

The Asset Management module supports **all standard depreciation methods** to give temple administrators maximum flexibility. Temple admins can consult their auditors and choose the most appropriate method for each asset type.

---

## Supported Depreciation Methods

### 1. Straight-Line Method ✅
**Most Common - Recommended for most assets**

**Formula:** `Annual Depreciation = (Cost - Salvage Value) / Useful Life`

**Characteristics:**
- Even distribution over useful life
- Simple and predictable
- Easy to understand and audit

**Best For:**
- Buildings
- Infrastructure
- Assets with consistent usage
- Most fixed assets

**Example:**
- Cost: ₹60,000
- Salvage Value: ₹10,000
- Useful Life: 5 years
- Annual Depreciation: (60,000 - 10,000) / 5 = ₹10,000

---

### 2. Written Down Value (WDV) / Diminishing Balance ✅
**Approved by Income Tax Act**

**Formula:** `Annual Depreciation = (Book Value × Depreciation Rate) / 100`

**Characteristics:**
- Higher depreciation in early years
- Reflects faster wear in initial stages
- Salvage value not considered in calculation
- Book value never reaches zero

**Best For:**
- Vehicles
- Computers
- Equipment with high initial wear
- Assets that lose value quickly

**Example:**
- Cost: ₹50,000
- Rate: 20%
- Year 1: 50,000 × 20% = ₹10,000 (Book Value: ₹40,000)
- Year 2: 40,000 × 20% = ₹8,000 (Book Value: ₹32,000)

---

### 3. Double Declining Balance ✅
**Accelerated Depreciation**

**Formula:** `Annual Depreciation = 2 × Beginning Book Value × (100% / Useful Life)`

**Characteristics:**
- Front-loads depreciation expenses
- Double the straight-line rate
- Higher early-year depreciation
- Useful for tax benefits

**Best For:**
- Assets that lose value very quickly
- When tax benefits are priority
- Equipment with rapid obsolescence

**Example:**
- Cost: ₹60,000
- Useful Life: 5 years
- Rate: 2 × (100% / 5) = 40%
- Year 1: 60,000 × 40% = ₹24,000 (Book Value: ₹36,000)
- Year 2: 36,000 × 40% = ₹14,400 (Book Value: ₹21,600)

---

### 4. Declining Balance Method ✅
**Constant Rate on Reducing Value**

**Formula:** `Annual Depreciation = Book Value × Depreciation Rate`

**Characteristics:**
- Constant percentage rate
- Applied to reducing book value
- Similar to WDV but rate may differ

**Best For:**
- Assets with higher initial depreciation
- When specific rate is required

---

### 5. Units of Production Method ✅
**Usage-Based Depreciation**

**Formula:** `Depreciation = [(Cost - Salvage Value) / Total Estimated Units] × Actual Units Produced`

**Characteristics:**
- Based on actual usage, not time
- Depreciation varies with production/usage
- More accurate for variable usage assets

**Best For:**
- Manufacturing equipment
- Vehicles (mileage-based)
- Machinery with variable usage
- Production-based assets

**Example:**
- Cost: ₹1,00,000
- Salvage Value: ₹10,000
- Total Estimated Units: 50,000
- Depreciation per Unit: (1,00,000 - 10,000) / 50,000 = ₹1.80
- If 10,000 units produced: 10,000 × ₹1.80 = ₹18,000

---

### 6. Annuity Method ✅
**Time Value of Money Consideration**

**Formula:**
```
Annuity = [i × TDA × (1+i)^n] / [(1+i)^n - 1]
Depreciation = Annuity - (i × Book Value at Start)
```

**Characteristics:**
- Considers time value of money
- Assumes steady cash flow
- More complex calculation
- Appropriate for long-life assets

**Best For:**
- Long-life assets
- Large purchase price
- Assets with fixed returns
- When interest component matters

**Example:**
- Cost: ₹80,000
- Salvage Value: ₹10,000
- Useful Life: 5 years
- Interest Rate: 8%
- Annual Depreciation: Calculated considering interest

---

### 7. Depletion Method ✅
**For Natural Resources**

**Formula:** `Depreciation = (Cost - Salvage Value) / Total Units × Units Extracted`

**Characteristics:**
- For natural resources
- Based on extraction/usage
- Rarely used for temples

**Best For:**
- Mineral deposits
- Timber
- Oil reserves
- Natural resource extraction

---

### 8. Sinking Fund Method ✅
**Replacement Fund Approach**

**Formula:** `A = [{1+(r/m)}^(n×m) - 1} / (r/m)] × P`

**Characteristics:**
- Sets aside funds for replacement
- Considers interest on fund
- Useful for expensive replacements

**Best For:**
- Expensive assets requiring replacement
- When replacement planning is critical
- Utility companies
- Large infrastructure

---

## System Implementation

### Configuration Per Asset
- Each asset can have a **different depreciation method**
- Method selection is **configurable** at asset creation/update
- Temple admin can **consult auditor** and choose method
- System calculates depreciation automatically based on selected method

### Calculation Engine
- All methods implemented in `DepreciationCalculator` class
- Automatic calculation based on asset parameters
- Supports monthly and yearly depreciation
- Handles edge cases and validations

### Audit Trail
- Method used is recorded in depreciation schedule
- All calculations are traceable
- Supports auditor review and verification

---

## Selection Guidelines

### For Temple Administrators

1. **Consult Your Auditor**
   - Different methods have different tax implications
   - Auditor can advise best method for your situation
   - Method can be changed (with proper documentation)

2. **Consider Asset Type**
   - Buildings → Straight-Line
   - Vehicles → WDV or Double Declining
   - Equipment → WDV or Units of Production
   - Computers → WDV (high obsolescence)

3. **Consider Financial Goals**
   - Tax benefits → Accelerated methods (WDV, Double Declining)
   - Even expenses → Straight-Line
   - Usage-based → Units of Production

4. **Consistency**
   - Use same method for similar assets
   - Document method selection rationale
   - Maintain consistency for audit compliance

---

## Accounting Standards Compliance

### Indian Accounting Standards
- **AS 6** - Depreciation Accounting: ✅ Compliant
- **Ind AS 16** - Property, Plant and Equipment: ✅ Compliant
- **Income Tax Act** - WDV method approved: ✅ Supported

### Audit Requirements
- ✅ Method selection documented
- ✅ Calculations traceable
- ✅ Depreciation schedule maintained
- ✅ Journal entries created
- ✅ Disclosure reports available

---

## System Features

1. **Flexible Method Selection** - Choose per asset
2. **Automatic Calculation** - System calculates based on method
3. **Audit Trail** - Complete history of calculations
4. **Reports** - Depreciation schedule, asset register
5. **Compliance** - Follows accounting standards

---

**Status:** All depreciation methods implemented and ready for use. Temple admins can choose based on auditor advice.




