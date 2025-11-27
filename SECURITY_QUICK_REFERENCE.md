# Security Quick Reference

## 🔒 What's Protected

### ✅ Devotee Personal Data
- **Phone Numbers:** Masked (`9876543210` → `98765*****`)
- **Addresses:** Masked (only first 10 chars visible)
- **Emails:** Masked (`user@example.com` → `u***@example.com`)
- **Access Control:** Only users with `VIEW_DEVOTEE_PHONE` permission see full data

### ✅ Financial Records
- **Access:** Role-based (accountant, admin only)
- **Modification:** Requires `POST_JOURNAL_ENTRIES` permission
- **Export:** Requires `EXPORT_REPORTS` permission
- **Audit:** All changes logged

### ✅ Religious Information
- **Gotras, Nakshatras:** Access controlled by role
- **Modification:** Admin only
- **Audit:** All changes logged

### ✅ 80G Tax Certificates
- **Storage:** Secure directory with random filenames
- **Upload:** Requires `UPLOAD_CERTIFICATES` permission
- **Download:** Requires `DOWNLOAD_CERTIFICATES` permission
- **Audit:** All access logged

---

## 🛡️ Security Features

### 1. Authentication
- ✅ Strong password policy (8+ chars, uppercase, lowercase, digits, special)
- ✅ Rate limiting (5 login attempts per 15 minutes)
- ✅ Account lockout after failed attempts
- ✅ JWT tokens with expiration

### 2. Authorization
- ✅ Role-based access control (RBAC)
- ✅ 30+ granular permissions
- ✅ Permission checks on all sensitive operations

### 3. Data Protection
- ✅ Data masking (phone, address, email)
- ✅ Field-level encryption (optional)
- ✅ Secure file storage

### 4. Monitoring
- ✅ Comprehensive audit trail
- ✅ IP address tracking
- ✅ Login attempt tracking

### 5. Security Headers
- ✅ X-Content-Type-Options
- ✅ X-Frame-Options
- ✅ X-XSS-Protection
- ✅ Content-Security-Policy
- ✅ Strict-Transport-Security

---

## ⚙️ Configuration

### Required in .env:
```bash
# Generate these keys:
SECRET_KEY=<generate-secure-key>
JWT_SECRET_KEY=<generate-secure-key>
ENCRYPTION_KEY=<generate-encryption-key>

# Generate encryption key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 📋 User Roles & Permissions

| Role | Can View Phone/Address | Can Export Data | Can Manage Users | Can View Audit Logs |
|------|----------------------|-----------------|------------------|---------------------|
| Admin | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Temple Manager | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| Accountant | ❌ No | ✅ Yes | ❌ No | ❌ No |
| Staff/Clerk | ❌ No | ❌ No | ❌ No | ❌ No |
| Priest | ❌ No | ❌ No | ❌ No | ❌ No |

---

## 🚨 Important Security Notes

1. **Change Default Passwords** - All clerk users have default password `clerk123`
2. **Set Encryption Key** - Required for data encryption
3. **Use HTTPS** - Set `FORCE_HTTPS=True` in production
4. **Regular Backups** - External responsibility but critical
5. **Review Audit Logs** - Check regularly for suspicious activity

---

**See `SECURITY_IMPLEMENTATION.md` for complete documentation.**







