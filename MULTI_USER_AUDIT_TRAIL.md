# Multi-User Support & Audit Trail Implementation

## Overview

Complete multi-user support and comprehensive audit trail system for standalone version. Tracks all user actions (who did what, when, and what changed).

---

## ✅ Features Implemented

### 1. Multi-User Management ✅

**User Roles:**
- `admin` - Full access, can manage users
- `staff` / `clerk` - Regular staff members
- `accountant` - Accounting access
- `priest` - Limited access

**User Management API:**
- `POST /api/v1/users/` - Create user (admin only)
- `GET /api/v1/users/` - List users (admin only)
- `GET /api/v1/users/me` - Get current user info
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Deactivate user (admin only)

**Files:**
- `backend/app/api/users.py` - User management endpoints
- `backend/app/models/user.py` - User model (already exists)

---

### 2. Enhanced Authentication ✅

**Login Tracking:**
- Tracks successful logins
- Tracks failed login attempts
- Updates `last_login_at` timestamp
- Records IP address and user agent

**Security Features:**
- Failed login attempt counter
- Account lockout capability
- Password change tracking

**Files:**
- `backend/app/api/auth.py` - Enhanced login with audit
- `backend/app/core/security.py` - Security utilities

---

### 3. Comprehensive Audit Trail ✅

**Audit Log Model:**
- Tracks all user actions
- Records: Who, What, When, What Changed
- Stores IP address and user agent
- JSON storage for old/new values

**Audit Log API:**
- `GET /api/v1/audit-logs/` - View audit logs (admin only)
- `GET /api/v1/audit-logs/summary` - Audit summary statistics

**Files:**
- `backend/app/models/audit_log.py` - Audit log model
- `backend/app/core/audit.py` - Audit logging utilities
- `backend/app/api/audit_logs.py` - Audit log API

---

### 4. Automatic Audit Logging ✅

**Actions Tracked:**
- ✅ User creation/update/deletion
- ✅ Login (success/failure)
- ✅ Donation creation/update
- ✅ Seva booking creation/update
- ✅ Journal entry creation
- ✅ Account modifications
- ✅ Settings changes

**How It Works:**
- Uses `log_action()` function from `app.core.audit`
- Automatically captures user, IP, timestamp
- Stores before/after values for updates
- Calculates changes (diff)

---

## 📋 Setup Instructions

### Step 1: Database Migration

Create audit_logs table:

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    user_name VARCHAR(200) NOT NULL,
    user_email VARCHAR(100) NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changes JSONB,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX idx_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

Or use Alembic migration (recommended).

---

### Step 2: Create Clerk Users

Run the script to create clerk users:

```bash
cd backend
python -m scripts.create_clerk_users --num-clerks 3 --password clerk123
```

This creates:
- `clerk1@temple.local` / `clerk123`
- `clerk2@temple.local` / `clerk123`
- `clerk3@temple.local` / `clerk123`

**⚠️ IMPORTANT:** Change default passwords after first login!

---

### Step 3: Test Login

1. Login as admin (existing user)
2. Login as clerk1, clerk2, clerk3
3. Check audit logs: `/api/v1/audit-logs/`

---

## 🔍 Using Audit Trail

### View Audit Logs (Admin Only)

**API Endpoint:**
```
GET /api/v1/audit-logs/
```

**Query Parameters:**
- `user_id` - Filter by user
- `action` - Filter by action (CREATE_DONATION, UPDATE_SEVA, etc.)
- `entity_type` - Filter by entity (Donation, SevaBooking, etc.)
- `entity_id` - Filter by specific entity ID
- `from_date` - Start date
- `to_date` - End date
- `skip` - Pagination offset
- `limit` - Results per page

**Example:**
```
GET /api/v1/audit-logs/?user_id=2&action=CREATE_DONATION&limit=50
```

### View Audit Summary

**API Endpoint:**
```
GET /api/v1/audit-logs/summary?from_date=2025-11-01&to_date=2025-11-30
```

Returns:
- Total logs
- Count by action type
- Count by user

---

## 📊 Audit Log Fields

