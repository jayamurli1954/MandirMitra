# Simple Database Security Setup Guide
## For Small & Medium Temples

This guide explains how to set up the simple tampering detection system.

---

## ✅ What This System Does

1. **Creates a fingerprint (hash) for every transaction**
   - If someone changes a transaction, the fingerprint won't match
   - System detects this immediately on startup

2. **Saves all transactions to a separate file (`audit_log.txt`)**
   - Even if main database is tampered, this file has the truth
   - Simple text file - easy to read and verify

3. **Checks everything automatically when you start the application**
   - No manual work needed
   - Shows alert if tampering detected

---

## 📋 Setup Steps

### Step 1: Run Migration Script

Add the `integrity_hash` column to your database:

```bash
cd backend
python scripts/add_integrity_hash_column.py
```

**What it does:**
- Adds `integrity_hash` column to `journal_entries` table
- Creates index for faster checking
- Safe to run multiple times (won't duplicate column)

### Step 2: Restart Application

The system will automatically:
- Generate hashes for new transactions
- Check integrity on every startup
- Create `audit_log.txt` file automatically

### Step 3: Protect Audit Log File (Optional but Recommended)

**Windows:**
1. Find `audit_log.txt` file (in application directory)
2. Right-click → Properties
3. Check "Read-only" checkbox
4. Click OK

**Linux/Mac:**
```bash
chmod 444 audit_log.txt
```

**Why?** This prevents accidental deletion or modification of the audit log.

---

## 🔍 How It Works

### Normal Operation:

1. User creates transaction
2. System generates fingerprint (hash) for the transaction
3. Transaction saved to database with fingerprint
4. Transaction also written to `audit_log.txt`
5. Next transaction uses previous fingerprint → Creates unbreakable chain

### If Someone Tampers:

1. User modifies transaction in database
2. Fingerprint (hash) no longer matches
3. On next startup → System checks all fingerprints
4. System detects mismatch → Shows alert
5. Admin can check `audit_log.txt` to see original transaction

---

## 📊 What You'll See

### On Normal Startup:
```
============================================================
DATABASE INTEGRITY CHECK
============================================================
✅ Database integrity verified (25 transactions checked)
============================================================
```

### If Tampering Detected:
```
============================================================
DATABASE INTEGRITY CHECK
============================================================
🚨 SECURITY ALERT: DATABASE TAMPERING DETECTED!

Found 1 transaction(s) that have been modified:

  • Entry #JE/2024/0005 (ID: 12)
    Expected: abc123def4567890...
    Actual:   xyz789ghi0123456...

⚠️  This indicates unauthorized modification of financial data.
Please contact administrator immediately.
Check audit_log.txt file for original transaction details.
============================================================
```

---

## 📁 Audit Log File Format

The `audit_log.txt` file contains one line per transaction:

```
# Audit Log - Immutable Transaction Record
# Format: DATE|USER|ACTION|ENTRY_ID|ENTRY_NUMBER|AMOUNT|NARRATION|STATUS|HASH
# This file is append-only. Do not modify or delete entries.
# ======================================================================
2024-12-15 10:30:45|admin@temple.com|CREATED|1|JE/2024/0001|5000.00|Donation received|draft|abc123...
2024-12-15 11:15:20|clerk@temple.com|CREATED|2|JE/2024/0002|2000.00|Seva booking|draft|def456...
2024-12-15 14:20:10|admin@temple.com|POSTED|1|JE/2024/0001|5000.00|Donation received|posted|abc123...
```

**Fields:**
- `DATE`: When transaction was created/modified
- `USER`: Who created/modified it
- `ACTION`: CREATED, UPDATED, POSTED, CANCELLED
- `ENTRY_ID`: Database ID
- `ENTRY_NUMBER`: Entry number (e.g., JE/2024/0001)
- `AMOUNT`: Transaction amount
- `NARRATION`: Description
- `STATUS`: draft, posted, cancelled
- `HASH`: Integrity hash (fingerprint)

---

## 🛡️ What This Protects Against

✅ **Modifying transaction amounts** → Hash doesn't match  
✅ **Deleting transactions** → Missing entry in chain  
✅ **Changing dates** → Hash includes date, doesn't match  
✅ **Backdating transactions** → Hash includes timestamp  
✅ **Modifying user information** → Hash includes user ID  

---

## ⚠️ Limitations

**This system protects against:**
- Casual tampering (someone modifying database directly)
- Accidental changes
- Unauthorized modifications by staff

**This system does NOT protect against:**
- Advanced hackers with full system access (they could modify code too)
- Physical access to server with admin rights
- Database-level attacks (if attacker has database admin access)

**For stronger protection, consider:**
- Database encryption (SQLCipher)
- File system permissions
- Regular encrypted backups
- See `DATABASE_TAMPERING_PREVENTION.md` for advanced options

---

## 🔧 Troubleshooting

### "Column integrity_hash does not exist"
**Solution:** Run migration script:
```bash
python scripts/add_integrity_hash_column.py
```

### "Could not write to audit log"
**Solution:** Check file permissions. Make sure application has write access to directory.

### "Integrity check failed"
**Solution:** 
1. Check if database was modified manually
2. Review `audit_log.txt` for original transactions
3. Contact administrator

### "Audit log mismatch"
**Solution:**
- Some entries may have been deleted from audit log
- Check if file was modified manually
- Restore from backup if available

---

## 📞 Support

**For temple administrators:**

> "The system creates a fingerprint for every transaction. If someone tries to change anything, the fingerprint won't match and we'll know immediately. Also, every transaction is saved in a separate file (`audit_log.txt`) that can't be easily deleted. The system checks everything automatically when you start the application."

**Simple explanation:**
- Every transaction gets a unique fingerprint
- If someone changes a transaction, the fingerprint breaks
- System checks fingerprints on startup
- Separate file (`audit_log.txt`) keeps a backup of all transactions

---

## ✅ Summary

**What you get:**
- ✅ Simple setup (just run one script)
- ✅ Automatic detection (runs on startup)
- ✅ Immediate alert (shows message if tampering found)
- ✅ Separate audit log (survives database tampering)
- ✅ No complex configuration needed

**What temples need to do:**
- ✅ Run migration script once
- ✅ (Optional) Set audit log file to read-only
- ✅ (Optional) Review audit log monthly

**Protection level:**
- ✅ Prevents casual tampering
- ✅ Detects any modification immediately
- ✅ Provides audit trail for investigation
- ⚠️ Advanced hackers with full system access can still bypass (but they'd need to modify code too)

This is a **practical balance** between security and simplicity for small/medium temples.






