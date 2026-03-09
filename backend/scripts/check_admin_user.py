"""Quick script to check or create the configured bootstrap admin user."""

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash


def check_admin_user():
    admin_email = (settings.BOOTSTRAP_ADMIN_EMAIL or 'admin@temple.com').strip().lower()
    admin_password = settings.BOOTSTRAP_ADMIN_PASSWORD or 'admin123'

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == admin_email).first()
        if user:
            print('Admin user found:')
            print(f'  Email: {user.email}')
            print(f'  Role: {user.role}')
            print(f'  Active: {user.is_active}')
            print(f'  Full Name: {user.full_name}')
            return

        print('Admin user not found')
        print('Creating admin user...')
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
        print(f'Admin user created: {admin_email} / {admin_password}')
    finally:
        db.close()


if __name__ == '__main__':
    check_admin_user()
