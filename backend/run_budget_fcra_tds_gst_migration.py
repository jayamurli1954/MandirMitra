"""
Run migration to add Budget, FCRA, TDS/GST support
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL environment variable not set.")
    sys.exit(1)


def run_migration():
    print("============================================================")
    print("Budget, FCRA, TDS/GST Migration")
    print("============================================================")

    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        print("🔌 Connecting to database...")
        print(f"   Host: {engine.url.host}")
        print(f"   Port: {engine.url.port}")
        print(f"   Database: {engine.url.database}")
        print(f"   User: {engine.url.username}")

        migration_sql_path = os.path.join(
            os.path.dirname(__file__), "migrations", "add_budget_fcra_tds_gst.sql"
        )
        with open(migration_sql_path, "r") as f:
            migration_sql = f.read()

        print("📝 Executing migration SQL...")
        conn.execute(text(migration_sql))
        conn.commit()
        print("✅ Migration completed successfully!")

        # Verify tables
        print("\n✅ Tables created/updated successfully!")
        tables_to_check = ["budgets", "budget_items", "budget_revisions"]
        for table_name in tables_to_check:
            result = conn.execute(
                text(
                    f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');"
                )
            ).scalar()
            if result:
                print(f"  ✓ {table_name}")
            else:
                print(f"  ✗ {table_name} (FAILED TO CREATE)")

        # Verify donation columns
        print("\n✅ Donation columns added:")
        result = conn.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'donations' 
            AND column_name IN ('is_fcra_donation', 'tds_applicable', 'gst_applicable')
        """
            )
        )
        columns = [row[0] for row in result]
        for col in ["is_fcra_donation", "tds_applicable", "gst_applicable"]:
            if col in columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} (FAILED TO ADD)")

        print("\nNext steps:")
        print("1. Create budgets for financial planning")
        print("2. Mark foreign donations as FCRA")
        print("3. Configure TDS/GST rates")
        print("4. Generate FCRA-4 reports")
        print("5. Generate TDS/GST reports")

    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        if "conn" in locals() and not conn.closed:
            conn.rollback()
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Error: Migration SQL file not found at {migration_sql_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        if "conn" in locals() and not conn.closed:
            conn.close()
            print("Connection closed.")


if __name__ == "__main__":
    run_migration()
