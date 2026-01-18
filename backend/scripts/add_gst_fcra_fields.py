"""
Database Migration Script: Add GST and FCRA Optional Fields to Temples Table
Run this script to add GST and FCRA fields to the temples table
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings


def run_migration():
    """Add GST and FCRA fields to temples table"""

    # Create database connection
    database_url = settings.DATABASE_URL
    engine = create_engine(database_url)

    print("🔄 Starting migration: Add GST/FCRA fields to temples table...")

    with engine.connect() as conn:
        try:
            # Check if columns already exist
            check_query = text(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'temples' 
                AND column_name IN ('gst_applicable', 'fcra_applicable')
            """
            )
            result = conn.execute(check_query)
            existing_columns = [row[0] for row in result]

            if "gst_applicable" in existing_columns and "fcra_applicable" in existing_columns:
                print("✅ GST/FCRA fields already exist. Migration not needed.")
                return

            # Add GST fields
            if "gst_applicable" not in existing_columns:
                print("  Adding GST fields...")
                conn.execute(
                    text(
                        """
                    ALTER TABLE temples 
                    ADD COLUMN IF NOT EXISTS gst_applicable BOOLEAN DEFAULT FALSE,
                    ADD COLUMN IF NOT EXISTS gstin VARCHAR(15),
                    ADD COLUMN IF NOT EXISTS gst_registration_date VARCHAR(50),
                    ADD COLUMN IF NOT EXISTS gst_tax_rates TEXT
                """
                    )
                )
                conn.commit()
                print("  ✅ GST fields added")

            # Add FCRA fields
            if "fcra_applicable" not in existing_columns:
                print("  Adding FCRA fields...")
                conn.execute(
                    text(
                        """
                    ALTER TABLE temples 
                    ADD COLUMN IF NOT EXISTS fcra_applicable BOOLEAN DEFAULT FALSE,
                    ADD COLUMN IF NOT EXISTS fcra_bank_account_id INTEGER
                """
                    )
                )
                conn.commit()
                print("  ✅ FCRA fields added")

            print("✅ Migration completed successfully!")

        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            conn.rollback()
            raise


if __name__ == "__main__":
    run_migration()
