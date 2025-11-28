"""
Trial Validator - Middleware to check license on app startup
"""

from fastapi import HTTPException, status
from .license_manager import get_license_manager, LicenseStatus


def check_trial_status() -> dict:
    """
    Check trial/license status

    Returns:
        License status information

    Raises:
        HTTPException if license is expired or invalid
    """
    manager = get_license_manager()
    status_info = manager.check_license_status()

    return status_info


def is_trial_active() -> bool:
    """
    Quick check if trial/license is active

    Returns:
        True if active, False otherwise
    """
    status_info = check_trial_status()
    return status_info.get("is_active", False)


def require_active_license():
    """
    Dependency function to require active license

    Usage in FastAPI:
        @app.get("/api/protected", dependencies=[Depends(require_active_license)])

    Raises:
        HTTPException if license is not active
    """
    status_info = check_trial_status()

    if not status_info.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": status_info.get("message"),
                "status": status_info.get("status"),
                "action_required": "Please activate or renew your license",
            }
        )

    # Warn if in grace period
    if status_info.get("is_grace_period"):
        # You can log this or notify admins
        pass

    return status_info
