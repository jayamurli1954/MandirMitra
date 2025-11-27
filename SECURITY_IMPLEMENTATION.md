# Security Implementation Guide

## 🔒 Comprehensive Security Measures for Temple Software

This document outlines all software-side security implementations to protect:
- **Devotee Personal Data** (phone, address, email)
- **Financial Records** (donations, accounts)
- **Religious Information** (gotras, nakshatras)
- **80G Tax Certificates**

---

## ✅ Implemented Security Features

### 1. **Authentication & Authorization** ✅

#### Password Security
- ✅ **Bcrypt hashing** - Passwords are hashed using bcrypt (industry standard)
- ✅ **Password policy** - Enforces strong passwords:
  - Minimum 8 characters
  - Requires uppercase, lowercase, digits, special characters
  - Prevents common passwords
  - Prevents repeated characters

#### JWT Tokens
- ✅ **Secure token generation** - JWT tokens with expiration
- ✅ **Token expiration** - 120 minutes default (configurable)
- ✅ **Secure algorithm** - HS256

#### Login Security
- ✅ **Rate limiting** - 5 login attempts per 15 minutes
- ✅ **Account lockout** - Temporary lockout after failed attempts
- ✅ **Login tracking** - Records successful/failed logins
- ✅ **IP tracking** - Tracks IP address and user agent

**Files:**
- `backend/app/core/security.py` - Password hashing, JWT tokens
- `backend/app/core/password_policy.py` - Password validation
- `backend/app/core/rate_limiting.py` - Rate limiting
- `backend/app/api/auth.py` - Login with rate limiting

---

### 2. **Role-Based Access Control (RBAC)** ✅

#### Permission System
- ✅ **Granular permissions** - 30+ specific permissions
- ✅ **Role-based access** - Different permissions for admin, staff, clerk, accountant, priest
- ✅ **Permission checks** - Automatic permission validation

#### Roles & Permissions:

**Admin:**
- Full access to all features
- Can manage users
- Can view audit logs
- Can access all sensitive data

**Temple Manager:**
- Can view/edit donations and sevas
- Can view devotee phone/address
- Can view reports
- Can manage certificates

**Accountant:**
- Can view/edit accounting
- Can create journal entries
- Can view reports
- Cannot view devotee phone/address

**Staff/Clerk:**
- Can create donations/sevas
- Can view basic devotee info
- Cannot view phone/address
- Cannot export data

**Priest:**
- Can only view sevas and basic devotee info
- Very limited access

**Files:**
- `backend/app/core/permissions.py` - Permission definitions and checks

---

### 3. **Data Masking** ✅

#### Sensitive Data Protection
- ✅ **Phone masking** - `9876543210` → `98765*****` (for non-authorized users)
- ✅ **Address masking** - Shows only first 10 characters
- ✅ **Email masking** - `user@example.com` → `u***@example.com`
- ✅ **PAN masking** - Only last 4 digits visible
- ✅ **Aadhaar masking** - Only last 4 digits visible

**Permission-based:**
- Only users with `VIEW_DEVOTEE_PHONE` permission see full phone
- Only users with `VIEW_DEVOTEE_ADDRESS` permission see full address
- Admins see all data

**Files:**
- `backend/app/core/data_masking.py` - Data masking utilities
- `backend/app/api/devotees.py` - Applies masking in responses

---

### 4. **Data Encryption** ✅

#### Encryption at Rest
- ✅ **Field-level encryption** - Sensitive fields can be encrypted
- ✅ **Fernet encryption** - Uses cryptography.fernet (symmetric encryption)
- ✅ **Key management** - Encryption key from environment variable

**Usage:**
```python
from app.core.data_encryption import encrypt_sensitive_data, decrypt_sensitive_data

# Encrypt
encrypted_phone = encrypt_sensitive_data(phone_number)

# Decrypt (when needed)
decrypted_phone = decrypt_sensitive_data(encrypted_phone)
```

**Files:**
- `backend/app/core/data_encryption.py` - Encryption utilities

