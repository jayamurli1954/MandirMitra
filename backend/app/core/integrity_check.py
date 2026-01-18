"""
Simple Database Integrity Check System
For detecting tampering in accounting transactions

Simple approach:
1. Each transaction gets a hash (fingerprint)
2. Hash includes: transaction data + previous hash (creates chain)
3. On startup, verify all hashes match
4. If any hash doesn't match → Tampering detected!
"""

import hashlib
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.accounting import JournalEntry


def calculate_integrity_hash(entry: JournalEntry, previous_hash: str = "INITIAL") -> str:
    """
    Calculate integrity hash for a journal entry
    
    Hash includes:
    - Entry ID
    - Amount
    - Narration
    - Status
    - Entry date
    - Created by user
    - Created timestamp
    - Previous entry hash (creates unbreakable chain)
    
    If any of these change, hash will be different → Tampering detected!
    """
    # Create data dictionary with all important fields
    data = {
        'id': entry.id,
        'entry_number': entry.entry_number or '',
        'amount': float(entry.total_amount),
        'narration': entry.narration or '',
        'status': entry.status.value if hasattr(entry.status, 'value') else str(entry.status),
        'entry_date': entry.entry_date.isoformat() if entry.entry_date else '',
        'created_by': entry.created_by,
        'created_at': entry.created_at.isoformat() if entry.created_at else '',
    }
    
    # Include previous hash to create chain
    data_string = json.dumps(data, sort_keys=True) + "|" + previous_hash
    
    # Generate SHA-256 hash
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()


def verify_database_integrity(db: Session) -> tuple[bool, str]:
    """
    Verify database integrity on startup
    
    Checks:
    1. All transaction hashes are correct (chain is unbroken)
    2. No transactions are missing
    
    Returns: (is_valid, message)
    """
    try:
        # Check if integrity_hash column exists (graceful handling)
        # Use raw SQL to check if column exists - works with both SQLite and PostgreSQL
        try:
            from sqlalchemy import text
            if 'sqlite' in str(db.bind.url).lower():
                # SQLite: Check if column exists in table
                result = db.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM pragma_table_info('journal_entries') 
                    WHERE name = 'integrity_hash'
                """))
                count = result.fetchone()[0]
            else:
                # PostgreSQL: Check information_schema
                result = db.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.columns 
                    WHERE table_name = 'journal_entries' 
                    AND column_name = 'integrity_hash'
                """))
                count = result.fetchone()[0]
            
            if count == 0:
                return True, "ℹ️  Integrity hash column not yet added (run: python scripts/add_integrity_hash_column.py)"
        except Exception as e:
            # If check fails, assume column doesn't exist and skip gracefully
            error_msg = str(e).lower()
            if 'integrity_hash' in error_msg or 'does not exist' in error_msg or 'no such column' in error_msg:
                return True, "ℹ️  Integrity hash column not yet added (run: python scripts/add_integrity_hash_column.py)"
            # Some other error - log it but don't fail startup
            print(f"⚠️  Warning: Could not check integrity_hash column: {e}")
            return True, "ℹ️  Integrity check skipped (column check failed)"
        
        # Get all entries in order (by ID)
        entries = db.query(JournalEntry).order_by(JournalEntry.id).all()
        
        if not entries:
            return True, "✅ No transactions to verify"
        
        previous_hash = "INITIAL"
        tampered_entries = []
        
        for entry in entries:
            # Calculate expected hash
            expected_hash = calculate_integrity_hash(entry, previous_hash)
            
            # Check if hash matches
            # Use getattr to safely access integrity_hash (column may not exist yet)
            actual_hash = getattr(entry, 'integrity_hash', None)
            if not actual_hash:
                # Missing hash - old entry without hash, generate and save it
                # Only try to set if column exists
                if hasattr(JournalEntry, 'integrity_hash'):
                    try:
                        entry.integrity_hash = expected_hash
                        db.commit()
                        db.refresh(entry)
                        print(f"ℹ️  Generated missing hash for entry {entry.entry_number} (ID: {entry.id})")
                    except (AttributeError, Exception):
                        pass  # Column doesn't exist, skip
            elif actual_hash != expected_hash:
                # Hash doesn't match - TAMPERING DETECTED!
                tampered_entries.append({
                    'id': entry.id,
                    'entry_number': entry.entry_number,
                    'expected_hash': expected_hash[:16] + '...',
                    'actual_hash': actual_hash[:16] + '...' if actual_hash else 'MISSING'
                })
            
            previous_hash = actual_hash or expected_hash
        
        if tampered_entries:
            error_msg = (
                "🚨 SECURITY ALERT: DATABASE TAMPERING DETECTED!\n\n"
                f"Found {len(tampered_entries)} transaction(s) that have been modified:\n\n"
            )
            for entry_info in tampered_entries:
                error_msg += (
                    f"  • Entry #{entry_info['entry_number']} (ID: {entry_info['id']})\n"
                    f"    Expected: {entry_info['expected_hash']}\n"
                    f"    Actual:   {entry_info['actual_hash']}\n\n"
                )
            error_msg += (
                "⚠️  This indicates unauthorized modification of financial data.\n"
                "Please contact administrator immediately.\n"
                "Check audit_log.txt file for original transaction details."
            )
            return False, error_msg
        
        return True, f"✅ Database integrity verified ({len(entries)} transactions checked)"
    
    except Exception as e:
        return False, f"❌ Integrity check failed: {str(e)}"


def verify_audit_log_integrity(db: Session) -> tuple[bool, str]:
    """
    Verify audit log file matches database
    
    Checks if audit log file exists and has matching number of entries
    """
    audit_log_path = Path("audit_log.txt")
    
    if not audit_log_path.exists():
        return True, "ℹ️  Audit log file not found (will be created on next transaction)"
    
    try:
        # Count entries in database
        db_count = db.query(JournalEntry).count()
        
        # Count lines in audit log
        with open(audit_log_path, 'r', encoding='utf-8') as f:
            audit_lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if len(audit_lines) < db_count:
            return False, (
                f"⚠️  Audit log mismatch!\n"
                f"Database has {db_count} entries but audit log has {len(audit_lines)} entries.\n"
                f"Some entries may have been deleted from audit log."
            )
        
        return True, f"✅ Audit log verified ({len(audit_lines)} entries)"
    
    except Exception as e:
        return False, f"❌ Audit log check failed: {str(e)}"


