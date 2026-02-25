# Temple Donation & Accounting Management System
## Comprehensive Solution Proposal

**Document Version:** 1.0
**Date:** November 23, 2025
**Prepared for:** Temple Management & Trust Discussions

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Temple Registration & Multi-tenant Architecture](#temple-registration--multi-tenant-architecture)
4. [Donation Management](#donation-management)
5. [In-Kind Donations](#in-kind-donations)
6. [Sponsorship Management](#sponsorship-management)
7. [UPI Payment Tracking & Reconciliation](#upi-payment-tracking--reconciliation)
8. [Double-Entry Accounting System](#double-entry-accounting-system)
9. [Receipt Generation & Acknowledgment](#receipt-generation--acknowledgment)
10. [Reports & Compliance](#reports--compliance)
11. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

MandirMitra is a comprehensive temple management system designed specifically for Indian temples to handle complex donation scenarios, inventory management, and maintain proper accounting records. The system addresses real-world challenges faced by temples including:

- Multiple types of donations (cash, online, in-kind, sponsorships)
- UPI payment tracking without payment gateway integration
- Consumable inventory management (Annadana items)
- Precious asset register (gold, silver ornaments)
- Expense sponsorships with direct vendor payments
- Proper double-entry bookkeeping
- 80G certificate generation and compliance
- Multi-temple support (SaaS) or standalone deployment

---

## System Overview

### Key Modules

1. **Temple Settings & Configuration**
2. **Devotee Management**
3. **Donation Management** (Cash, Online, In-Kind)
4. **Seva/Archana Booking System**
5. **Sponsorship Management**
6. **Inventory Management** (Consumables & Assets)
7. **UPI Payment Logging & Reconciliation**
8. **Vendor Management**
9. **Double-Entry Accounting**
10. **Receipt Generation**
11. **Reports & Analytics**

---

## Temple Registration & Multi-tenant Architecture

### Why This Matters

Different temples have different names, addresses, logos, and banking details. Hardcoding any temple's information limits the system's usability. Our solution supports:

- **SaaS Mode:** Multiple temples using the same platform (cloud-based)
- **Standalone Mode:** Single temple installation on local server

### Temple Settings Include

#### Basic Information
- Temple Name (in multiple languages: English, Kannada, Sanskrit)
- Deity/Main God Name
- Complete Address with Pincode
- Contact Details (Phone, Email, Website)
- Trust Registration Numbers
- Tax Exemption Certificates (80G, 12A, FCRA)

#### Banking Information
- Bank Name
- Account Number
- IFSC Code
- UPI QR Code details
- Multiple bank accounts support

#### Visual Identity
- Temple Logo (displayed on receipts, website)
- Authorized Signatory Name
- Digital Signature for receipts
- Header/Footer design for documents

#### Configuration
- Financial Year Start Month (April/January)
- Receipt Number Format/Prefix
- Enable/Disable specific features
- Language preferences

### Setup Process

#### For SaaS (Multi-Temple Cloud Platform)
1. Temple administrator visits registration page
2. Completes registration form with temple details
3. Email verification
4. Guided onboarding wizard
5. Initial chart of accounts setup
6. First admin user creation

#### For Standalone Installation
1. Install software on temple's server
2. First-time setup wizard on startup
3. Single temple configuration
4. Admin user creation
5. Basic settings configuration

### Impact on System

- **All Receipts:** Automatically show correct temple name, logo, address
- **All Headers:** Display temple branding
- **Email/SMS Templates:** Use temple contact information
- **Reports:** Generate with temple-specific letterhead
- **Accounting:** Separate books for each temple (in SaaS mode)

---

## Donation Management

### Types of Donations

#### 1. Cash Donations
Regular cash donations received at temple counter or hundi collection.

**Recording:**
- Devotee details (optional or mandatory based on amount)
- Amount
- Purpose (General/Specific deity/Festival)
- Receipt generation
- Daily hundi counting and reconciliation

**Accounting Treatment:**
```
Dr. Cash in Hand                 1,000
   Cr. Donation Income - Cash         1,000
```

#### 2. Online Donations (Bank Transfer/UPI)
Covered in detail in UPI Payment section below.

#### 3. Foreign Donations (FCRA Compliance)
For temples registered under FCRA:
- Separate tracking of foreign donations
- Foreign currency conversion
- FCRA compliance reports
- Separate bank account maintenance

---

## In-Kind Donations

### Overview

Many temples receive donations in the form of goods rather than money. These need proper acknowledgment, inventory tracking, and accounting treatment.

### Categories of In-Kind Donations

#### A. Consumable Items (for Annadana/Prasadam)

**Common Items:**
- Rice (various types)
- Wheat/Atta
- Dal (Toor, Moong, Chana)
- Sugar
- Cooking Oil (Sunflower, Groundnut)
- Vegetables
- Milk and Milk Products
- Spices
- Fruits

**Management Process:**

1. **Receipt:**
   - Record item name and category
   - Weigh/measure quantity (kg, liters, pieces)
   - Estimate market value
   - Generate acknowledgment receipt
   - Add to inventory

2. **Storage:**
   - Track current stock levels
   - Monitor expiry dates (if applicable)
   - Location tracking (which storage room)
   - Alert for low stock levels
   - Alert for items nearing expiry

3. **Consumption:**
   - Record usage for Annadana/events
   - Track daily consumption
   - Update inventory balance
   - Link to specific events/festivals

**Accounting Treatment:**

```
When Received:
Dr. Inventory - Annadana Stores (Asset)    2,500
   Cr. In-Kind Donation Income (Income)         2,500
   (25 kg Rice @ ₹100/kg)

When Consumed:
Dr. Annadana Expenses (Expense)            2,500
   Cr. Inventory - Annadana Stores (Asset)      2,500
```

**Receipt Format:**
```
════════════════════════════════════════════
         [TEMPLE NAME & LOGO]
      IN-KIND DONATION RECEIPT
════════════════════════════════════════════

Receipt No: IK/2025/001
Date: 23-November-2025

Received with gratitude from:
Name: Sri Ram Kumar
Phone: 9876543210
Address: Bangalore

Donation Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Item          : Basmati Rice
Quantity      : 25 Kg
Estimated Value: ₹2,500
Purpose       : Annadana Service
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your generous donation will be used to serve
prasadam to devotees visiting our temple.

May the divine blessings be upon you and
your family.

                    [Digital Signature]
                    Temple Administrator

════════════════════════════════════════════
Note: This receipt is for acknowledgment
purposes and may be used for tax exemption
under Section 80G of Income Tax Act.
════════════════════════════════════════════
```

#### B. Precious Items (Gold, Silver, Precious Stones)

**Common Items:**
- Gold Ornaments (chains, bangles, rings)
- Silver Articles (vessels, plates, idols)
- Diamond/Precious Stone jewelry
- Antique items

**Management Process:**

1. **Receipt:**
   - Detailed description of item
   - Weight measurement (grams)
   - Purity assessment (22K, 24K gold)
   - Professional appraisal (for high-value items)
   - Photograph documentation
   - Generate detailed receipt
   - Add to Asset Register

2. **Storage:**
   - Secure locker/vault storage
   - Location documentation
   - Insurance coverage
   - Periodic physical verification
   - Valuation updates (annual)

3. **Usage:**
   - Adorning deity during festivals
   - Display in temple
   - Sale/Melting (only with trust approval)
   - Transfer to other temple assets

**Accounting Treatment:**

```
When Received:
Dr. Temple Assets - Gold Ornaments (Asset)  3,25,000
   Cr. Asset Donation Income (Income)            3,25,000
   (Gold Chain, 50 grams, 22K, appraised value)
```

**Receipt Format:**
```
════════════════════════════════════════════
         [TEMPLE NAME & LOGO]
    PRECIOUS ITEM DONATION RECEIPT
════════════════════════════════════════════

Receipt No: PD/2025/001
Date: 23-November-2025

Received with gratitude from:
Name: Smt. Lakshmi Devi
Phone: 9876543210

Donation Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Item Description: Gold Chain with Pendant
Weight          : 50 grams
Purity          : 22 Karat Gold
Appraised By    : [Certified Jeweler Name]
Appraised Value : ₹3,25,000
Date of Appraisal: 23-November-2025
Purpose         : Temple Asset
Asset ID        : GOLD/2025/045
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The donated item has been added to the
temple's asset register and will be
maintained with utmost care and security.

Photo documentation attached.

May Lord's blessings shower upon you.

                    [Digital Signature]
                    Temple Administrator

════════════════════════════════════════════
```

#### C. General Items

**Common Items:**
- Cloth (for deity decoration)
- Utensils (for temple kitchen)
- Furniture
- Electronic items (TV, speakers)
- Books (religious texts)
- Musical instruments

**Management:**
- Similar to consumables but without consumption tracking
- Track condition and location
- Depreciation for accounting
- Periodic physical verification

### Inventory Reports

1. **Current Stock Report:**
   - Item-wise current balance
   - Value of inventory
   - Items below reorder level
   - Items nearing expiry

2. **Consumption Report:**
   - Daily/Monthly/Annual consumption
   - Item-wise usage analysis
   - Event-wise consumption
   - Cost per meal (for Annadana)

3. **Asset Register:**
   - Complete list of precious items
   - Current valuation
   - Location and custody
   - Insurance details
   - Physical verification status

---

## Sponsorship Management

### Overview

Sponsorships allow devotees to support specific temple activities or expenses. This is different from general donations as it's purpose-specific.

### Types of Sponsorships

#### 1. Expense Sponsorship (Temple Pays Vendor)

**Scenario:**
A devotee commits to sponsor flower decoration for a festival. The devotee pays the temple, and the temple pays the florist.

**Example:**
- Event: Rathotsava Festival
- Sponsorship: Flower Decoration
- Amount: ₹10,000
- Devotee: Sri Ram Kumar

**Process Flow:**

1. **Commitment Stage:**
   - Devotee expresses intent to sponsor
   - Temple records sponsorship commitment
   - Generate sponsorship acknowledgment

2. **Payment Stage:**
   - Devotee pays ₹10,000 to temple
   - Temple issues receipt
   - Mark sponsorship as "Paid"

3. **Service Stage:**
   - Temple hires florist
   - Florist decorates for festival (₹10,000)
   - Temple pays florist from collected amount
   - Mark sponsorship as "Fulfilled"

**Accounting Treatment:**

```
When sponsorship is committed:
Dr. Sponsorship Receivable - Ram Kumar (Asset)    10,000
   Cr. Sponsorship Income - Flower Decoration (Income) 10,000

When devotee pays temple:
Dr. Cash/Bank (Asset)                              10,000
   Cr. Sponsorship Receivable - Ram Kumar (Asset)      10,000

When temple pays florist:
Dr. Flower Decoration Expense (Expense)            10,000
   Cr. Cash/Bank (Asset)                               10,000
```

**Sponsorship Acknowledgment:**
```
════════════════════════════════════════════
         [TEMPLE NAME & LOGO]
     SPONSORSHIP ACKNOWLEDGMENT
════════════════════════════════════════════

Receipt No: SP/2025/001
Date: 23-November-2025

Received with gratitude from:
Sri Ram Kumar
Phone: 9876543210

Sponsorship Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose       : Flower Decoration
Event         : Rathotsava Festival
Event Date    : 28-November-2025
Amount Committed: ₹10,000
Payment Status: Paid in Full
Payment Date  : 23-November-2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your generous sponsorship will grace our
temple festival and bring joy to thousands
of devotees.

The flower decoration will be arranged as
per the festival requirements.

May Lord's blessings be upon you and
your family.

                    [Digital Signature]
                    Temple Administrator
════════════════════════════════════════════
```

#### 2. Direct Payment to Vendor (Devotee Pays Vendor Directly)

**Scenario:**
A devotee directly pays a tent vendor for temple festival arrangements, then provides the invoice to the temple.

**Example:**
- Event: Annual Brahmotsavam
- Service: Tent Arrangement
- Vendor: ABC Tent House
- Amount: ₹25,000
- Devotee: Smt. Lakshmi Devi
- **Devotee pays vendor directly**

**Process Flow:**

1. **Arrangement:**
   - Devotee contacts vendor (or temple provides vendor details)
   - Service is agreed upon
   - Devotee commits to pay vendor

2. **Service & Payment:**
   - Vendor provides service (tent setup)
   - Devotee pays vendor ₹25,000 directly
   - Devotee receives invoice from vendor

3. **Documentation:**
   - Devotee submits invoice copy to temple
   - Temple verifies invoice and service completion
   - Temple issues donation acknowledgment

**Accounting Treatment:**

```
When devotee provides proof of payment:
Dr. Tent Hiring Expense (Expense)                  25,000
   Cr. Donation Income - Direct Payment (Income)        25,000

Note: This is a non-cash transaction. Both the expense
incurred and the donation received are recorded, but no
actual money flows through temple accounts.
```

**Acknowledgment Receipt:**
```
════════════════════════════════════════════
         [TEMPLE NAME & LOGO]
  DONATION ACKNOWLEDGMENT (Direct Payment)
════════════════════════════════════════════

Receipt No: DP/2025/001
Date: 23-November-2025

Received with gratitude from:
Smt. Lakshmi Devi
Phone: 9876543210

Donation Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose       : Tent Arrangement
Event         : Annual Brahmotsavam
Event Date    : 5-December-2025
Vendor Name   : ABC Tent House
Vendor Invoice: TH/2025/456
Amount Paid   : ₹25,000
Payment Date  : 20-November-2025
Payment Mode  : Direct to Vendor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your direct payment to the vendor for temple
service is gratefully acknowledged. This is
a valuable contribution to the successful
conduct of our temple festival.

Copy of vendor invoice attached with this
acknowledgment for your tax records.

Your devotion and generosity are deeply
appreciated.

                    [Digital Signature]
                    Temple Administrator

════════════════════════════════════════════
Note: Eligible for tax exemption under
Section 80G. Vendor invoice attached.
════════════════════════════════════════════
```

### Sponsorship Categories

Common sponsorship categories in temples:

1. **Festival Sponsorships:**
   - Overall festival sponsorship
   - Specific day sponsorship
   - Opening ceremony sponsorship

2. **Decoration Sponsorships:**
   - Flower decoration
   - Lighting decoration
   - Rangoli/Kolam

3. **Service Sponsorships:**
   - Tent arrangement
   - Sound system
   - Photography/Videography
   - Stage setup

4. **Ritual Sponsorships:**
   - Abhisheka sponsorship
   - Special pooja sponsorship
   - Homam/Havan sponsorship

5. **Annadana Sponsorships:**
   - Daily Annadana (specific date)
   - Festival Annadana
   - Weekly Annadana (every Saturday, etc.)

6. **Maintenance Sponsorships:**
   - Furniture donation
   - Equipment donation
   - Building renovation

### Vendor Management

For effective sponsorship management, especially direct payments, maintain vendor database:

**Vendor Information:**
- Vendor name and type (florist, caterer, tent supplier, electrician)
- Contact person and phone
- Address
- GSTIN (for GST invoices)
- Bank details
- Service categories
- Previous work history
- Rating/feedback

**Benefits:**
- Temple can recommend reliable vendors to devotees
- Track which vendor serviced which event
- Maintain vendor payment records
- Quality control and feedback
- Future planning and budgeting

---

## UPI Payment Tracking & Reconciliation

### Real-World Scenario

Many temples have:
- **Informational Website** (temple details, timings, events)
- **Static UPI QR Code** (from bank or UPI provider like PhonePe/GPay)
- **No online payment processing** on website

When devotees scan QR code and pay:
- Temple admin receives SMS notification
- Very limited information in SMS
- Website doesn't capture payment details
- Need to manually track who paid for what

### Typical SMS Format

```
Rs 500 credited to A/c XX1234
from 9876543210@paytm
on 23-Nov-2025 10:30 AM
Ref: 123456789012
```

Or even simpler:
```
A/c XX1234 credited Rs 500
on 23-Nov 10:30
```

### The Challenge

System doesn't automatically know:
- **Who paid?** (only phone number from UPI ID)
- **For what purpose?** (Donation? Seva? Sponsorship?)
- **Which seva?** (if seva booking)
- **Which event?** (if sponsorship)

### Solution: Quick Payment Entry System

#### Step 1: Immediate Logging (Real-time)

**Mobile-Friendly Quick Entry Interface:**

When admin receives SMS, immediately open app and log payment:

```
┌─────────────────────────────────────────┐
│  🔔 Log UPI Payment                     │
├─────────────────────────────────────────┤
│  Amount Received: ₹ [500        ]      │
│                                         │
│  Phone Number: [9876543210]  [Search]  │
│    ✓ Found: Ram Kumar                  │
│    [Not in system? Add Devotee]        │
│                                         │
│  Payment For:                           │
│    ○ General Donation                   │
│    ● Seva Booking                       │
│    ○ Sponsorship                        │
│    ○ Annadana Contribution              │
│                                         │
│  [Seva Selected]                        │
│  Which Seva: [Abhisheka ▼]             │
│  Booking Date: [Today ▼]                │
│                                         │
│  UPI Reference: [123456789012]         │
│  (from SMS - optional)                  │
│                                         │
│  Notes: [                          ]    │
│                                         │
│  [Cancel]  [Save & Generate Receipt]   │
└─────────────────────────────────────────┘
```

**Process:**
1. Admin gets SMS: "Rs 500 from 9876543210@paytm"
2. Opens app on phone/tablet
3. Enters ₹500
4. Enters/scans phone: 9876543210
5. System auto-finds devotee "Ram Kumar"
6. Selects purpose: "Seva Booking" → "Abhisheka" → "Today"
7. Adds UPI reference from SMS
8. Clicks "Save"

**System Actions:**
- Creates seva booking record
- Links to devotee
- Marks payment as UPI
- Posts to accounting (Dr. Bank, Cr. Seva Income)
- Generates receipt with temple letterhead
- Sends SMS/Email to Ram Kumar with receipt PDF
- **All in < 30 seconds!**

#### Step 2: Bank Reconciliation (Daily/Weekly)

To ensure no payments are missed:

**Download Bank Statement:**
- Login to internet banking
- Download statement (CSV/Excel format)
- Contains: Date, Time, Amount, UPI Ref, Sender UPI ID

**Upload to System:**
```
┌─────────────────────────────────────────┐
│  Bank Reconciliation                    │
├─────────────────────────────────────────┤
│  Bank Account: [SBI Current ▼]         │
│  Upload Statement: [Choose File]       │
│                      [Upload]           │
│                                         │
│  Date Range: 23-Nov to 23-Nov           │
│                                         │
│  Bank Statement Summary:                │
│  Total Credits: ₹25,500 (52 txns)      │
│                                         │
│  System Records:                        │
│  Total Logged: ₹25,500 (52 txns)       │
│                                         │
│  ✓ All transactions matched!            │
│                                         │
│  [View Detailed Report]                 │
└─────────────────────────────────────────┘
```

**If Discrepancies Found:**
```
┌─────────────────────────────────────────┐
│  ⚠️  Reconciliation Alert               │
├─────────────────────────────────────────┤
│  Bank Statement: ₹25,500 (52 txns)     │
│  System Records:  ₹24,500 (50 txns)     │
│                                         │
│  Difference: ₹1,000 (2 missing)         │
│                                         │
│  Missing Transactions:                  │
│  ┌─────────────────────────────────┐   │
│  │ Date  │Amount│UPI ID  │Action   │   │
│  ├─────────────────────────────────┤   │
│  │23-Nov │  500 │9876...│[Add Now]│   │
│  │23-Nov │  500 │8765...│[Add Now]│   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Review & Complete Reconciliation]     │
└─────────────────────────────────────────┘
```

Clicking "Add Now" opens the quick entry form pre-filled with bank statement data.

### Smart Features

#### Auto-Matching by Phone Number
```python
# When devotee enters phone: 9876543210
# System extracts from UPI ID: 9876543210@paytm
# Searches devotee database
# Auto-fills: "Ram Kumar"
```

#### Duplicate Detection
```
⚠️  Similar payment found:
   ₹500 from Ram Kumar (9876543210)
   Logged 5 minutes ago

   Is this a duplicate entry?
   [Yes, Skip]  [No, Continue]
```

#### Daily Summary Dashboard
```
┌─────────────────────────────────────────┐
│  Today's UPI Payments (23-Nov-2025)    │
├─────────────────────────────────────────┤
│  Total Received: ₹12,500 (25 payments) │
│                                         │
│  Breakdown:                             │
│  • Donations:     ₹5,000  (10 txns)    │
│  • Seva Bookings: ₹6,500  (12 txns)    │
│  • Sponsorships:  ₹1,000  (3 txns)     │
│                                         │
│  Reconciliation Status:                 │
│  ✓ All payments logged and matched     │
│                                         │
│  [View Details]  [Log New Payment]     │
└─────────────────────────────────────────┘
```

### Accounting Integration

Every UPI payment automatically posts to accounts:

**For Donation:**
```
Dr. Bank Account - SBI (Asset)           500
   Cr. Donation Income (Income)              500
```

**For Seva:**
```
Dr. Bank Account - SBI (Asset)           500
   Cr. Seva Income - Abhisheka (Income)      500
```

**For Sponsorship:**
```
Dr. Bank Account - SBI (Asset)         1,000
   Cr. Sponsorship Income (Income)          1,000
```

### Benefits of This Approach

1. **Fast Entry:** Admin can log payment in < 30 seconds
2. **Mobile Friendly:** Works on phone while at temple
3. **Auto-Matching:** Finds devotee automatically by phone
4. **Immediate Receipt:** Devotee gets receipt within minutes
5. **No Missing Payments:** Bank reconciliation catches everything
6. **Proper Accounting:** Auto-posts to double-entry books
7. **Audit Trail:** Complete record of who entered what and when
8. **Devotee Satisfaction:** Quick acknowledgment builds trust

---

## Double-Entry Accounting System

### Overview

Proper accounting is essential for:
- Financial transparency
- Audit compliance
- Tax exemption maintenance (80G, 12A)
- Trust management
- Regulatory reporting
- Decision making

### Chart of Accounts Structure

A comprehensive, hierarchical account structure:

```
ASSETS
├── Current Assets
│   ├── Cash & Bank
│   │   ├── Cash in Hand - Counter
│   │   ├── Cash in Hand - Hundi
│   │   ├── Bank - SBI Current Account
│   │   ├── Bank - HDFC Savings Account
│   │   └── Bank - Fixed Deposits
│   ├── Receivables
│   │   ├── Sponsorship Receivable
│   │   └── Other Receivables
│   └── Inventories
│       ├── Annadana Stores (Rice, Dal, Oil)
│       ├── Pooja Materials Inventory
│       └── General Supplies
├── Fixed Assets
│   ├── Temple Building
│   ├── Land
│   ├── Furniture & Fixtures
│   ├── Vehicles
│   ├── Computer & Equipment
│   └── Accumulated Depreciation
└── Precious Assets
    ├── Gold Ornaments
    ├── Silver Articles
    ├── Precious Stones
    └── Antique Items

LIABILITIES
├── Current Liabilities
│   ├── Vendor Payables
│   ├── Salary Payables
│   ├── Advance from Devotees
│   └── Other Payables
└── Long-term Liabilities
    ├── Corpus Fund (Endowment - cannot be spent)
    └── Building Fund

INCOME
├── Donation Income
│   ├── General Donation - Cash
│   ├── General Donation - Online/UPI
│   ├── General Donation - Bank Transfer
│   ├── Hundi Collection
│   ├── Donation - Direct Payment (vendor payments)
│   └── Foreign Donations (FCRA)
├── Sponsorship Income
│   ├── Festival Sponsorship Income
│   ├── Flower Decoration Sponsorship
│   ├── Lighting Sponsorship
│   ├── Annadana Sponsorship
│   └── Other Sponsorships
├── Seva Income
│   ├── Abhisheka Seva Income
│   ├── Alankara Seva Income
│   ├── Archana Income
│   ├── Special Pooja Income
│   └── Other Seva Income
├── In-Kind Donation Income
│   ├── Consumables Donation Income
│   └── Asset Donation Income
└── Other Income
    ├── Interest Income
    ├── Rent Income (if temple has rental property)
    └── Miscellaneous Income

EXPENSES
├── Operational Expenses
│   ├── Salaries & Wages
│   │   ├── Priest Salaries
│   │   ├── Administrative Staff Salaries
│   │   └── Support Staff Wages
│   ├── Utilities
│   │   ├── Electricity Charges
│   │   ├── Water Charges
│   │   └── Internet & Phone
│   └── Maintenance & Repairs
│       ├── Building Maintenance
│       ├── Equipment Repairs
│       └── Cleaning & Sanitation
├── Pooja & Ritual Expenses
│   ├── Flower Decoration Expense
│   ├── Lighting Expense
│   ├── Pooja Materials (oil, camphor, incense)
│   ├── Prasadam Expenses
│   └── Special Ritual Expenses
├── Annadana Expenses
│   ├── Vegetables & Groceries
│   ├── Cooking Gas
│   ├── Disposables (plates, cups)
│   └── Kitchen Supplies
├── Festival Expenses
│   ├── Decoration Expenses
│   ├── Tent Hiring
│   ├── Sound System Rental
│   ├── Stage & Lighting
│   └── Special Arrangements
└── Administrative Expenses
    ├── Audit Fees
    ├── Legal & Professional Fees
    ├── Bank Charges
    ├── Printing & Stationery
    ├── Postage & Communication
    └── Insurance
```

### Accounting Treatment Examples

#### Example 1: Cash Donation
```
Devotee gives ₹1,000 cash donation

Journal Entry:
Dr. Cash in Hand - Counter (Asset)         1,000
   Cr. Donation Income - Cash (Income)          1,000
```

#### Example 2: UPI Seva Payment
```
Devotee pays ₹500 via UPI for Abhisheka Seva

Journal Entry:
Dr. Bank - SBI Current Account (Asset)       500
   Cr. Seva Income - Abhisheka (Income)          500
```

#### Example 3: In-Kind Donation - Rice
```
Devotee donates 25 kg rice (valued at ₹2,500)

Journal Entry:
Dr. Inventory - Annadana Stores (Asset)    2,500
   Cr. In-Kind Donation Income (Income)         2,500

When rice is consumed for Annadana:
Dr. Annadana Expenses (Expense)            2,500
   Cr. Inventory - Annadana Stores (Asset)      2,500
```

#### Example 4: Gold Ornament Donation
```
Devotee donates gold chain (50g, valued at ₹3,25,000)

Journal Entry:
Dr. Precious Assets - Gold (Asset)       3,25,000
   Cr. Asset Donation Income (Income)          3,25,000
```

#### Example 5: Sponsorship - Temple Pays Vendor
```
Stage 1: Devotee commits ₹10,000 for flower decoration
Dr. Sponsorship Receivable (Asset)        10,000
   Cr. Sponsorship Income (Income)             10,000

Stage 2: Devotee pays temple
Dr. Bank - SBI (Asset)                    10,000
   Cr. Sponsorship Receivable (Asset)          10,000

Stage 3: Temple pays florist
Dr. Flower Decoration Expense (Expense)   10,000
   Cr. Bank - SBI (Asset)                      10,000
```

#### Example 6: Direct Vendor Payment by Devotee
```
Devotee pays tent vendor ₹25,000 directly for temple event

Journal Entry (Non-cash transaction):
Dr. Tent Hiring Expense (Expense)         25,000
   Cr. Donation - Direct Payment (Income)      25,000

Note: No actual money flows through temple accounts,
but both expense and income are recorded.
```

#### Example 7: Priest Salary Payment
```
Monthly salary of ₹30,000 paid to head priest

Journal Entry:
Dr. Salary Expense - Priest (Expense)     30,000
   Cr. Bank - SBI (Asset)                      30,000
```

#### Example 8: Electricity Bill Payment
```
Monthly electricity bill of ₹15,000 paid

Journal Entry:
Dr. Electricity Charges (Expense)         15,000
   Cr. Bank - SBI (Asset)                      15,000
```

### Key Accounting Reports

#### 1. Trial Balance
Lists all accounts with their debit and credit balances. Must balance (Total Debits = Total Credits).

```
TRIAL BALANCE
As on 31-March-2025
═══════════════════════════════════════════════
Account Name                    Debit      Credit
───────────────────────────────────────────────
Cash in Hand                   50,000
Bank - SBI Current            5,00,000
Inventory - Annadana          1,00,000
Gold Ornaments              25,00,000
Temple Building           1,00,00,000
Vendor Payables                          25,000
Corpus Fund                           50,00,000
Donation Income                       45,00,000
Seva Income                           15,00,000
Sponsorship Income                     5,00,000
Salary Expense               10,00,000
Electricity Expense           1,50,000
Annadana Expense             5,00,000
───────────────────────────────────────────────
TOTAL                     1,48,00,000 1,48,00,000
═══════════════════════════════════════════════
```

#### 2. Income & Expenditure Statement
(Similar to Profit & Loss, but for non-profit organizations)

```
INCOME & EXPENDITURE STATEMENT
For the Year Ended 31-March-2025
═══════════════════════════════════════════════

INCOME:
  Donation Income              45,00,000
  Seva Income                  15,00,000
  Sponsorship Income            5,00,000
  In-Kind Donation Income       2,00,000
  Interest Income                 50,000
                              ───────────
  Total Income                           67,50,000

EXPENDITURE:
  Salary & Wages               10,00,000
  Annadana Expenses             5,00,000
  Pooja Materials               2,00,000
  Electricity & Water           2,00,000
  Festival Expenses             3,00,000
  Maintenance & Repairs         1,50,000
  Administrative Expenses       1,00,000
                              ───────────
  Total Expenditure                     24,50,000
                                        ───────────
SURPLUS (Income - Expenditure)          43,00,000
═══════════════════════════════════════════════
```

#### 3. Balance Sheet
Shows financial position (Assets = Liabilities + Surplus)

```
BALANCE SHEET
As on 31-March-2025
═══════════════════════════════════════════════

ASSETS:
Current Assets:
  Cash in Hand                    50,000
  Bank Balances                5,00,000
  Inventories                  1,00,000
                              ──────────
                                         6,50,000
Fixed Assets:
  Temple Building          1,00,00,000
  Furniture & Fixtures         10,00,000
  Less: Depreciation          (5,00,000)
                              ──────────
                                      1,05,00,000
Precious Assets:
  Gold & Silver               25,00,000
                              ──────────
TOTAL ASSETS                          1,36,50,000
                                      ═══════════

LIABILITIES:
Current Liabilities:
  Vendor Payables                 25,000
                              ──────────
                                            25,000

CORPUS & FUNDS:
  Corpus Fund                 50,00,000
  General Fund                43,00,000
  Opening Balance             43,25,000
  Add: Current Year Surplus   43,00,000
                              ──────────
                                      1,36,25,000
                                      ──────────
TOTAL LIABILITIES & FUNDS             1,36,50,000
                                      ═══════════
```

#### 4. Cash Flow Statement
Shows actual cash movements (important for day-to-day management)

```
CASH FLOW STATEMENT
For the Year Ended 31-March-2025
═══════════════════════════════════════════════

OPERATING ACTIVITIES:
  Donations Received (Cash)    45,00,000
  Seva Payments Received       15,00,000
  Sponsorships Received         5,00,000
  Salaries Paid              (10,00,000)
  Operating Expenses Paid     (8,50,000)
                              ──────────
  Net Cash from Operations              46,50,000

INVESTING ACTIVITIES:
  Fixed Deposit Made          (20,00,000)
  Interest Received               50,000
                              ──────────
  Net Cash from Investing              (19,50,000)

FINANCING ACTIVITIES:
  Corpus Fund Contribution     10,00,000
                              ──────────
  Net Cash from Financing               10,00,000
                                       ──────────
NET INCREASE IN CASH                    37,00,000
Opening Cash Balance                    13,50,000
                                       ──────────
CLOSING CASH BALANCE                    50,50,000
═══════════════════════════════════════════════
```

#### 5. Donation Summary Report (for 80G)
Essential for issuing 80G certificates and tax compliance

```
DONATION SUMMARY REPORT
For the Year 2024-25
═══════════════════════════════════════════════

Month        Cash     Online    In-Kind    Total
───────────────────────────────────────────────
April      2,50,000  1,00,000    50,000  4,00,000
May        3,00,000  1,50,000    75,000  5,25,000
June       2,75,000  1,25,000    25,000  4,25,000
...
March      4,50,000  2,00,000  1,00,000  7,50,000
───────────────────────────────────────────────
TOTAL     45,00,000 15,00,000  2,00,000 62,00,000
═══════════════════════════════════════════════

Top Donors (for acknowledgment):
1. Sri Ramesh Kumar      - ₹5,00,000
2. Smt. Lakshmi Devi     - ₹3,00,000
3. ABC Corporation       - ₹2,50,000
...

Purpose-wise Breakdown:
General Donations        : 35,00,000
Festival Contributions   : 15,00,000
Annadana Donations      : 10,00,000
Building Fund           :  2,00,000
```

#### 6. Inventory Report
For consumable items tracking

```
ANNADANA INVENTORY REPORT
As on 23-November-2025
═══════════════════════════════════════════════

Item         Opening   Received   Consumed  Closing  Value
             Stock     (Donated)            Stock    (₹)
──────────────────────────────────────────────────────────
Rice (kg)      500      250        600       150   15,000
Wheat (kg)     200      100        200       100    5,000
Toor Dal (kg)  100       50        120        30    4,500
Oil (L)        100       25         80        45    6,750
Sugar (kg)     150       50        150        50    2,500
──────────────────────────────────────────────────────────
TOTAL INVENTORY VALUE:                            33,750
══════════════════════════════════════════════════════════

Items Below Reorder Level:
⚠️  Toor Dal: 30 kg (Reorder level: 50 kg)
⚠️  Oil: 45 L (Reorder level: 60 L)
```

---

## Receipt Generation & Acknowledgment

### Importance of Receipts

1. **Legal Requirement:** Mandatory for donations above certain amounts
2. **Tax Exemption:** Required for donors to claim 80G deduction
3. **Transparency:** Builds trust with devotees
4. **Audit Trail:** Essential for accounting and audits
5. **Record Keeping:** Helps both temple and devotee maintain records

### Receipt Components

Every receipt must include:

#### Essential Information
- Temple Name, Logo, Address
- Receipt Number (unique, sequential)
- Date of Receipt
- Devotee Name and Contact
- Amount (in numbers and words)
- Payment Method
- Purpose of Donation
- 80G Certificate Number (if applicable)
- PAN Number of Temple/Trust
- Authorized Signature (digital or scanned)

#### Optional Information
- Gotra, Nakshatra (for sevas)
- Event/Festival name
- Specific deity
- Blessing message
- QR code for verification

### Receipt Formats

#### 1. General Donation Receipt
```
════════════════════════════════════════════════════════════
                    [TEMPLE LOGO]
              SRI VARADHANJANEVA SWAMY TEMPLE
                123, Temple Street, Bangalore - 560001
              Phone: 080-12345678 | Email: info@temple.com
════════════════════════════════════════════════════════════

                  DONATION RECEIPT

Receipt No: DON/2024-25/001                Date: 23-Nov-2025
────────────────────────────────────────────────────────────

Received with thanks from:

Name    : Sri Ram Kumar
Address : 456, MG Road, Bangalore - 560002
Phone   : 9876543210
Email   : ram.kumar@email.com
PAN     : ABCDE1234F (Optional)

────────────────────────────────────────────────────────────

Amount Received  : ₹ 10,000 (Rupees Ten Thousand Only)
Payment Mode     : UPI
Transaction Ref  : 123456789012
Purpose          : General Donation

────────────────────────────────────────────────────────────

80G Certificate Details:
This donation is eligible for tax deduction under Section
80G of the Income Tax Act, 1961.

Temple Registration No : ABC/12345/2020
PAN of Temple/Trust    : AAACT1234E
80G Registration No    : AAACT1234EF20201
Valid from 01-Apr-2020 to Perpetuity

────────────────────────────────────────────────────────────

Your generous contribution supports our temple activities
and serves the community. May the divine blessings of
Lord Varadhanjaneva Swamy be with you and your family.

                                        [Digital Signature]
                                        Temple Administrator

────────────────────────────────────────────────────────────
This is a computer-generated receipt.
Verify authenticity at www.temple.com/verify/DON-2024-25-001
════════════════════════════════════════════════════════════
```

#### 2. Seva Booking Receipt
```
════════════════════════════════════════════════════════════
                    [TEMPLE LOGO]
              SRI VARADHANJANEVA SWAMY TEMPLE
════════════════════════════════════════════════════════════

               SEVA BOOKING CONFIRMATION

Receipt No: SEVA/2024-25/123              Date: 23-Nov-2025
────────────────────────────────────────────────────────────

Devotee Details:
Name     : Sri Ram Kumar
Phone    : 9876543210
Gotra    : Bharadwaja
Nakshatra: Rohini

Seva Details:
────────────────────────────────────────────────────────────
Seva Name       : Abhisheka Seva
                  ಅಭಿಷೇಕ ಸೇವೆ
Seva Date       : 28-November-2025 (Thursday)
Seva Time       : 6:00 AM - 7:00 AM
Amount Paid     : ₹ 500
Payment Mode    : UPI
────────────────────────────────────────────────────────────

Additional Devotee Names:
1. Smt. Sita Devi (wife)
2. Kumara Ravi Kumar (son)
3. Kumari Priya (daughter)

Special Request: Family wellbeing and prosperity

────────────────────────────────────────────────────────────

Important Instructions:
• Please arrive 15 minutes before the seva time
• Dress code: Traditional attire preferred
• Mobile phones to be kept in silent mode
• Photography during seva is not permitted

────────────────────────────────────────────────────────────

Prasadam will be distributed after the seva.

May Lord's abundant blessings be upon you and your family.

                                        [Digital Signature]
                                        Temple Office

────────────────────────────────────────────────────────────
For queries: 080-12345678 | sevas@temple.com
════════════════════════════════════════════════════════════
```

### Digital Receipt Delivery

1. **Email:** PDF attachment with proper formatting
2. **SMS:** Short confirmation with download link
3. **WhatsApp:** Receipt image or PDF
4. **Mobile App:** In-app receipt view and download
5. **Website:** Login to view and download past receipts

### Receipt Verification System

To prevent fraud and enable verification:

```
Each receipt has unique QR code containing:
- Receipt number
- Date
- Amount
- Verification hash

Devotees/Auditors can scan QR code or visit:
www.temple.com/verify/DON-2024-25-001

System displays:
✓ Valid Receipt
  Amount: ₹10,000
  Date: 23-Nov-2025
  Devotee: Ram Kumar
  Purpose: General Donation
```

---

## Reports & Compliance

### Financial Reports

1. **Daily Reports:**
   - Cash Collection Summary
   - Hundi Collection
   - UPI Payments Received
   - Sevas Booked
   - Daily Expenses

2. **Monthly Reports:**
   - Income & Expenditure Statement
   - Bank Reconciliation
   - Inventory Consumption
   - Sponsorship Status
   - Vendor Payments

3. **Annual Reports:**
   - Complete Financial Statements
   - Balance Sheet
   - Income & Expenditure Account
   - Cash Flow Statement
   - Asset Register
   - 80G Donation Summary

### Compliance Reports

#### 1. 80G Certificate Maintenance
- Annual submission to Income Tax Department
- Donor-wise summary
- Category-wise breakdown
- Foreign donation segregation (if applicable)

#### 2. FCRA Compliance (if applicable)
For temples receiving foreign contributions:
- Quarterly returns
- Annual returns (FC-4)
- Separate bank account maintenance
- Utilization certificates

#### 3. Trust/Society Compliance
- Annual General Body Meeting reports
- Audit reports
- Trust deed compliance
- Regulatory filings

#### 4. GST Compliance (if applicable)
For temples with GST registration:
- GST returns (if services are taxable)
- Input tax credit tracking

### Audit Reports

1. **Internal Audit:**
   - Monthly/Quarterly review
   - Cash verification
   - Inventory physical verification
   - Precious asset verification

2. **Statutory Audit:**
   - Annual audit by Chartered Accountant
   - Audit report for trust compliance
   - Tax audit (if applicable)

### Management Reports

1. **Donation Analysis:**
   - Donor trends
   - Peak donation periods
   - Purpose-wise analysis
   - Growth analysis

2. **Seva Analysis:**
   - Popular sevas
   - Revenue by seva type
   - Booking patterns
   - Capacity utilization

3. **Expense Analysis:**
   - Category-wise expenses
   - Budget vs. actual
   - Cost per activity
   - Vendor-wise expenses

4. **Sponsorship Report:**
   - Active sponsorships
   - Fulfilled vs. pending
   - Sponsor retention
   - Event-wise sponsorship

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Week 1: Temple Settings & Basic Setup**
- Temple registration module (SaaS/Standalone)
- Temple settings page (logo, address, bank details)
- User management (admin, staff roles)
- Basic dashboard

**Week 2: Chart of Accounts & Devotee Management**
- Create chart of accounts structure
- Account master CRUD
- Devotee registration and management
- Basic search and filtering

### Phase 2: Core Transactions (Weeks 3-5)

**Week 3: Donation Management**
- Cash donation entry
- Receipt generation with temple branding
- Daily collection summary
- Basic reporting

**Week 4: UPI Payment Tracking**
- Quick UPI payment entry interface
- Phone number-based devotee lookup
- Purpose selection (donation/seva/sponsorship)
- Automatic accounting posting
- SMS/Email receipt delivery

**Week 5: Seva Booking System**
- Seva master setup (already done)
- Seva booking interface (already done)
- Payment integration with accounting
- Booking reports

### Phase 3: Advanced Features (Weeks 6-8)

**Week 6: In-Kind Donations**
- In-kind donation entry (consumables)
- Inventory tracking
- Consumption recording
- Stock reports

**Week 7: Precious Asset Management**
- Asset donation entry (gold/silver)
- Asset register
- Appraisal tracking
- Physical verification module

**Week 8: Sponsorship Management**
- Sponsorship recording
- Vendor management
- Direct payment tracking
- Sponsorship reports

### Phase 4: Accounting & Reporting (Weeks 9-11)

**Week 9: Journal Entries & Ledgers**
- Manual journal entry
- Auto-posting from transactions
- General ledger view
- Account statements

**Week 10: Financial Statements**
- Trial balance
- Income & Expenditure statement
- Balance sheet
- Cash flow statement

**Week 11: Bank Reconciliation**
- Bank statement upload
- Auto-matching
- Reconciliation interface
- Reconciliation reports

### Phase 5: Reports & Compliance (Week 12)

**Week 12: Advanced Reports & Compliance**
- 80G certificate generation
- Donation summary reports
- Audit reports
- Custom report builder
- Data export (Excel, PDF)

### Phase 6: Polish & Launch (Weeks 13-14)

**Week 13: Testing & Refinement**
- End-to-end testing
- User acceptance testing
- Bug fixes
- Performance optimization

**Week 14: Training & Deployment**
- User documentation
- Video tutorials
- Staff training
- Go-live support

---

## Technical Architecture

### Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (REST API framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Alembic (Database migrations)

**Frontend:**
- React 18
- Material-UI (MUI)
- React Router
- Axios (API client)

**Mobile:**
- Progressive Web App (PWA) for mobile access
- Responsive design for all screen sizes

**Deployment:**
- Docker containers
- Cloud hosting (AWS/Azure/DigitalOcean)
- Automated backups
- SSL certificates

### Security Features

1. **Authentication & Authorization:**
   - JWT-based authentication
   - Role-based access control
   - Session management
   - Password encryption (bcrypt)

2. **Data Security:**
   - Database encryption at rest
   - HTTPS/SSL for all communications
   - API rate limiting
   - Input validation and sanitization

3. **Audit Trail:**
   - All financial transactions logged
   - User action tracking
   - IP address logging
   - Change history

4. **Backup & Recovery:**
   - Daily automated backups
   - Point-in-time recovery
   - Disaster recovery plan
   - Data retention policies

### Scalability

- **Multi-tenant architecture** for SaaS mode
- **Horizontal scaling** for increased load
- **Caching** for performance (Redis)
- **CDN** for static assets
- **Database optimization** and indexing

---

## Conclusion

This comprehensive temple management system addresses the unique needs of Indian temples, from simple cash donations to complex sponsorship scenarios, from consumable inventory to precious asset management, and from basic UPI payment tracking to complete double-entry accounting.

### Key Differentiators

1. **No Hardcoding:** Every temple can brand the system as their own
2. **Practical UPI Tracking:** Works without payment gateway integration
3. **In-Kind Donations:** Proper handling of non-monetary donations
4. **Sponsorships:** Direct vendor payment tracking
5. **Proper Accounting:** Full double-entry bookkeeping
6. **Compliance Ready:** 80G, FCRA, audit support
7. **User-Friendly:** Designed for temple staff, not accountants
8. **Mobile-First:** Quick entry on phones for real-time updates

### Next Steps

1. **Review this proposal** with stakeholders
2. **Discuss specific customization** requirements
3. **Plan phased implementation** based on priority
4. **Schedule demonstration** of current features
5. **Finalize timeline and budget**

---

## Appendix

### Sample Workflows

#### Workflow 1: Cash Donation
```
1. Devotee comes to counter
2. Gives ₹1,000 cash for general donation
3. Staff opens donation entry screen
4. Enters devotee name, phone, amount
5. Selects purpose: "General Donation"
6. System generates receipt number
7. Receipt prints/emails immediately
8. System auto-posts to accounts:
   Dr. Cash in Hand
   Cr. Donation Income
9. Daily total updated on dashboard
```

#### Workflow 2: UPI Payment for Seva
```
1. Devotee scans temple QR code on website
2. Pays ₹500 via GPay
3. Temple admin receives SMS: "Rs 500 from 9876..."
4. Admin opens app on phone
5. Clicks "Log UPI Payment"
6. Enters amount: 500
7. Enters phone: 9876543210
8. System finds: Ram Kumar
9. Selects: Seva → Abhisheka → Tomorrow
10. Clicks Save
11. System creates booking, posts to accounts, sends receipt
12. Ram Kumar receives SMS/Email with seva details
13. Total time: < 30 seconds
```

#### Workflow 3: In-Kind Donation
```
1. Devotee brings 25kg rice
2. Staff weighs rice
3. Opens in-kind donation screen
4. Selects devotee
5. Item: Rice, Quantity: 25kg
6. System shows market rate: ₹100/kg
7. Auto-calculates value: ₹2,500
8. Generates receipt
9. Adds to inventory
10. Posts to accounts:
    Dr. Inventory
    Cr. In-Kind Donation Income
11. Stock level updated
```

#### Workflow 4: Direct Vendor Payment Sponsorship
```
1. Devotee approaches temple
2. Wants to sponsor tent for festival
3. Temple provides approved vendor list
4. Devotee contacts ABC Tent House
5. Arranges service directly
6. Pays vendor ₹25,000 cash/online
7. Receives invoice from vendor
8. Submits invoice copy to temple
9. Temple staff verifies invoice
10. Creates sponsorship record
11. Links vendor invoice
12. Posts to accounts (non-cash):
    Dr. Tent Expense
    Cr. Donation - Direct Payment
13. Generates acknowledgment receipt
14. Sends to devotee for tax purposes
```

---

## Contact Information

For further discussions, clarifications, or demonstrations, please contact:

**MandirMitra Development Team**
Email: info@MandirMitra.com
Phone: +91-XXXXXXXXXX

---

**Document End**

*This proposal is subject to modifications based on specific temple requirements and regulatory compliance needs.*
