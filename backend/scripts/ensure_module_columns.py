"""
Ensure module configuration columns exist in temples table
Works with both SQLite and PostgreSQL
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, db_url, column_exists, engine
from sqlalchemy import text


def ensure_module_columns():
    """Ensure all module configuration columns exist in temples table"""
    db = SessionLocal()
    try:
        is_sqlite = db_url.startswith("sqlite")
        
        columns_to_add = [
            ("module_hundi_enabled", "BOOLEAN DEFAULT 1"),
        ]
        
        for column_name, column_def in columns_to_add:
            if not column_exists(db, "temples", column_name):
                print(f"Adding column: {column_name}")
                
                if is_sqlite:
                    # SQLite doesn't support IF NOT EXISTS in ALTER TABLE
                    # So we just try to add it and ignore if it fails
                    try:
                        db.execute(
                            text(f"ALTER TABLE temples ADD COLUMN {column_name} {column_def}")
                        )
                        db.commit()
                        print(f"  [OK] Added {column_name}")
                    except Exception as e:
                        if "duplicate column" in str(e).lower():
                            print(f"  [INFO] Column {column_name} already exists")
                        else:
                            raise
                else:
                    # PostgreSQL supports IF NOT EXISTS
                    db.execute(
                        text(
                            f"ALTER TABLE temples ADD COLUMN IF NOT EXISTS {column_name} {column_def}"
                        )
                    )
                    db.commit()
                    print(f"  [OK] Added {column_name}")
            else:
                print(f"  [INFO] Column {column_name} already exists")
        
        print("\n[OK] All module columns verified!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("Ensuring module configuration columns exist...")
    print("-" * 60)
    ensure_module_columns()

