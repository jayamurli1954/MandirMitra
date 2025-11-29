# Backend Error Fix - Bank Reconciliation Relationship

## ✅ Error Fixed

**Error**: 
```
Could not determine join condition between parent/child tables on relationship BankReconciliation.outstanding_items - there are multiple foreign key paths linking the tables.
```

**Cause**: `ReconciliationOutstandingItem` has two foreign keys to `bank_reconciliations`:
- `reconciliation_id` (main relationship)
- `cleared_in_reconciliation_id` (optional reference)

**Fix Applied**: Added explicit `foreign_keys` and `primaryjoin` to relationships in `backend/app/models/bank_reconciliation.py`

---

## 🔄 How to Restart Backend

### Step 1: Stop Current Server
Press `CTRL+C` in the terminal where uvicorn is running

### Step 2: Restart Server
```powershell
cd D:\MandirSync\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Step 3: Verify It's Working
- Check console for: `INFO: Application startup complete.` (no errors)
- Test health: `curl http://localhost:8000/health`
- Should return: `{"status":"healthy","service":"MandirSync","version":"1.0.0"}`

---

## 🔐 Login Credentials

**Email**: `admin@temple.com` (note: dot `.` not comma `,`)
**Password**: `admin123`

**Important**: 
- Use `admin@temple.com` (with **dot**)
- NOT `admin@temple,com` (with comma)

---

## ✅ Verification

After restart, you should see:
```
INFO:     Application startup complete.
```

**NOT**:
```
❌ Error creating admin user: ...
```

---

## 🧪 Test Login

1. Open: http://localhost:8000/docs
2. Go to `/api/v1/login` endpoint
3. Click "Try it out"
4. Enter:
   - `username`: `admin@temple.com`
   - `password`: `admin123`
5. Click "Execute"
6. Should return: `{"access_token": "...", "token_type": "bearer"}`

---

## 📝 Summary

- ✅ Relationship error fixed
- ✅ App imports successfully
- ✅ Ready to restart server
- ✅ Login credentials: `admin@temple.com` / `admin123`








