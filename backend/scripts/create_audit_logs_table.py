"""
Python script to create audit_logs table
Alternative to running SQL directly - uses SQLAlchemy
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.core.database import engine, init_db


def create_audit_logs_table():
    """
    Create audit_logs table using SQLAlchemy
    """
    print("Creating audit_logs table...")
    print("=" * 60)
    
    # SQL script content
    sql_script = """
    CREATE TABLE IF NOT EXISTS audit_logs (
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
    );

    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs(entity_type);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_id ON audit_logs(entity_id);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_user_role ON audit_logs(user_role);
    """
    
    try:
        with engine.connect() as conn:
            # Execute each statement separately
            statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                if statement:
                    try:
                        conn.execute(text(statement))
                        print(f"✅ Executed: {statement[:50]}...")
                    except Exception as e:
                        # Ignore "already exists" errors
                        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                            print(f"⚠️  Already exists: {statement[:50]}...")
                        else:
                            print(f"❌ Error: {str(e)}")
                            print(f"   Statement: {statement[:100]}")
            
            conn.commit()
        
        print("=" * 60)
        print("✅ Audit logs table created successfully!")
        print()
        print("Next step: Run Step 2 to create clerk users")
        print("   python -m scripts.create_clerk_users --num-clerks 3 --password clerk123")
        
    except Exception as e:
        print(f"❌ Error creating audit_logs table: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    create_audit_logs_table()









