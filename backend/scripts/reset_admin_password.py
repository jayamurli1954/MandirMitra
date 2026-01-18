"""
Reset Admin User Password
Updates the admin user's password using the new hashing function
Uses raw SQL to avoid ORM relationship issues
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.auto_setup import is_standalone_mode, setup_standalone_database
import os as os_module

# Monkey patch for passlib 1.7.4 compatibility with bcrypt 4.0.0+
import bcrypt
if not hasattr(bcrypt, '__about__'):
    class MockAbout:
        __version__ = bcrypt.__version__
    bcrypt.__about__ = MockAbout()

# Import after monkey patch
from app.core.security import get_password_hash

def reset_admin_password():
    """Reset admin user password using raw SQL"""
    # Get database URL
    if is_standalone_mode():
        db_url = setup_standalone_database()
    else:
        db_url = os_module.environ.get("DATABASE_URL", settings.DATABASE_URL)
    
    engine = create_engine(db_url)
    
    # Hash password using passlib's get_password_hash (which truncates properly)
    password_hash = get_password_hash("admin123")
    now = datetime.utcnow().isoformat()
    
    with engine.connect() as conn:
        try:
            # Check if user exists
            result = conn.execute(text("""
                SELECT id, email, role, is_active 
                FROM users 
                WHERE email = 'admin@temple.com'
            """))
            
            user = result.fetchone()
            
            if user:
                # Update existing user - use parameterized query for both SQLite and PostgreSQL
                update_sql = """
                    UPDATE users 
                    SET password_hash = :password_hash,
                        is_active = :is_active,
                        role = 'temple_manager',
                        full_name = COALESCE(full_name, 'Admin User'),
                        updated_at = :updated_at
                    WHERE email = 'admin@temple.com'
                """
                is_active_val = 1 if db_url.startswith("sqlite") else True
                conn.execute(text(update_sql), {
                    "password_hash": password_hash, 
                    "is_active": is_active_val,
                    "updated_at": now
                })
                conn.commit()
                print("[OK] Admin user password UPDATED:")
            else:
                # Create new user
                insert_sql = """
                    INSERT INTO users (email, password_hash, full_name, role, is_active, is_superuser, created_at, updated_at)
                    VALUES ('admin@temple.com', :password_hash, 'Admin User', 'temple_manager', :is_active, :is_superuser, :created_at, :updated_at)
                """
                is_active_val = 1 if db_url.startswith("sqlite") else True
                is_superuser_val = 1 if db_url.startswith("sqlite") else True
                conn.execute(text(insert_sql), {
                    "password_hash": password_hash,
                    "is_active": is_active_val,
                    "is_superuser": is_superuser_val,
                    "created_at": now,
                    "updated_at": now
                })
                conn.commit()
                print("[OK] Admin user CREATED:")
            
            print("   Email:    admin@temple.com")
            print("   Password: admin123")
            print("   Role:     temple_manager")
            print("   Active:   True")
            
            print("\n" + "="*50)
            print("[OK] ADMIN USER READY:")
            print("="*50)
            print("   Email:    admin@temple.com")
            print("   Password: admin123")
            print("="*50)
            print("\n[OK] You can now login with these credentials!")
            
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            raise

if __name__ == "__main__":
    reset_admin_password()

