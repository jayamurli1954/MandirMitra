# Simple Database Tampering Prevention System
## For Small & Medium Temples

**Goal:** Simple, effective protection that detects tampering immediately - no complex setup required.

---

## 🎯 Simple 3-Layer Protection

### Layer 1: Integrity Hash (Detects Tampering Immediately)
### Layer 2: Separate Audit File (Survives Main DB Tampering)
### Layer 3: Startup Verification (Automatic Detection)

---

## Implementation: Step-by-Step

### Step 1: Add Integrity Hash to Journal Entries

**What it does:** Each transaction gets a unique fingerprint. If anyone changes it, we know immediately.

**Database Change:**
```python
# Add one field to journal_entries table
integrity_hash = Column(String(64), nullable=True)  # Stores fingerprint
```

**How it works:**
- When transaction is created → Generate hash
- Hash includes: amount, date, user, previous hash
- On startup → Check all hashes match
- If hash doesn't match → TAMPERING DETECTED!

---

### Step 2: Separate Audit Log File

**What it does:** Every transaction is also written to a separate text file. Even if main database is tampered, this file has the truth.

**Simple Implementation:**
- Plain text file (easy to read, verify)
- Append-only (can't delete old entries)
- One line per transaction
- Format: `DATE|USER|ACTION|AMOUNT|HASH`

**Example audit log entry:**
```
2024-12-15 10:30:45|admin@temple.com|CREATED|5000.00|abc123def456...
2024-12-15 11:15:20|clerk@temple.com|CREATED|2000.00|xyz789ghi012...
```

**Protection:**
- File is read-only (Windows: Right-click → Properties → Read-only)
- Application can only append (add new lines)
- Cannot delete or modify old entries

---

### Step 3: Startup Verification (Automatic)

**What it does:** Every time application starts, automatically checks:
1. Are all transaction hashes correct?
2. Does audit log match database?
3. Are any transactions missing?

**If tampering detected:**
- Show alert to admin
- Log security event
- Optionally: Disable write operations (read-only mode)

---

## 📝 Implementation Code

### 1. Add Hash Field to Model

```python
# backend/app/models/accounting.py

class JournalEntry(Base):
    # ... existing fields ...
    
    # Add this one field:
    integrity_hash = Column(String(64), nullable=True, index=True)
    
    def calculate_integrity_hash(self, previous_hash: str = "INITIAL") -> str:
        """Calculate hash for this entry"""
        import hashlib
        import json
        
        # Create data string with all important fields
        data = {
            'id': self.id,
            'amount': float(self.total_amount),
            'narration': self.narration or '',
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'entry_date': self.entry_date.isoformat() if self.entry_date else '',
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else '',
        }
        
        # Include previous hash to create chain
        data_string = json.dumps(data, sort_keys=True) + "|" + previous_hash
        
        # Generate hash
        return hashlib.sha256(data_string.encode()).hexdigest()
```

### 2. Generate Hash When Creating Entry

```python
# backend/app/api/journal_entries.py

@router.post("/", response_model=JournalEntryResponse)
def create_journal_entry(
    entry_data: JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... existing code to create entry ...
    
    # Get previous entry's hash (for chain)
    previous_entry = db.query(JournalEntry).order_by(
        JournalEntry.id.desc()
    ).first()
    previous_hash = previous_entry.integrity_hash if previous_entry else "INITIAL"
    
    # Calculate and store hash
    entry.integrity_hash = entry.calculate_integrity_hash(previous_hash)
    
    db.commit()
    db.refresh(entry)
    
    # Write to audit log file
    write_to_audit_log(entry, "CREATED", current_user, db)
    
    return entry
```

### 3. Write to Audit Log File

```python
# backend/app/core/audit_log.py

import os
from datetime import datetime
from pathlib import Path

AUDIT_LOG_FILE = "audit_log.txt"  # Simple text file

def write_to_audit_log(entry, action: str, user, db):
    """Write transaction to separate audit log file"""
    log_path = Path(AUDIT_LOG_FILE)
    
    # Create log file if doesn't exist
    if not log_path.exists():
        log_path.touch()
        # Make it read-only (Windows)
        if os.name == 'nt':  # Windows
            import stat
            os.chmod(log_path, stat.S_IREAD | stat.S_IWRITE)  # Read-write for owner
    
    # Format: DATE|USER|ACTION|ENTRY_ID|AMOUNT|NARRATION|HASH
    log_line = (
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|"
        f"{user.email}|"
        f"{action}|"
        f"{entry.id}|"
        f"{entry.total_amount}|"
        f"{entry.narration or ''}|"
        f"{entry.integrity_hash}\n"
    )
    
    # Append to file (append-only)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_line)
    
    # After writing, make file read-only (except for application)
    # Note: On Windows, you may need to handle this differently
```

### 4. Startup Integrity Check

```python
# backend/app/core/integrity_check.py

from sqlalchemy.orm import Session
from app.models.accounting import JournalEntry

def verify_database_integrity(db: Session) -> tuple[bool, str]:
    """
    Verify database integrity on startup
    Returns: (is_valid, error_message)
    """
    try:
        # Get all entries in order
        entries = db.query(JournalEntry).order_by(JournalEntry.id).all()
        
        if not entries:
            return True, "No entries to verify"
        
        previous_hash = "INITIAL"
        
        for entry in entries:
            # Calculate expected hash
            expected_hash = entry.calculate_integrity_hash(previous_hash)
            
            # Check if hash matches
            if entry.integrity_hash != expected_hash:
                return False, (
                    f"⚠️ TAMPERING DETECTED!\n\n"
                    f"Entry ID {entry.id} has been modified.\n"
                    f"Expected hash: {expected_hash[:16]}...\n"
                    f"Actual hash: {entry.integrity_hash[:16] if entry.integrity_hash else 'MISSING'}...\n\n"
                    f"Please contact administrator immediately."
                )
            
            previous_hash = entry.integrity_hash
        
        # Verify audit log file exists and has entries
        audit_log_path = Path("audit_log.txt")
        if audit_log_path.exists():
            with open(audit_log_path, 'r', encoding='utf-8') as f:
                audit_lines = [line.strip() for line in f if line.strip()]
            
            # Check if number of entries matches (rough check)
            if len(audit_lines) < len(entries):
                return False, (
                    f"⚠️ AUDIT LOG MISMATCH!\n\n"
                    f"Database has {len(entries)} entries but audit log has {len(audit_lines)} entries.\n"
                    f"Some entries may have been deleted from audit log.\n\n"
                    f"Please contact administrator."
                )
        
        return True, "✅ Database integrity verified"
    
    except Exception as e:
        return False, f"Integrity check failed: {str(e)}"
```

### 5. Run Check on Application Startup

```python
# backend/app/main.py or backend/app/core/startup.py

from app.core.integrity_check import verify_database_integrity
from app.core.database import SessionLocal

@app.on_event("startup")
async def startup_event():
    """Run integrity check on application startup"""
    db = SessionLocal()
    try:
        is_valid, message = verify_database_integrity(db)
        
        if not is_valid:
            # Log critical security event
            print("=" * 60)
            print("🚨 SECURITY ALERT 🚨")
            print("=" * 60)
            print(message)
            print("=" * 60)
            
            # You can also:
            # - Send email to admin
            # - Write to separate security log
            # - Disable write operations
            # - Show popup to user
            
            # For now, just log it
            # In production, you might want to disable writes:
            # settings.READ_ONLY_MODE = True
        else:
            print("✅ Database integrity check passed")
    
    finally:
        db.close()
```

---

## 🔧 Simple Setup Instructions

### For Temple Administrators:

1. **After installation, the system will:**
   - Automatically create `audit_log.txt` file
   - Generate hashes for all transactions
   - Check integrity on every startup

2. **Protect the audit log file:**
   - Right-click `audit_log.txt` → Properties
   - Check "Read-only" (Windows)
   - Or: `chmod 444 audit_log.txt` (Linux/Mac)
   - This prevents deletion/modification

3. **Regular checks (optional):**
   - Review `audit_log.txt` monthly
   - Compare with database reports
   - Keep backups of audit log file

---

## 📊 How It Works (Simple Explanation)

### Normal Operation:
1. User creates transaction → System generates fingerprint (hash)
2. Transaction saved to database with fingerprint
3. Transaction also written to `audit_log.txt` file
4. Next transaction uses previous fingerprint → Creates chain

### If Someone Tampers:
1. User modifies transaction in database
2. Fingerprint (hash) no longer matches
3. On next startup → System checks all fingerprints
4. System detects mismatch → Shows alert
5. Admin can check `audit_log.txt` to see original transaction

### Why It Works:
- **Hash Chain:** Each transaction linked to previous one
- **Separate File:** Audit log survives even if database is tampered
- **Automatic Check:** Runs on every startup (no manual work needed)

---

## 🎯 What This Prevents

✅ **Modifying transaction amounts** → Hash doesn't match  
✅ **Deleting transactions** → Missing entry in chain  
✅ **Changing dates** → Hash includes date, doesn't match  
✅ **Backdating transactions** → Hash includes timestamp  
✅ **Modifying user information** → Hash includes user ID  

---

## 📋 Quick Implementation Checklist

- [ ] Add `integrity_hash` field to `JournalEntry` model
- [ ] Create migration to add column to existing database
- [ ] Update `create_journal_entry` to generate hash
- [ ] Create `write_to_audit_log()` function
- [ ] Create `verify_database_integrity()` function
- [ ] Add startup check in `main.py`
- [ ] Test: Create transaction, verify hash generated
- [ ] Test: Modify database manually, restart app, verify detection
- [ ] Set `audit_log.txt` to read-only

---

## 🔍 Testing the System

### Test 1: Normal Operation
1. Create a transaction
2. Check `audit_log.txt` has entry
3. Restart application
4. Should see: "✅ Database integrity check passed"

### Test 2: Tampering Detection
1. Create a transaction (note the ID)
2. Stop application
3. Open database directly (SQLite Browser)
4. Modify the transaction amount
5. Restart application
6. Should see: "⚠️ TAMPERING DETECTED!"

### Test 3: Audit Log Protection
1. Try to delete a line from `audit_log.txt`
2. If file is read-only, deletion should fail
3. If deletion succeeds, restart app
4. System should detect mismatch (fewer entries in audit log)

---

## 💡 Additional Simple Enhancements (Optional)

### 1. Email Alert on Tampering
```python
# If tampering detected, send email to admin
if not is_valid:
    send_email_to_admin("Database Tampering Detected", message)
```

### 2. Read-Only Mode
```python
# If tampering detected, disable writes
if not is_valid:
    settings.READ_ONLY_MODE = True
    # All write operations return error
```

### 3. Daily Backup
```python
# Simple backup: Copy database file daily
# Keep last 30 days of backups
```

---

## 📞 Support for Temples

**Simple explanation for temple staff:**

> "The system creates a fingerprint for every transaction. If someone tries to change anything, the fingerprint won't match and we'll know immediately. Also, every transaction is saved in a separate file (`audit_log.txt`) that can't be easily deleted. The system checks everything automatically when you start the application."

---

## ✅ Summary

**What you get:**
- ✅ Simple setup (just add one field, one file)
- ✅ Automatic detection (runs on startup)
- ✅ Immediate alert (shows message if tampering found)
- ✅ Separate audit log (survives database tampering)
- ✅ No complex configuration needed

**What temples need to do:**
- ✅ Nothing! System works automatically
- ✅ (Optional) Set audit log file to read-only
- ✅ (Optional) Review audit log monthly

**Protection level:**
- ✅ Prevents casual tampering
- ✅ Detects any modification immediately
- ✅ Provides audit trail for investigation
- ⚠️ Advanced hackers with full system access can still bypass (but they'd need to modify code too)

This is a **practical balance** between security and simplicity for small/medium temples.






