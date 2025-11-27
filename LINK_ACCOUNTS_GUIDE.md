# Guide: Linking Accounts to Donation Categories and Sevas

## Problem

You've created accounts in Chart of Accounts (like 4101, 4111, 4201, etc.), but they're not being used because:
1. **Donation categories** and **sevas** need to be linked to these accounts
2. The `account_id` field in categories/sevas must be set to point to the correct account

## Solution

### Option 1: Use the Automated Script (Recommended)

Run the script to automatically link accounts based on account codes:

```bash
cd backend
python -m scripts.link_accounts_to_categories_sevas
```

This script will:
- Find accounts by account code (4101, 4111, 4201, etc.)
- Match them to donation categories/sevas based on name
- Link them automatically
- Show you what was linked and what couldn't be linked

**Before running**, edit the script to add your specific mappings:

**File:** `backend/scripts/link_accounts_to_categories_sevas.py`

```python
# Add your category mappings here
CATEGORY_ACCOUNT_MAPPING = {
    "General Donation": "4101",
    "Building Fund": "4111",
    "Annadana Fund": "4112",
    "Festival Sponsorship": "4113",
    "Corpus Fund Donation": "4114",
    "Education Fund": "4115",
    # Add your actual category names here
}

# Add your seva mappings here
SEVA_ACCOUNT_MAPPING = {
    "abhisheka": "4201",
    "archana": "4202",
    "pooja": "4203",
    "alankara": "4204",
    "vahana_seva": "4205",
    # Add specific seva names if needed
    "Satyanarayana Pooja": "4206",
    "Navagraha Pooja": "4207",
}
```

### Option 2: Link Manually via API

#### Link Donation Category to Account

1. **Find the category ID:**
   ```bash
   GET /api/v1/donations/categories/
   ```

2. **Find the account ID:**
   ```bash
   GET /api/v1/accounts/
   # Look for account_code: "4101", "4111", etc.
   ```

3. **Update the category:**
   ```bash
   PUT /api/v1/donations/categories/{category_id}
   {
     "account_id": 123  # The account ID from step 2
   }
   ```

#### Link Seva to Account

1. **Find the seva ID:**
   ```bash
   GET /api/v1/sevas/
   ```

2. **Find the account ID:**
   ```bash
   GET /api/v1/accounts/
   # Look for account_code: "4201", "4202", etc.
   ```

3. **Update the seva:**
   ```bash
   PUT /api/v1/sevas/{seva_id}
   {
     "account_id": 123  # The account ID from step 2
   }
   ```

### Option 3: Link via Database (Direct SQL)

If you prefer SQL:

```sql
-- Link donation category to account
UPDATE donation_categories 
SET account_id = (SELECT id FROM accounts WHERE account_code = '4101' LIMIT 1)
WHERE name = 'General Donation';

-- Link seva to account
UPDATE sevas 
SET account_id = (SELECT id FROM accounts WHERE account_code = '4201' LIMIT 1)
WHERE name_english = 'Abhisheka Seva';
```

## Verify Links

After linking, verify:

1. **Check categories:**
   ```bash
   GET /api/v1/donations/categories/
   # Each category should have account_id set
   ```

2. **Check sevas:**
   ```bash
   GET /api/v1/sevas/
   # Each seva should have account_id set
   ```

3. **Test with a new donation/seva:**
   - Create a new donation or seva booking
   - Check the journal entry - it should use the linked account
   - Verify in Trial Balance that the correct account shows the income

## Account Code Reference

### Donation Income Accounts (4100 series)
- `4101` - Donation - General
- `4111` - Donation - Building Fund
- `4112` - Donation - Annadana Fund
- `4113` - Donation - Festival Fund
- `4114` - Donation - Corpus Fund
- `4115` - Donation - Education Fund

### Seva Income Accounts (4200 series)
- `4201` - Abhisheka Seva Income
- `4202` - Archana Income
- `4203` - Special Pooja Income
- `4204` - Alankara Seva Income
- `4205` - Vahana Seva Income
- `4206` - Satyanarayana Pooja Income
- `4207` - Navagraha Pooja Income

## Troubleshooting

### Issue: Accounts still not showing in reports

**Check:**
1. Are categories/sevas linked? (account_id is not NULL)
2. Are the accounts created in Chart of Accounts?
3. Are journal entries being created? (Check journal_entries table)
4. Are journal entries POSTED? (status = 'posted')

**Debug:**
```bash
# Check if category is linked
SELECT id, name, account_id FROM donation_categories;

# Check if seva is linked
SELECT id, name_english, account_id FROM sevas;

# Check if accounts exist
SELECT id, account_code, account_name FROM accounts WHERE account_code LIKE '41%' OR account_code LIKE '42%';

# Check journal entries
SELECT je.id, je.entry_number, jl.account_id, a.account_code, a.account_name
FROM journal_entries je
JOIN journal_lines jl ON je.id = jl.journal_entry_id
JOIN accounts a ON jl.account_id = a.id
WHERE je.reference_type = 'donation' OR je.reference_type = 'seva'
ORDER BY je.id DESC
LIMIT 10;
```

### Issue: Script can't find accounts

**Solution:**
1. Verify account codes match exactly (case-sensitive)
2. Check temple_id matches (for multi-tenant)
3. Manually link via API or SQL

### Issue: Wrong accounts being used

**Solution:**
1. Check the link: `SELECT * FROM donation_categories WHERE account_id = X`
2. Update the link to point to correct account
3. Re-run backfill script if needed

## Next Steps

After linking:
1. ✅ Run the linking script
2. ✅ Verify links are correct
3. ✅ Test with a new donation/seva
4. ✅ Check Trial Balance shows correct accounts
5. ✅ Run backfill script if needed for existing transactions:
   ```bash
   python -m scripts.backfill_donation_journal_entries
   python -m scripts.backfill_seva_journal_entries
   ```

---

**Last Updated:** November 2025







