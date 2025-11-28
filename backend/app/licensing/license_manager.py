"""
License Manager for MandirSync
Handles trial periods, license validation, and expiry checking
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from typing import Optional, Dict, Any
import os


class LicenseType(str, Enum):
    """License types"""
    TRIAL = "trial"
    FULL = "full"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class LicenseStatus(str, Enum):
    """License status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALID = "invalid"
    NOT_FOUND = "not_found"


class LicenseManager:
    """
    Manages software licensing and trial periods

    Features:
    - Trial period management (10, 15, 30 days, etc.)
    - Automatic expiry checking
    - License upgrade support
    - Tamper protection with checksums
    - Grace period support
    """

    def __init__(self, license_file_path: Optional[str] = None):
        """
        Initialize License Manager

        Args:
            license_file_path: Path to license file. If None, uses default location.
        """
        if license_file_path:
            self.license_file = Path(license_file_path)
        else:
            # Store license file in application data directory
            app_data = os.getenv("APPDATA") or os.path.expanduser("~/.mandirsync")
            self.license_file = Path(app_data) / "license.dat"

        # Create directory if it doesn't exist
        self.license_file.parent.mkdir(parents=True, exist_ok=True)

    def _generate_checksum(self, data: Dict[str, Any]) -> str:
        """Generate checksum for license data to prevent tampering"""
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        # Add a secret salt (in production, use environment variable)
        salt = os.getenv("LICENSE_SALT", "mandirsync_secret_2025")
        combined = f"{sorted_data}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _validate_checksum(self, data: Dict[str, Any], stored_checksum: str) -> bool:
        """Validate checksum to detect tampering"""
        calculated = self._generate_checksum(data)
        return calculated == stored_checksum

    def create_trial_license(
        self,
        temple_name: str,
        trial_days: int = 15,
        contact_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new trial license

        Args:
            temple_name: Name of the temple
            trial_days: Number of days for trial (default: 15)
            contact_email: Contact email for the temple

        Returns:
            License information dictionary
        """
        now = datetime.utcnow()
        expiry_date = now + timedelta(days=trial_days)

        license_data = {
            "temple_name": temple_name,
            "license_type": LicenseType.TRIAL,
            "status": LicenseStatus.ACTIVE,
            "created_at": now.isoformat(),
            "activated_at": now.isoformat(),
            "expires_at": expiry_date.isoformat(),
            "trial_days": trial_days,
            "contact_email": contact_email,
            "version": "1.0.0",
        }

        # Generate checksum
        checksum = self._generate_checksum(license_data)

        # Save to file
        full_data = {
            "license": license_data,
            "checksum": checksum,
        }

        with open(self.license_file, "w") as f:
            json.dump(full_data, f, indent=2)

        return license_data

    def create_full_license(
        self,
        temple_name: str,
        license_key: str,
        license_type: LicenseType = LicenseType.FULL,
        contact_email: Optional[str] = None,
        expires_at: Optional[str] = None,  # None = lifetime
    ) -> Dict[str, Any]:
        """
        Create a full/premium/enterprise license

        Args:
            temple_name: Name of the temple
            license_key: License key provided to customer
            license_type: Type of license (FULL, PREMIUM, ENTERPRISE)
            contact_email: Contact email
            expires_at: Expiry date (None for lifetime license)

        Returns:
            License information dictionary
        """
        now = datetime.utcnow()

        license_data = {
            "temple_name": temple_name,
            "license_type": license_type,
            "license_key": license_key,
            "status": LicenseStatus.ACTIVE,
            "created_at": now.isoformat(),
            "activated_at": now.isoformat(),
            "expires_at": expires_at,  # None for lifetime
            "contact_email": contact_email,
            "version": "1.0.0",
        }

        # Generate checksum
        checksum = self._generate_checksum(license_data)

        # Save to file
        full_data = {
            "license": license_data,
            "checksum": checksum,
        }

        with open(self.license_file, "w") as f:
            json.dump(full_data, f, indent=2)

        return license_data

    def get_license_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current license information

        Returns:
            License data or None if not found
        """
        if not self.license_file.exists():
            return None

        try:
            with open(self.license_file, "r") as f:
                data = json.load(f)

            license_data = data.get("license")
            stored_checksum = data.get("checksum")

            # Validate checksum to detect tampering
            if not self._validate_checksum(license_data, stored_checksum):
                return {
                    "status": LicenseStatus.INVALID,
                    "message": "License file has been tampered with",
                }

            return license_data

        except Exception as e:
            return {
                "status": LicenseStatus.INVALID,
                "message": f"Error reading license: {str(e)}",
            }

    def check_license_status(self) -> Dict[str, Any]:
        """
        Check current license status

        Returns:
            Dictionary with status, message, and remaining days
        """
        license_info = self.get_license_info()

        if not license_info:
            return {
                "status": LicenseStatus.NOT_FOUND,
                "message": "No license found. Please activate your license.",
                "is_active": False,
            }

        # Check if already marked as invalid
        if license_info.get("status") == LicenseStatus.INVALID:
            return {
                "status": LicenseStatus.INVALID,
                "message": license_info.get("message", "Invalid license"),
                "is_active": False,
            }

        # Check expiry
        expires_at = license_info.get("expires_at")

        # No expiry = lifetime license
        if not expires_at:
            return {
                "status": LicenseStatus.ACTIVE,
                "message": "License is active (Lifetime)",
                "is_active": True,
                "license_type": license_info.get("license_type"),
                "temple_name": license_info.get("temple_name"),
            }

        # Check if expired
        expiry_date = datetime.fromisoformat(expires_at)
        now = datetime.utcnow()

        if now > expiry_date:
            # Grace period (2 days after expiry)
            grace_period_end = expiry_date + timedelta(days=2)

            if now > grace_period_end:
                return {
                    "status": LicenseStatus.EXPIRED,
                    "message": "License has expired. Please contact support to renew.",
                    "is_active": False,
                    "expired_on": expires_at,
                    "license_type": license_info.get("license_type"),
                }
            else:
                # In grace period
                grace_days_left = (grace_period_end - now).days
                return {
                    "status": LicenseStatus.ACTIVE,
                    "message": f"License expired. Grace period: {grace_days_left} days remaining",
                    "is_active": True,
                    "is_grace_period": True,
                    "grace_days_left": grace_days_left,
                    "license_type": license_info.get("license_type"),
                }

        # Active license
        days_remaining = (expiry_date - now).days

        return {
            "status": LicenseStatus.ACTIVE,
            "message": f"License is active. {days_remaining} days remaining.",
            "is_active": True,
            "days_remaining": days_remaining,
            "expires_at": expires_at,
            "license_type": license_info.get("license_type"),
            "temple_name": license_info.get("temple_name"),
        }

    def upgrade_trial_to_full(
        self,
        license_key: str,
        license_type: LicenseType = LicenseType.FULL,
        expires_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upgrade trial license to full license

        Args:
            license_key: License key for full version
            license_type: Type of full license
            expires_at: Expiry date (None for lifetime)

        Returns:
            Updated license information
        """
        current_license = self.get_license_info()

        if not current_license:
            raise ValueError("No existing license found")

        temple_name = current_license.get("temple_name")
        contact_email = current_license.get("contact_email")

        return self.create_full_license(
            temple_name=temple_name,
            license_key=license_key,
            license_type=license_type,
            contact_email=contact_email,
            expires_at=expires_at,
        )

    def extend_trial(self, additional_days: int) -> Dict[str, Any]:
        """
        Extend trial period

        Args:
            additional_days: Number of days to extend

        Returns:
            Updated license information
        """
        license_info = self.get_license_info()

        if not license_info:
            raise ValueError("No license found")

        if license_info.get("license_type") != LicenseType.TRIAL:
            raise ValueError("Can only extend trial licenses")

        # Calculate new expiry
        current_expiry = datetime.fromisoformat(license_info["expires_at"])
        new_expiry = current_expiry + timedelta(days=additional_days)

        # Update license data
        license_info["expires_at"] = new_expiry.isoformat()
        license_info["trial_days"] = license_info.get("trial_days", 0) + additional_days

        # Generate new checksum
        checksum = self._generate_checksum(license_info)

        # Save
        full_data = {
            "license": license_info,
            "checksum": checksum,
        }

        with open(self.license_file, "w") as f:
            json.dump(full_data, f, indent=2)

        return license_info

    def deactivate_license(self) -> bool:
        """
        Deactivate/remove license

        Returns:
            True if successful
        """
        if self.license_file.exists():
            self.license_file.unlink()
            return True
        return False


# Singleton instance
_license_manager = None


def get_license_manager() -> LicenseManager:
    """Get singleton license manager instance"""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager
