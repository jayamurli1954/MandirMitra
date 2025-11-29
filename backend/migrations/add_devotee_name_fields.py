"""
Migration Script: Add name_prefix, first_name, and last_name columns to devotees table
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
    """Run the migration to add name fields to devotees table"""
    
    migration_sql = """
    -- Add name_prefix column (if not exists)
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'devotees' AND column_name = 'name_prefix'
        ) THEN
            ALTER TABLE devotees ADD COLUMN name_prefix VARCHAR(10);
            COMMENT ON COLUMN devotees.name_prefix IS 'Mr., Mrs., Ms., M/s, Dr., etc.';
        END IF;
    END $$;

    -- Add first_name column (if not exists)
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'devotees' AND column_name = 'first_name'
        ) THEN
            ALTER TABLE devotees ADD COLUMN first_name VARCHAR(100);
            COMMENT ON COLUMN devotees.first_name IS 'First name of devotee';
        END IF;
    END $$;

    -- Add last_name column (if not exists)
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'devotees' AND column_name = 'last_name'
        ) THEN
            ALTER TABLE devotees ADD COLUMN last_name VARCHAR(100);
            COMMENT ON COLUMN devotees.last_name IS 'Last name of devotee (optional)';
        END IF;
    END $$;

    -- Add country_code column (if not exists)
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'devotees' AND column_name = 'country_code'
        ) THEN
            ALTER TABLE devotees ADD COLUMN country_code VARCHAR(5) DEFAULT '+91';
            COMMENT ON COLUMN devotees.country_code IS 'Country code for phone (e.g., +91, +1, +44)';
        END IF;
    END $$;

    -- Migrate existing data: Split name into first_name and last_name
    UPDATE devotees 
    SET 
        first_name = CASE 
            WHEN name IS NOT NULL AND name != '' THEN
                SPLIT_PART(TRIM(name), ' ', 1)
            ELSE 'Unknown'
        END,
        last_name = CASE 
            WHEN name IS NOT NULL AND name != '' AND LENGTH(TRIM(name)) > LENGTH(SPLIT_PART(TRIM(name), ' ', 1)) THEN
                SUBSTRING(TRIM(name) FROM LENGTH(SPLIT_PART(TRIM(name), ' ', 1)) + 2)
            ELSE NULL
        END
    WHERE first_name IS NULL OR first_name = '';

    -- Make first_name NOT NULL
    DO $$ 
    BEGIN
        ALTER TABLE devotees ALTER COLUMN first_name SET NOT NULL;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Could not set first_name NOT NULL: %', SQLERRM;
    END $$;
    """
    
    print("Running migration: Add name_prefix, first_name, and last_name to devotees table...")
    
    with engine.connect() as conn:
        try:
            # Execute migration
            conn.execute(text(migration_sql))
            conn.commit()
            print("Migration completed successfully!")
            print("   - Added name_prefix column")
            print("   - Added first_name column")
            print("   - Added last_name column")
            print("   - Added country_code column")
            print("   - Migrated existing data from name field")
        except Exception as e:
            print(f"Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    run_migration()

