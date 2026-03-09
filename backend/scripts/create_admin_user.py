"""
Create or Update Bootstrap Admin User
Ensures the configured bootstrap admin exists.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.temple import Temple
from app.models.user import User
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.core.config import settings


def create_admin_user():
    """Create or update bootstrap admin user."""
    admin_email = (settings.BOOTSTRAP_ADMIN_EMAIL or 'admin@temple.com').strip().lower()
    admin_password = settings.BOOTSTRAP_ADMIN_PASSWORD or 'admin123'

    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == admin_email).first()

        if admin_user:
            admin_user.password_hash = get_password_hash(admin_password)
            admin_user.is_active = True
            admin_user.role = 'super_admin'
            admin_user.is_superuser = True
            if not admin_user.full_name:
                admin_user.full_name = 'Admin User'
            db.commit()
            print('Admin user updated:')
            print(f'  Email: {admin_user.email}')
            print(f'  Password: {admin_password}')
            print(f'  Role: {admin_user.role}')
            print(f'  Active: {admin_user.is_active}')
        else:
            admin_user = User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                full_name='Admin User',
                role='super_admin',
                is_active=True,
                is_superuser=True,
            )
            db.add(admin_user)
            db.commit()
            print('Admin user created:')
            print(f'  Email: {admin_user.email}')
            print(f'  Password: {admin_password}')
            print(f'  Role: {admin_user.role}')
            print(f'  Active: {admin_user.is_active}')

        print()
        print('Login credentials:')
        print(f'  Email: {admin_email}')
        print(f'  Password: {admin_password}')

    except Exception as e:
        print(f'Error: {e}')
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    create_admin_user()
