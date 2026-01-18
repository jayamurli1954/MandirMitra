"""
Migration script to add token seva columns to database
Run this script to add the required columns for token seva functionality
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine
from sqlalchemy import text


def run_migration():
    """Run the migration to add token seva columns"""
    print("Starting token seva migration...")

    migration_sql = """
    -- Add token seva columns to sevas table
    ALTER TABLE sevas 
    ADD COLUMN IF NOT EXISTS is_token_seva BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS token_color VARCHAR(50),
    ADD COLUMN IF NOT EXISTS token_threshold FLOAT;

    -- Add token seva threshold to temples table
    ALTER TABLE temples 
    ADD COLUMN IF NOT EXISTS token_seva_threshold FLOAT DEFAULT 50.0;

    -- Create token_inventory table
    CREATE TABLE IF NOT EXISTS token_inventory (
        id SERIAL PRIMARY KEY,
        temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
        seva_id INTEGER NOT NULL REFERENCES sevas(id) ON DELETE CASCADE,
        token_color VARCHAR(50) NOT NULL,
        serial_number VARCHAR(50) NOT NULL UNIQUE,
        token_number VARCHAR(50) NOT NULL,
        status VARCHAR(20) DEFAULT 'available' NOT NULL,
        batch_number VARCHAR(50),
        printed_date DATE,
        expiry_date DATE,
        sold_at TIMESTAMP,
        sold_by INTEGER REFERENCES users(id),
        counter_number VARCHAR(20),
        used_at TIMESTAMP,
        used_by_devotee_id INTEGER REFERENCES devotees(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_token_inventory_temple ON token_inventory(temple_id);
    CREATE INDEX IF NOT EXISTS idx_token_inventory_seva ON token_inventory(seva_id);
    CREATE INDEX IF NOT EXISTS idx_token_inventory_serial ON token_inventory(serial_number);
    CREATE INDEX IF NOT EXISTS idx_token_inventory_status ON token_inventory(status);

    -- Create token_sales table
    CREATE TABLE IF NOT EXISTS token_sales (
        id SERIAL PRIMARY KEY,
        temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
        seva_id INTEGER NOT NULL REFERENCES sevas(id) ON DELETE CASCADE,
        sale_date DATE NOT NULL,
        sale_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        token_id INTEGER NOT NULL REFERENCES token_inventory(id),
        token_serial_number VARCHAR(50) NOT NULL,
        amount FLOAT NOT NULL,
        payment_mode VARCHAR(20) NOT NULL,
        upi_reference VARCHAR(100),
        counter_number VARCHAR(20),
        sold_by INTEGER NOT NULL REFERENCES users(id),
        devotee_id INTEGER REFERENCES devotees(id),
        devotee_name VARCHAR(200),
        devotee_phone VARCHAR(20),
        journal_entry_id INTEGER REFERENCES journal_entries(id),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_token_sales_temple ON token_sales(temple_id);
    CREATE INDEX IF NOT EXISTS idx_token_sales_seva ON token_sales(seva_id);
    CREATE INDEX IF NOT EXISTS idx_token_sales_date ON token_sales(sale_date);
    CREATE INDEX IF NOT EXISTS idx_token_sales_serial ON token_sales(token_serial_number);
    CREATE INDEX IF NOT EXISTS idx_token_sales_counter ON token_sales(counter_number);

    -- Create token_reconciliations table
    CREATE TABLE IF NOT EXISTS token_reconciliations (
        id SERIAL PRIMARY KEY,
        temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
        reconciliation_date DATE NOT NULL UNIQUE,
        token_counts TEXT,
        total_tokens_sold INTEGER DEFAULT 0,
        total_amount_cash FLOAT DEFAULT 0.0,
        total_amount_upi FLOAT DEFAULT 0.0,
        total_amount FLOAT DEFAULT 0.0,
        counter_summary TEXT,
        is_reconciled BOOLEAN DEFAULT FALSE,
        reconciled_by INTEGER REFERENCES users(id),
        reconciled_at TIMESTAMP,
        discrepancy_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_token_reconciliations_temple ON token_reconciliations(temple_id);
    CREATE INDEX IF NOT EXISTS idx_token_reconciliations_date ON token_reconciliations(reconciliation_date);
    """

    try:
        with engine.connect() as conn:
            # Execute migration in a transaction
            conn.execute(text(migration_sql))
            conn.commit()
            print("✅ Migration completed successfully!")
            print("   - Added is_token_seva, token_color, token_threshold to sevas table")
            print("   - Added token_seva_threshold to temples table")
            print("   - Created token_inventory, token_sales, token_reconciliations tables")
            return True
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
