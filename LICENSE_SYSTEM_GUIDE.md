# MandirSync License & Trial System Guide

## 📋 Overview

MandirSync includes a built-in trial license system that allows you to:
- **Offer free trials** (10, 15, 30 days - you decide)
- **Automatically disable** the application after trial expiry
- **Upgrade to full license** with a license key
- **Grace period** of 2 days after expiry
- **Tamper protection** using checksums

---

## 🔑 License Types

| License Type | Duration | Features |
|-------------|----------|----------|
| **Trial** | 10/15/30 days | Full features, time-limited |
| **Full** | Lifetime | All features, no expiry |
| **Premium** | Lifetime | All features + premium support |
| **Enterprise** | Custom | Custom features + SLA |

---

## 🚀 Quick Start

### For Temple Users (Activating Trial)

When you first install MandirSync, you'll see a license activation screen:

1. **Enter temple name** and **contact email**
2. **Select trial period** (10, 15, or 30 days)
3. Click **"Start Free Trial"**
4. ✅ You're ready to use MandirSync!

### For Developers/Admins

Use the CLI tool to manage licenses:

```bash
cd backend

# Check license status
python manage_license.py status

# Create a 15-day trial
python manage_license.py create-trial "Sri Krishna Temple" --days 15

# Create a 30-day trial with email
python manage_license.py create-trial "Hanuman Temple" --days 30 --email contact@temple.com

# Extend trial by 5 days
python manage_license.py extend-trial 5

# Activate full license
python manage_license.py activate-full "Sri Krishna Temple" --key XXXX-XXXX-XXXX-XXXX

# Deactivate license
python manage_license.py deactivate
```

---

## 📖 How It Works

### 1. **Trial Creation**

When a temple activates a trial:

```
1. User enters temple name and email
2. System creates license file with:
   - Temple information
   - Trial start date
   - Expiry date (start + trial days)
   - Tamper-proof checksum
3. License file saved to:
   Windows: %APPDATA%/.mandirsync/license.dat
   Linux/Mac: ~/.mandirsync/license.dat
```

### 2. **License Validation (On Every App Start)**

```
1. App checks for license file
2. Validates checksum (detects tampering)
3. Checks expiry date
4. If expired:
   - Check grace period (2 days)
   - If grace period expired: Block access
   - Show renewal message
5. If active: Allow access
```

### 3. **Automatic Disabling**

When trial expires:

```
Day 15 (Expiry): App still works (Grace period day 1)
Day 16: App still works (Grace period day 2)
Day 17: ❌ App blocks access

User sees:
"Your trial has expired. Please contact support to activate full license."
```

### 4. **License Upgrade**

To upgrade from trial to full:

```bash
# Using CLI
python manage_license.py activate-full "Temple Name" --key FULL-LICENSE-KEY

# Or via API
POST /api/license/activate-full
{
  "temple_name": "Sri Krishna Temple",
  "license_key": "XXXX-XXXX-XXXX-XXXX"
}
```

---

## 🔧 API Endpoints

### Check License Status

```bash
GET /api/license/status
```

**Response:**
```json
{
  "temple_name": "Sri Krishna Temple",
  "license_type": "trial",
  "status": "active",
  "message": "License is active. 12 days remaining.",
  "is_active": true,
  "days_remaining": 12,
  "expires_at": "2025-12-10T10:30:00"
}
```

### Activate Trial

```bash
POST /api/license/activate-trial
{
  "temple_name": "Sri Krishna Temple",
  "contact_email": "contact@temple.com",
  "trial_days": 15
}
```

### Activate Full License

```bash
POST /api/license/activate-full
{
  "temple_name": "Sri Krishna Temple",
  "license_key": "XXXX-XXXX-XXXX-XXXX",
  "contact_email": "contact@temple.com"
}
```

### Extend Trial (Admin Only)

```bash
POST /api/license/extend-trial
{
  "additional_days": 5
}
```

---

## 🛡️ Security Features

### 1. **Tamper Protection**

- License file has checksum using SHA-256
- If user modifies dates → Checksum fails → License invalid
- Uses secret salt (configurable via environment variable)

### 2. **Cannot Bypass by Changing System Date**

- Dates stored in ISO format
- Even if user changes system date, license file has absolute dates
- Checksum prevents editing dates in license file

### 3. **Grace Period**

- 2-day grace period after expiry
- Prevents immediate lockout if expiry happens on weekend
- User sees warning during grace period

---

## 💻 Integration with Your App

### Backend Integration

**Option 1: Protect All Routes (Recommended)**

```python
# In app/main.py
from fastapi import Depends
from app.licensing.trial_validator import require_active_license

# Add dependency to all protected routes
@app.get("/api/donations", dependencies=[Depends(require_active_license)])
async def get_donations():
    # Your code here
    pass
```

**Option 2: Check on App Startup**

```python
# In app/main.py
from app.licensing import check_trial_status

@app.on_event("startup")
async def startup_event():
    """Check license on app startup"""
    status = check_trial_status()

    if not status.get("is_active"):
        print(f"⚠️  LICENSE WARNING: {status.get('message')}")
        # Optionally block startup
        # raise Exception("License expired")

    print(f"✅ License active: {status.get('message')}")
```

**Option 3: Manual Check**

```python
from app.licensing import is_trial_active

def some_function():
    if not is_trial_active():
        raise Exception("License expired")

    # Your code here
    pass
```

