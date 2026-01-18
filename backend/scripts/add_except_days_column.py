"""
Migration script to add except_days column to sevas table
Run this script to add the new column for multiple excluded days support.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings

def add_except_days_column():
    """Add except_days column to sevas table if it doesn't exist"""
    
    db = SessionLocal()
    
    try:
        # Check database type
        db_url = os.environ.get('DATABASE_URL', settings.DATABASE_URL)
        is_sqlite = db_url.startswith('sqlite')
        
        if is_sqlite:
            # SQLite: Check if column exists using PRAGMA
            result = db.execute(text("PRAGMA table_info(sevas)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'except_days' not in columns:
                print("Adding except_days column to sevas table (SQLite)...")
                db.execute(text("ALTER TABLE sevas ADD COLUMN except_days TEXT"))
                db.commit()
                print("[SUCCESS] Column 'except_days' added successfully!")
            else:
                print("[INFO] Column 'except_days' already exists.")
        else:
            # PostgreSQL: Check if column exists using information_schema
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'sevas' AND column_name = 'except_days'
            """))
            
            if result.fetchone() is None:
                print("Adding except_days column to sevas table (PostgreSQL)...")
                db.execute(text("ALTER TABLE sevas ADD COLUMN except_days TEXT"))
                db.commit()
                print("[SUCCESS] Column 'except_days' added successfully!")
            else:
                print("[INFO] Column 'except_days' already exists.")
                
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error adding column: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Running migration: Add except_days column to sevas table")
    print("=" * 60)
    add_except_days_column()
    print("=" * 60)
    print("Migration complete!")

