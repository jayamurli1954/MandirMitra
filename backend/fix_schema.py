"""Fix database schema - add missing columns to devotees table"""
from app.core.database import engine
from sqlalchemy import text

conn = engine.connect()

# Add missing columns
columns = [
    "ALTER TABLE devotees ADD COLUMN IF NOT EXISTS family_head_id INTEGER",
    "ALTER TABLE devotees ADD COLUMN IF NOT EXISTS date_of_birth DATE",
    "ALTER TABLE devotees ADD COLUMN IF NOT EXISTS gothra VARCHAR(100)",
    "ALTER TABLE devotees ADD COLUMN IF NOT EXISTS nakshatra VARCHAR(50)",
    "ALTER TABLE devotees ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(10) DEFAULT 'en'",
    "ALTER TABLE devotees ADD COLUMN IF NOT EXISTS receive_sms BOOLEAN DEFAULT TRUE",
    "ALTER TABLE devotees ADD COLUMN IF NOT EXISTS receive_email BOOLEAN DEFAULT TRUE",
    "ALTER TABLE devotees ADD COLUMN IF NOT EXISTS tags TEXT",
    "ALTER TABLE devotees ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"
]

for col_sql in columns:
    try:
        conn.execute(text(col_sql))
        print(f"✅ {col_sql.split('ADD COLUMN IF NOT EXISTS')[1].split()[0]}")
    except Exception as e:
        print(f"⚠️  {col_sql.split('ADD COLUMN IF NOT EXISTS')[1].split()[0]}: {e}")

conn.commit()
conn.close()
print("\n✅ Database schema migration completed!")
