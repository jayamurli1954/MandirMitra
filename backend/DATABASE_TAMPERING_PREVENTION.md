# Database Tampering Prevention - Practical Solutions

## Threat Analysis

**Scenario:** A user with technical knowledge could:
1. Stop the application
2. Directly access the database file (SQLite) or database server
3. Modify/delete records to hide fraudulent transactions
4. Restart the application with tampered data

**Risk Level:** HIGH - Especially for SQLite (single file database)

---

## Multi-Layer Defense Strategy

### Layer 1: Database Encryption (First Line of Defense)

#### For SQLite: SQLCipher Encryption

**Implementation:**
- Use SQLCipher extension (encrypted SQLite)
- Database file is encrypted at rest
- Requires passphrase to access (stored separately, not in code)

**How it works:**
- Database file is encrypted using AES-256
- Cannot be read without the passphrase
- Even if someone accesses the file, they cannot read it

**Python Implementation:**
```python
# Install: pip install pysqlcipher3
# Or use: apsw with SQLCipher extension

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Encrypted SQLite connection
DATABASE_URL = f"sqlite+pysqlcipher://:{passphrase}@/{db_path}?kdf_iter=64000"

# Passphrase should be:
# 1. Stored in environment variable (not in code)
# 2. Or stored in encrypted config file
# 3. Or entered by admin at startup (most secure)
```

**Pros:**
- ✅ Strong encryption (AES-256)
- ✅ Database file is unreadable without passphrase
- ✅ Transparent to application code

**Cons:**
- ⚠️ If passphrase is compromised, encryption is useless
- ⚠️ Requires SQLCipher library installation

---

### Layer 2: Checksums & Data Integrity (Detection)

#### A. Transaction Hash Chain

**Concept:** Each transaction creates a hash that includes:
- Previous transaction hash
- Current transaction data
- Timestamp
- User ID

**If any transaction is modified, the chain breaks and is detectable.**

**Implementation:**

```python
import hashlib
import hmac

class TransactionHashChain:
    """
    Creates an unbroken chain of hashes for all transactions
    If any transaction is tampered, the chain breaks
    """
    
    @staticmethod
    def generate_hash(entry_id, entry_data, previous_hash, user_id, timestamp):
        """Generate hash for a journal entry"""
        data_string = f"{entry_id}|{entry_data}|{previous_hash}|{user_id}|{timestamp}"
        secret_key = os.getenv("HASH_SECRET_KEY")  # Secret key stored separately
        return hmac.new(
            secret_key.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_chain(db: Session):
        """Verify integrity of all transactions"""
        entries = db.query(JournalEntry).order_by(JournalEntry.id).all()
        previous_hash = "INITIAL_HASH"
        
        for entry in entries:
            expected_hash = TransactionHashChain.generate_hash(
                entry.id,
                json.dumps({
                    'amount': entry.total_amount,
                    'narration': entry.narration,
                    'status': entry.status
                }),
                previous_hash,
                entry.created_by,
                entry.created_at.isoformat()
            )
            
            if entry.transaction_hash != expected_hash:
                return False, entry.id  # Tampering detected!
            
            previous_hash = entry.transaction_hash
        
        return True, None
```

**Database Schema Addition:**
```python
class JournalEntry(Base):
    # ... existing fields ...
    transaction_hash = Column(String(64), nullable=False, unique=True, index=True)
    previous_entry_hash = Column(String(64), nullable=True)  # Links to previous entry
```

#### B. Periodic Integrity Checks

**Automated Verification:**
- Run integrity checks periodically (every hour, or on startup)
- If tampering detected: Alert admin, disable write operations, create alert log

