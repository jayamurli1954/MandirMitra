# Donation Features Guide

## Date: 28th November 2025

## Overview

This guide explains how to use the donation features in MandirMitra v1.0, including:
- Quick Donation Entry (Cash & In-Kind)
- Anonymous Donations
- Donation List View

---

## 1. Quick Donation Entry Widget

**Location:** Donations Page → "Record Donations" Tab

### Features:
- **Multiple Entries:** Record up to 5 donations at once
- **Auto-fill:** Mobile number auto-fills devotee details
- **PIN Code Lookup:** Auto-fills city/state from PIN code
- **Donation Types:** Supports both Cash and In-Kind donations

### How to Record a Cash Donation:

1. **Mobile Number** (Required) - Enter 10-digit mobile number
   - System auto-searches for existing devotee
   - Auto-fills name if found

2. **Devotee Name** (Required) - Enter or auto-filled

3. **PIN Code** (Optional) - Enter 6-digit PIN
   - Auto-fills city and state

4. **City & State** (Optional) - Auto-filled from PIN or enter manually

5. **Donation Type** - Select "Cash" (default)

6. **Amount** (Required) - Enter donation amount

7. **Category** (Required) - Select donation category

8. **Payment Mode** (Required for Cash) - Select: Cash, Card, UPI, Cheque, Online

9. **Anonymous** (Optional) - Check if donor wants to remain anonymous

10. Click **"Save All Donations"**

---

## 2. In-Kind Donation Entry

**Location:** Same Quick Donation Widget - Select "In-Kind" as Donation Type

### Steps:

1. Fill basic details (Mobile, Name, etc.) - **Optional for in-kind**
   - For in-kind, devotee details are optional

2. **Donation Type** - Select **"In-Kind"**

3. **Assessed Value** (Required) - Enter the assessed/market value

4. **Category** (Required) - Select category

5. **In-Kind Subtype** (Required) - Select one:
   - **Inventory** - Consumables (Rice, Dal, Oil, Sugar, etc.)
   - **Event Sponsorship** - Flower decoration, Lighting, etc.
   - **Asset** - Gold, Silver, Jewellery, Idols, Movable/Immovable assets

6. **Item Name** (Required) - e.g., "Rice", "Gold", "Flowers"

7. **Quantity** (Optional) - Enter quantity

8. **Unit** (Optional) - e.g., "kg", "pieces", "grams"

9. **Assessed Value** (Optional) - If different from amount

10. **Item Description** (Optional) - Additional details

11. Click **"Save All Donations"**

### Notes:
- Payment Mode is **NOT required** for in-kind donations
- System automatically creates inventory/asset entries based on subtype
- Journal entries are created with appropriate debit accounts

---

## 3. Anonymous Donations

**Location:** Quick Donation Widget - Check "Anonymous" checkbox

### How It Works:

1. **For Cash Donations:**
   - Check the **"Anonymous"** checkbox
   - Fill in amount, category, and payment mode
   - Devotee name can be left blank or will be stored as "Anonymous Donor"
   - System creates/uses a generic "Anonymous Donor" devotee record

2. **For In-Kind Donations:**
   - Check the **"Anonymous"** checkbox
   - Fill in in-kind details
   - Devotee information is optional

### Accounting Treatment:

- **Journal Entry Narration:** Shows "Donation from Anonymous Donor"
- **Devotee Record:** Uses a shared "Anonymous Donor" devotee (phone: 0000000000)
- **Receipt:** Can still generate receipt with "Anonymous Donor" name
- **Reports:** Anonymous donations are included in all reports but donor identity is protected

### Use Cases:
- Donors who want privacy
- Donations where donor identity is not known
- Bulk anonymous donations

---

## 4. Donation List View

**Location:** Donations Page → "Donation List" Tab

### Features:
- View all recorded donations
- Shows: Date, Devotee, Amount, Category, Payment Mode, Receipt Number
- Displays donation type (Cash/In-Kind)
- Shows anonymous status

### Display Fields:
- **Date** - Donation date
- **Devotee** - Donor name (or "Anonymous Donor")
- **Amount** - Donation amount or assessed value
- **Category** - Donation category
- **Payment** - Payment mode (for cash donations)
- **Receipt** - Receipt number
- **Type** - Cash or In-Kind indicator

---

## 5. Accounting Integration

### Cash Donations:
- **Debit:** Cash/Bank Account (based on payment mode)
- **Credit:** Donation Income Account (linked to category)
- **Narration:** "Donation from [Donor Name]" or "Donation from Anonymous Donor"

### In-Kind Donations:
- **Debit:** 
  - Inventory Account (if subtype = Inventory)
  - Asset Account (if subtype = Asset)
  - Expense Account (if subtype = Event Sponsorship)
- **Credit:** Donation Income Account
- **Narration:** "In-kind donation from [Donor Name]: [Item Name]"

### Anonymous Donations:
- Same accounting treatment as regular donations
- Narration shows "Anonymous Donor" instead of actual name
- All accounting entries are created normally

---

## 6. Quick Reference

### Cash Donation Fields:
- ✅ Mobile Number (Required)
- ✅ Devotee Name (Required)
- ✅ Amount (Required)
- ✅ Category (Required)
- ✅ Payment Mode (Required)
- ☑️ Anonymous (Optional)
- ☑️ Address fields (Optional)

### In-Kind Donation Fields:
- ☑️ Mobile Number (Optional)
- ☑️ Devotee Name (Optional)
- ✅ Donation Type = "In-Kind" (Required)
- ✅ Assessed Value (Required)
- ✅ Category (Required)
- ✅ In-Kind Subtype (Required)
- ✅ Item Name (Required)
- ☑️ Quantity, Unit, Description (Optional)
- ☑️ Anonymous (Optional)

---

## 7. Tips

1. **Quick Entry:** Use mobile number lookup to speed up entry
2. **PIN Code:** Enter PIN code first to auto-fill city/state
3. **Anonymous:** Check anonymous box if donor requests privacy
4. **In-Kind:** Select appropriate subtype for proper accounting
5. **Multiple Entries:** Add up to 5 entries and save all at once

---

## 8. Troubleshooting

### Donation List Not Showing:
- ✅ **Fixed:** Added `donation_type` field to response
- Refresh the page after recording donations

### In-Kind Donation Not Saving:
- Ensure all required fields are filled:
  - Donation Type = "In-Kind"
  - In-Kind Subtype
  - Item Name
  - Assessed Value

### Anonymous Donation Issues:
- System automatically creates "Anonymous Donor" devotee
- All anonymous donations link to the same devotee record
- Accounting entries are created normally

---

**Last Updated:** 28th November 2025


