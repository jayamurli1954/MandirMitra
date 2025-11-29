"""
Migration script to add reschedule columns to seva_bookings table
Run this script to add the required columns for seva booking reschedule functionality
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine
from sqlalchemy import text

def run_migration():
    """Run the migration to add reschedule columns to seva_bookings"""
    print("Starting seva booking reschedule columns migration...")
    
    migration_sql = """
    -- Add reschedule columns to seva_bookings table
    ALTER TABLE seva_bookings 
    ADD COLUMN IF NOT EXISTS original_booking_date DATE,
    ADD COLUMN IF NOT EXISTS reschedule_requested_date DATE,
    ADD COLUMN IF NOT EXISTS reschedule_reason TEXT,
    ADD COLUMN IF NOT EXISTS reschedule_approved BOOLEAN,
    ADD COLUMN IF NOT EXISTS reschedule_approved_by INTEGER REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS reschedule_approved_at TIMESTAMP;
    """
    
    try:
        with engine.connect() as conn:
            # Execute migration in a transaction
            conn.execute(text(migration_sql))
            conn.commit()
            print("✅ Migration completed successfully!")
            print("   - Added reschedule columns to seva_bookings table:")
            print("     * original_booking_date")
            print("     * reschedule_requested_date")
            print("     * reschedule_reason")
            print("     * reschedule_approved")
            print("     * reschedule_approved_by")
            print("     * reschedule_approved_at")
            return True
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)




