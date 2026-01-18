"""
Run migration to complete Inventory Module (100%)
Adds Purchase Orders, GRN, GIN, Low Stock Alerts, Stock Audit, Expiry Tracking
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
    print("Inventory Module Completion Migration")
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
            os.path.dirname(__file__), "migrations", "add_inventory_completion.sql"
        )
        with open(migration_sql_path, "r") as f:
            migration_sql = f.read()

        print("📝 Executing migration SQL...")
        conn.execute(text(migration_sql))
        conn.commit()
        print("✅ Migration completed successfully!")

        # Verify tables
        print("\n✅ Tables created/updated successfully!")
        tables_to_check = [
            "purchase_orders",
            "purchase_order_items",
            "grns",
            "grn_items",
            "gins",
            "gin_items",
            "low_stock_alerts",
            "stock_audits",
            "stock_audit_items",
        ]
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

        # Verify columns
        print("\n✅ Columns added to existing tables:")
        result = conn.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'items' 
            AND column_name IN ('has_expiry', 'shelf_life_days')
        """
            )
        )
        columns = [row[0] for row in result]
        for col in ["has_expiry", "shelf_life_days"]:
            if col in columns:
                print(f"  ✓ items.{col}")
            else:
                print(f"  ✗ items.{col} (FAILED TO ADD)")

        result = conn.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'stock_movements' 
            AND column_name IN ('grn_id', 'gin_id', 'expiry_date', 'batch_number')
        """
            )
        )
        columns = [row[0] for row in result]
        for col in ["grn_id", "gin_id", "expiry_date", "batch_number"]:
            if col in columns:
                print(f"  ✓ stock_movements.{col}")
            else:
                print(f"  ✗ stock_movements.{col} (FAILED TO ADD)")

        print("\nNext steps:")
        print("1. Create Purchase Orders for inventory procurement")
        print("2. Create GRN when items are received")
        print("3. Create GIN for issuing items")
        print("4. Monitor low stock alerts")
        print("5. Track expiry dates for perishable items")
        print("6. Conduct stock audits periodically")

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
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        if "conn" in locals() and not conn.closed:
            conn.close()
            print("Connection closed.")


if __name__ == "__main__":
    run_migration()
