# Quick Start: Multi-User & Audit Trail

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Audit Logs Table

**Where to run:** From **PROJECT ROOT** (`D:\MandirSync`) OR directly in your database client

**Option A: Using psql command (from project root)**
```bash
# From project root: D:\MandirSync
psql -d your_database_name -f backend/scripts/create_audit_logs_table.sql

# Or if you need to specify host/user:
psql -h localhost -U postgres -d your_database_name -f backend/scripts/create_audit_logs_table.sql
```

**Option B: Using database client (pgAdmin, DBeaver, etc.)**
1. Open `backend/scripts/create_audit_logs_table.sql` in a text editor
2. Copy the SQL content
3. Paste and run it in your database client (pgAdmin, DBeaver, etc.)

**Option C: Using Python (from backend directory)**
```bash
# From backend directory: D:\MandirSync\backend
python -c "from app.core.database import engine; exec(open('../backend/scripts/create_audit_logs_table.sql').read())"
```

---

### Step 2: Create Clerk Users

**Where to run:** From **BACKEND DIRECTORY** (`D:\MandirSync\backend`)

```bash
# Make sure you're in the backend directory
cd D:\MandirSync\backend

# Run the script
python -m scripts.create_clerk_users --num-clerks 3 --password clerk123
```

**Note:** You're already in the backend directory based on your terminal, so you can run directly:
```bash
python -m scripts.create_clerk_users --num-clerks 3 --password clerk123
```

This creates:
- `clerk1@temple.local` / Password: `clerk123`
- `clerk2@temple.local` / Password: `clerk123`
- `clerk3@temple.local` / Password: `clerk123`

### Step 3: Test Login

1. Login as admin (existing user)
2. Login as `clerk1@temple.local` with password `clerk123`
3. Create a donation
4. Check audit logs: `GET /api/v1/audit-logs/`

---

## 📋 What's Implemented

### ✅ Multi-User Support
- User management API (`/api/v1/users/`)
- Role-based access (admin, staff, clerk, accountant, priest)
- User creation, update, deactivation
- Login tracking

### ✅ Audit Trail
- Comprehensive logging of all actions
- Tracks: Who, What, When, What Changed
- IP address and user agent tracking
- Admin-only access to audit logs

### ✅ Enhanced Authentication
- Login success/failure tracking
- Last login timestamp
- Failed login attempt counter

---

## 🔍 Viewing Audit Logs

### API Endpoint
```
GET /api/v1/audit-logs/
```

### Query Parameters
- `user_id` - Filter by user
- `action` - Filter by action (CREATE_DONATION, etc.)
- `entity_type` - Filter by entity (Donation, SevaBooking, etc.)
- `from_date` - Start date
- `to_date` - End date

### Example
```
GET /api/v1/audit-logs/?user_id=2&action=CREATE_DONATION&limit=50
```

---

## 👥 Managing Users

### Create User (Admin Only)
```
POST /api/v1/users/
{
  "email": "clerk4@temple.local",
  "password": "clerk123",
  "full_name": "Clerk 4",
  "role": "staff",
  "is_active": true
}
```

### List Users (Admin Only)
```
GET /api/v1/users/
```

### Update User
```
PUT /api/v1/users/{id}
```

---

## 📊 What Gets Logged

- ✅ User creation/update/deletion
- ✅ Login (success/failure)
- ✅ Donation creation/update
- ✅ Seva booking creation/update
- ✅ Journal entry creation
- ✅ Account modifications

---

## 🔒 Security Notes

1. **Change Default Passwords!**
   - Default clerk password: `clerk123`
   - Must be changed after first login

2. **Access Control:**
   - Only admins can view audit logs
   - Only admins can create/manage users

3. **Audit Trail:**
   - Immutable (cannot be deleted)
   - Tracks all critical actions

---

## 📚 Full Documentation

See `MULTI_USER_AUDIT_TRAIL.md` for complete documentation.

---

**Ready to use!** 🎉

