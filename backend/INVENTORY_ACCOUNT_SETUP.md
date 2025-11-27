# Inventory Account Setup Guide

## Overview

The Inventory Management module uses a **dedicated account code series (1400-1499)** for proper accounting and reporting.

## Account Code Structure

### Inventory Asset Accounts (1400-1499)

**Parent Account:**
- **1400** - Inventory Assets (Parent account for all inventory)

**Category-wise Accounts:**
- **1401** - Inventory - Pooja Materials (Flowers, oil, camphor, incense, kumkum)
- **1402** - Inventory - Grocery & Annadanam (Rice, dal, oil, spices, vegetables)
- **1403** - Inventory - Cleaning Supplies (Soap, detergent, cleaning supplies)
- **1404** - Inventory - Maintenance Items (Electrical, plumbing, maintenance)
- **1405** - Inventory - General (Other inventory items)
- **1406-1499** - Reserved for future inventory categories

### Expense Accounts (for Consumption)

When inventory is issued/consumed, it's debited to expense accounts:
- **5001** - Pooja Expense
- **5002** - Annadanam Expense
- **5003** - Cleaning & Maintenance Expense
- **5004** - Maintenance Expense
- **5005** - General Operational Expense

## Setup Instructions

### Option 1: Using API Endpoint (Recommended)

1. **Start your backend server**
2. **Login and get your authentication token**
3. **Call the setup endpoint:**
   ```bash
   POST http://localhost:8000/api/v1/inventory/setup-accounts/
   Headers: Authorization: Bearer <your_token>
   ```

This will:
- ✅ Create all inventory accounts (1400-1405)
- ✅ Link existing items to their category-specific accounts
- ✅ Link existing stores to default inventory account (1400)

### Option 2: Using Python Script

```bash
cd backend
python scripts/setup_inventory_accounts.py
```

## How It Works

### Automatic Account Linking

1. **When creating an Item:**
   - Item category determines which inventory account (1401-1405) it links to
   - Example: Item with category "Pooja Material" → Links to account 1401

2. **When creating a Store:**
   - Store links to default inventory account (1400) or can be customized

3. **When recording Purchase:**
   - Dr: Inventory Account (1401-1405 based on item category)
   - Cr: Cash/Bank (1101/1110)

4. **When recording Issue/Consumption:**
   - Dr: Expense Account (5001-5005 based on item category/purpose)
   - Cr: Inventory Account (1401-1405)

## Account Priority Logic

For **Purchase** transactions:
1. **Store's inventory_account_id** (if store has specific account)
2. **Item's inventory_account_id** (if item is linked to specific account)
3. **Fallback to 1400** (Inventory Assets - Parent)

For **Issue** transactions:
1. **Item's expense_account_id** (if item has specific expense account)
2. **Purpose-based mapping** (Annadanam → 5002, Pooja → 5001)
3. **Fallback to 5005** (General Operational Expense)

## Benefits

✅ **Proper Accounting:** All inventory transactions properly recorded
✅ **Category-wise Reporting:** Easy to see inventory value by category
✅ **Trial Balance:** Clean inventory asset line (1400) or detailed (1401-1405)
✅ **Consumption Analysis:** Track expenses by purpose (Pooja, Annadanam, etc.)
✅ **Scalable:** 1406-1499 reserved for future categories

## Verification

After setup, verify accounts exist:

```sql
SELECT account_code, account_name, account_type
FROM accounts
WHERE account_code BETWEEN '1400' AND '1499'
ORDER BY account_code;
```

## Troubleshooting

**Issue:** "Parent account 1000 (Assets) not found"
- **Solution:** Run `python seed_chart_of_accounts.py` first

**Issue:** Items not linked to accounts
- **Solution:** Run setup script again, or manually link items via API

**Issue:** Accounts created but items not linked
- **Solution:** Check item categories match the mapping in setup script


