"""
Migration Script: Add integrity_hash column to journal_entries table

This script adds the integrity_hash column for tampering detection.
Run this once to add the column to existing databases.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.auto_setup import is_standalone_mode, setup_standalone_database

def add_integrity_hash_column():
    """Add integrity_hash column to journal_entries table"""
    
    # Get database URL
    if is_standalone_mode():
        db_url = setup_standalone_database()
    else:
        db_url = os.environ.get("DATABASE_URL", settings.DATABASE_URL)
    
    # Create engine
    engine = create_engine(db_url)
    
    print("=" * 60)
    print("Adding integrity_hash column to journal_entries table")
    print("=" * 60)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            if db_url.startswith("sqlite"):
                result = conn.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM pragma_table_info('journal_entries') 
                    WHERE name = 'integrity_hash'
                """))
            else:  # PostgreSQL
                result = conn.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.columns 
                    WHERE table_name = 'journal_entries' 
                    AND column_name = 'integrity_hash'
                """))
            
            count = result.fetchone()[0]
            
            if count > 0:
                print("✅ Column 'integrity_hash' already exists")
                return
            
            # Add column
            print("Adding column...")
            if db_url.startswith("sqlite"):
                conn.execute(text("""
                    ALTER TABLE journal_entries 
                    ADD COLUMN integrity_hash VARCHAR(64)
                """))
            else:  # PostgreSQL
                conn.execute(text("""
                    ALTER TABLE journal_entries 
                    ADD COLUMN integrity_hash VARCHAR(64)
                """))
            
            conn.commit()
            
            # Create index
            print("Creating index...")
            try:
                if db_url.startswith("sqlite"):
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_journal_entries_integrity_hash 
                        ON journal_entries(integrity_hash)
                    """))
                else:  # PostgreSQL
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_journal_entries_integrity_hash 
                        ON journal_entries(integrity_hash)
                    """))
                conn.commit()
            except Exception as e:
                print(f"⚠️  Index creation warning: {e}")
            
            print("✅ Column 'integrity_hash' added successfully")
            print("\nNote: Existing entries will get hashes generated on next transaction")
            print("      or when integrity check runs on application startup.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_integrity_hash_column()






