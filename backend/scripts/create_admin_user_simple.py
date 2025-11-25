"""
Create Admin User - Simple SQL Approach
Bypasses ORM relationship issues by using raw SQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.security import get_password_hash

def create_admin_user():
    """Create or update admin user using raw SQL"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Hash password
    password_hash = get_password_hash("admin123")
    
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
                # Update existing user
                conn.execute(text("""
                    UPDATE users 
                    SET password_hash = :password_hash,
                        is_active = true,
                        role = 'temple_manager',
                        full_name = COALESCE(full_name, 'Admin User')
                    WHERE email = 'admin@temple.com'
                """), {"password_hash": password_hash})
                conn.commit()
                print("✅ Admin user UPDATED:")
                print(f"   Email: admin@temple.com")
                print(f"   Password: admin123")
                print(f"   Role: temple_manager")
                print(f"   Active: true")
            else:
                # Create new user
                conn.execute(text("""
                    INSERT INTO users (email, password_hash, full_name, role, is_active, is_superuser, created_at, updated_at)
                    VALUES ('admin@temple.com', :password_hash, 'Admin User', 'temple_manager', true, true, NOW(), NOW())
                """), {"password_hash": password_hash})
                conn.commit()
                print("✅ Admin user CREATED:")
                print(f"   Email: admin@temple.com")
                print(f"   Password: admin123")
                print(f"   Role: temple_manager")
                print(f"   Active: true")
            
            print("\n" + "="*50)
            print("✅ LOGIN CREDENTIALS:")
            print("="*50)
            print("   Email:    admin@temple.com")
            print("   Password: admin123")
            print("="*50)
            print("\n✅ You can now login with these credentials!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            raise

if __name__ == "__main__":
    create_admin_user()