### Frontend Integration

```typescript
// Check license status on app load
async function checkLicense() {
  const response = await fetch('/api/license/status');
  const data = await response.json();

  if (!data.is_active) {
    // Show license expired modal
    showLicenseExpiredDialog(data.message);
    // Disable app functionality
    return false;
  }

  // Show warning if in grace period
  if (data.is_grace_period) {
    showGracePeriodWarning(data.grace_days_left);
  }

  return true;
}
```

---

## 📝 Common Scenarios

### Scenario 1: Temple Requests 15-Day Trial

```bash
# You run:
python manage_license.py create-trial "Lakshmi Temple" --days 15 --email info@lakshmitemple.org

# Output:
✅ Trial License Created Successfully!
Temple: Lakshmi Temple
Trial Days: 15
Expires: 2025-12-13T10:30:00
```

### Scenario 2: Trial Expires, Temple Wants to Continue

```bash
# Option A: Extend trial (temporary)
python manage_license.py extend-trial 5  # Add 5 more days

# Option B: Activate full license (permanent)
python manage_license.py activate-full "Lakshmi Temple" --key FULL-2025-XXXX
```

### Scenario 3: Temple Wants Longer Trial (30 Days)

```bash
# Before expiry, extend:
python manage_license.py extend-trial 15  # Extends current trial

# Or deactivate and create new:
python manage_license.py deactivate
python manage_license.py create-trial "Temple Name" --days 30
```

### Scenario 4: Check How Many Days Left

```bash
python manage_license.py status

# Output:
Status: active
Active: True
Message: License is active. 8 days remaining.
Days Remaining: 8
```

---

## 🎯 Best Practices

### For You (Vendor)

1. **Standard Trial**: 15 days is ideal
   - Long enough to evaluate
   - Short enough to encourage purchase

2. **Grace Period**: 2 days (already built-in)
   - Prevents lockout on weekends
   - Gives time to process payment

3. **Follow-up Emails**:
   - Day 10: "5 days left in trial"
   - Day 14: "1 day left, upgrade now"
   - Day 17: "Trial expired, contact us"

4. **License Key Format**:
   - Use format: `FULL-2025-XXXX-YYYY`
   - Store centrally for verification
   - Consider online activation (future)

### For Temple Users

1. **Backup License File**:
   - Location: `%APPDATA%/.mandirsync/license.dat`
   - Keep copy in safe place
   - Needed for reinstallation

2. **Contact Support Early**:
   - Don't wait until last day
   - Start purchase process at day 10

---

## 🔧 Customization

### Change Trial Duration

```python
# Default is 15 days, change to 30:
manager.create_trial_license(
    temple_name="Temple",
    trial_days=30  # Change this
)
```

### Change Grace Period

```python
# In license_manager.py, find:
grace_period_end = expiry_date + timedelta(days=2)

# Change to 5 days:
grace_period_end = expiry_date + timedelta(days=5)
```

### Change License File Location

```python
# In license_manager.py, change:
app_data = os.getenv("APPDATA") or os.path.expanduser("~/.mandirsync")

# To custom location:
app_data = "C:/MandirSync/License"  # Windows
app_data = "/opt/mandirsync/license"  # Linux
```

---

## 🐛 Troubleshooting

### Issue 1: "License file has been tampered with"

**Cause**: User tried to manually edit license file
**Solution**: Deactivate and create new license

```bash
python manage_license.py deactivate
python manage_license.py create-trial "Temple Name" --days 15
```

### Issue 2: "No license found"

**Cause**: License file deleted or moved
**Solution**: Create new license or restore from backup

```bash
# Check file location:
python manage_license.py info

# Create new:
python manage_license.py create-trial "Temple Name" --days 15
```

### Issue 3: Trial expired but should be active

**Cause**: System date changed
**Solution**: Extend trial or activate full license

```bash
python manage_license.py extend-trial 5
```

---

## 📊 License File Format

The license file (`license.dat`) contains:

```json
{
  "license": {
    "temple_name": "Sri Krishna Temple",
    "license_type": "trial",
    "status": "active",
    "created_at": "2025-11-28T10:00:00",
    "activated_at": "2025-11-28T10:00:00",
    "expires_at": "2025-12-13T10:00:00",
    "trial_days": 15,
    "contact_email": "contact@temple.com",
    "version": "1.0.0"
  },
  "checksum": "a1b2c3d4e5f6..."
}
```

**DO NOT** manually edit this file - checksum will fail!

---

## 🚀 Future Enhancements

### Online License Activation

```python
# Future: Validate license key with server
def validate_license_key(license_key):
    response = requests.post("https://licensing.mandirsync.com/validate", {
        "license_key": license_key
    })
    return response.json()["is_valid"]
```

### Hardware Locking

```python
# Future: Bind license to specific machine
import uuid

def get_machine_id():
    return uuid.getnode()  # MAC address
```

### Subscription Model

```python
# Future: Monthly/yearly subscriptions
manager.create_full_license(
    license_type=LicenseType.SUBSCRIPTION,
    expires_at="2026-11-28"  # 1 year from now
)
```

---

## 📞 Support

If you have questions about the license system:

1. Check this guide first
2. Run `python manage_license.py status` to debug
3. Check license file location: `python manage_license.py info`

---

**Last Updated**: 2025-11-28
**Version**: 1.0.0
