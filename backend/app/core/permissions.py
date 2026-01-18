"""
Role-Based Access Control (RBAC)
Define permissions for different user roles
"""

from typing import List, Set
from enum import Enum
from fastapi import HTTPException, status
from app.models.user import User


class Permission(str, Enum):
    """System permissions"""

    # Donations
    VIEW_DONATIONS = "view_donations"
    CREATE_DONATIONS = "create_donations"
    EDIT_DONATIONS = "edit_donations"
    DELETE_DONATIONS = "delete_donations"
    EXPORT_DONATIONS = "export_donations"

    # Sevas
    VIEW_SEVAS = "view_sevas"
    CREATE_SEVAS = "create_sevas"
    EDIT_SEVAS = "edit_sevas"
    DELETE_SEVAS = "delete_sevas"
    RESCHEDULE_SEVAS = "reschedule_sevas"
    APPROVE_RESCHEDULE = "approve_reschedule"

    # Devotees
    VIEW_DEVOTEES = "view_devotees"
    CREATE_DEVOTEES = "create_devotees"
    EDIT_DEVOTEES = "edit_devotees"
    DELETE_DEVOTEES = "delete_devotees"
    VIEW_DEVOTEE_PHONE = "view_devotee_phone"  # Sensitive
    VIEW_DEVOTEE_ADDRESS = "view_devotee_address"  # Sensitive

    # Accounting
    VIEW_ACCOUNTS = "view_accounts"
    CREATE_ACCOUNTS = "create_accounts"
    EDIT_ACCOUNTS = "edit_accounts"
    DELETE_ACCOUNTS = "delete_accounts"
    VIEW_JOURNAL_ENTRIES = "view_journal_entries"
    CREATE_JOURNAL_ENTRIES = "create_journal_entries"
    POST_JOURNAL_ENTRIES = "post_journal_entries"
    VIEW_REPORTS = "view_reports"
    EXPORT_REPORTS = "export_reports"

    # Users
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"

    # Audit Logs
    VIEW_AUDIT_LOGS = "view_audit_logs"

    # Settings
    VIEW_SETTINGS = "view_settings"
    EDIT_SETTINGS = "edit_settings"

    # Certificates (80G, etc.)
    VIEW_CERTIFICATES = "view_certificates"
    UPLOAD_CERTIFICATES = "upload_certificates"
    DOWNLOAD_CERTIFICATES = "download_certificates"
    DELETE_CERTIFICATES = "delete_certificates"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    "admin": set(Permission),  # Admin has all permissions
    "temple_manager": {
        Permission.VIEW_DONATIONS,
        Permission.CREATE_DONATIONS,
        Permission.EDIT_DONATIONS,
        Permission.VIEW_SEVAS,
        Permission.CREATE_SEVAS,
        Permission.EDIT_SEVAS,
        Permission.RESCHEDULE_SEVAS,
        Permission.APPROVE_RESCHEDULE,
        Permission.VIEW_DEVOTEES,
        Permission.CREATE_DEVOTEES,
        Permission.EDIT_DEVOTEES,
        Permission.VIEW_DEVOTEE_PHONE,
        Permission.VIEW_DEVOTEE_ADDRESS,
        Permission.VIEW_ACCOUNTS,
        Permission.VIEW_JOURNAL_ENTRIES,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_USERS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_SETTINGS,
        Permission.VIEW_CERTIFICATES,
        Permission.UPLOAD_CERTIFICATES,
        Permission.DOWNLOAD_CERTIFICATES,
    },
    "accountant": {
        Permission.VIEW_DONATIONS,
        Permission.VIEW_SEVAS,
        Permission.VIEW_DEVOTEES,
        Permission.VIEW_ACCOUNTS,
        Permission.CREATE_ACCOUNTS,
        Permission.EDIT_ACCOUNTS,
        Permission.VIEW_JOURNAL_ENTRIES,
        Permission.CREATE_JOURNAL_ENTRIES,
        Permission.POST_JOURNAL_ENTRIES,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_CERTIFICATES,
        Permission.DOWNLOAD_CERTIFICATES,
    },
    "staff": {
        Permission.VIEW_DONATIONS,
        Permission.CREATE_DONATIONS,
        Permission.VIEW_SEVAS,
        Permission.CREATE_SEVAS,
        Permission.VIEW_DEVOTEES,
        Permission.CREATE_DEVOTEES,
        Permission.EDIT_DEVOTEES,
    },
    "clerk": {
        Permission.VIEW_DONATIONS,
        Permission.CREATE_DONATIONS,
        Permission.VIEW_SEVAS,
        Permission.CREATE_SEVAS,
        Permission.VIEW_DEVOTEES,
        Permission.CREATE_DEVOTEES,
    },
    "priest": {
        Permission.VIEW_SEVAS,
        Permission.VIEW_DEVOTEES,
    },
}


def get_user_permissions(user: User) -> Set[Permission]:
    """
    Get permissions for a user based on their role
    """
    return ROLE_PERMISSIONS.get(user.role, set())


def has_permission(user: User, permission: Permission) -> bool:
    """
    Check if user has a specific permission
    """
    user_perms = get_user_permissions(user)
    return permission in user_perms


def require_permission(permission: Permission):
    """
    Decorator to require a specific permission
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get current_user from kwargs or args
            user = None
            if "current_user" in kwargs:
                user = kwargs["current_user"]
            elif args and hasattr(args[0], "current_user"):
                user = args[0].current_user

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
                )

            if not has_permission(user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value}",
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def check_permission(user: User, permission: Permission):
    """
    Check permission and raise exception if not allowed
    """
    if not has_permission(user, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied: {permission.value}"
        )
