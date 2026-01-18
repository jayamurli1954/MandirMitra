# Troubleshooting Guide

## Quick Fixes

### 1. Frontend Syntax Error (FIXED)
- **Issue**: Duplicate `let response;` declaration in `Reports.js`
- **Status**: ✅ Fixed
- **Action**: Restart frontend dev server if it's running

### 2. Backend Not Running
- **Check**: Is backend running on `http://localhost:8000`?
- **Start**: 
  ```bash
  cd backend
  .\venv\Scripts\activate
  uvicorn app.main:app --reload
  ```

### 3. Frontend Not Running
- **Check**: Is frontend running on `http://localhost:3000`?
- **Start**:
  ```bash
  cd frontend
  npm start
  ```

### 4. API Connection Issues
- **Check browser console** (F12) for errors
- **Check Network tab** to see if API calls are failing
- **Verify**: Backend URL is `http://localhost:8000`

### 5. Common Issues

#### Devotee Count Shows 0
- **Cause**: No donations in database yet, or API call failing
- **Fix**: Record a donation first, then check dashboard

#### Donation Submission Shows "Not Found"
- **Cause**: Backend not running or endpoint not registered
- **Fix**: Ensure backend is running and check `/api/v1/donations` endpoint exists

#### Panchang Widget Not Working
- **Cause**: Panchang API endpoint not responding
- **Fix**: Check `/api/v1/panchang/today` endpoint in backend

#### Excel/PDF Export Not Working
- **Cause**: Backend dependencies not installed (`openpyxl`, `reportlab`)
- **Fix**: 
  ```bash
  cd backend
  .\venv\Scripts\activate
  pip install openpyxl reportlab Pillow requests
  ```

#### Devotees Page Blank
- **Cause**: No donations recorded yet (devotees are auto-created from donations)
- **Fix**: Record some donations first

## Verification Steps

1. **Backend Health Check**:
   - Open: `http://localhost:8000/health`
   - Should return: `{"status": "healthy", ...}`

2. **API Docs**:
   - Open: `http://localhost:8000/docs`
   - Should show Swagger UI with all endpoints

3. **Frontend Console**:
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Check Network tab for failed API calls

4. **Database**:
   - Ensure PostgreSQL is running
   - Check if tables exist: `temples`, `users`, `donations`, `devotees`, etc.

## Next Steps

If issues persist:
1. Check browser console for specific error messages
2. Check backend logs for errors
3. Verify database connection
4. Ensure all dependencies are installed

