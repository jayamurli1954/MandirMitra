"""
Run migration to add GST and FCRA fields to temples table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Run the GST/FCRA migration"""
    try:
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        
        migration_sql = """
        -- Add GST (Goods and Services Tax) fields - Optional
        ALTER TABLE temples 
        ADD COLUMN IF NOT EXISTS gst_applicable BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS gstin VARCHAR(15),
        ADD COLUMN IF NOT EXISTS gst_registration_date VARCHAR(50),
        ADD COLUMN IF NOT EXISTS gst_tax_rates TEXT;

        -- Add FCRA (Foreign Contribution Regulation Act) fields - Optional
        ALTER TABLE temples 
        ADD COLUMN IF NOT EXISTS fcra_applicable BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS fcra_bank_account_id INTEGER;
        """
        
        with engine.connect() as conn:
            conn.execute(text(migration_sql))
            conn.commit()
        
        print("✅ Migration completed successfully!")
        print("Added GST and FCRA fields to temples table")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()






