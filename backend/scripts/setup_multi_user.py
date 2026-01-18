"""
Simple Setup Script for Multi-User & Audit Trail
Just run this one script - it does everything!
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text, inspect, create_engine
from sqlalchemy.orm import Session, sessionmaker
import bcrypt
from datetime import datetime
import os


# Password hashing using bcrypt directly
def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


# Database setup
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import all models to fix SQLAlchemy relationships
# This ensures all relationships are properly configured
from app.models.temple import Temple
from app.models.user import User
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine
from app.models.panchang_display_settings import PanchangDisplaySettings


def check_table_exists(table_name):
    """Check if a table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def create_audit_logs_table():
    """Create audit_logs table"""
    print("\n" + "=" * 60)
    print("STEP 1: Creating Audit Logs Table...")
    print("=" * 60)

    # Check if table already exists
    if check_table_exists("audit_logs"):
        print("✅ Audit logs table already exists. Skipping...")
        return True

    # SQL to create table
    sql_statements = [
        """CREATE TABLE audit_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            user_name VARCHAR(200) NOT NULL,
            user_email VARCHAR(100) NOT NULL,
            user_role VARCHAR(50) NOT NULL,
            action VARCHAR(100) NOT NULL,
            entity_type VARCHAR(100) NOT NULL,
            entity_id INTEGER,
            old_values JSONB,
            new_values JSONB,
            changes JSONB,
            ip_address VARCHAR(50),
            user_agent VARCHAR(500),
            description TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )""",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs(entity_type)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_id ON audit_logs(entity_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_role ON audit_logs(user_role)",
    ]

    try:
        with engine.connect() as conn:
            for sql in sql_statements:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                except Exception as e:
                    if "already exists" in str(e).lower():
                        pass  # Ignore if already exists
                    else:
                        print(f"⚠️  Warning: {str(e)[:100]}")

        print("✅ Audit logs table created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating audit logs table: {str(e)}")
        return False


def create_clerk_users(num_clerks=3, default_password="clerk123"):
    """Create clerk users using raw SQL to avoid ORM relationship issues"""
    print("\n" + "=" * 60)
    print("STEP 2: Creating Clerk Users...")
    print("=" * 60)

    try:
        # Get temple_id using raw SQL
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name FROM temples LIMIT 1"))
            temple_row = result.fetchone()

            if not temple_row:
                print("❌ No temple found. Please create a temple first.")
                return False

            temple_id = temple_row[0]
            temple_name = temple_row[1]

        print(f"Creating {num_clerks} clerk users for temple: {temple_name}")
        print()

        created_count = 0
        skipped_count = 0
        password_hash = get_password_hash(default_password)
        now = datetime.utcnow().isoformat()

        with engine.connect() as conn:
            for i in range(1, num_clerks + 1):
                email = f"clerk{i}@temple.local"
                full_name = f"Clerk {i}"

                # Check if exists
                check_result = conn.execute(
                    text("SELECT id FROM users WHERE email = :email"), {"email": email}
                )
                if check_result.fetchone():
                    print(f"⚠️  {email} already exists. Skipping...")
                    skipped_count += 1
                    continue

                # Create user using raw SQL
                conn.execute(
                    text(
                        """
                        INSERT INTO users (email, password_hash, full_name, role, is_active, temple_id, created_at, updated_at)
                        VALUES (:email, :password_hash, :full_name, :role, :is_active, :temple_id, :created_at, :updated_at)
                    """
                    ),
                    {
                        "email": email,
                        "password_hash": password_hash,
                        "full_name": full_name,
                        "role": "staff",
                        "is_active": True,
                        "temple_id": temple_id,
                        "created_at": now,
                        "updated_at": now,
                    },
                )
                conn.commit()

                print(f"✅ Created: {full_name}")
                print(f"   Email: {email}")
                print(f"   Password: {default_password}")
                print()

                created_count += 1

        print("=" * 60)
        print(f"Summary: Created {created_count}, Skipped {skipped_count}")
        print()

        if created_count > 0:
            print("⚠️  IMPORTANT: Change default passwords after first login!")
            print()

        return True

    except Exception as e:
        print(f"❌ Error creating clerk users: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main setup function"""
    print("\n" + "=" * 60)
    print("MULTI-USER & AUDIT TRAIL SETUP")
    print("=" * 60)
    print()
    print("This script will:")
    print("  1. Create audit_logs table")
    print("  2. Create 3 clerk users (clerk1, clerk2, clerk3)")
    print()

    # Step 1: Create audit logs table
    if not create_audit_logs_table():
        print("\n❌ Setup failed at Step 1. Please check the error above.")
        return

    # Step 2: Create clerk users
    if not create_clerk_users():
        print("\n❌ Setup failed at Step 2. Please check the error above.")
        return

    # Success!
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Clerk users created:")
    print("  - clerk1@temple.local / Password: clerk123")
    print("  - clerk2@temple.local / Password: clerk123")
    print("  - clerk3@temple.local / Password: clerk123")
    print()
    print("Next steps:")
    print("  1. Login as clerk1@temple.local with password 'clerk123'")
    print("  2. Change the password after first login")
    print("  3. Create a donation to test audit trail")
    print("  4. View audit logs as admin: GET /api/v1/audit-logs/")
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
