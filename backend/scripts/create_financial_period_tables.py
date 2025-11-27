"""
Migration script to create financial period management tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Create financial period tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Create financial_years table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS financial_years (
                    id SERIAL PRIMARY KEY,
                    temple_id INTEGER REFERENCES temples(id),
                    year_code VARCHAR(10) NOT NULL UNIQUE,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_closed BOOLEAN DEFAULT FALSE,
                    closed_at TIMESTAMP,
                    closed_by INTEGER REFERENCES users(id),
                    opening_balance_carried_forward BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Create financial_periods table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS financial_periods (
                    id SERIAL PRIMARY KEY,
                    financial_year_id INTEGER NOT NULL REFERENCES financial_years(id) ON DELETE CASCADE,
                    temple_id INTEGER REFERENCES temples(id),
                    period_name VARCHAR(50) NOT NULL,
                    period_type VARCHAR(20) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    status VARCHAR(50) DEFAULT 'open',
                    is_locked BOOLEAN DEFAULT FALSE,
                    is_closed BOOLEAN DEFAULT FALSE,
                    closed_at TIMESTAMP,
                    closed_by INTEGER REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Create period_closings table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS period_closings (
                    id SERIAL PRIMARY KEY,
                    financial_year_id INTEGER NOT NULL REFERENCES financial_years(id),
                    period_id INTEGER REFERENCES financial_periods(id),
                    temple_id INTEGER REFERENCES temples(id),
                    closing_type VARCHAR(50) NOT NULL,
                    closing_date DATE NOT NULL,
                    total_income FLOAT DEFAULT 0,
                    total_expenses FLOAT DEFAULT 0,
                    net_surplus FLOAT DEFAULT 0,
                    closing_journal_entry_id INTEGER REFERENCES journal_entries(id),
                    is_completed BOOLEAN DEFAULT FALSE,
                    completed_at TIMESTAMP,
                    completed_by INTEGER NOT NULL REFERENCES users(id),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_financial_years_temple ON financial_years(temple_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_financial_years_code ON financial_years(year_code)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_financial_periods_year ON financial_periods(financial_year_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_period_closings_year ON period_closings(financial_year_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_period_closings_date ON period_closings(closing_date)"))
            
            conn.commit()
            print("✅ Successfully created financial period tables")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    run_migration()






