"""
Migration Script: Add payment detail fields to donations table
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
    """Run the migration to add payment fields to donations table"""
    
    migration_sql = """
    -- Add UPI payment fields
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'donations' AND column_name = 'sender_upi_id'
        ) THEN
            ALTER TABLE donations ADD COLUMN sender_upi_id VARCHAR(100);
            COMMENT ON COLUMN donations.sender_upi_id IS 'Sender UPI ID (e.g., 9876543210@paytm)';
        END IF;
    END $$;

    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'donations' AND column_name = 'upi_reference_number'
        ) THEN
            ALTER TABLE donations ADD COLUMN upi_reference_number VARCHAR(100);
            COMMENT ON COLUMN donations.upi_reference_number IS 'UPI transaction reference (UTR/RRN)';
        END IF;
    END $$;

    -- Update cheque fields (rename if needed, add new ones)
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'donations' AND column_name = 'cheque_bank_name'
        ) THEN
            -- Check if bank_name exists and rename it, or create new
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'donations' AND column_name = 'bank_name'
            ) THEN
                ALTER TABLE donations RENAME COLUMN bank_name TO cheque_bank_name;
            ELSE
                ALTER TABLE donations ADD COLUMN cheque_bank_name VARCHAR(100);
            END IF;
            COMMENT ON COLUMN donations.cheque_bank_name IS 'Name of bank for cheque payment';
        END IF;
    END $$;

    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'donations' AND column_name = 'cheque_branch'
        ) THEN
            ALTER TABLE donations ADD COLUMN cheque_branch VARCHAR(100);
            COMMENT ON COLUMN donations.cheque_branch IS 'Branch name for cheque payment';
        END IF;
    END $$;

    -- Add online transfer fields
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'donations' AND column_name = 'utr_number'
        ) THEN
            ALTER TABLE donations ADD COLUMN utr_number VARCHAR(100);
            COMMENT ON COLUMN donations.utr_number IS 'UTR (Unique Transfer Reference) for online payments';
        END IF;
    END $$;

    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'donations' AND column_name = 'payer_name'
        ) THEN
            ALTER TABLE donations ADD COLUMN payer_name VARCHAR(200);
            COMMENT ON COLUMN donations.payer_name IS 'Payer name (may be different from devotee)';
        END IF;
    END $$;
    """
    
    print("Running migration: Add payment detail fields to donations table...")
    
    with engine.connect() as conn:
        try:
            # Execute migration
            conn.execute(text(migration_sql))
            conn.commit()
            print("Migration completed successfully!")
            print("   - Added sender_upi_id column")
            print("   - Added upi_reference_number column")
            print("   - Added/renamed cheque_bank_name column")
            print("   - Added cheque_branch column")
            print("   - Added utr_number column")
            print("   - Added payer_name column")
        except Exception as e:
            print(f"Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    run_migration()

