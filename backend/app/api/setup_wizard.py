"""
First-login setup wizard status API.
Computes onboarding readiness from existing temple configuration.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.temple import Temple
from app.models.upi_banking import BankAccount
from app.models.user import User

router = APIRouter(prefix="/api/v1/setup-wizard", tags=["setup-wizard"])


def _resolve_current_temple_id(db: Session, current_user: User) -> int | None:
    if current_user.temple_id:
        return current_user.temple_id

    first_temple = db.query(Temple.id).filter(Temple.is_active == True).order_by(Temple.id.asc()).first()
    return first_temple.id if first_temple else None


@router.get('/status')
def get_setup_wizard_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    temple_id = _resolve_current_temple_id(db, current_user)
    if not temple_id:
        raise HTTPException(status_code=404, detail='Temple not found')

    can_manage_setup = current_user.role in {'admin', 'temple_manager', 'super_admin'} or bool(current_user.is_superuser)

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
        'name': bool((temple.name or '').strip()),
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
            'title': 'Temple Details',
            'description': 'Temple identity, address, and primary contacts',
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

    first_incomplete_required = next((index for index, step in enumerate(steps) if step['required'] and not step['completed']), None)
    required_complete = first_incomplete_required is None

    return {
        'temple_id': temple.id,
        'temple_name': temple.name,
        'can_manage_setup': can_manage_setup,
        'needs_setup': not required_complete,
        'setup_complete': required_complete,
        'active_step': first_incomplete_required if first_incomplete_required is not None else min(len(steps) - 1, 3),
        'steps': steps,
        'summary': {
            'active_bank_accounts': active_bank_accounts,
            'active_users': active_users,
        },
    }
