"""
Script to add reschedule fields to seva_bookings table
Run this script to apply the database migration
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

def run_migration():
    """Run the SQL migration to add reschedule fields"""
    
    migration_sql = """
    -- Add reschedule fields
    ALTER TABLE seva_bookings 
    ADD COLUMN IF NOT EXISTS original_booking_date DATE,
    ADD COLUMN IF NOT EXISTS reschedule_requested_date DATE,
    ADD COLUMN IF NOT EXISTS reschedule_reason TEXT,
    ADD COLUMN IF NOT EXISTS reschedule_approved BOOLEAN,
    ADD COLUMN IF NOT EXISTS reschedule_approved_by INTEGER REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS reschedule_approved_at TIMESTAMP;

    -- Add index for faster queries
    CREATE INDEX IF NOT EXISTS idx_seva_bookings_reschedule_approved 
    ON seva_bookings(reschedule_approved) 
    WHERE reschedule_approved IS NULL;
    """
    
    try:
        with engine.connect() as conn:
            # Execute migration
            conn.execute(text(migration_sql))
            conn.commit()
            print("✅ Migration successful! Reschedule fields added to seva_bookings table.")
            return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("Running migration to add reschedule fields to seva_bookings table...")
    success = run_migration()
    if success:
        print("\n✅ Migration completed successfully!")
        print("You can now use the reschedule functionality for seva bookings.")
    else:
        print("\n❌ Migration failed. Please check the error above.")
        sys.exit(1)









