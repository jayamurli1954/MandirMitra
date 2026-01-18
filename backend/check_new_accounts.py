"""Quick script to check if new expense accounts exist"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    codes = ['52001', '52003', '53002']
    print("Checking new expense accounts:")
    print("-" * 50)
    
    for code in codes:
        query = text("""
            SELECT id, account_code, account_name, is_active
            FROM accounts
            WHERE temple_id = 1 AND account_code = :code
        """)
        result = db.execute(query, {"code": code})
        row = result.fetchone()
        
        if row:
            print(f"[OK] {code}: {row[2]} (ID: {row[0]}, Active: {row[3]})")
        else:
            print(f"[MISSING] {code}: NOT FOUND")
    print("-" * 50)
finally:
    db.close()

