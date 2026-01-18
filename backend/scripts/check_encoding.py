
import sys
import os
from sqlalchemy import create_engine, text

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app.core.config import settings

def check_encoding():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n--- Checking Seva Data ---")
        try:
            result = conn.execute(text("SELECT name_english, name_kannada FROM sevas LIMIT 5"))
            for row in result:
                print(f"English: {row[0]}")
                print(f"Kannada: {row[1]}")
                print(f"Kannada Repr: {ascii(row[1])}") # Show python's representation
                print("-" * 20)
        except Exception as e:
            print(f"Error reading sevas: {e}")

if __name__ == "__main__":
    check_encoding()
