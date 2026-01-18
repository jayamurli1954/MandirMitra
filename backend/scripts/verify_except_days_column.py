"""
Script to verify except_days column exists and add it if missing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal
from app.core.config import settings

def verify_and_add_column():
    """Verify except_days column exists, add if missing"""
    db = SessionLocal()
    
    try:
        db_url = os.environ.get('DATABASE_URL', settings.DATABASE_URL)
        is_sqlite = db_url.startswith('sqlite')
        
        if is_sqlite:
            result = db.execute(text("PRAGMA table_info(sevas)"))
            columns = [row[1] for row in result.fetchall()]
            column_exists = 'except_days' in columns
        else:
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'sevas' AND column_name = 'except_days'
            """))
            column_exists = result.fetchone() is not None
        
        if not column_exists:
            print("Column except_days does not exist. Adding it now...")
            db.execute(text("ALTER TABLE sevas ADD COLUMN except_days TEXT"))
            db.commit()
            print("Column except_days added successfully!")
        else:
            print("Column except_days already exists.")
            
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    verify_and_add_column()







