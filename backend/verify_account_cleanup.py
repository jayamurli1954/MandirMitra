"""Verify that all 4-digit and 0-prefixed account codes have been removed"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Check for any remaining accounts with 4-digit or 0-prefixed codes
    query = text("""
        SELECT COUNT(*) FROM accounts
        WHERE temple_id = 1
        AND (LENGTH(account_code) < 5 OR account_code LIKE '0%')
    """)
    result = db.execute(query)
    count = result.fetchone()[0]
    
    print("=" * 70)
    print("ACCOUNT CODE CLEANUP VERIFICATION")
    print("=" * 70)
    print()
    
    if count == 0:
        print("[SUCCESS] No accounts with 4-digit or 0-prefixed codes found.")
        print("All accounts now use 5-digit codes (without leading zeros).")
    else:
        print(f"[WARNING] Found {count} account(s) with invalid codes:")
        
        list_query = text("""
            SELECT account_code, account_name, is_active
            FROM accounts
            WHERE temple_id = 1
            AND (LENGTH(account_code) < 5 OR account_code LIKE '0%')
            ORDER BY account_code
        """)
        list_result = db.execute(list_query)
        for row in list_result:
            print(f"  - {row[0]} ({row[1]}) - Active: {row[2]}")
    
    print()
    
    # Show count of valid 5-digit accounts
    valid_query = text("""
        SELECT COUNT(*) FROM accounts
        WHERE temple_id = 1
        AND LENGTH(account_code) = 5
        AND account_code NOT LIKE '0%'
    """)
    valid_result = db.execute(valid_query)
    valid_count = valid_result.fetchone()[0]
    print(f"Valid 5-digit accounts: {valid_count}")
    
finally:
    db.close()




