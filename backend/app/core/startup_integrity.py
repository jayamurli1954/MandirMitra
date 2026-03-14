"""
Startup Integrity Check Module
Handles integrity checks on application startup.
"""

from app.core.database import SessionLocal
from app.core.integrity_check import verify_audit_log_integrity, verify_database_integrity


def _ascii_safe(value):
    return str(value).encode('ascii', 'backslashreplace').decode('ascii')


def run_startup_integrity_check():
    """
    Run integrity checks on application startup.
    Returns: (all_checks_passed: bool, messages: list)
    """
    messages = []
    all_passed = True

    db = SessionLocal()
    try:
        is_valid, message = verify_database_integrity(db)
        messages.append(("Database Integrity", is_valid, message))
        if not is_valid:
            all_passed = False

        audit_valid, audit_message = verify_audit_log_integrity(db)
        messages.append(("Audit Log Integrity", audit_valid, audit_message))
        if not audit_valid:
            all_passed = False

    except Exception as exc:
        messages.append(("Integrity Check Error", False, f"Error running integrity check: {str(exc)}"))
        all_passed = False
    finally:
        db.close()

    return all_passed, messages


def print_integrity_check_results(messages):
    """Print formatted integrity check results using ASCII-safe output."""
    print("\n" + "=" * 60)
    print("DATABASE INTEGRITY CHECK")
    print("=" * 60)

    for check_name, passed, message in messages:
        prefix = "[OK]" if passed else "[WARN]"
        print(f"{prefix} {_ascii_safe(check_name)}: {_ascii_safe(message)}")

    print("=" * 60 + "\n")

    for _check_name, passed, message in messages:
        if not passed and "TAMPERING DETECTED" in str(message).upper():
            print("CRITICAL SECURITY ALERT")
            print("Database tampering has been detected!")
            print("Application will continue, but please investigate immediately.")
            print("Check audit_log.txt file for original transaction details.\n")
            break
