# Panchang Network Error - Troubleshooting Guide

## 🔴 Problem
Frontend shows: "Failed to load panchang data: Network Error"

## ✅ Solutions

### 1. **Check Backend is Running**

The backend must be running on port 8000:

```bash
# In backend directory
cd backend
uvicorn app.main:app --reload --port 8000
```

**Verify:** Open http://localhost:8000/docs in browser - should show Swagger UI

---

### 2. **Check API URL Configuration**

**File:** `frontend/src/services/api.js`

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

**Verify:**
- Backend is running on `http://localhost:8000`
- No firewall blocking port 8000
- Frontend proxy is set correctly in `package.json`:
  ```json
  "proxy": "http://localhost:8000"
  ```

---

### 3. **Check Authentication**

The panchang endpoint requires authentication. Make sure:

1. **User is logged in:**
   - Check browser console for token
   - Check `localStorage.getItem('token')` in browser DevTools

2. **Token is valid:**
   - Token should be in format: `Bearer <token>`
   - Token should not be expired (120 minutes default)

**Test:** Try accessing http://localhost:8000/api/v1/panchang/today directly
- Without token: Should return 401 Unauthorized
- With token: Should return panchang data

---

### 4. **Check CORS Configuration**

**Backend:** `backend/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # Should include http://localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Verify:** `backend/app/core/config.py` has:
```python
ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
```

---

### 5. **Check Browser Console**

Open browser DevTools (F12) and check:

1. **Network Tab:**
   - Look for request to `/api/v1/panchang/today`
   - Check status code (should be 200, not 401/404/500)
   - Check if request is being sent

2. **Console Tab:**
   - Look for CORS errors
   - Look for authentication errors
   - Look for network errors

---

### 6. **Quick Fix: Test API Directly**

Test the endpoint directly in browser or Postman:

```bash
# Get token first (login)
POST http://localhost:8000/api/v1/login
Body: {
  "username": "admin@temple.com",
  "password": "admin123"
}

# Then call panchang endpoint
GET http://localhost:8000/api/v1/panchang/today
Headers: {
  "Authorization": "Bearer <token_from_login>"
}
```

---

### 7. **Common Issues & Fixes**

#### Issue: "Network Error" (no response)
**Cause:** Backend not running or wrong URL
**Fix:** Start backend server

#### Issue: "401 Unauthorized"
**Cause:** Not logged in or token expired
**Fix:** Login again

#### Issue: "CORS error"
**Cause:** Backend CORS not configured for frontend origin
**Fix:** Add frontend URL to `ALLOWED_ORIGINS` in backend config

#### Issue: "404 Not Found"
**Cause:** Wrong endpoint URL
**Fix:** Check endpoint is `/api/v1/panchang/today` (not `/panchang/today`)

---

### 8. **Debug Steps**

1. **Check backend logs:**
   ```bash
   # Should see request in backend terminal:
   INFO: 127.0.0.1:xxxxx - "GET /api/v1/panchang/today HTTP/1.1" 200 OK
   ```

2. **Check frontend network:**
   - Open DevTools → Network tab
   - Filter by "panchang"
   - Check request URL, headers, response

3. **Test with curl:**
   ```bash
   # Get token
   curl -X POST http://localhost:8000/api/v1/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@temple.com&password=admin123"
   
   # Use token to get panchang
   curl http://localhost:8000/api/v1/panchang/today \
     -H "Authorization: Bearer <token>"
   ```

---

### 9. **Expected Behavior**

**When Working:**
- Backend running on port 8000 ✅
- Frontend running on port 3000 ✅
- User logged in with valid token ✅
- API call succeeds with 200 OK ✅
- Panchang data displays ✅

**Error Messages:**
- "Network Error" → Backend not reachable
- "401 Unauthorized" → Not logged in
- "404 Not Found" → Wrong endpoint
- "500 Internal Server Error" → Backend error (check backend logs)

---

## 🚀 Quick Checklist

- [ ] Backend is running (`uvicorn app.main:app --reload --port 8000`)
- [ ] Frontend is running (`npm start`)
- [ ] User is logged in (check localStorage for token)
- [ ] Backend accessible at http://localhost:8000/docs
- [ ] No CORS errors in browser console
- [ ] Network request shows in DevTools Network tab

---

## 📝 Next Steps

1. **Start backend** if not running
2. **Login** to frontend if not logged in
3. **Check browser console** for specific error
4. **Check backend logs** for errors
5. **Test API directly** with Postman/curl

---

**If still not working, share:**
- Backend terminal output
- Browser console errors
- Network tab request details



