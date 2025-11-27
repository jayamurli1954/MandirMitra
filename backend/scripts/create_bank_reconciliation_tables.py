"""
Migration script to create bank reconciliation tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Create bank reconciliation tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Create bank_statements table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bank_statements (
                    id SERIAL PRIMARY KEY,
                    account_id INTEGER NOT NULL REFERENCES accounts(id),
                    temple_id INTEGER REFERENCES temples(id),
                    statement_date DATE NOT NULL,
                    from_date DATE NOT NULL,
                    to_date DATE NOT NULL,
                    opening_balance FLOAT NOT NULL,
                    closing_balance FLOAT NOT NULL,
                    imported_at TIMESTAMP DEFAULT NOW(),
                    imported_by INTEGER REFERENCES users(id),
                    source_file VARCHAR(500),
                    is_reconciled BOOLEAN DEFAULT FALSE,
                    reconciled_at TIMESTAMP,
                    reconciled_by INTEGER REFERENCES users(id)
                )
            """))
            
            # Create bank_statement_entries table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bank_statement_entries (
                    id SERIAL PRIMARY KEY,
                    statement_id INTEGER NOT NULL REFERENCES bank_statements(id) ON DELETE CASCADE,
                    transaction_date DATE NOT NULL,
                    value_date DATE,
                    entry_type VARCHAR(50) NOT NULL,
                    amount FLOAT NOT NULL,
                    description TEXT,
                    reference_number VARCHAR(100),
                    narration TEXT,
                    balance_after FLOAT,
                    is_matched BOOLEAN DEFAULT FALSE,
                    matched_journal_line_id INTEGER REFERENCES journal_lines(id),
                    matched_at TIMESTAMP,
                    matched_by INTEGER REFERENCES users(id),
                    notes TEXT
                )
            """))
            
            # Create bank_reconciliations table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bank_reconciliations (
                    id SERIAL PRIMARY KEY,
                    account_id INTEGER NOT NULL REFERENCES accounts(id),
                    statement_id INTEGER NOT NULL REFERENCES bank_statements(id) UNIQUE,
                    temple_id INTEGER REFERENCES temples(id),
                    reconciliation_date DATE NOT NULL,
                    from_date DATE NOT NULL,
                    to_date DATE NOT NULL,
                    book_balance_as_on FLOAT NOT NULL,
                    book_opening_balance FLOAT NOT NULL,
                    bank_balance_as_per_statement FLOAT NOT NULL,
                    bank_opening_balance FLOAT NOT NULL,
                    deposits_in_transit FLOAT DEFAULT 0,
                    cheques_issued_not_cleared FLOAT DEFAULT 0,
                    bank_charges_not_recorded FLOAT DEFAULT 0,
                    interest_credited_not_recorded FLOAT DEFAULT 0,
                    other_adjustments FLOAT DEFAULT 0,
                    adjusted_book_balance FLOAT NOT NULL,
                    adjusted_bank_balance FLOAT NOT NULL,
                    difference FLOAT DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_by INTEGER NOT NULL REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP,
                    completed_by INTEGER REFERENCES users(id),
                    notes TEXT,
                    discrepancy_notes TEXT
                )
            """))
            
            # Create reconciliation_outstanding_items table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS reconciliation_outstanding_items (
                    id SERIAL PRIMARY KEY,
                    reconciliation_id INTEGER NOT NULL REFERENCES bank_reconciliations(id) ON DELETE CASCADE,
                    item_type VARCHAR(50) NOT NULL,
                    description TEXT NOT NULL,
                    amount FLOAT NOT NULL,
                    date DATE NOT NULL,
                    reference_number VARCHAR(100),
                    journal_entry_id INTEGER REFERENCES journal_entries(id),
                    statement_entry_id INTEGER REFERENCES bank_statement_entries(id),
                    is_cleared BOOLEAN DEFAULT FALSE,
                    cleared_at TIMESTAMP,
                    cleared_in_reconciliation_id INTEGER REFERENCES bank_reconciliations(id),
                    notes TEXT
                )
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bank_statements_account ON bank_statements(account_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bank_statements_date ON bank_statements(statement_date)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_statement_entries_statement ON bank_statement_entries(statement_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_statement_entries_date ON bank_statement_entries(transaction_date)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_reconciliations_account ON bank_reconciliations(account_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_reconciliations_date ON bank_reconciliations(reconciliation_date)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_outstanding_reconciliation ON reconciliation_outstanding_items(reconciliation_id)"))
            
            conn.commit()
            print("✅ Successfully created bank reconciliation tables")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    run_migration()






