"""
CI helper script: Creates all database tables directly on PostgreSQL.
Bypasses the app's standalone-mode detection that would fall back to SQLite.
Usage: python scripts/ci_create_tables.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine  # noqa: E402

# Get the DB URL from environment
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://testuser:testpass@localhost:5432/mandirmitra_test"
)

print(f"Connecting to: {DATABASE_URL.split('@')[-1]}")  # Log host only, not credentials

# Import Base (without triggering app startup/standalone mode)
from app.core.database import Base  # noqa: E402

# Import all models so they register with Base.metadata
import app.models.temple               # noqa: E402, F401
import app.models.user                 # noqa: E402, F401
import app.models.devotee              # noqa: E402, F401
import app.models.donation             # noqa: E402, F401
import app.models.seva                 # noqa: E402, F401
import app.models.accounting           # noqa: E402, F401
import app.models.vendor               # noqa: E402, F401
import app.models.inkind_sponsorship   # noqa: E402, F401
import app.models.upi_banking          # noqa: E402, F401
import app.models.bank_reconciliation  # noqa: E402, F401
import app.models.panchang_display_settings  # noqa: E402, F401
import app.models.sacred_events_cache  # noqa: E402, F401

# Create engine directly with PostgreSQL URL
pg_engine = create_engine(DATABASE_URL)
Base.metadata.create_all(pg_engine)

print(f"Successfully created {len(Base.metadata.tables)} tables in PostgreSQL")
print("Tables:", ", ".join(sorted(Base.metadata.tables.keys())))