**Implementation:**
```python
def verify_database_integrity(db: Session) -> tuple[bool, str]:
    """
    Verify database integrity
    Returns: (is_valid, error_message)
    """
    try:
        # Check 1: Verify hash chain
        is_valid, tampered_entry_id = TransactionHashChain.verify_chain(db)
        if not is_valid:
            return False, f"Transaction hash chain broken at entry ID: {tampered_entry_id}"
        
        # Check 2: Verify audit log integrity
        audit_logs = db.query(AccountingAuditLog).all()
        for log in audit_logs:
            # Verify log hasn't been deleted (count check)
            # Verify log entries match journal entries
            pass
        
        # Check 3: Verify account balances match transactions
        # (Sum of all journal lines should match account balances)
        accounts = db.query(Account).all()
        for account in accounts:
            expected_balance = calculate_balance_from_journal_lines(account.id, db)
            if abs(account.balance - expected_balance) > 0.01:
                return False, f"Account {account.account_code} balance mismatch"
        
        return True, "Database integrity verified"
    except Exception as e:
        return False, f"Integrity check failed: {str(e)}"
```

---

### Layer 3: Separate Audit Database (Immutable Log)

#### Concept: Write-Only Audit Log in Separate Database

**Architecture:**
1. **Main Database:** Normal operations (SQLite/PostgreSQL)
2. **Audit Database:** Separate file/database for audit logs only
   - Write-only access from application
   - Read-only for reports
   - Cannot be modified/deleted by application

**Implementation:**

```python
# Separate audit database
AUDIT_DB_PATH = "audit_logs.db"  # Separate file
AUDIT_DB_ENCRYPTED = True  # Encrypted audit database

# Audit database connection (separate engine)
audit_engine = create_engine(
    f"sqlite+pysqlcipher://:{audit_passphrase}@/{AUDIT_DB_PATH}?kdf_iter=64000",
    connect_args={'check_same_thread': False}
)

# Create audit log in separate database
def create_audit_log_in_separate_db(action_data):
    """
    Write audit log to separate, encrypted database
    This database is append-only (no UPDATE/DELETE operations)
    """
    # Use raw SQL to prevent ORM from allowing updates/deletes
    with audit_engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO audit_logs (entity_type, entity_id, action, user_id, timestamp, data)
            VALUES (:entity_type, :entity_id, :action, :user_id, :timestamp, :data)
        """), action_data)
        conn.commit()
```

**Database Schema (Audit DB):**
```sql
-- Audit database only has INSERT capability (no UPDATE/DELETE)
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    data TEXT NOT NULL,  -- JSON string of full entry
    hash TEXT NOT NULL,  -- Hash of the data
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create index for performance
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
```

**Protection:**
- Audit database file permissions: Read-only for all except application
- Application only allows INSERT operations
- Database-level trigger to prevent UPDATE/DELETE (if supported)

---

### Layer 4: External Backup & Verification

#### A. Automated Encrypted Backups

**Strategy:**
- Daily automated backups to separate location (external drive, cloud, etc.)
- Backups are encrypted
- Backup includes both main DB and audit DB
- Backups cannot be overwritten (append-only or versioned)

**Implementation:**
```python
import shutil
from cryptography.fernet import Fernet
from datetime import datetime

def create_encrypted_backup():
    """Create encrypted backup of database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy database files
    main_db_backup = f"{backup_dir}/main_db_{timestamp}.db"
    audit_db_backup = f"{backup_dir}/audit_db_{timestamp}.db"
    
    shutil.copy2("MandirMitra.db", main_db_backup)
    shutil.copy2("audit_logs.db", audit_db_backup)
    
    # Encrypt backup files
    key = Fernet.generate_key()
    fernet = Fernet(key)
    
    with open(main_db_backup, 'rb') as f:
        encrypted = fernet.encrypt(f.read())
    
    with open(f"{main_db_backup}.enc", 'wb') as f:
        f.write(encrypted)
    
    # Store encryption key separately (not with backup)
    save_encryption_key(timestamp, key)
    
    # Delete unencrypted backup
    os.remove(main_db_backup)
```

#### B. Backup Verification

**Periodic Verification:**
- Compare current database with recent backups
- Detect any discrepancies
- Alert if tampering detected

---

### Layer 5: Application-Level Controls

#### A. Checksums on Critical Tables

