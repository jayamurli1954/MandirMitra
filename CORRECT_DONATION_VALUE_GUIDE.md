# Guide to Correct Donation Assessed Value

## Problem
You created an in-kind donation receipt for 200 kg of Rice with assessed value of ₹1,300 instead of ₹13,000.

## Solution
You can correct the assessed value using the API endpoint or by adding an edit feature in the frontend.

## Method 1: Using Browser Console (Quick Fix)

1. **Find the Donation ID:**
   - Go to Donations page
   - Find the receipt for 200 kg Rice
   - Note the donation ID (or receipt number)

2. **Open Browser Console (F12)**

3. **Get your auth token:**
   ```javascript
   localStorage.getItem('token')
   ```

4. **Update the donation:**
   ```javascript
   const donationId = 48; // Replace with your actual donation ID
   const token = localStorage.getItem('token');
   
   fetch(`http://localhost:8000/api/v1/donations/${donationId}`, {
     method: 'PATCH',
     headers: {
       'Authorization': `Bearer ${token}`,
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       amount: 13000,  // Correct assessed value
       value_assessed: 13000,
       notes: 'Corrected assessed value from 1300 to 13000'
     })
   })
   .then(r => r.json())
   .then(data => {
     console.log('Updated:', data);
     alert('Donation updated successfully!');
   })
   .catch(err => {
     console.error('Error:', err);
     alert('Error: ' + err.message);
   });
   ```

## Method 2: Using Postman or curl

**Using curl:**
```bash
curl -X PATCH http://localhost:8000/api/v1/donations/48 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 13000,
    "value_assessed": 13000,
    "notes": "Corrected assessed value from 1300 to 13000"
  }'
```

**Using Postman:**
- Method: PATCH
- URL: `http://localhost:8000/api/v1/donations/{donation_id}`
- Headers:
  - `Authorization: Bearer YOUR_TOKEN`
  - `Content-Type: application/json`
- Body (JSON):
  ```json
  {
    "amount": 13000,
    "value_assessed": 13000,
    "notes": "Corrected assessed value from 1300 to 13000"
  }
  ```

## What Gets Updated Automatically

When you correct the assessed value, the system automatically updates:

1. **Donation Record:**
   - `amount` field
   - `value_assessed` field

2. **Inventory Stock Movement:**
   - Unit price (recalculated)
   - Total value

3. **Stock Balance:**
   - Value adjusted by the difference

4. **Journal Entry (Accounting):**
   - Journal line amounts updated
   - Notes added about the correction

## Where to View Inventory

After correcting the value, you can view the inventory in:

### 1. **Item Master** (`/inventory/item-master`)
   - Shows all inventory items
   - Your Rice item should be listed here
   - Shows item details, category, unit, etc.

### 2. **Stock Report** (`/inventory/stock-report`)
   - Shows current stock levels
   - Displays quantity and value for each item
   - Your 200 kg of Rice should show with corrected value

### 3. **Purchase Entry** (`/inventory/purchase-entry`)
   - Shows purchase/stock movement history
   - The donation receipt should appear as a stock movement
   - Value should now show ₹13,000

### 4. **Stock Balance Report**
   - Shows current balances by store
   - Rice should show: 200 kg, Value: ₹13,000

## Navigation Path

1. Go to **Inventory** in the left sidebar
2. Click on **Item Master** to see all items
3. Click on **Stock Report** to see stock levels and values
4. Click on **Purchase Entry** to see stock movements (including donations)

## Verification

After updating:
1. Check the donation receipt - amount should show ₹13,000
2. Check Item Master - Rice item should exist
3. Check Stock Report - Rice should show 200 kg with value ₹13,000
4. Check Stock Balance - Value should be corrected

## Notes

- The correction updates all related records automatically
- Accounting entries are also corrected
- Stock movements are updated with new unit price
- All changes are logged in the audit trail







