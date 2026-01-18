# Panchang Service Setup Guide

## Issue: Network Error / Module Not Found

If you're seeing "Network Error" when loading Panchang, it's likely because `pyswisseph` is not installed or not working.

## Solution for Windows

### Option 1: Install Visual C++ Build Tools (Recommended)

1. Download and install **Microsoft C++ Build Tools**:
   - Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Download "Build Tools for Visual Studio"
   - During installation, select "C++ build tools" workload
   - This will install the required compiler

2. After installation, restart your terminal and run:
   ```powershell
   pip install pyswisseph==2.10.3.2
   ```

### Option 2: Use Pre-built Wheel (If Available)

Try installing from a pre-built wheel:
```powershell
pip install --only-binary :all: pyswisseph
```

### Option 3: Use Alternative Package

If pyswisseph continues to fail, you can temporarily use a mock implementation for development.

## Verify Installation

After installing, verify it works:
```powershell
python -c "import swisseph as swe; print('Swiss Ephemeris version:', swe.version)"
```

## Backend Error Logs

To see detailed error logs:

1. **Check if backend is running:**
   ```powershell
   # In backend directory
   python -m uvicorn app.main:app --reload
   ```

2. **Check console output** for errors like:
   - `ModuleNotFoundError: No module named 'swisseph'`
   - `ImportError: DLL load failed`
   - Any traceback errors

3. **Check browser console** (F12) for network errors:
   - 500 Internal Server Error
   - Connection refused
   - CORS errors

## Common Issues

### Issue 1: Module Not Found
**Error:** `ModuleNotFoundError: No module named 'swisseph'`
**Solution:** Install pyswisseph (see above)

### Issue 2: DLL Load Failed
**Error:** `ImportError: DLL load failed while importing swisseph`
**Solution:** 
- Reinstall pyswisseph
- Check if you have the correct Python version (3.8-3.11)
- Try installing Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

### Issue 3: Backend Not Running
**Error:** Network Error / Connection Refused
**Solution:**
1. Make sure backend is running on port 8000
2. Check if port 8000 is available: `netstat -ano | findstr :8000`
3. Start backend: `python -m uvicorn app.main:app --reload`

### Issue 4: Authentication Error
**Error:** 401 Unauthorized
**Solution:** Make sure you're logged in and have a valid token in localStorage

## Testing the API Directly

Test the API endpoint directly:
```powershell
# Get your auth token from browser localStorage
$token = "your-token-here"

# Test the endpoint
curl -H "Authorization: Bearer $token" http://localhost:8000/api/v1/panchang/today
```

Or use Python:
```python
import requests

token = "your-token-here"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/panchang/today", headers=headers)
print(response.json())
```

## Next Steps

Once pyswisseph is installed:
1. Restart the backend server
2. Refresh the frontend page
3. Check browser console for any remaining errors
4. Check backend logs for detailed error messages