**Implementation:**
```python
class TableIntegrityCheck:
    """Store checksums of critical tables"""
    
    @staticmethod
    def calculate_table_hash(db: Session, table_name: str) -> str:
        """Calculate hash of entire table"""
        # Get all rows, sort by ID, hash the content
        if table_name == 'journal_entries':
            entries = db.query(JournalEntry).order_by(JournalEntry.id).all()
            data = json.dumps([{
                'id': e.id,
                'amount': e.total_amount,
                'narration': e.narration,
                'status': e.status,
                'created_at': e.created_at.isoformat()
            } for e in entries])
        else:
            # Handle other tables
            pass
        
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def verify_table_integrity(db: Session):
        """Verify all critical tables"""
        critical_tables = ['journal_entries', 'journal_lines', 'accounts']
        
        for table in critical_tables:
            current_hash = TableIntegrityCheck.calculate_table_hash(db, table)
            stored_hash = db.query(IntegrityCheck).filter_by(
                table_name=table
            ).order_by(IntegrityCheck.check_date.desc()).first()
            
            if stored_hash and stored_hash.table_hash != current_hash:
                raise SecurityError(f"Table {table} integrity check failed - possible tampering!")
            
            # Store new hash
            integrity_check = IntegrityCheck(
                table_name=table,
                table_hash=current_hash,
                check_date=datetime.utcnow()
            )
            db.add(integrity_check)
            db.commit()
```

**Database Schema:**
```python
class IntegrityCheck(Base):
    """Store integrity check results"""
    __tablename__ = "integrity_checks"
    
    id = Column(Integer, primary_key=True)
    table_name = Column(String(50), nullable=False)
    table_hash = Column(String(64), nullable=False)
    check_date = Column(DateTime, default=datetime.utcnow)
```

---

### Layer 6: Database-Level Protection

#### A. Database Triggers (PostgreSQL)

**For PostgreSQL, use triggers to prevent unauthorized modifications:**

```sql
-- Create function to check if modification is allowed
CREATE OR REPLACE FUNCTION prevent_unauthorized_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if modification is happening through application (has session variable)
    IF current_setting('app.session_id', true) IS NULL THEN
        RAISE EXCEPTION 'Direct database modification not allowed. Use application interface.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to critical tables
CREATE TRIGGER journal_entries_protect
    BEFORE UPDATE OR DELETE ON journal_entries
    FOR EACH ROW
    EXECUTE FUNCTION prevent_unauthorized_modification();

CREATE TRIGGER audit_logs_protect
    BEFORE UPDATE OR DELETE ON accounting_audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_unauthorized_modification();
```

**Application sets session variable:**
```python
# In application connection
db.execute(text("SET app.session_id = :session_id"), {"session_id": session_id})
```

#### B. Read-Only Users (PostgreSQL)

**Create separate database users:**
- `MandirMitra_app`: Read-write access (application uses this)
- `MandirMitra_readonly`: Read-only access (for reports)
- `MandirMitra_backup`: Read-only access (for backups)

**Prevent direct access to application user credentials.**

---

### Layer 7: File System Protection (SQLite)

#### A. File Permissions

**Windows:**
- Database file: Read-write for application user only
- Audit database: Read-write for application user, read-only for others
- Backup directory: Write-only for application, read-only for admin

**Linux/Mac:**
```bash
# Set file permissions
chmod 600 MandirMitra.db  # Read-write for owner only
chmod 400 audit_logs.db  # Read-only for all (except application)
chmod 700 backups/       # Directory accessible only by owner
```

#### B. Hidden Database Location

**Store database in protected location:**
- Not in user-accessible folder
- Protected system directory
- Or encrypted volume

---

## Recommended Implementation Plan

### Phase 1: Quick Wins (High Impact, Low Effort)

1. **Separate Audit Database** (Highest Priority)
   - Create separate audit database file
   - Write-only access from application
   - Cannot be modified/deleted
   - **Impact:** Even if main DB is tampered, audit log remains intact

2. **Transaction Hash Chain**
   - Add hash field to journal entries
   - Generate hash on creation
   - Verify on startup/periodically
   - **Impact:** Detects any tampering immediately

3. **Integrity Checks on Startup**
   - Run integrity verification when application starts
   - Compare account balances with transaction sums
   - Alert if mismatch
   - **Impact:** Detects tampering when system starts

### Phase 2: Enhanced Security (Medium Effort)

