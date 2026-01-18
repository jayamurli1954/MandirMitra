"""
Migration script to add priest_id column to seva_bookings table
Run this after updating the model
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings


def run_migration():
    """Add priest_id column to seva_bookings table"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        try:
            # Check if column already exists
            check_query = text(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='seva_bookings' AND column_name='priest_id'
            """
            )
            result = conn.execute(check_query)
            if result.fetchone():
                print("✅ Column 'priest_id' already exists in seva_bookings table")
                return

            # Add priest_id column
            alter_query = text(
                """
                ALTER TABLE seva_bookings 
                ADD COLUMN priest_id INTEGER REFERENCES users(id)
            """
            )
            conn.execute(alter_query)
            conn.commit()

            print("✅ Successfully added priest_id column to seva_bookings table")

        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    run_migration()