**⚠️ Important:** Set `ENCRYPTION_KEY` in `.env` file for production!

---

### 5. **Audit Trail** ✅

#### Comprehensive Logging
- ✅ **All actions logged** - Who did what, when, from where
- ✅ **Change tracking** - Before/after values for updates
- ✅ **IP address tracking** - Records user's IP
- ✅ **User agent tracking** - Records browser/client info
- ✅ **Immutable logs** - Cannot be deleted

**Logged Actions:**
- User creation/update/deletion
- Login (success/failure)
- Donation creation/update
- Seva booking/update
- Journal entry creation
- Account modifications
- Certificate uploads/downloads

**Files:**
- `backend/app/models/audit_log.py` - Audit log model
- `backend/app/core/audit.py` - Audit logging utilities
- `backend/app/api/audit_logs.py` - View audit logs (admin only)

---

### 6. **Rate Limiting** ✅

#### Protection Against Abuse
- ✅ **Login rate limiting** - 5 attempts per 15 minutes
- ✅ **API rate limiting** - 100 requests per minute (configurable)
- ✅ **IP-based tracking** - Tracks by IP address
- ✅ **Automatic lockout** - Locks IP/user after limit exceeded

**Files:**
- `backend/app/core/rate_limiting.py` - Rate limiting implementation

---

### 7. **Security Headers** ✅

#### HTTP Security Headers
- ✅ **X-Content-Type-Options: nosniff** - Prevents MIME sniffing
- ✅ **X-Frame-Options: DENY** - Prevents clickjacking
- ✅ **X-XSS-Protection: 1; mode=block** - XSS protection
- ✅ **Strict-Transport-Security** - Forces HTTPS (when enabled)
- ✅ **Content-Security-Policy** - Prevents XSS attacks
- ✅ **Referrer-Policy** - Controls referrer information
- ✅ **Permissions-Policy** - Restricts browser features

**Files:**
- `backend/app/core/security_headers.py` - Security headers middleware
- `backend/app/main.py` - Middleware registration

---

### 8. **Secure File Storage** ✅

#### 80G Certificates & Documents
- ✅ **Secure file uploads** - Validates file type and size
- ✅ **Random filenames** - Uses secure random tokens
- ✅ **Permission-based access** - Only authorized users can download
- ✅ **File type validation** - Only PDF, JPEG, PNG allowed
- ✅ **Size limits** - Maximum 5MB per file

**Files:**
- `backend/app/api/certificates.py` - Certificate management API

---

### 9. **Input Validation** ✅

#### Data Sanitization
- ✅ **Pydantic schemas** - Automatic validation
- ✅ **Email validation** - Validates email format
- ✅ **Phone validation** - Validates phone numbers
- ✅ **SQL injection prevention** - SQLAlchemy ORM (parameterized queries)
- ✅ **XSS prevention** - FastAPI auto-escaping

---

### 10. **Session Management** ✅

#### Secure Sessions
- ✅ **JWT tokens** - Stateless authentication
- ✅ **Token expiration** - Automatic expiry
- ✅ **Last login tracking** - Records when user last logged in
- ✅ **Failed attempt tracking** - Tracks failed login attempts

---

## 📋 Security Checklist

### ✅ Implemented
- [x] Password hashing (bcrypt)
- [x] Password policy enforcement
- [x] JWT token authentication
- [x] Role-based access control
- [x] Data masking (phone, address, email)
- [x] Data encryption utilities
- [x] Comprehensive audit trail
- [x] Rate limiting
- [x] Security headers
- [x] Secure file storage
- [x] Input validation
- [x] Session management
- [x] Login attempt tracking
- [x] IP address logging