Each audit log entry contains:

- **User Info:**
  - `user_id` - User ID
  - `user_name` - User's full name
  - `user_email` - User's email
  - `user_role` - User's role

- **Action Info:**
  - `action` - Action type (CREATE_DONATION, UPDATE_SEVA, etc.)
  - `entity_type` - Entity type (Donation, SevaBooking, etc.)
  - `entity_id` - ID of affected entity

- **Change Tracking:**
  - `old_values` - Previous state (JSON)
  - `new_values` - New state (JSON)
  - `changes` - Diff of what changed (JSON)

- **Context:**
  - `ip_address` - User's IP address
  - `user_agent` - Browser/client info
  - `description` - Human-readable description
  - `created_at` - Timestamp

---

## 🔐 User Management

### Create Clerk User (Admin Only)

**API:**
```
POST /api/v1/users/
```

**Request Body:**
```json
{
  "email": "clerk1@temple.local",
  "password": "clerk123",
  "full_name": "Clerk 1",
  "phone": "9876543210",
  "role": "staff",
  "is_active": true
}
```

### Update User

**API:**
```
PUT /api/v1/users/{id}
```

Users can update their own profile (limited fields).
Admins can update any user.

### Deactivate User

**API:**
```
DELETE /api/v1/users/{id}
```

Soft delete (sets `is_active = false`).

---

## 🎯 Action Types Tracked

### User Actions:
- `CREATE_USER` - User created
- `UPDATE_USER` - User updated
- `DELETE_USER` - User deactivated
- `LOGIN_SUCCESS` - Successful login
- `LOGIN_FAILED` - Failed login attempt

### Donation Actions:
- `CREATE_DONATION` - Donation created
- `UPDATE_DONATION` - Donation updated
- `CANCEL_DONATION` - Donation cancelled

### Seva Actions:
- `CREATE_SEVA_BOOKING` - Seva booked
- `UPDATE_SEVA_BOOKING` - Seva updated
- `CANCEL_SEVA_BOOKING` - Seva cancelled
- `RESCHEDULE_SEVA` - Seva rescheduled

### Accounting Actions:
- `CREATE_JOURNAL_ENTRY` - Journal entry created
- `UPDATE_JOURNAL_ENTRY` - Journal entry updated
- `POST_JOURNAL_ENTRY` - Journal entry posted

---

## 📝 Adding Audit Logging to New Endpoints

To add audit logging to any endpoint:

```python
from app.core.audit import log_action, get_entity_dict
from fastapi import Request

@router.post("/your-endpoint")
def your_function(
    data: YourSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    # Your logic here
    entity = create_or_update_entity(data)
    
    # Audit log
    log_action(
        db=db,
        user=current_user,
        action="CREATE_ENTITY",
        entity_type="Entity",
        entity_id=entity.id,
        new_values=get_entity_dict(entity),
        description=f"Created entity: {entity.name}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return entity
```

---

## 🚀 Frontend Integration (TODO)

Frontend pages needed:
1. **User Management Page** - `/users` (admin only)
   - List users
   - Create/edit users
   - Deactivate users

2. **Audit Logs Page** - `/audit-logs` (admin only)
   - View audit logs
   - Filter by user/action/date
   - Export logs

---

## 📋 Checklist

- [x] User model with roles
- [x] User management API
- [x] Enhanced login with tracking
- [x] Audit log model
- [x] Audit logging utilities
- [x] Audit log API
- [x] Automatic logging in donations
- [x] Script to create clerk users
- [ ] Frontend user management page
- [ ] Frontend audit logs page
- [ ] Add audit logging to all endpoints

---

## 🔒 Security Notes

1. **Passwords:**
   - Default clerk password: `clerk123`
   - **MUST be changed after first login**
   - Passwords are hashed using bcrypt

2. **Access Control:**
   - Only admins can view audit logs
   - Only admins can create/manage users
   - Users can view/edit their own profile

3. **Audit Trail:**
   - Cannot be deleted (immutable)
   - Only admins can view
   - Tracks all critical actions

---

**Last Updated:** November 2025



