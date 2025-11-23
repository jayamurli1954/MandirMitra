"""
Migration 002: Add Account Linking to Donation Categories and Sevas

Adds account_id foreign key to donation_categories and sevas tables
to enable category-specific accounting.
"""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import Column, Integer, ForeignKey, text
from app.core.database import SessionLocal, engine

def upgrade():
    """
    Add account_id column to donation_categories and sevas tables
    """
    db = SessionLocal()

    try:
        print("Running Migration 002: Add Account Linking")
        print("=" * 60)

        # Add account_id to donation_categories
        print("\n1️⃣  Adding account_id to donation_categories table...")
        try:
            db.execute(text("""
                ALTER TABLE donation_categories
                ADD COLUMN account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL
            """))
            db.commit()
            print("   ✅ Added account_id to donation_categories")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("   ⏭️  Column already exists, skipping")
                db.rollback()
            else:
                raise

        # Add account_id to sevas
        print("\n2️⃣  Adding account_id to sevas table...")
        try:
            db.execute(text("""
                ALTER TABLE sevas
                ADD COLUMN account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL
            """))
            db.commit()
            print("   ✅ Added account_id to sevas")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("   ⏭️  Column already exists, skipping")
                db.rollback()
            else:
                raise

        print("\n" + "=" * 60)
        print("✅ Migration 002 completed successfully!")
        print("\nNext steps:")
        print("1. Run: python seed_chart_of_accounts.py (if not done)")
        print("2. Run: python link_categories_to_accounts.py")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def downgrade():
    """
    Remove account_id column from donation_categories and sevas tables
    """
    db = SessionLocal()

    try:
        print("Reverting Migration 002: Remove Account Linking")
        print("=" * 60)

        # Remove account_id from donation_categories
        print("\n1️⃣  Removing account_id from donation_categories...")
        db.execute(text("ALTER TABLE donation_categories DROP COLUMN IF EXISTS account_id"))
        db.commit()
        print("   ✅ Removed")

        # Remove account_id from sevas
        print("\n2️⃣  Removing account_id from sevas...")
        db.execute(text("ALTER TABLE sevas DROP COLUMN IF EXISTS account_id"))
        db.commit()
        print("   ✅ Removed")

        print("\n✅ Migration 002 reverted successfully!")

    except Exception as e:
        print(f"\n❌ Downgrade failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
