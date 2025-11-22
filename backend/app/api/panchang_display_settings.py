"""
Panchang Display Settings API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.panchang_display_settings import (
    PanchangDisplaySettingsCreate,
    PanchangDisplaySettingsUpdate,
    PanchangDisplaySettingsResponse,
)
from app.services.panchang_display_settings_service import PanchangDisplaySettingsService

router = APIRouter(
    prefix="/api/v1/panchang/display-settings",
    tags=["panchang-display-settings"]
)


@router.get(
    "/",
    response_model=PanchangDisplaySettingsResponse,
    summary="Get panchang display settings",
    description="Get panchang display settings for the current user's temple"
)
def get_display_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get panchang display settings for the temple"""
    if not current_user.temple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a temple"
        )
    
    service = PanchangDisplaySettingsService(db)
    settings = service.get_or_create_default(current_user.temple_id)
    
    return settings


@router.get(
    "/temple/{temple_id}",
    response_model=PanchangDisplaySettingsResponse,
    summary="Get panchang display settings by temple ID",
    description="Get panchang display settings for a specific temple (admin only)"
)
def get_display_settings_by_temple(
    temple_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get panchang display settings for a specific temple"""
    # Check if user has permission (admin or same temple)
    if not current_user.is_superuser and current_user.temple_id != temple_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this temple's settings"
        )
    
    service = PanchangDisplaySettingsService(db)
    settings = service.get_or_create_default(temple_id)
    
    return settings


@router.post(
    "/",
    response_model=PanchangDisplaySettingsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create panchang display settings",
    description="Create new panchang display settings for a temple"
)
def create_display_settings(
    settings_data: PanchangDisplaySettingsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create panchang display settings"""
    # Check permissions
    if not current_user.is_superuser:
        if not current_user.temple_id or current_user.temple_id != settings_data.temple_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create settings for this temple"
            )
    
    service = PanchangDisplaySettingsService(db)
    
    try:
        settings = service.create(settings_data)
        return settings
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/",
    response_model=PanchangDisplaySettingsResponse,
    summary="Update panchang display settings",
    description="Update panchang display settings for the current user's temple"
)
def update_display_settings(
    settings_data: PanchangDisplaySettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update panchang display settings"""
    if not current_user.temple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a temple"
        )
    
    service = PanchangDisplaySettingsService(db)
    
    try:
        settings = service.update(current_user.temple_id, settings_data)
        return settings
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/temple/{temple_id}",
    response_model=PanchangDisplaySettingsResponse,
    summary="Update panchang display settings by temple ID",
    description="Update panchang display settings for a specific temple (admin only)"
)
def update_display_settings_by_temple(
    temple_id: int,
    settings_data: PanchangDisplaySettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update panchang display settings for a specific temple"""
    # Check permissions
    if not current_user.is_superuser and current_user.temple_id != temple_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this temple's settings"
        )
    
    service = PanchangDisplaySettingsService(db)
    
    try:
        settings = service.update(temple_id, settings_data)
        return settings
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/apply-preset/{preset_name}",
    response_model=PanchangDisplaySettingsResponse,
    summary="Apply preset configuration",
    description="Apply a preset configuration (minimal, standard, comprehensive) to temple settings"
)
def apply_preset(
    preset_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply a preset configuration to panchang display settings"""
    if not current_user.temple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a temple"
        )
    
    service = PanchangDisplaySettingsService(db)
    
    try:
        settings = service.apply_preset(current_user.temple_id, preset_name)
        return settings
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/reset",
    response_model=PanchangDisplaySettingsResponse,
    summary="Reset to default settings",
    description="Reset panchang display settings to default values"
)
def reset_to_defaults(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset panchang display settings to defaults"""
    if not current_user.temple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a temple"
        )
    
    service = PanchangDisplaySettingsService(db)
    settings = service.reset_to_defaults(current_user.temple_id)
    
    return settings


@router.get(
    "/presets",
    summary="Get available presets",
    description="Get list of available preset configurations"
)
def get_available_presets(db: Session = Depends(get_db)):
    """Get available preset configurations"""
    service = PanchangDisplaySettingsService(db)
    presets = service.get_available_presets()
    
    return {
        "success": True,
        "data": presets
    }


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete panchang display settings",
    description="Delete panchang display settings for the current user's temple"
)
def delete_display_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete panchang display settings"""
    if not current_user.temple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a temple"
        )
    
    service = PanchangDisplaySettingsService(db)
    deleted = service.delete(current_user.temple_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panchang display settings not found"
        )
    
    return None

