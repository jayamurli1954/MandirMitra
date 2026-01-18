# Chart of Accounts - Block-Based Structure

## Overview

The chart of accounts uses a **block-based code reservation system** for scalability and better analytics. Each income/expense type has a reserved code range for future expansion.

## Income Code Blocks (4000-4999)

### 4100-4199: DONATION INCOME BLOCK
**Parent:** 4100 - Donation Income

**Current Categories:**
- **4101** - General Donation
- **4102** - Cash Donation
- **4103** - Online/UPI Donation
- **4104** - Hundi Collection
- **4110** - Annadana Fund Donation
- **4111** - Building/Construction Fund
- **4112** - Festival Fund Donation
- **4113** - Education Fund Donation
- **4114** - Corpus Fund Donation
- **4115** - Medical Aid Fund Donation
- **4116-4199** - *Reserved for future donation categories*

**Usage:**
- Query all donations: `WHERE account_code BETWEEN '4100' AND '4199'`
- Add new category: Pick next available code (4116, 4117, etc.)

---

### 4200-4299: SEVA INCOME BLOCK
**Parent:** 4200 - Seva Income

**Current Categories:**
- **4201** - Abhisheka Seva
- **4202** - Archana
- **4203** - Kumkumarchana
- **4204** - Alankara Seva
- **4205** - Vahana Seva
- **4206** - Satyanarayana Pooja
- **4207** - Navagraha Pooja
- **4208** - Special Pooja
- **4209** - Kalyanam/Marriage Ceremony
- **4210** - Upanayana/Thread Ceremony
- **4211** - Annaprasana
- **4212** - Namakarana
- **4213** - Ayushya Homam
- **4214** - Mrityunjaya Homam
- **4215** - Ganapathi Homam
- **4216-4299** - *Reserved for future seva types*

**Usage:**
- Query all sevas: `WHERE account_code BETWEEN '4200' AND '4299'`
- Add new seva type: Pick next available code (4216, 4217, etc.)

---

### 4300-4399: SPONSORSHIP INCOME BLOCK
**Parent:** 4300 - Sponsorship Income

**Current Categories:**
- **4301** - Festival Sponsorship
- **4302** - Annadana Sponsorship
- **4303-4399** - *Reserved*

---

### 4500-4599: OTHER INCOME BLOCK
**Parent:** 4500 - Other Income

**Current Categories:**
- **4501** - Interest Income
- **4502-4599** - *Reserved*

---

## Category-Account Linking

### Database Schema

**donation_categories table:**
```sql
account_id INTEGER REFERENCES accounts(id)
```

**sevas table:**
```sql
account_id INTEGER REFERENCES accounts(id)
```

### Automatic Linking

Categories are automatically linked to accounts using the `link_categories_to_accounts.py` script:

```bash
python link_categories_to_accounts.py
```

This script:
1. Matches donation categories to accounts (e.g., "Building Fund" → 4111)
2. Matches seva types to accounts (e.g., "Abhisheka" → 4201)
3. Sets fallback defaults for unmatched categories

---

## Journal Entry Flow

### Donations
```
When donation is created:
  1. Find donation.category.account_id
  2. If linked → Use category's account
  3. Else → Fallback to payment-mode account (4102-4104)

Journal Entry:
  Dr: Cash/Bank (1101/1110)
  Cr: Category-specific account (41xx)
```

### Sevas
```
When seva booking is created:
  1. Find seva.account_id
  2. If linked → Use seva's account
  3. Else → Fallback to Special Pooja (4208)

Journal Entry:
  Dr: Cash/Bank (1101/1110)
  Cr: Seva-specific account (42xx)
```

---

## Analytics & Reporting

### Total Donation Income
```sql
SELECT SUM(credit_amount)
FROM journal_lines jl
JOIN accounts a ON jl.account_id = a.id
WHERE a.account_code BETWEEN '4100' AND '4199'
```

### Donation by Category
```sql
SELECT a.account_code, a.account_name, SUM(jl.credit_amount) AS total
FROM journal_lines jl
JOIN accounts a ON jl.account_id = a.id
WHERE a.account_code LIKE '41__'
GROUP BY a.account_code, a.account_name
ORDER BY total DESC
```

### Total Seva Income
```sql
SELECT SUM(credit_amount)
FROM journal_lines jl
JOIN accounts a ON jl.account_id = a.id
WHERE a.account_code BETWEEN '4200' AND '4299'
```

### Top 10 Sevas by Revenue
```sql
SELECT a.account_name, SUM(jl.credit_amount) AS total
FROM journal_lines jl
JOIN accounts a ON jl.account_id = a.id
WHERE a.account_code LIKE '42__'
GROUP BY a.account_name
ORDER BY total DESC
LIMIT 10
```

---

## Adding New Categories

### New Donation Category
```python
# 1. Create donation category in UI/API
POST /api/v1/donation-categories/
{
  "name": "Cow Protection Fund",
  "description": "Donations for Goshala"
}

# 2. Create new account (code 4116)
INSERT INTO accounts (account_code, account_name, account_type, parent_account_id)
VALUES ('4116', 'Cow Protection Fund', 'INCOME', <parent_id_of_4100>)

# 3. Link category to account
UPDATE donation_categories
SET account_id = <new_account_id>
WHERE name = 'Cow Protection Fund'
```

### New Seva Type
```python
# 1. Create seva in UI/API
POST /api/v1/sevas/
{
  "name_english": "Rudrabhisheka",
  "category": "abhisheka",
  "amount": 500
}

# 2. Create new account (code 4216)
INSERT INTO accounts (account_code, account_name, account_type, parent_account_id)
VALUES ('4216', 'Rudrabhisheka', 'INCOME', <parent_id_of_4200>)

# 3. Link seva to account
UPDATE sevas
SET account_id = <new_account_id>
WHERE name_english = 'Rudrabhisheka'
```

---

## Migration Scripts

### Initial Setup
```bash
# 1. Add account_id columns
python migrations/002_add_account_linking.py

# 2. Seed chart of accounts with block structure
python seed_chart_of_accounts.py

# 3. Link existing categories to accounts
python link_categories_to_accounts.py

# 4. Sync historical donations to accounting
python sync_donations_to_accounting.py

# 5. Sync historical sevas to accounting
python sync_sevas_to_accounting.py
```

### Future Maintenance
```bash
# Re-link categories if you add new accounts
python link_categories_to_accounts.py
```

---

## Benefits

✅ **Scalability:** Reserved code ranges allow adding 99 donations + 99 sevas
✅ **Analytics:** Easy SQL queries by code range
✅ **Clarity:** Grouped accounts in chart of accounts
✅ **Flexibility:** Fallback logic ensures nothing breaks
✅ **Reports:** Category-wise income analysis
✅ **Admin Dashboard:** Future charting by code blocks
