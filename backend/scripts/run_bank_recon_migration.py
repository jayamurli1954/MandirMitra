import sqlite3
import os
import sys

# Add backend to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_migration():
    # Try to find the database
    db_paths = [
        "data/temple.db",
        "mandir_mitra.db",
        "backend/data/temple.db"
    ]
    
    db_path = None
    for p in db_paths:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            db_path = p
            break
            
    if not db_path:
        db_path = "mandir_mitra.db" # Fallback
    
    print(f"Running migration on {db_path}...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(journal_lines)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_cleared' not in columns:
            print("Adding is_cleared column...")
            cursor.execute("ALTER TABLE journal_lines ADD COLUMN is_cleared BOOLEAN DEFAULT 1")
        
        if 'cleared_at' not in columns:
            print("Adding cleared_at column...")
            cursor.execute("ALTER TABLE journal_lines ADD COLUMN cleared_at TIMESTAMP NULL")
            
        # Create index if not exists
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_journal_lines_is_cleared ON journal_lines (is_cleared)")
        
        conn.commit()
        conn.close()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
