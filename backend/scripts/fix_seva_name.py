"""
Fix incorrect seva name in database
Talla / Machu Abhisheka -> Taila / Madhu Abhisheka
ತಲೆ / ಮಚ್ಚು ಅಭಿಷೇಕ -> ತೈಲ / ಮಧು ಅಭಿಷೇಕ
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from sqlalchemy import text

def fix_seva_name():
    """Update incorrect seva name in database using raw SQL"""
    db = SessionLocal()
    try:
        # First, check what sevas exist (for debugging)
        all_sevas_query = text("""
            SELECT id, name_english, name_kannada 
            FROM sevas 
            WHERE name_english LIKE '%Abhisheka%' OR name_kannada LIKE '%ಭಿಷೇಕ%'
            ORDER BY id
        """)
        
        result = db.execute(all_sevas_query)
        all_abhisheka_sevas = result.fetchall()
        
        if all_abhisheka_sevas:
            print(f"Found {len(all_abhisheka_sevas)} Abhisheka seva(s) in database:")
            for row in all_abhisheka_sevas:
                print(f"  - ID: {row[0]}, English: '{row[1]}', Kannada: '{row[2]}'")
        
        # Check if there are any sevas with incorrect name
        check_query = text("""
            SELECT id, name_english, name_kannada 
            FROM sevas 
            WHERE name_english = 'Talla / Machu Abhisheka' 
               OR name_kannada = 'ತಲೆ / ಮಚ್ಚು ಅಭಿಷೇಕ'
        """)
        
        result = db.execute(check_query)
        incorrect_sevas = result.fetchall()
        
        if not incorrect_sevas:
            print("✅ No sevas found with incorrect name. They may have already been fixed.")
            return
        
        print(f"Found {len(incorrect_sevas)} seva(s) with incorrect name:")
        for row in incorrect_sevas:
            print(f"  - ID: {row[0]}, English: {row[1]}, Kannada: {row[2]}")
        
        # Update them using raw SQL
        update_query = text("""
            UPDATE sevas 
            SET 
                name_english = 'Taila / Madhu Abhisheka',
                name_kannada = 'ತೈಲ / ಮಧು ಅಭಿಷೇಕ',
                updated_at = NOW()
            WHERE 
                name_english = 'Talla / Machu Abhisheka' 
                OR name_kannada = 'ತಲೆ / ಮಚ್ಚು ಅಭಿಷೇಕ'
        """)
        
        result = db.execute(update_query)
        db.commit()
        
        print(f"\n✅ Successfully updated {result.rowcount} seva(s)")
        print("   Changed: Talla / Machu Abhisheka -> Taila / Madhu Abhisheka")
        print("   Changed: ತಲೆ / ಮಚ್ಚು ಅಭಿಷೇಕ -> ತೈಲ / ಮಧು ಅಭಿಷೇಕ")
        
        # Verify
        verify_query = text("""
            SELECT id, name_english, name_kannada 
            FROM sevas 
            WHERE name_english = 'Taila / Madhu Abhisheka'
        """)
        
        result = db.execute(verify_query)
        verified = result.fetchone()
        
        if verified:
            print(f"\n✅ Verification: Found updated seva (ID: {verified[0]})")
            print(f"   English: {verified[1]}")
            print(f"   Kannada: {verified[2]}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating seva: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Fixing Seva Name: Talla -> Taila, Machu -> Madhu")
    print("=" * 60)
    fix_seva_name()
    print("=" * 60)



