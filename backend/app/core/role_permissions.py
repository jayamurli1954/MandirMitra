"""
Business-role templates and effective permission helpers.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.role_permission import RolePermissionProfile, UserRoleAssignment
from app.models.user import User

MODULE_PERMISSION_DEFINITIONS = [
    {"key": "dashboard", "label": "Dashboard", "description": "Allow access to the main dashboard."},
    {"key": "donations", "label": "Donations", "description": "Allow access to donation receipts and donation screens."},
    {"key": "sevas", "label": "Sevas", "description": "Allow access to seva booking and seva-related screens."},
    {"key": "devotees", "label": "Devotees", "description": "Allow access to devotee records."},
    {"key": "reports", "label": "Reports", "description": "Allow access to operational and financial reports."},
    {"key": "panchang", "label": "Panchang", "description": "Allow access to Panchang screens."},
    {"key": "settings", "label": "Settings", "description": "Allow access to settings and organization configuration."},
    {"key": "accounting", "label": "Accounting", "description": "Allow access to accounting pages."},
    {"key": "inventory", "label": "Inventory", "description": "Allow access to inventory pages when enabled."},
    {"key": "assets", "label": "Temple Assets", "description": "Allow access to temple asset pages when enabled."},
    {"key": "hr", "label": "HR & Salary", "description": "Allow access to HR and payroll pages when enabled."},
    {"key": "hundi", "label": "Hundi", "description": "Allow access to hundi pages when enabled."},
    {"key": "users", "label": "User Management", "description": "Allow access to user and role-management tools."},
    {"key": "backups", "label": "Backup Tools", "description": "Allow access to backup and restore controls."},
]

ACTION_PERMISSION_DEFINITIONS = [
    {"key": "create_donation_receipts", "label": "Create Donation Receipts", "description": "Record donation collections and issue receipts."},
    {"key": "create_seva_bookings", "label": "Create Seva Bookings", "description": "Book sevas and issue seva receipts."},
    {"key": "manage_devotees", "label": "Manage Devotees", "description": "Create or update devotee profiles."},
    {"key": "manage_seva_master", "label": "Manage Seva Master", "description": "Create or edit seva definitions and pricing."},
    {"key": "approve_seva_reschedule", "label": "Approve Seva Reschedule", "description": "Approve or reject seva reschedule requests."},
    {"key": "record_income_entries", "label": "Record Income Entries", "description": "Record miscellaneous income, cash, and bank receipts."},
    {"key": "record_expenses", "label": "Record Expenses", "description": "Record expense vouchers and cash/bank payments."},
    {"key": "create_journal_entries", "label": "Create Journal Entries", "description": "Create manual journal entries."},
    {"key": "post_journal_entries", "label": "Post Journal Entries", "description": "Post draft journal entries into accounts."},
    {"key": "reverse_accounting_entries", "label": "Reverse Accounting Entries", "description": "Reverse posted accounting transactions with a reason. No deletion or in-place cancellation is allowed."},
    {"key": "approve_accounting_reversals", "label": "Approve Accounting Reversals", "description": "Approve reversal requests for controlled audit trail."},
    {"key": "manage_bank_accounts", "label": "Manage Bank Accounts", "description": "Add or update bank accounts and payment accounts."},
    {"key": "manage_opening_balances", "label": "Manage Opening Balances", "description": "Upload or adjust opening balances."},
    {"key": "import_legacy_accounts", "label": "Import Legacy Accounts", "description": "Import legacy chart of accounts and opening balances."},
    {"key": "view_financial_reports", "label": "View Financial Reports", "description": "View ledger, trial balance, receipts and payments, income and expenditure, and balance sheet."},
    {"key": "approve_expenses", "label": "Approve Expenses", "description": "Approve expense vouchers when approval workflow is in use."},
    {"key": "approve_bank_payments", "label": "Approve Bank Payments", "description": "Approve high-value or bank-based payment disbursements."},
    {"key": "approve_period_closing", "label": "Approve Period Closing", "description": "Approve financial period close and lock operations."},
    {"key": "manage_users", "label": "Manage Users", "description": "Create, update, and deactivate users."},
    {"key": "manage_role_permissions", "label": "Manage Role Permissions", "description": "Enable or disable roles and edit the permission matrix."},
    {"key": "manage_temple_profile", "label": "Manage Temple / Trust Profile", "description": "Update temple/trust profile, receipt settings, and organization setup."},
    {"key": "manage_backups", "label": "Manage Backups", "description": "Create manual backups or access restore controls."},
    {"key": "view_audit_logs", "label": "View Audit Logs", "description": "Review audit logs and trace sensitive changes."},
]

MODULE_PERMISSION_KEYS = [item["key"] for item in MODULE_PERMISSION_DEFINITIONS]
ACTION_PERMISSION_KEYS = [item["key"] for item in ACTION_PERMISSION_DEFINITIONS]
ROLE_KEY_ORDER = [
    "president",
    "secretary",
    "treasurer",
    "counter_clerk",
    "accounts_clerk",
    "priest_operator",
]

DEFAULT_ROLE_KEY_BY_SYSTEM_ROLE = {
    "super_admin": "president",
    "admin": "president",
    "temple_manager": "secretary",
    "accountant": "treasurer",
    "counter_staff": "counter_clerk",
    "clerk": "counter_clerk",
    "staff": "priest_operator",
    "priest": "priest_operator",
}

SYSTEM_ROLE_FALLBACK_LABELS = {
    "super_admin": "Super Admin",
    "admin": "Admin",
    "temple_manager": "Temple Manager",
    "accountant": "Accountant",
    "counter_staff": "Counter Staff",
    "clerk": "Clerk",
    "staff": "Staff",
    "priest": "Priest",
}

ROLE_TEMPLATES: dict[str, dict[str, Any]] = {
    "president": {
        "display_name": "President",
        "description": "Governance and final approval role.",
        "mapped_system_role": "admin",
        "is_enabled": True,
        "module_permissions": {
            "dashboard": True, "donations": True, "sevas": True, "devotees": True,
            "reports": True, "panchang": True, "settings": True, "accounting": True,
            "inventory": False, "assets": False, "hr": False, "hundi": False,
            "users": True, "backups": False,
        },
        "action_permissions": {
            "create_donation_receipts": False, "create_seva_bookings": False, "manage_devotees": False,
            "manage_seva_master": False, "approve_seva_reschedule": True, "record_income_entries": False,
            "record_expenses": False, "create_journal_entries": False, "post_journal_entries": False,
            "reverse_accounting_entries": True, "approve_accounting_reversals": True,
            "manage_bank_accounts": True, "manage_opening_balances": True, "import_legacy_accounts": True,
            "view_financial_reports": True, "approve_expenses": True, "approve_bank_payments": True,
            "approve_period_closing": True, "manage_users": False, "manage_role_permissions": True,
            "manage_temple_profile": True, "manage_backups": False, "view_audit_logs": True,
        },
    },
    "secretary": {
        "display_name": "Secretary",
        "description": "Operations controller for users, masters, and day-to-day administration.",
        "mapped_system_role": "temple_manager",
        "is_enabled": True,
        "module_permissions": {
            "dashboard": True, "donations": True, "sevas": True, "devotees": True,
            "reports": True, "panchang": True, "settings": True, "accounting": True,
            "inventory": False, "assets": False, "hr": False, "hundi": False,
            "users": True, "backups": True,
        },
        "action_permissions": {
            "create_donation_receipts": True, "create_seva_bookings": True, "manage_devotees": True,
            "manage_seva_master": True, "approve_seva_reschedule": True, "record_income_entries": False,
            "record_expenses": False, "create_journal_entries": False, "post_journal_entries": False,
            "reverse_accounting_entries": False, "approve_accounting_reversals": False,
            "manage_bank_accounts": False, "manage_opening_balances": False, "import_legacy_accounts": False,
            "view_financial_reports": True, "approve_expenses": True, "approve_bank_payments": False,
            "approve_period_closing": False, "manage_users": True, "manage_role_permissions": True,
            "manage_temple_profile": True, "manage_backups": True, "view_audit_logs": True,
        },
    },
    "treasurer": {
        "display_name": "Treasurer",
        "description": "Primary finance operator for receipts, payments, and accounting.",
        "mapped_system_role": "accountant",
        "is_enabled": True,
        "module_permissions": {
            "dashboard": True, "donations": True, "sevas": True, "devotees": True,
            "reports": True, "panchang": True, "settings": False, "accounting": True,
            "inventory": False, "assets": False, "hr": False, "hundi": False,
            "users": False, "backups": False,
        },
        "action_permissions": {
            "create_donation_receipts": True, "create_seva_bookings": True, "manage_devotees": True,
            "manage_seva_master": False, "approve_seva_reschedule": True, "record_income_entries": True,
            "record_expenses": True, "create_journal_entries": True, "post_journal_entries": True,
            "reverse_accounting_entries": True, "approve_accounting_reversals": False,
            "manage_bank_accounts": True, "manage_opening_balances": True, "import_legacy_accounts": True,
            "view_financial_reports": True, "approve_expenses": True, "approve_bank_payments": True,
            "approve_period_closing": True, "manage_users": False, "manage_role_permissions": False,
            "manage_temple_profile": False, "manage_backups": False, "view_audit_logs": True,
        },
    },
    "counter_clerk": {
        "display_name": "Counter Clerk",
        "description": "Front-desk operator for collections and bookings.",
        "mapped_system_role": "counter_staff",
        "is_enabled": True,
        "module_permissions": {
            "dashboard": True, "donations": True, "sevas": True, "devotees": True,
            "reports": False, "panchang": True, "settings": False, "accounting": False,
            "inventory": False, "assets": False, "hr": False, "hundi": False,
            "users": False, "backups": False,
        },
        "action_permissions": {
            "create_donation_receipts": True, "create_seva_bookings": True, "manage_devotees": True,
            "manage_seva_master": False, "approve_seva_reschedule": False, "record_income_entries": False,
            "record_expenses": False, "create_journal_entries": False, "post_journal_entries": False,
            "reverse_accounting_entries": False, "approve_accounting_reversals": False,
            "manage_bank_accounts": False, "manage_opening_balances": False, "import_legacy_accounts": False,
            "view_financial_reports": False, "approve_expenses": False, "approve_bank_payments": False,
            "approve_period_closing": False, "manage_users": False, "manage_role_permissions": False,
            "manage_temple_profile": False, "manage_backups": False, "view_audit_logs": False,
        },
    },
    "accounts_clerk": {
        "display_name": "Accounts Clerk",
        "description": "Back-office accounting support role.",
        "mapped_system_role": "accountant",
        "is_enabled": True,
        "module_permissions": {
            "dashboard": True, "donations": False, "sevas": False, "devotees": False,
            "reports": True, "panchang": False, "settings": False, "accounting": True,
            "inventory": False, "assets": False, "hr": False, "hundi": False,
            "users": False, "backups": False,
        },
        "action_permissions": {
            "create_donation_receipts": False, "create_seva_bookings": False, "manage_devotees": False,
            "manage_seva_master": False, "approve_seva_reschedule": False, "record_income_entries": True,
            "record_expenses": True, "create_journal_entries": True, "post_journal_entries": False,
            "reverse_accounting_entries": False, "approve_accounting_reversals": False,
            "manage_bank_accounts": False, "manage_opening_balances": True, "import_legacy_accounts": True,
            "view_financial_reports": True, "approve_expenses": False, "approve_bank_payments": False,
            "approve_period_closing": False, "manage_users": False, "manage_role_permissions": False,
            "manage_temple_profile": False, "manage_backups": False, "view_audit_logs": False,
        },
    },
    "priest_operator": {
        "display_name": "Priest / Temple Operator",
        "description": "Fallback operating role for small temples where one person handles daily work.",
        "mapped_system_role": "staff",
        "is_enabled": False,
        "module_permissions": {
            "dashboard": True, "donations": True, "sevas": True, "devotees": True,
            "reports": True, "panchang": True, "settings": False, "accounting": False,
            "inventory": False, "assets": False, "hr": False, "hundi": False,
            "users": False, "backups": False,
        },
        "action_permissions": {
            "create_donation_receipts": True, "create_seva_bookings": True, "manage_devotees": True,
            "manage_seva_master": False, "approve_seva_reschedule": False, "record_income_entries": True,
            "record_expenses": True, "create_journal_entries": False, "post_journal_entries": False,
            "reverse_accounting_entries": False, "approve_accounting_reversals": False,
            "manage_bank_accounts": False, "manage_opening_balances": False, "import_legacy_accounts": False,
            "view_financial_reports": True, "approve_expenses": False, "approve_bank_payments": False,
            "approve_period_closing": False, "manage_users": False, "manage_role_permissions": False,
            "manage_temple_profile": False, "manage_backups": False, "view_audit_logs": False,
        },
    },
}


def _normalize_permission_map(source: dict[str, Any] | None, keys: list[str]) -> dict[str, bool]:
    source = source or {}
    return {key: bool(source.get(key, False)) for key in keys}


def get_default_role_payload(role_key: str) -> dict[str, Any]:
    template = deepcopy(ROLE_TEMPLATES[role_key])
    template["role_key"] = role_key
    template["module_permissions"] = _normalize_permission_map(template.get("module_permissions"), MODULE_PERMISSION_KEYS)
    template["action_permissions"] = _normalize_permission_map(template.get("action_permissions"), ACTION_PERMISSION_KEYS)
    return template


def get_effective_role_profiles(db: Session, temple_id: int | None) -> list[dict[str, Any]]:
    overrides_by_key: dict[str, RolePermissionProfile] = {}
    if temple_id:
        overrides = (
            db.query(RolePermissionProfile)
            .filter(RolePermissionProfile.temple_id == temple_id)
            .all()
        )
        overrides_by_key = {item.role_key: item for item in overrides}

    profiles: list[dict[str, Any]] = []
    for role_key in ROLE_KEY_ORDER:
        default_payload = get_default_role_payload(role_key)
        override = overrides_by_key.get(role_key)
        if override:
            default_payload.update(
                {
                    "id": override.id,
                    "display_name": override.display_name or default_payload["display_name"],
                    "description": override.description or default_payload["description"],
                    "mapped_system_role": override.mapped_system_role or default_payload["mapped_system_role"],
                    "is_enabled": bool(override.is_enabled),
                    "module_permissions": _normalize_permission_map(override.module_permissions, MODULE_PERMISSION_KEYS),
                    "action_permissions": _normalize_permission_map(override.action_permissions, ACTION_PERMISSION_KEYS),
                    "created_at": override.created_at,
                    "updated_at": override.updated_at,
                }
            )
        profiles.append(default_payload)
    return profiles


def get_role_profile_by_key(db: Session, temple_id: int | None, role_key: str) -> dict[str, Any] | None:
    for profile in get_effective_role_profiles(db, temple_id):
        if profile["role_key"] == role_key:
            return profile
    return None


def upsert_role_profile(
    db: Session,
    temple_id: int,
    role_key: str,
    is_enabled: bool,
    module_permissions: dict[str, Any] | None,
    action_permissions: dict[str, Any] | None,
) -> dict[str, Any]:
    template = get_default_role_payload(role_key)
    profile = (
        db.query(RolePermissionProfile)
        .filter(
            RolePermissionProfile.temple_id == temple_id,
            RolePermissionProfile.role_key == role_key,
        )
        .first()
    )
    if not profile:
        profile = RolePermissionProfile(
            temple_id=temple_id,
            role_key=role_key,
            display_name=template["display_name"],
            description=template["description"],
            mapped_system_role=template["mapped_system_role"],
        )
        db.add(profile)

    profile.display_name = template["display_name"]
    profile.description = template["description"]
    profile.mapped_system_role = template["mapped_system_role"]
    profile.is_enabled = bool(is_enabled)
    profile.module_permissions = _normalize_permission_map(module_permissions or template["module_permissions"], MODULE_PERMISSION_KEYS)
    profile.action_permissions = _normalize_permission_map(action_permissions or template["action_permissions"], ACTION_PERMISSION_KEYS)
    profile.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(profile)
    return get_role_profile_by_key(db, temple_id, role_key)


def get_assignable_role_options(db: Session, temple_id: int | None) -> list[dict[str, Any]]:
    return [
        {
            "role_key": profile["role_key"],
            "display_name": profile["display_name"],
            "mapped_system_role": profile["mapped_system_role"],
        }
        for profile in get_effective_role_profiles(db, temple_id)
        if profile.get("is_enabled")
    ]


def get_role_key_from_input(role_value: str | None) -> str | None:
    normalized = str(role_value or "").strip().lower()
    if normalized in ROLE_TEMPLATES:
        return normalized
    return DEFAULT_ROLE_KEY_BY_SYSTEM_ROLE.get(normalized)


def resolve_role_input(db: Session, temple_id: int | None, role_value: str | None) -> tuple[str, str | None, str]:
    normalized = str(role_value or "").strip().lower() or "priest_operator"
    role_key = get_role_key_from_input(normalized)

    if role_key:
        profile = get_role_profile_by_key(db, temple_id, role_key)
        if profile and not profile.get("is_enabled"):
            raise ValueError(f"Role '{profile['display_name']}' is disabled for this temple/trust")
        if profile:
            return profile["mapped_system_role"], role_key, profile["display_name"]

    return normalized, None, SYSTEM_ROLE_FALLBACK_LABELS.get(normalized, normalized.replace("_", " ").title())


def assign_role_to_user(db: Session, user: User, temple_id: int | None, role_key: str | None) -> None:
    if not user.id or not temple_id:
        return

    assignment = db.query(UserRoleAssignment).filter(UserRoleAssignment.user_id == user.id).first()
    if role_key:
        if not assignment:
            assignment = UserRoleAssignment(user_id=user.id, temple_id=temple_id, role_key=role_key)
            db.add(assignment)
        else:
            assignment.temple_id = temple_id
            assignment.role_key = role_key
            assignment.updated_at = datetime.utcnow().isoformat()
    elif assignment:
        db.delete(assignment)


def get_user_role_context(db: Session, user: User, temple_id: int | None = None) -> dict[str, Any]:
    effective_temple_id = temple_id or user.temple_id
    assignment = None
    if user.id:
        assignment = db.query(UserRoleAssignment).filter(UserRoleAssignment.user_id == user.id).first()
        if assignment and not effective_temple_id:
            effective_temple_id = assignment.temple_id

    role_key = assignment.role_key if assignment else DEFAULT_ROLE_KEY_BY_SYSTEM_ROLE.get(user.role)
    role_profile = get_role_profile_by_key(db, effective_temple_id, role_key) if role_key else None

    if role_profile:
        return {
            "system_role": user.role,
            "role_key": role_profile["role_key"],
            "role_label": role_profile["display_name"],
            "module_permissions": role_profile["module_permissions"],
            "action_permissions": role_profile["action_permissions"],
        }

    return {
        "system_role": user.role,
        "role_key": role_key or user.role,
        "role_label": SYSTEM_ROLE_FALLBACK_LABELS.get(user.role, user.role.replace("_", " ").title()),
        "module_permissions": {key: True for key in MODULE_PERMISSION_KEYS},
        "action_permissions": {key: False for key in ACTION_PERMISSION_KEYS},
    }
