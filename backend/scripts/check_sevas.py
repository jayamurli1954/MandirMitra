"""
Check all sevas in database
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from sqlalchemy import text

def check_sevas():
    """Check all sevas in database"""
    db = SessionLocal()
    try:
        # Get all sevas
        query = text("SELECT id, name_english, name_kannada, amount FROM sevas ORDER BY id")
        result = db.execute(query)
        sevas = result.fetchall()
        
        if not sevas:
            print("No sevas found in database.")
            return
        
        print(f"Found {len(sevas)} seva(s) in database:\n")
        for row in sevas:
            print(f"ID: {row[0]}")
            print(f"  English: '{row[1]}'")
            print(f"  Kannada: '{row[2]}'")
            print(f"  Amount: ₹{row[3]}")
            print()
        
        # Check for incorrect name
        incorrect_query = text("""
            SELECT id, name_english, name_kannada 
            FROM sevas 
            WHERE name_english LIKE '%Talla%' 
               OR name_english LIKE '%Machu%'
               OR name_kannada LIKE '%ತಲೆ%'
               OR name_kannada LIKE '%ಮಚ್ಚು%'
        """)
        
        result = db.execute(incorrect_query)
        incorrect = result.fetchall()
        
        if incorrect:
            print(f"\n⚠️  Found {len(incorrect)} seva(s) with similar incorrect names:")
            for row in incorrect:
                print(f"  - ID: {row[0]}, English: '{row[1]}', Kannada: '{row[2]}'")
        else:
            print("\n✅ No sevas found with incorrect names.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Checking All Sevas in Database")
    print("=" * 60)
    check_sevas()
    print("=" * 60)
























