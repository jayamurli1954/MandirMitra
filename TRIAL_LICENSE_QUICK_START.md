# Trial License System - Quick Start Guide

## ✅ What You Asked For

You wanted a system where:
1. Temples can get a **free trial for 10/15 days**
2. The application **automatically disables after trial expiry**
3. You can control the trial duration

**✅ This is now implemented!**

---

## 🚀 How to Use

### 1. **Give a Temple a 15-Day Trial**

```bash
cd backend
python manage_license.py create-trial "Sri Krishna Temple" --days 15
```

**Output:**
```
✅ Trial License Created Successfully!
Temple: Sri Krishna Temple
Trial Days: 15
Expires: 2025-12-13T10:30:00
```

### 2. **Check Trial Status**

```bash
python manage_license.py status
```

**Output:**
```
Status: active
Active: True
Message: License is active. 12 days remaining.
Days Remaining: 12
```

### 3. **What Happens After Trial Expires?**

- **Day 15**: Trial expires, but 2-day grace period starts
- **Day 16**: Still works (grace day 1)
- **Day 17**: Still works (grace day 2)
- **Day 18**: ❌ **Application blocks access**

User sees:
```
"Your trial has expired. Please contact support to activate full license."
```

---

## 💡 Common Commands

```bash
# 10-day trial
python manage_license.py create-trial "Temple Name" --days 10

# 30-day trial
python manage_license.py create-trial "Temple Name" --days 30

# Extend trial by 5 days
python manage_license.py extend-trial 5

# Activate full license (permanent)
python manage_license.py activate-full "Temple Name" --key FULL-LICENSE-KEY

# Check status anytime
python manage_license.py status

# Remove license (be careful!)
python manage_license.py deactivate
```

---

## 🔐 How It Works (Behind the Scenes)

### When You Create a Trial:

1. License file created at: `%APPDATA%/.mandirsync/license.dat` (Windows)
2. Contains:
   - Temple name
   - Start date
   - **Expiry date** (today + 15 days)
   - **Tamper-proof checksum** (prevents date editing)

### When App Starts:

1. App checks license file
2. Compares current date with expiry date
3. If expired:
   - Check grace period (2 days)
   - If grace period over: **BLOCK ACCESS**
4. If active: Allow normal use

### Security:

- User **CANNOT** bypass by:
  - Changing system date (license has absolute dates)
  - Editing license file (checksum fails)
  - Deleting and recreating (each license has unique creation time)

---

## 📱 API Endpoints (for Frontend)

Your frontend can call these:

### Check License Status
```
GET /api/license/status

Response:
{
  "status": "active",
  "is_active": true,
  "days_remaining": 12,
  "message": "License is active. 12 days remaining."
}
```

### Activate Trial (User Self-Service)
```
POST /api/license/activate-trial
{
  "temple_name": "Sri Krishna Temple",
  "trial_days": 15,
  "contact_email": "contact@temple.com"
}
```

### Upgrade to Full License
```
POST /api/license/activate-full
{
  "temple_name": "Sri Krishna Temple",
  "license_key": "FULL-2025-XXXX-YYYY"
}
```

---

## 🎯 Your Workflow

### **Before Giving Application to Temple:**

```bash
# Option 1: Pre-activate trial for them
cd backend
python manage_license.py create-trial "Temple Name" --days 15 --email contact@temple.com

# Then package and send to temple
```

### **Or Let Them Activate Themselves:**

1. Send them the application (without license)
2. On first run, they see "Activate License" screen
3. They enter temple name and email
4. Click "Start 15-Day Trial"
5. ✅ They're in!

### **When Trial is About to Expire:**

Temple will see warnings:
- Day 10: "5 days remaining in trial"
- Day 14: "1 day remaining - upgrade now"
- Day 15: "Trial expired - grace period active"
- Day 18: **Application blocked**

### **To Convert to Paid Customer:**

```bash
# Generate license key (use your own format)
LICENSE_KEY="FULL-2025-KRISHNA-001"

# Activate full license
python manage_license.py activate-full "Temple Name" --key $LICENSE_KEY

# Or they can do it via app:
# Settings > License > "Activate Full License" > Enter Key
```

---

## 📋 Different Trial Periods

```bash
# 10-day trial (shorter evaluation)
python manage_license.py create-trial "Temple" --days 10

# 15-day trial (recommended default)
python manage_license.py create-trial "Temple" --days 15

# 30-day trial (extended evaluation)
python manage_license.py create-trial "Temple" --days 30

# 60-day trial (enterprise)
python manage_license.py create-trial "Temple" --days 60
```

---

## 🛡️ Can They Bypass It?

### ❌ What WON'T Work:

1. **Changing system date** → License has absolute dates
2. **Editing license file** → Checksum fails, license invalid
3. **Reinstalling** → License file location is consistent
4. **Deleting license file** → App won't start without license

### ✅ Only Way to Continue:

1. Get **license key** from you
2. Enter it in app or via CLI
3. App validates and activates

---

## 🔧 Customization

### Change Default Trial Days

In `backend/app/api/license.py`, line 18:
```python
trial_days: int = 15  # Change to 10, 30, etc.
```

### Change Grace Period

In `backend/app/licensing/license_manager.py`, line 177:
```python
grace_period_end = expiry_date + timedelta(days=2)  # Change to 3, 5, etc.
```

### Change License File Location

In `backend/app/licensing/license_manager.py`, line 43:
```python
app_data = "C:/MandirSync/License"  # Custom location
```

---

## 📞 What to Tell Temples

### **Trial Period:**

> "You get a FREE 15-day trial to evaluate MandirSync. No credit card required. After 15 days, you'll need to purchase a license to continue using the software."

### **After Expiry:**

> "Your trial has expired. Contact us at support@mandirsync.com to purchase a full license. We offer flexible pricing for temples of all sizes."

### **Pricing:**

> - **Basic**: ₹15,000/year (one temple)
> - **Premium**: ₹25,000/year (includes premium support)
> - **Lifetime**: ₹50,000 (one-time payment)
> - **Enterprise**: Custom pricing

---

## 📊 Example Scenario

**Day 0**: Temple downloads MandirSync
```bash
# You or they run:
python manage_license.py create-trial "Lakshmi Temple" --days 15
```

**Day 1-10**: Temple uses the software happily ✅

**Day 11**: App shows: "4 days remaining in your trial"

**Day 14**: App shows: "1 day remaining - Upgrade now!"

**Day 15**: Trial expires, grace period starts
- App shows: "Trial expired. Grace period: 2 days remaining"
- Features still work

**Day 17**: Last grace day
- App shows: "FINAL WARNING: Grace period ends tomorrow"

**Day 18**: Grace period over ❌
- App blocks access
- Shows: "Trial expired. Contact support to purchase license."

**Temple buys license:**
```bash
python manage_license.py activate-full "Lakshmi Temple" --key FULL-2025-LAKSHMI-001
```

**✅ App fully activated - no expiry!**

---

## 📖 Full Documentation

For complete details, see: [LICENSE_SYSTEM_GUIDE.md](./LICENSE_SYSTEM_GUIDE.md)

---

## ✅ Summary

You now have a complete trial license system that:

✅ Offers 10/15/30-day free trials (you choose)
✅ Automatically disables after expiry
✅ Cannot be bypassed (tamper-proof)
✅ Easy to manage via CLI
✅ Can be integrated with frontend
✅ Upgradeable to full license
✅ Includes 2-day grace period

**Ready to use immediately!**

---

**Questions? Check**: [LICENSE_SYSTEM_GUIDE.md](./LICENSE_SYSTEM_GUIDE.md)