4. **Database Encryption (SQLCipher)**
   - Encrypt database file
   - Passphrase stored separately (or entered at startup)
   - **Impact:** Database file is unreadable without passphrase

5. **Automated Encrypted Backups**
   - Daily backups to external location
   - Encrypted backup files
   - **Impact:** Can restore to known-good state if tampering detected

### Phase 3: Advanced Protection (Higher Effort)

6. **Database Triggers (PostgreSQL)**
   - Prevent direct database modifications
   - **Impact:** Blocks unauthorized access attempts

7. **File System Protection**
   - Restrict file permissions
   - Hidden/protected database location
   - **Impact:** Makes database file harder to access

---

## Practical Recommendation for Your Use Case

**For SQLite Desktop Application:**

### Immediate Implementation (Week 1):

1. **Separate Audit Database** ⭐ **HIGHEST PRIORITY**
   ```python
   # Create separate audit database
   # Application writes to both main DB and audit DB
   # Audit DB is append-only (no updates/deletes)
   # Audit DB is encrypted
   ```

2. **Transaction Hash Chain**
   ```python
   # Each journal entry gets a hash
   # Hash includes: entry data + previous entry hash
   # On startup, verify all hashes match
   # Alert if chain is broken
   ```

3. **Startup Integrity Check**
   ```python
   # On application start:
   # - Verify hash chain
   # - Verify account balances match transactions
   # - Compare with last known good state
   # - Alert if tampering detected
   ```

### Short-term (Week 2-3):

4. **SQLCipher Encryption**
   ```python
   # Encrypt main database file
   # Passphrase entered by admin at startup (or from secure config)
   # Database unreadable without passphrase
   ```

5. **Automated Backups**
   ```python
   # Daily encrypted backups
   # Store in separate location (external drive, cloud)
   # Versioned backups (don't overwrite)
   ```

---

## Detection vs Prevention

**Important Distinction:**
- **Prevention:** Make tampering difficult (encryption, file permissions)
- **Detection:** Identify tampering when it occurs (hash chains, integrity checks)

**Best Strategy:** Combine both
- Make it difficult to tamper (encryption, permissions)
- Detect tampering if it occurs (hash chains, audit logs)
- Have recovery mechanism (backups, separate audit DB)

---

## Testing Tampering Prevention

### Test Scenarios:

1. **Direct Database Modification:**
   - Stop application
   - Modify database file directly
   - Restart application
   - **Expected:** Integrity check detects tampering, alerts admin

2. **Deleting Audit Logs:**
   - Attempt to delete from audit database
   - **Expected:** Separate audit DB prevents deletion, or application detects missing logs

3. **Modifying Transaction Amount:**
   - Change amount in journal entry
   - **Expected:** Hash chain breaks, integrity check fails

4. **Backdating Transactions:**
   - Modify transaction date
   - **Expected:** Hash includes timestamp, chain breaks

---

## Alert Mechanisms

When tampering is detected:

1. **Immediate Actions:**
   - Log security event to separate audit file
   - Disable write operations (read-only mode)
   - Alert admin (popup, email, SMS)
   - Create forensic log with details

2. **Admin Actions:**
   - Review audit logs
   - Compare with backups
   - Identify what was changed
   - Restore from backup if needed
   - Investigate who had access

---

## Summary: Best Practice for Your System

**Recommended Approach (SQLite Desktop App):**

1. ✅ **Separate Encrypted Audit Database** - Immutable log, separate file
2. ✅ **Transaction Hash Chain** - Detect any modifications
3. ✅ **Startup Integrity Checks** - Verify on every startup
4. ✅ **SQLCipher Encryption** - Encrypt main database
5. ✅ **Automated Encrypted Backups** - Daily backups, versioned
6. ✅ **File Permissions** - Restrict database file access

**With these measures:**
- ✅ Tampering is **difficult** (encryption, permissions)
- ✅ Tampering is **detectable** (hash chains, integrity checks)
- ✅ Tampering is **recoverable** (backups, audit logs)
- ✅ Tampering is **traceable** (audit database, logs)

**Most Important:** Separate audit database ensures that even if main database is compromised, the audit trail remains intact and can be used for investigation and recovery.







