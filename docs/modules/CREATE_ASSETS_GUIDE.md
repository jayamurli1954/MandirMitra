# Guide to Create Assets for Existing Donations

## Problem
The Asset Register is showing empty because assets weren't created for existing in-kind donations (Gold, Silver, Diamond Necklace).

## Solution
Use the utility endpoint to create assets for existing donations.

## Steps

### Option 1: Using Browser Console (Easiest)

1. Open your browser and go to `http://localhost:3000`
2. Open Developer Tools (F12)
3. Go to the Console tab
4. Get your auth token (check Network tab for any API call, copy the Authorization header)
5. Run this command:

```javascript
fetch('http://localhost:8000/api/v1/donations/create-missing-assets/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN_HERE',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log('Result:', data);
  alert(`Created ${data.created_count} assets!`);
})
.catch(error => {
  console.error('Error:', error);
});
```

### Option 2: Using Postman or curl

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/v1/donations/create-missing-assets/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Using Postman:**
- Method: POST
- URL: `http://localhost:8000/api/v1/donations/create-missing-assets/`
- Headers:
  - `Authorization: Bearer YOUR_TOKEN_HERE`
  - `Content-Type: application/json`

### Option 3: Create a Simple HTML Page

Create a file `create_assets.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Create Assets</title>
</head>
<body>
    <h1>Create Assets for Donations</h1>
    <button onclick="createAssets()">Create Assets</button>
    <div id="result"></div>
    
    <script>
        async function createAssets() {
            // Get token from localStorage (adjust based on your app's token storage)
            const token = localStorage.getItem('token') || prompt('Enter your auth token:');
            
            try {
                const response = await fetch('http://localhost:8000/api/v1/donations/create-missing-assets/', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                document.getElementById('result').innerHTML = `
                    <h2>Result:</h2>
                    <p>Created: ${data.created_count} assets</p>
                    ${data.errors ? `<p>Errors: ${JSON.stringify(data.errors)}</p>` : ''}
                `;
            } catch (error) {
                document.getElementById('result').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
```

## What the Endpoint Does

1. Finds all in-kind donations that:
   - Don't have an asset linked (`asset_id` is null)
   - Are marked as ASSET subtype, OR
   - Are precious items (gold, silver, jewellery, ornaments) based on item name or purity

2. For each donation:
   - Creates or finds an appropriate asset category
   - Creates an asset entry with proper details
   - Links the donation to the asset

3. Returns:
   - Number of assets created
   - Any errors encountered

## After Running

1. Refresh the Asset Register page
2. Check backend logs for `[CREATE MISSING ASSETS]` messages
3. Assets should now appear in the register
4. Try clearing the "Precious" filter to see all assets

## Backend Logs

Check your backend console for messages like:
```
[CREATE MISSING ASSETS] Found X donations needing assets
[CREATE MISSING ASSETS] Created asset AST-2025-00001 for donation TMP001-2025-00047
[CREATE MISSING ASSETS] ✓ Asset created successfully
```







