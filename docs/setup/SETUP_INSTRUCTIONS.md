# Setup Instructions - Multi-User & Audit Trail

## 📍 Where to Run Each Step

### Step 1: Create Audit Logs Table

**Location:** Can be run from **PROJECT ROOT** or **database client**

#### Option A: From Project Root (Recommended for psql)
```bash
# Navigate to project root
cd D:\MandirSync

# Run SQL script using psql
psql -d temple_db -f backend/scripts/create_audit_logs_table.sql

# Or with full connection details:
psql -h localhost -U postgres -d temple_db -f backend/scripts/create_audit_logs_table.sql
```

#### Option B: Using Database Client (Easiest)
1. Open your database client (pgAdmin, DBeaver, DataGrip, etc.)
2. Connect to your database
3. Open file: `D:\MandirSync\backend\scripts\create_audit_logs_table.sql`
4. Copy all SQL content
5. Paste and execute in your database client

#### Option C: Using Python Script (EASIEST - Recommended)
```bash
# Navigate to backend directory
cd D:\MandirSync\backend

# Activate your virtual environment (if using one)
# conda activate your_env_name

# Run the Python script
python -m scripts.create_audit_logs_table
```

**This is the easiest method if psql is not available!**

---

### Step 2: Create Clerk Users

**Location:** Must be run from **BACKEND DIRECTORY** (`D:\MandirSync\backend`)

```bash
# Navigate to backend directory
cd D:\MandirSync\backend

# Activate virtual environment (if using one)
# conda activate your_env_name
# OR
# source venv/bin/activate  # On Linux/Mac
# venv\Scripts\activate  # On Windows

# Run the script
python -m scripts.create_clerk_users --num-clerks 3 --password clerk123
```

**Current Directory Check:**
- If you're in `D:\MandirSync` (project root), run: `cd backend` first
- If you're in `D:\MandirSync\backend`, run directly

**Verify you're in the right directory:**
```bash
# Windows PowerShell
pwd
# Should show: D:\MandirSync\backend

# Or check if scripts folder exists
ls scripts
# Should show: create_clerk_users.py, create_audit_logs_table.sql, etc.
```

---

## 🔍 Quick Verification

### After Step 1 (Audit Logs Table):
```sql
-- Run in your database client
SELECT COUNT(*) FROM audit_logs;
-- Should return 0 (table exists but empty)
```

### After Step 2 (Clerk Users):
```bash
# From backend directory
python -c "
from app.core.database import SessionLocal
from app.models.user import User
db = SessionLocal()
clerks = db.query(User).filter(User.email.like('clerk%@temple.local')).all()
print(f'Found {len(clerks)} clerk users:')
for clerk in clerks:
    print(f'  - {clerk.email} ({clerk.full_name})')
"
```

---

## 📋 Complete Setup Checklist

- [ ] **Step 1:** Create audit_logs table (using Option A, B, or C above)
- [ ] **Step 2:** Create clerk users (from backend directory)
- [ ] **Step 3:** Test login with clerk1@temple.local / clerk123
- [ ] **Step 4:** Create a donation as clerk1
- [ ] **Step 5:** Check audit logs: `GET /api/v1/audit-logs/` (as admin)

---

## 🚨 Common Issues

### Issue 1: "Module not found" when running Step 2
**Solution:** Make sure you're in the backend directory and have activated your virtual environment.

### Issue 2: "Database connection error" in Step 1
**Solution:** Check your database connection string in `.env` or `app/core/config.py`

### Issue 3: "Table already exists" in Step 1
**Solution:** Table already created. Skip this step or drop and recreate if needed.

### Issue 4: "User already exists" in Step 2
**Solution:** Clerk users already created. You can skip or delete existing ones first.

---

## 💡 Tips

1. **Easiest Method for Step 1:** Use Option B (database client) - just copy/paste SQL
2. **For Step 2:** Always run from `D:\MandirSync\backend` directory
3. **Verify Setup:** Run the verification commands above to confirm everything worked

---

**Need Help?** Check `MULTI_USER_AUDIT_TRAIL.md` for detailed documentation.
