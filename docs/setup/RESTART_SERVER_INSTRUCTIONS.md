# 🔄 Restart Backend Server - Required

## ⚠️ Important: Server Must Be Restarted

The admin user is created, but you need to **restart the backend server** for the relationship fixes to take effect.

---

## 📋 Step-by-Step Instructions

### Step 1: Stop Current Server
1. Go to the terminal/command prompt where uvicorn is running
2. Press: `CTRL + C`
3. Wait for it to stop

### Step 2: Restart Server
```powershell
cd D:\MandirSync\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Step 3: Verify Server Started
You should see:
```
INFO:     Application startup complete.
```

**NOT**:
```
❌ Error creating admin user: ...
```

---

## ✅ After Restart

### Test Login
1. Open your frontend application
2. Go to login page
3. Enter:
   - **Email**: `admin@temple.com`
   - **Password**: `admin123`
4. Click Login

---

## 🔐 Login Credentials (Already Created)

- **Email**: `admin@temple.com`
- **Password**: `admin123`

The user is already in the database - just restart the server and login!

---

## 🧪 Quick Test After Restart

```powershell
# Test health
curl http://localhost:8000/health

# Should return: {"status":"healthy","service":"MandirSync","version":"1.0.0"}
```

---

## ✅ Summary

1. ✅ Admin user created: `admin@temple.com` / `admin123`
2. ⏳ **Restart server** (required)
3. ✅ Login through frontend

**No Swagger UI needed** - just restart and use your frontend login!


