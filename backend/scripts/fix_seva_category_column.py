"""
Script to convert sevas.category from enum to VARCHAR
This fixes the issue where the database enum type doesn't match our lowercase values
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

def fix_category_column():
    """Convert category column from enum to VARCHAR"""
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        try:
            # Check current column type
            result = conn.execute(text("""
                SELECT data_type, udt_name 
                FROM information_schema.columns 
                WHERE table_name = 'sevas' AND column_name = 'category'
            """))
            row = result.fetchone()
            print(f"Current category column type: {row[0]} ({row[1]})")
            
            # If it's an enum, convert to VARCHAR
            if row[1] == 'sevacategory' or 'enum' in str(row[1]).lower():
                print("Converting category column from enum to VARCHAR...")
                
                # Step 1: Add a temporary column
                conn.execute(text("ALTER TABLE sevas ADD COLUMN category_new VARCHAR(50)"))
                
                # Step 2: Copy data (lowercase the enum values)
                conn.execute(text("""
                    UPDATE sevas 
                    SET category_new = LOWER(category::text)
                    WHERE category IS NOT NULL
                """))
                
                # Step 3: Drop the old column
                conn.execute(text("ALTER TABLE sevas DROP COLUMN category"))
                
                # Step 4: Rename the new column
                conn.execute(text("ALTER TABLE sevas RENAME COLUMN category_new TO category"))
                
                # Step 5: Make it NOT NULL if needed
                conn.execute(text("ALTER TABLE sevas ALTER COLUMN category SET NOT NULL"))
                
                print("Successfully converted category column to VARCHAR")
            else:
                print("Column is already VARCHAR, no changes needed")
            
            # Commit transaction
            trans.commit()
            print("Transaction committed successfully")
            
        except Exception as e:
            trans.rollback()
            print(f"Error: {str(e)}")
            raise

if __name__ == "__main__":
    print("Fixing sevas.category column type...")
    fix_category_column()
    print("Done!")

