"""
License API endpoints
Handles trial activation, license checking, and upgrades
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.licensing import (
    get_license_manager,
    LicenseType,
    LicenseStatus,
    check_trial_status,
)


router = APIRouter(prefix="/api/license", tags=["License"])


# Request/Response Models
class TrialActivationRequest(BaseModel):
    """Request to activate trial"""
    temple_name: str
    contact_email: Optional[EmailStr] = None
    trial_days: int = 15  # Default 15 days


class LicenseActivationRequest(BaseModel):
    """Request to activate full license"""
    temple_name: str
    license_key: str
    contact_email: Optional[EmailStr] = None


class ExtendTrialRequest(BaseModel):
    """Request to extend trial"""
    additional_days: int


class LicenseResponse(BaseModel):
    """License information response"""
    temple_name: Optional[str] = None
    license_type: Optional[str] = None
    status: str
    message: str
    is_active: bool
    days_remaining: Optional[int] = None
    expires_at: Optional[str] = None
    is_grace_period: Optional[bool] = False
    grace_days_left: Optional[int] = None


@router.post("/activate-trial", response_model=LicenseResponse)
async def activate_trial(request: TrialActivationRequest):
    """
    Activate a new trial license

    This endpoint creates a trial license for the specified temple.
    Trial period can be 10, 15, or 30 days.
    """
    try:
        manager = get_license_manager()

        # Check if license already exists
        existing = manager.get_license_info()
        if existing and existing.get("status") != LicenseStatus.INVALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License already exists. Deactivate first to create new trial."
            )

        # Create trial
        license_data = manager.create_trial_license(
            temple_name=request.temple_name,
            trial_days=request.trial_days,
            contact_email=request.contact_email,
        )

        # Get status
        status_info = manager.check_license_status()

        return LicenseResponse(
            temple_name=license_data.get("temple_name"),
            license_type=license_data.get("license_type"),
            status=status_info.get("status"),
            message=f"Trial activated successfully! {request.trial_days} days remaining.",
            is_active=True,
            days_remaining=request.trial_days,
            expires_at=license_data.get("expires_at"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate trial: {str(e)}"
        )


@router.post("/activate-full", response_model=LicenseResponse)
async def activate_full_license(request: LicenseActivationRequest):
    """
    Activate a full license

    This endpoint activates a full/premium license with the provided license key.
    """
    try:
        manager = get_license_manager()

        # TODO: Validate license key against your licensing server
        # For now, accepting any key

        # Check if trial exists (for upgrade)
        existing = manager.get_license_info()
        if existing and existing.get("license_type") == LicenseType.TRIAL:
            # Upgrade trial to full
            license_data = manager.upgrade_trial_to_full(
                license_key=request.license_key,
                license_type=LicenseType.FULL,
                expires_at=None,  # Lifetime
            )
        else:
            # Create new full license
            license_data = manager.create_full_license(
                temple_name=request.temple_name,
                license_key=request.license_key,
                license_type=LicenseType.FULL,
                contact_email=request.contact_email,
                expires_at=None,  # Lifetime
            )

        return LicenseResponse(
            temple_name=license_data.get("temple_name"),
            license_type=license_data.get("license_type"),
            status=LicenseStatus.ACTIVE,
            message="Full license activated successfully!",
            is_active=True,
            expires_at=None,  # Lifetime
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate license: {str(e)}"
        )


@router.get("/status", response_model=LicenseResponse)
async def get_license_status():
    """
    Get current license status

    This endpoint returns the current license status, including:
    - Whether it's active or expired
    - Days remaining (for trial/time-limited licenses)
    - Grace period information
    """
    status_info = check_trial_status()

    return LicenseResponse(
        temple_name=status_info.get("temple_name"),
        license_type=status_info.get("license_type"),
        status=status_info.get("status"),
        message=status_info.get("message"),
        is_active=status_info.get("is_active", False),
        days_remaining=status_info.get("days_remaining"),
        expires_at=status_info.get("expires_at"),
        is_grace_period=status_info.get("is_grace_period", False),
        grace_days_left=status_info.get("grace_days_left"),
    )


@router.post("/extend-trial", response_model=LicenseResponse)
async def extend_trial(request: ExtendTrialRequest):
    """
    Extend trial period

    Admin endpoint to extend an existing trial by additional days.
    """
    try:
        manager = get_license_manager()

        license_data = manager.extend_trial(
            additional_days=request.additional_days
        )

        status_info = manager.check_license_status()

        return LicenseResponse(
            temple_name=license_data.get("temple_name"),
            license_type=license_data.get("license_type"),
            status=status_info.get("status"),
            message=f"Trial extended by {request.additional_days} days",
            is_active=True,
            days_remaining=status_info.get("days_remaining"),
            expires_at=license_data.get("expires_at"),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extend trial: {str(e)}"
        )


@router.delete("/deactivate")
async def deactivate_license():
    """
    Deactivate/remove current license

    Admin endpoint to remove the license file.
    Use with caution!
    """
    try:
        manager = get_license_manager()
        success = manager.deactivate_license()

        if success:
            return {"message": "License deactivated successfully"}
        else:
            return {"message": "No license found to deactivate"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate license: {str(e)}"
        )
