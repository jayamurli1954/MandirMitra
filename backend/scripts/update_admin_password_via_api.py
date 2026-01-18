"""
Update Admin Password via Database Direct Update
This script updates the password hash in the database using a bcrypt hash
that will be compatible with passlib's verification
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use the same approach as the server - import after monkey patch
import bcrypt
if not hasattr(bcrypt, '__about__'):
    class MockAbout:
        __version__ = bcrypt.__version__
    bcrypt.__about__ = MockAbout()

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.auto_setup import is_standalone_mode, setup_standalone_database
import os as os_module

def create_bcrypt_hash(password: str) -> str:
    """Create a bcrypt hash that passlib can verify"""
    # Truncate password to 72 bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    # Generate hash with bcrypt - passlib expects $2b$ prefix format
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def update_password():
    """Update admin password in database"""
    # Get database URL (same as server)
    if is_standalone_mode():
        db_url = setup_standalone_database()
    else:
        db_url = os_module.environ.get("DATABASE_URL", settings.DATABASE_URL)
    
    engine = create_engine(db_url)
    
    # Create hash
    password_hash = create_bcrypt_hash("admin123")
    now = datetime.utcnow().isoformat()
    
    print(f"Generated hash (first 50 chars): {password_hash[:50]}...")
    print(f"Hash format: {'$2b$' if password_hash.startswith('$2b$') else 'Other'}")
    
    with engine.begin() as conn:  # Use begin() for automatic transaction
        # Check if user exists
        result = conn.execute(text("""
            SELECT id, email FROM users WHERE email = 'admin@temple.com'
        """))
        user = result.fetchone()
        
        if user:
            # Update existing user
            conn.execute(text("""
                UPDATE users 
                SET password_hash = :password_hash,
                    updated_at = :updated_at
                WHERE email = 'admin@temple.com'
            """), {"password_hash": password_hash, "updated_at": now})
            print("[OK] Admin user password UPDATED in database")
        else:
            # Create new user
            is_active_val = 1 if db_url.startswith("sqlite") else True
            is_superuser_val = 1 if db_url.startswith("sqlite") else True
            conn.execute(text("""
                INSERT INTO users (email, password_hash, full_name, role, is_active, is_superuser, created_at, updated_at)
                VALUES ('admin@temple.com', :password_hash, 'Admin User', 'temple_manager', :is_active, :is_superuser, :created_at, :updated_at)
            """), {
                "password_hash": password_hash,
                "is_active": is_active_val,
                "is_superuser": is_superuser_val,
                "created_at": now,
                "updated_at": now
            })
            print("[OK] Admin user CREATED in database")
        
        print("\n" + "="*50)
        print("LOGIN CREDENTIALS:")
        print("="*50)
        print("   Email:    admin@temple.com")
        print("   Password: admin123")
        print("="*50)

if __name__ == "__main__":
    update_password()








