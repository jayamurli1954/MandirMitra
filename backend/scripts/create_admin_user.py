"""
Create or Update Admin User
Ensures admin@temple.com / admin123 exists
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models first to ensure relationships are configured
from app.models.temple import Temple
from app.models.user import User
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine

from app.core.database import SessionLocal
from app.core.security import get_password_hash

def create_admin_user():
    """Create or update admin user"""
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@temple.com").first()
        
        if admin_user:
            # Update password to ensure it's correct
            admin_user.password_hash = get_password_hash("admin123")
            admin_user.is_active = True
            admin_user.role = "temple_manager"  # or "admin" if you prefer
            if not admin_user.full_name:
                admin_user.full_name = "Admin User"
            db.commit()
            print("✅ Admin user updated:")
            print(f"   Email: {admin_user.email}")
            print(f"   Password: admin123")
            print(f"   Role: {admin_user.role}")
            print(f"   Active: {admin_user.is_active}")
        else:
            # Create new admin user
            admin_user = User(
                email="admin@temple.com",
                password_hash=get_password_hash("admin123"),
                full_name="Admin User",
                role="temple_manager",
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created:")
            print(f"   Email: {admin_user.email}")
            print(f"   Password: admin123")
            print(f"   Role: {admin_user.role}")
            print(f"   Active: {admin_user.is_active}")
        
        print("\n✅ Login credentials:")
        print("   Email: admin@temple.com")
        print("   Password: admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()

