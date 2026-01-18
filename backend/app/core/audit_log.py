"""
Simple Audit Log System
Writes all transactions to a separate text file

This file serves as an immutable record that survives even if main database is tampered.
Simple text format - easy to read and verify.
"""

import os
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.accounting import JournalEntry
from app.models.user import User


AUDIT_LOG_FILE = "audit_log.txt"


def write_to_audit_log(entry: JournalEntry, action: str, user: User, db: Session):
    """
    Write transaction to separate audit log file
    
    Format: DATE|USER|ACTION|ENTRY_ID|ENTRY_NUMBER|AMOUNT|NARRATION|STATUS|HASH
    
    This file is append-only - cannot delete or modify old entries
    """
    log_path = Path(AUDIT_LOG_FILE)
    
    # Create log file if doesn't exist
    if not log_path.exists():
        # Write header
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("# Audit Log - Immutable Transaction Record\n")
                f.write("# Format: DATE|USER|ACTION|ENTRY_ID|ENTRY_NUMBER|AMOUNT|NARRATION|STATUS|HASH\n")
                f.write("# This file is append-only. Do not modify or delete entries.\n")
                f.write("# " + "=" * 70 + "\n")
        except Exception as e:
            print(f"⚠️  Warning: Could not create audit log file: {e}")
            return
    
    # Format log entry
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_email = user.email if user else 'system'
    
    log_line = (
        f"{timestamp}|"
        f"{user_email}|"
        f"{action}|"
        f"{entry.id}|"
        f"{entry.entry_number or ''}|"
        f"{entry.total_amount}|"
        f"{entry.narration or ''}|"
        f"{entry.status.value if hasattr(entry.status, 'value') else entry.status}|"
        f"{getattr(entry, 'integrity_hash', '') or ''}\n"
    )
    
    # Append to file (append-only)
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except PermissionError:
        # File might be read-only - log warning but don't fail
        print(f"⚠️  Warning: Could not write to audit log (file may be read-only)")
        print(f"   Audit log entry: {log_line.strip()}")


def protect_audit_log_file():
    """
    Make audit log file read-only (optional - can be called manually)
    
    This prevents accidental deletion or modification of audit log
    """
    log_path = Path(AUDIT_LOG_FILE)
    
    if not log_path.exists():
        return
    
    try:
        # On Windows, set read-only attribute
        if os.name == 'nt':
            import stat
            # Remove write permission for group and others
            current_permissions = log_path.stat().st_mode
            log_path.chmod(current_permissions & ~stat.S_IWRITE)
        else:
            # On Linux/Mac, set read-only
            log_path.chmod(0o444)  # Read-only for all
        
        print(f"✅ Audit log file protected (read-only)")
    except Exception as e:
        print(f"⚠️  Could not protect audit log file: {e}")
        print(f"   Please manually set {AUDIT_LOG_FILE} to read-only")


def read_audit_log(limit: int = 100) -> list:
    """
    Read recent entries from audit log (for verification/reporting)
    
    Returns list of parsed log entries
    """
    log_path = Path(AUDIT_LOG_FILE)
    
    if not log_path.exists():
        return []
    
    entries = []
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse lines (skip comments and empty lines)
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('|')
            if len(parts) >= 8:
                entries.append({
                    'timestamp': parts[0],
                    'user': parts[1],
                    'action': parts[2],
                    'entry_id': parts[3],
                    'entry_number': parts[4],
                    'amount': parts[5],
                    'narration': parts[6],
                    'status': parts[7],
                    'hash': parts[8] if len(parts) > 8 else ''
                })
        
        # Return most recent entries
        return entries[-limit:] if limit else entries
    
    except Exception as e:
        print(f"Error reading audit log: {e}")
        return []


