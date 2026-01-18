# Login Module - Frozen Documentation

## ⚠️ CRITICAL: DO NOT MODIFY WITHOUT TESTING

The login authentication system has been stabilized and verified working. The following files contain critical authentication logic:

### Core Files (FROZEN):
1. **`backend/app/core/security.py`**
   - `verify_password()` - **CRITICAL** - Verifies user passwords during login
   - `get_password_hash()` - Creates password hashes for new/updated passwords
   - `hash_password()` - Alternative password hashing function

### Related Files:
2. **`backend/app/api/auth.py`** (or similar) - Login endpoint
3. **`backend/app/core/database.py`** - Database initialization (admin user creation)

## Current Working Configuration

- **Login Credentials:**
  - Email: `admin@temple.com`
  - Password: `admin123`

- **Password Hashing:**
  - Uses bcrypt via passlib
  - Fallback to direct bcrypt if passlib fails
  - Handles 72-byte password limit automatically

- **Database:**
  - Admin user exists in database
  - Password hash format: `$2b$12$...` (bcrypt)

## Testing Checklist

Before modifying any authentication-related code, verify:

- [ ] Login with `admin@temple.com` / `admin123` works
- [ ] Existing users can still log in
- [ ] New password hashes are created correctly
- [ ] Password verification works for all hash formats
- [ ] No 401 Unauthorized errors in logs
- [ ] JWT token generation works correctly

## Known Issues & Solutions

1. **Bcrypt 72-byte limit:**
   - Solution: All password functions truncate to 72 bytes

2. **Passlib bug detection:**
   - Solution: Fallback to direct bcrypt verification

3. **Password hash format:**
   - Solution: Uses standard bcrypt format (`$2b$12$...`)

## Last Verified
- Date: 2024-12-XX
- Status: ✅ Working
- Login endpoint: `POST /api/v1/login` returns 200 OK

## Notes
- The `verify_password()` function includes multiple fallback mechanisms
- Do not remove the bcrypt direct verification fallback
- Always test with existing database users after changes







