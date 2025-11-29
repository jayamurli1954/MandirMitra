"""
Migration Script: Add module_hundi_enabled column to temples table
Run this script to update the database schema
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine
from sqlalchemy import text

def run_migration():
    """Run the migration to add module_hundi_enabled column to temples table"""
    
    migration_sql = """
    -- Add module_hundi_enabled column (if not exists)
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'temples' AND column_name = 'module_hundi_enabled'
        ) THEN
            ALTER TABLE temples ADD COLUMN module_hundi_enabled BOOLEAN DEFAULT TRUE;
            COMMENT ON COLUMN temples.module_hundi_enabled IS 'Enable/disable Hundi Management module';
        END IF;
    END $$;
    """
    
    print("Running migration: Add module_hundi_enabled column to temples table...")
    
    with engine.connect() as conn:
        try:
            # Execute migration
            conn.execute(text(migration_sql))
            conn.commit()
            print("Migration completed successfully!")
            print("   - Added module_hundi_enabled column")
        except Exception as e:
            print(f"Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    run_migration()

