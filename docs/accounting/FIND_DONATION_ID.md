# How to Find Donation ID

## Method 1: Using Browser Console (Easiest)

1. **Go to Donations page** (`http://localhost:3000/donations`)
2. **Open Browser Console** (Press F12, then click Console tab)
3. **Run this script** to find your Rice donation:

```javascript
// Get all donations and find the Rice one
fetch('http://localhost:8000/api/v1/donations/', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(r => r.json())
.then(donations => {
  // Find Rice donation
  const riceDonation = donations.find(d => 
    d.item_name && d.item_name.toLowerCase().includes('rice') &&
    (d.amount === 1300 || d.value_assessed === 1300)
  );
  
  if (riceDonation) {
    console.log('✅ Found Rice Donation:');
    console.log('ID:', riceDonation.id);
    console.log('Receipt Number:', riceDonation.receipt_number);
    console.log('Item Name:', riceDonation.item_name);
    console.log('Quantity:', riceDonation.quantity, riceDonation.unit);
    console.log('Current Amount:', riceDonation.amount);
    console.log('');
    console.log('To correct the value, run:');
    console.log(`
fetch('http://localhost:8000/api/v1/donations/${riceDonation.id}', {
  method: 'PATCH',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    amount: 13000,
    value_assessed: 13000,
    notes: 'Corrected assessed value from 1300 to 13000'
  })
})
.then(r => r.json())
.then(data => {
  console.log('✅ Updated!', data);
  alert('Donation updated successfully!');
})
.catch(err => alert('Error: ' + err.message));
    `);
  } else {
    console.log('❌ Rice donation not found. Showing all in-kind donations:');
    donations
      .filter(d => d.donation_type === 'in_kind')
      .forEach(d => {
        console.log(`ID: ${d.id}, Receipt: ${d.receipt_number}, Item: ${d.item_name}, Amount: ${d.amount}`);
      });
  }
})
.catch(err => console.error('Error:', err));
```

## Method 2: Find by Receipt Number

If you know the receipt number (e.g., `TMP001-2025-00048`):

```javascript
const receiptNumber = 'TMP001-2025-00048'; // Replace with your receipt number

fetch('http://localhost:8000/api/v1/donations/', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(r => r.json())
.then(donations => {
  const donation = donations.find(d => d.receipt_number === receiptNumber);
  if (donation) {
    console.log('Found! ID:', donation.id);
    console.log('Receipt:', donation.receipt_number);
    console.log('Amount:', donation.amount);
  } else {
    console.log('Not found. Available receipts:');
    donations.forEach(d => console.log(d.receipt_number));
  }
});
```

## Method 3: Check Network Tab

1. Go to Donations page
2. Open Developer Tools (F12)
3. Go to **Network** tab
4. Refresh the page or click "Donation List" tab
5. Look for request to `/api/v1/donations/`
6. Click on it → Go to **Response** tab
7. Find your Rice donation in the JSON
8. Note the `id` field

## Method 4: All-in-One Correction Script

This script finds AND corrects in one go:

```javascript
// Find and correct Rice donation
fetch('http://localhost:8000/api/v1/donations/', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(r => r.json())
.then(donations => {
  // Find Rice donation with wrong amount
  const riceDonation = donations.find(d => 
    d.item_name && d.item_name.toLowerCase().includes('rice') &&
    d.quantity === 200 &&
    (d.amount === 1300 || d.value_assessed === 1300)
  );
  
  if (!riceDonation) {
    console.log('❌ Rice donation (200 kg, ₹1300) not found.');
    console.log('Available in-kind donations:');
    donations
      .filter(d => d.donation_type === 'in_kind')
      .forEach(d => {
        console.log(`ID: ${d.id}, Receipt: ${d.receipt_number}, Item: ${d.item_name}, Qty: ${d.quantity}, Amount: ${d.amount}`);
      });
    return;
  }
  
  console.log('✅ Found Rice Donation:');
  console.log('ID:', riceDonation.id);
  console.log('Receipt:', riceDonation.receipt_number);
  console.log('Current Amount: ₹', riceDonation.amount);
  console.log('');
  console.log('Correcting to ₹13,000...');
  
  // Correct the value
  return fetch(`http://localhost:8000/api/v1/donations/${riceDonation.id}`, {
    method: 'PATCH',
    headers: {
      'Authorization': 'Bearer ' + localStorage.getItem('token'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      amount: 13000,
      value_assessed: 13000,
      notes: 'Corrected assessed value from 1300 to 13000'
    })
  });
})
.then(r => r ? r.json() : null)
.then(data => {
  if (data) {
    console.log('✅ Successfully updated!', data);
    alert('✅ Donation corrected! Amount updated from ₹1,300 to ₹13,000.\n\nCheck Inventory → Stock Report to verify.');
  }
})
.catch(err => {
  console.error('Error:', err);
  alert('Error: ' + err.message);
});
```

## Quick Steps

1. **Open Donations page** in your browser
2. **Press F12** to open Developer Tools
3. **Click Console tab**
4. **Copy and paste the "All-in-One Correction Script" above**
5. **Press Enter**
6. The script will:
   - Find your Rice donation (200 kg, ₹1,300)
   - Show you the ID
   - Automatically correct it to ₹13,000
   - Show a success message

That's it! The donation will be corrected and inventory will be updated automatically.







