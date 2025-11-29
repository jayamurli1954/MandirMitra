"""
Licensing module for MandirSync
Handles trial periods and license validation
"""

from .license_manager import LicenseManager, LicenseType, LicenseStatus
from .trial_validator import check_trial_status, is_trial_active

__all__ = [
    "LicenseManager",
    "LicenseType",
    "LicenseStatus",
    "check_trial_status",
    "is_trial_active",
]
