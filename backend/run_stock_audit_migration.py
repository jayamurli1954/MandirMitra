"""
Run migration to add Stock Audit and Wastage tables
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
    print("Stock Audit and Wastage Migration")
    print("============================================================")

    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        print("🔌 Connecting to database...")
        print(f"   Host: {engine.url.host}")
        print(f"   Port: {engine.url.port}")
        print(f"   Database: {engine.url.database}")
        print(f"   User: {engine.url.username}")

        migration_sql_path = os.path.join(os.path.dirname(__file__), 'migrations', 'add_stock_audit_tables.sql')
        with open(migration_sql_path, 'r') as f:
            migration_sql = f.read()

        print("📝 Executing migration SQL...")
        conn.execute(text(migration_sql))
        conn.commit()
        print("✅ Migration completed successfully!")

        # Verify tables
        print("\n✅ Tables created successfully!")
        tables_to_check = ["stock_audits", "stock_audit_items", "stock_wastages"]
        for table_name in tables_to_check:
            result = conn.execute(text(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');")).scalar()
            if result:
                print(f"  ✓ {table_name}")
            else:
                print(f"  ✗ {table_name} (FAILED TO CREATE)")

        print("\nNext steps:")
        print("1. Create stock audits for physical verification")
        print("2. Record stock wastages")
        print("3. View low stock alerts")
        print("4. Track expiring items")
        print("5. Analyze consumption patterns")

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

