"""Update a legacy bootstrap admin email to the configured email."""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User


def update_admin_email():
    old_email = os.environ.get('OLD_ADMIN_EMAIL', 'admin@temple.com').strip().lower()
    new_email = (os.environ.get('NEW_ADMIN_EMAIL') or settings.BOOTSTRAP_ADMIN_EMAIL or '').strip().lower()

    if not new_email:
        print('Set NEW_ADMIN_EMAIL or BOOTSTRAP_ADMIN_EMAIL before running this script.')
        return 1

    db = SessionLocal()
    try:
        target_user = db.query(User).filter(func.lower(User.email) == new_email).first()
        if target_user:
            print(f'Target email already exists: {new_email}')
            return 0

        admin_user = db.query(User).filter(func.lower(User.email) == old_email).first()
        if not admin_user:
            print(f'Legacy admin user not found: {old_email}')
            return 1

        admin_user.email = new_email
        admin_user.updated_at = datetime.utcnow().isoformat()
        db.commit()
        print(f'Updated admin email from {old_email} to {new_email}')
        return 0
    except Exception as exc:
        db.rollback()
        print(f'Failed to update admin email: {exc}')
        return 1
    finally:
        db.close()


if __name__ == '__main__':
    raise SystemExit(update_admin_email())
