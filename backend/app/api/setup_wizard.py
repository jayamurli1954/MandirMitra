"""
First-login setup wizard status API.
Computes onboarding readiness from existing temple configuration.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.temple_context import require_temple_id_for_user
from app.core.security import get_current_user
from app.models.accounting import JournalEntry
from app.models.donation import Donation
from app.models.seva import SevaBooking
from app.models.temple import Temple
from app.models.upi_banking import BankAccount
from app.models.user import User

router = APIRouter(prefix="/api/v1/setup-wizard", tags=["setup-wizard"])


def _resolve_current_temple_id(db: Session, current_user: User) -> int | None:
    return require_temple_id_for_user(db, current_user, active_only=False)


@router.get('/status')
def get_setup_wizard_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    temple_id = _resolve_current_temple_id(db, current_user)
    if not temple_id:
        raise HTTPException(status_code=404, detail='Temple not found')

    bootstrap_email = (settings.BOOTSTRAP_ADMIN_EMAIL or '').strip().lower()
    current_email = (current_user.email or '').strip().lower()
    is_platform_super_admin = current_user.role == 'super_admin' or bool(bootstrap_email and current_email == bootstrap_email)
    can_manage_setup = current_user.role in {'admin', 'temple_manager'} and not is_platform_super_admin

    temple = db.query(Temple).filter(Temple.id == temple_id).first()
    if not temple:
        raise HTTPException(status_code=404, detail='Temple not found')

    active_bank_accounts = db.query(BankAccount).filter(
        BankAccount.temple_id == temple_id,
        BankAccount.is_active == True,
    ).count()
    active_users = db.query(User).filter(
        User.temple_id == temple_id,
        User.is_active == True,
    ).count()

    profile_checks = {
        'temple_or_trust_name': bool((temple.name or '').strip() or (temple.trust_name or '').strip()),
        'address': bool((temple.address or '').strip()),
        'city': bool((temple.city or '').strip()),
        'state': bool((temple.state or '').strip()),
        'phone': bool((temple.phone or '').strip()),
        'email': bool((temple.email or '').strip()),
    }
    receipt_checks = {
        'financial_year_start_month': bool(temple.financial_year_start_month),
        'receipt_prefix_donation': bool((temple.receipt_prefix_donation or '').strip()),
        'receipt_prefix_seva': bool((temple.receipt_prefix_seva or '').strip()),
    }

    steps = [
        {
            'id': 'temple_profile',
            'title': 'Temple / Trust Details',
            'description': 'Temple name or trust name, address, and primary contacts',
            'required': True,
            'completed': all(profile_checks.values()),
            'details': profile_checks,
        },
        {
            'id': 'receipt_settings',
            'title': 'Receipt & Financial Settings',
            'description': 'Financial year and receipt prefixes',
            'required': True,
            'completed': all(receipt_checks.values()),
            'details': receipt_checks,
        },
        {
            'id': 'bank_account',
            'title': 'Primary Bank Account',
            'description': 'At least one active bank account is required',
            'required': True,
            'completed': active_bank_accounts > 0,
            'details': {
                'active_bank_accounts': active_bank_accounts,
            },
        },
        {
            'id': 'invite_users',
            'title': 'Invite Staff',
            'description': 'Add accountant, priest, or staff users',
            'required': False,
            'completed': active_users > 1,
            'details': {
                'active_users': active_users,
            },
        },
    ]

    active_donations = db.query(Donation).filter(
        Donation.temple_id == temple_id,
        Donation.is_cancelled.isnot(True),
    ).count()
    active_seva_bookings = db.query(SevaBooking).filter(
        SevaBooking.temple_id == temple_id,
        SevaBooking.status != 'cancelled',
    ).count()
    accounting_entries = db.query(JournalEntry).filter(
        JournalEntry.temple_id == temple_id,
    ).count()

    has_operational_activity = any([
        active_donations > 0,
        active_seva_bookings > 0,
        accounting_entries > 0,
    ])

    first_incomplete_required = next((index for index, step in enumerate(steps) if step['required'] and not step['completed']), None)
    required_complete = first_incomplete_required is None
    force_setup = bool(can_manage_setup and not required_complete and not has_operational_activity)

    return {
        'temple_id': temple.id,
        'temple_name': temple.name,
        'can_manage_setup': can_manage_setup,
        'force_setup': force_setup,
        'needs_setup': not required_complete,
        'setup_complete': required_complete,
        'is_platform_super_admin': is_platform_super_admin,
        'active_step': first_incomplete_required if first_incomplete_required is not None else min(len(steps) - 1, 3),
        'steps': steps,
        'summary': {
            'active_bank_accounts': active_bank_accounts,
            'active_users': active_users,
            'active_donations': active_donations,
            'active_seva_bookings': active_seva_bookings,
            'accounting_entries': accounting_entries,
            'has_operational_activity': has_operational_activity,
        },
    }
