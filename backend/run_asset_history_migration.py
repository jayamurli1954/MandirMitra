"""
Run migration to add Asset History, Transfer, Verification, Insurance, and Documents tables
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
    print("Asset History, Transfer, Verification, Insurance Migration")
    print("============================================================")

    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        print("🔌 Connecting to database...")
        print(f"   Host: {engine.url.host}")
        print(f"   Port: {engine.url.port}")
        print(f"   Database: {engine.url.database}")
        print(f"   User: {engine.url.username}")

        migration_sql_path = os.path.join(os.path.dirname(__file__), 'migrations', 'add_asset_history_tables.sql')
        with open(migration_sql_path, 'r') as f:
            migration_sql = f.read()

        print("📝 Executing migration SQL...")
        conn.execute(text(migration_sql))
        conn.commit()
        print("✅ Migration completed successfully!")

        # Verify tables
        print("\n✅ Tables created/updated successfully!")
        tables_to_check = ["asset_transfers", "asset_valuation_history", "asset_physical_verifications", "asset_insurance", "asset_documents"]
        for table_name in tables_to_check:
            result = conn.execute(text(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');")).scalar()
            if result:
                print(f"  ✓ {table_name}")
            else:
                print(f"  ✗ {table_name} (FAILED TO CREATE)")

        # Verify disposal columns
        print("\n✅ Disposal table enhanced:")
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'asset_disposals' 
            AND column_name IN ('approved_by', 'approved_at', 'rejection_reason')
        """))
        columns = [row[0] for row in result]
        for col in ['approved_by', 'approved_at', 'rejection_reason']:
            if col in columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} (FAILED TO ADD)")

        print("\nNext steps:")
        print("1. Track asset transfers between locations")
        print("2. Record physical verifications for audit")
        print("3. Add insurance policies with expiry alerts")
        print("4. Upload asset documents and images")
        print("5. View complete valuation history")
        print("6. Enhanced disposal workflow with approval")

    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        if 'conn' in locals() and not conn.closed:
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
        if 'conn' in locals() and not conn.closed:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    run_migration()