### 🔄 To Be Implemented (Optional)
- [ ] Two-factor authentication (2FA)
- [ ] Database encryption at rest
- [ ] Automated backups (software-side)
- [ ] Data export restrictions
- [ ] Secure deletion (GDPR compliance)
- [ ] Privacy controls (data retention policies)
- [ ] API key management
- [ ] Webhook security

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Security Keys (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# Data Encryption (Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your-encryption-key-here

# HTTPS (Set to True in production)
FORCE_HTTPS=False

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Password Policy
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_DIGITS=True
PASSWORD_REQUIRE_SPECIAL=True
```

---

## 🚀 Production Security Checklist

### Before Going Live:

1. **Change Default Secrets:**
   ```bash
   # Generate secure keys
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Set Encryption Key:**
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

3. **Enable HTTPS:**
   - Set `FORCE_HTTPS=True` in `.env`
   - Configure reverse proxy (nginx/Apache) with SSL certificate

4. **Database Security:**
   - Use strong database password
   - Restrict database access (firewall rules)
   - Enable SSL for database connections

5. **File Permissions:**
   ```bash
   # Secure uploads directory
   chmod 700 uploads/certificates
   ```

6. **Environment Variables:**
   - Never commit `.env` file
   - Use secure secret management in production

7. **Regular Updates:**
   - Keep dependencies updated
   - Monitor security advisories

---

## 📊 Data Protection by Type

### Devotee Personal Data
- **Phone:** Masked for non-authorized users
- **Address:** Masked for non-authorized users
- **Email:** Masked for non-authorized users
- **Encryption:** Optional field-level encryption
- **Access:** Permission-based (VIEW_DEVOTEE_PHONE, VIEW_DEVOTEE_ADDRESS)

### Financial Records
- **Access:** Role-based (accountant, admin only)
- **Audit:** All changes logged
- **Export:** Permission required (EXPORT_REPORTS)
- **Modification:** Requires POST_JOURNAL_ENTRIES permission

### Religious Information (Gotras, Nakshatras)
- **Access:** Staff and above can view
- **Modification:** Admin only
- **Audit:** All changes logged

### 80G Tax Certificates
- **Storage:** Secure directory with random filenames
- **Access:** Permission-based (DOWNLOAD_CERTIFICATES)
- **Upload:** Permission required (UPLOAD_CERTIFICATES)
- **Audit:** All uploads/downloads logged

---

## 🔍 Monitoring & Alerts

### Audit Log Review
- Review failed login attempts regularly
- Monitor permission changes
- Check for unusual access patterns
- Review certificate downloads

### Security Alerts
- Multiple failed logins from same IP
- Unauthorized access attempts
- Permission escalation attempts
- Bulk data exports

---

## 📚 External Security (Temple's Responsibility)

These are **NOT** software-side but critical:

1. **Physical Security:**
   - Lock computer room
   - CCTV cameras
   - Access control

2. **Backups:**
   - Regular database backups
   - External hard disk storage
   - Off-site backup copies
   - Test backup restoration

3. **Network Security:**
   - Firewall configuration
   - Network segmentation
   - VPN for remote access

4. **System Security:**
   - OS updates
   - Antivirus software
   - System monitoring

---

## 🎯 Usage Examples

### Check Permission
```python
from app.core.permissions import check_permission, Permission

# In API endpoint
check_permission(current_user, Permission.VIEW_DEVOTEE_PHONE)
```

### Mask Data
```python
from app.core.data_masking import mask_phone_for_user

# In response
masked_phone = mask_phone_for_user(devotee.phone, current_user)
```

### Rate Limit
```python
from app.core.rate_limiting import check_rate_limit

# In API endpoint
check_rate_limit(request, max_requests=10, window_seconds=60)
```

### Encrypt Data
```python
from app.core.data_encryption import encrypt_sensitive_data

# Before storing
encrypted = encrypt_sensitive_data(phone_number)
```

---

## ⚠️ Important Notes

1. **Encryption Key:** Must be set in production! Generate once and store securely.

2. **HTTPS:** Always use HTTPS in production. Set `FORCE_HTTPS=True`.

3. **Secrets:** Never commit secrets to git. Use `.env` file (in `.gitignore`).

4. **Backups:** Regular backups are critical. Test restoration regularly.

5. **Audit Logs:** Review regularly for security incidents.

6. **Updates:** Keep all dependencies updated for security patches.

---

**Last Updated:** November 2025
**Status:** Production-ready security implementation







