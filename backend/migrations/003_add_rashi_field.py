"""
Migration 003: Add Rashi Field to Seva Bookings

Adds rashi (zodiac sign) field to seva_bookings table to complement nakshatra.
"""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import SessionLocal


def upgrade():
    """
    Add rashi column to seva_bookings table
    """
    db = SessionLocal()

    try:
        print("Running Migration 003: Add Rashi Field")
        print("=" * 60)

        # Add rashi to seva_bookings
        print("\n1️⃣  Adding rashi field to seva_bookings table...")
        try:
            db.execute(
                text(
                    """
                ALTER TABLE seva_bookings
                ADD COLUMN rashi VARCHAR(50)
            """
                )
            )
            db.commit()
            print("   ✅ Added rashi field to seva_bookings")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("   ⏭️  Column already exists, skipping")
                db.rollback()
            else:
                raise

        print("\n" + "=" * 60)
        print("✅ Migration 003 completed successfully!")
        print("\nℹ️  The rashi field is now available for seva bookings")
        print("   Next: Update frontend to include Rashi, Gothra, and Nakshatra dropdowns")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def downgrade():
    """
    Remove rashi column from seva_bookings table
    """
    db = SessionLocal()

    try:
        print("Reverting Migration 003: Remove Rashi Field")
        print("=" * 60)

        # Remove rashi from seva_bookings
        print("\n1️⃣  Removing rashi from seva_bookings...")
        db.execute(text("ALTER TABLE seva_bookings DROP COLUMN IF EXISTS rashi"))
        db.commit()
        print("   ✅ Removed")

        print("\n✅ Migration 003 reverted successfully!")

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
