"""
Migration 004: Add Location Fields to Panchang Display Settings

Adds latitude, longitude, city_name, and timezone fields to panchang_display_settings table
for accurate location-based panchang calculations.
"""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import SessionLocal


def upgrade():
    """
    Add location fields to panchang_display_settings table
    """
    db = SessionLocal()

    try:
        print("Running Migration 004: Add Location Fields to Panchang Settings")
        print("=" * 60)

        # Add latitude field
        print("\n1️⃣  Adding latitude field...")
        try:
            db.execute(
                text(
                    """
                ALTER TABLE panchang_display_settings
                ADD COLUMN latitude VARCHAR(20) DEFAULT '12.9716'
            """
                )
            )
            db.commit()
            print("   ✅ Added latitude field")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("   ⏭️  Column already exists, skipping")
                db.rollback()
            else:
                raise

        # Add longitude field
        print("\n2️⃣  Adding longitude field...")
        try:
            db.execute(
                text(
                    """
                ALTER TABLE panchang_display_settings
                ADD COLUMN longitude VARCHAR(20) DEFAULT '77.5946'
            """
                )
            )
            db.commit()
            print("   ✅ Added longitude field")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("   ⏭️  Column already exists, skipping")
                db.rollback()
            else:
                raise

        # Add city_name field
        print("\n3️⃣  Adding city_name field...")
        try:
            db.execute(
                text(
                    """
                ALTER TABLE panchang_display_settings
                ADD COLUMN city_name VARCHAR(100) DEFAULT 'Bengaluru'
            """
                )
            )
            db.commit()
            print("   ✅ Added city_name field")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("   ⏭️  Column already exists, skipping")
                db.rollback()
            else:
                raise

        # Add timezone field
        print("\n4️⃣  Adding timezone field...")
        try:
            db.execute(
                text(
                    """
                ALTER TABLE panchang_display_settings
                ADD COLUMN timezone VARCHAR(50) DEFAULT 'Asia/Kolkata'
            """
                )
            )
            db.commit()
            print("   ✅ Added timezone field")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("   ⏭️  Column already exists, skipping")
                db.rollback()
            else:
                raise

        print("\n" + "=" * 60)
        print("✅ Migration 004 completed successfully!")
        print("\nℹ️  Location fields added to panchang_display_settings:")
        print("   - latitude (default: 12.9716 - Bangalore)")
        print("   - longitude (default: 77.5946 - Bangalore)")
        print("   - city_name (default: Bengaluru)")
        print("   - timezone (default: Asia/Kolkata)")
        print(
            "\n📝 Next: Update your temple's location in Panchang Settings for accurate calculations"
        )

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def downgrade():
    """
    Remove location fields from panchang_display_settings table
    """
    db = SessionLocal()

    try:
        print("Reverting Migration 004: Remove Location Fields")
        print("=" * 60)

        # Remove latitude
        print("\n1️⃣  Removing latitude field...")
        db.execute(text("ALTER TABLE panchang_display_settings DROP COLUMN IF EXISTS latitude"))
        db.commit()
        print("   ✅ Removed")

        # Remove longitude
        print("\n2️⃣  Removing longitude field...")
        db.execute(text("ALTER TABLE panchang_display_settings DROP COLUMN IF EXISTS longitude"))
        db.commit()
        print("   ✅ Removed")

        # Remove city_name
        print("\n3️⃣  Removing city_name field...")
        db.execute(text("ALTER TABLE panchang_display_settings DROP COLUMN IF EXISTS city_name"))
        db.commit()
        print("   ✅ Removed")

        # Remove timezone
        print("\n4️⃣  Removing timezone field...")
        db.execute(text("ALTER TABLE panchang_display_settings DROP COLUMN IF EXISTS timezone"))
        db.commit()
        print("   ✅ Removed")

        print("\n✅ Migration 004 reverted successfully!")

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
