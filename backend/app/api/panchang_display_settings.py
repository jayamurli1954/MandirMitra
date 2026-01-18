"""
Panchang Display Settings API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.panchang_display_settings import (
    PanchangDisplaySettingsCreate,
    PanchangDisplaySettingsUpdate,
    PanchangDisplaySettingsResponse,
)
from app.services.panchang_display_settings_service import PanchangDisplaySettingsService

router = APIRouter(prefix="/api/v1/panchang/display-settings", tags=["panchang-display-settings"])


@router.get(
    "/",
    response_model=PanchangDisplaySettingsResponse,
    summary="Get panchang display settings",
    description="Get panchang display settings for the current user's temple",
)
def get_display_settings(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get panchang display settings for the temple"""
    if not current_user.temple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not associated with a temple"
        )

    service = PanchangDisplaySettingsService(db)
    settings = service.get_or_create_default(current_user.temple_id)

    return settings


@router.get(
    "/temple/{temple_id}",
    response_model=PanchangDisplaySettingsResponse,
    summary="Get panchang display settings by temple ID",
    description="Get panchang display settings for a specific temple (admin only)",
)
def get_display_settings_by_temple(
    temple_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get panchang display settings for a specific temple"""
    # Check if user has permission (admin or same temple)
    if not current_user.is_superuser and current_user.temple_id != temple_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this temple's settings",
        )

    service = PanchangDisplaySettingsService(db)
    settings = service.get_or_create_default(temple_id)

    return settings


@router.post(
    "/",
    response_model=PanchangDisplaySettingsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create panchang display settings",
    description="Create new panchang display settings for a temple",
)
def create_display_settings(
    settings_data: PanchangDisplaySettingsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create panchang display settings"""
    # Check permissions
    if not current_user.is_superuser:
        if not current_user.temple_id or current_user.temple_id != settings_data.temple_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create settings for this temple",
            )

    service = PanchangDisplaySettingsService(db)

    try:
        settings = service.create(settings_data)
        return settings
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/",
    response_model=PanchangDisplaySettingsResponse,
    summary="Update panchang display settings",
    description="Update panchang display settings for the current user's temple",
)
def update_display_settings(
    settings_data: PanchangDisplaySettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update panchang display settings"""
    if not current_user.temple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not associated with a temple"
        )

    service = PanchangDisplaySettingsService(db)

    try:
        settings = service.update(current_user.temple_id, settings_data)
        return settings
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/temple/{temple_id}",
    response_model=PanchangDisplaySettingsResponse,
    summary="Update panchang display settings by temple ID",
    description="Update panchang display settings for a specific temple (admin only)",
)
def update_display_settings_by_temple(
    temple_id: int,
    settings_data: PanchangDisplaySettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update panchang display settings for a specific temple"""
    # Check permissions
    if not current_user.is_superuser and current_user.temple_id != temple_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this temple's settings",
        )

    service = PanchangDisplaySettingsService(db)

    try:
        settings = service.update(temple_id, settings_data)
        return settings
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/apply-preset/{preset_name}",
    response_model=PanchangDisplaySettingsResponse,
    summary="Apply preset configuration",
    description="Apply a preset configuration (minimal, standard, comprehensive) to temple settings",
)
def apply_preset(
    preset_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Apply a preset configuration to panchang display settings"""
    if not current_user.temple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not associated with a temple"
        )

    service = PanchangDisplaySettingsService(db)

    try:
        settings = service.apply_preset(current_user.temple_id, preset_name)
        return settings
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/reset",
    response_model=PanchangDisplaySettingsResponse,
    summary="Reset to default settings",
    description="Reset panchang display settings to default values",
)
def reset_to_defaults(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Reset panchang display settings to defaults"""
    if not current_user.temple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not associated with a temple"
        )

    service = PanchangDisplaySettingsService(db)
    settings = service.reset_to_defaults(current_user.temple_id)

    return settings


@router.get(
    "/presets",
    summary="Get available presets",
    description="Get list of available preset configurations",
)
def get_available_presets(db: Session = Depends(get_db)):
    """Get available preset configurations"""
    service = PanchangDisplaySettingsService(db)
    presets = service.get_available_presets()

    return {"success": True, "data": presets}


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete panchang display settings",
    description="Delete panchang display settings for the current user's temple",
)
def delete_display_settings(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Delete panchang display settings"""
    if not current_user.temple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not associated with a temple"
        )

    service = PanchangDisplaySettingsService(db)
    deleted = service.delete(current_user.temple_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Panchang display settings not found"
        )

    return None


# City Coordinates organized by region
CITY_COORDINATES = {
    "karnataka": [
        {
            "name": "Bengaluru",
            "lat": "12.9716",
            "lon": "77.5946",
            "display": "Bengaluru (Bangalore)",
        },
        {"name": "Mysuru", "lat": "12.2958", "lon": "76.6394", "display": "Mysuru (Mysore)"},
        {
            "name": "Mangaluru",
            "lat": "12.9141",
            "lon": "74.8560",
            "display": "Mangaluru (Mangalore)",
        },
        {"name": "Hubballi", "lat": "15.3647", "lon": "75.1240", "display": "Hubballi-Dharwad"},
        {"name": "Belagavi", "lat": "15.8497", "lon": "74.4977", "display": "Belagavi (Belgaum)"},
        {"name": "Davanagere", "lat": "14.4644", "lon": "75.9244", "display": "Davanagere"},
        {"name": "Ballari", "lat": "15.1394", "lon": "76.9214", "display": "Ballari (Bellary)"},
        {
            "name": "Vijayapura",
            "lat": "16.8302",
            "lon": "75.7100",
            "display": "Vijayapura (Bijapur)",
        },
        {
            "name": "Shivamogga",
            "lat": "13.9299",
            "lon": "75.5681",
            "display": "Shivamogga (Shimoga)",
        },
        {"name": "Tumakuru", "lat": "13.3392", "lon": "77.1011", "display": "Tumakuru (Tumkur)"},
        {"name": "Raichur", "lat": "16.2120", "lon": "77.3439", "display": "Raichur"},
        {"name": "Bidar", "lat": "17.9134", "lon": "77.5199", "display": "Bidar"},
        {"name": "Udupi", "lat": "13.3409", "lon": "74.7421", "display": "Udupi"},
        {"name": "Hassan", "lat": "13.0033", "lon": "76.0977", "display": "Hassan"},
        {"name": "Chitradurga", "lat": "14.2226", "lon": "76.3981", "display": "Chitradurga"},
        {"name": "Mandya", "lat": "12.5244", "lon": "76.8956", "display": "Mandya"},
        {"name": "Chikkamagaluru", "lat": "13.3161", "lon": "75.7720", "display": "Chikkamagaluru"},
        {"name": "Kolar", "lat": "13.1376", "lon": "78.1294", "display": "Kolar"},
    ],
    "south_india": [
        {"name": "Chennai", "lat": "13.0827", "lon": "80.2707", "display": "Chennai (Tamil Nadu)"},
        {
            "name": "Hyderabad",
            "lat": "17.3850",
            "lon": "78.4867",
            "display": "Hyderabad (Telangana)",
        },
        {
            "name": "Coimbatore",
            "lat": "11.0168",
            "lon": "76.9558",
            "display": "Coimbatore (Tamil Nadu)",
        },
        {"name": "Kochi", "lat": "9.9312", "lon": "76.2673", "display": "Kochi (Kerala)"},
        {
            "name": "Thiruvananthapuram",
            "lat": "8.5241",
            "lon": "76.9366",
            "display": "Thiruvananthapuram (Kerala)",
        },
        {"name": "Madurai", "lat": "9.9252", "lon": "78.1198", "display": "Madurai (Tamil Nadu)"},
        {
            "name": "Vijayawada",
            "lat": "16.5062",
            "lon": "80.6480",
            "display": "Vijayawada (Andhra Pradesh)",
        },
        {
            "name": "Visakhapatnam",
            "lat": "17.6868",
            "lon": "83.2185",
            "display": "Visakhapatnam (Andhra Pradesh)",
        },
        {
            "name": "Tirupati",
            "lat": "13.6288",
            "lon": "79.4192",
            "display": "Tirupati (Andhra Pradesh)",
        },
        {
            "name": "Tiruchirappalli",
            "lat": "10.7905",
            "lon": "78.7047",
            "display": "Tiruchirappalli (Tamil Nadu)",
        },
        {"name": "Salem", "lat": "11.6643", "lon": "78.1460", "display": "Salem (Tamil Nadu)"},
        {
            "name": "Tirunelveli",
            "lat": "8.7139",
            "lon": "77.7567",
            "display": "Tirunelveli (Tamil Nadu)",
        },
        {"name": "Kozhikode", "lat": "11.2588", "lon": "75.7804", "display": "Kozhikode (Kerala)"},
        {"name": "Warangal", "lat": "17.9689", "lon": "79.5941", "display": "Warangal (Telangana)"},
        {
            "name": "Guntur",
            "lat": "16.3067",
            "lon": "80.4365",
            "display": "Guntur (Andhra Pradesh)",
        },
        {"name": "Thrissur", "lat": "10.5276", "lon": "76.2144", "display": "Thrissur (Kerala)"},
        {"name": "Vellore", "lat": "12.9165", "lon": "79.1325", "display": "Vellore (Tamil Nadu)"},
        {
            "name": "Thanjavur",
            "lat": "10.7870",
            "lon": "79.1378",
            "display": "Thanjavur (Tamil Nadu)",
        },
    ],
    "major_cities": [
        {"name": "Delhi", "lat": "28.6139", "lon": "77.2090", "display": "Delhi"},
        {"name": "Mumbai", "lat": "19.0760", "lon": "72.8777", "display": "Mumbai"},
        {"name": "Kolkata", "lat": "22.5726", "lon": "88.3639", "display": "Kolkata"},
        {"name": "Pune", "lat": "18.5204", "lon": "73.8567", "display": "Pune"},
        {"name": "Ahmedabad", "lat": "23.0225", "lon": "72.5714", "display": "Ahmedabad"},
        {"name": "Jaipur", "lat": "26.9124", "lon": "75.7873", "display": "Jaipur"},
        {"name": "Surat", "lat": "21.1702", "lon": "72.8311", "display": "Surat"},
        {"name": "Lucknow", "lat": "26.8467", "lon": "80.9462", "display": "Lucknow"},
        {"name": "Kanpur", "lat": "26.4499", "lon": "80.3319", "display": "Kanpur"},
        {"name": "Nagpur", "lat": "21.1458", "lon": "79.0882", "display": "Nagpur"},
        {"name": "Indore", "lat": "22.7196", "lon": "75.8577", "display": "Indore"},
        {"name": "Bhopal", "lat": "23.2599", "lon": "77.4126", "display": "Bhopal"},
        {"name": "Patna", "lat": "25.5941", "lon": "85.1376", "display": "Patna"},
        {"name": "Vadodara", "lat": "22.3072", "lon": "73.1812", "display": "Vadodara"},
        {"name": "Ludhiana", "lat": "30.9010", "lon": "75.8573", "display": "Ludhiana"},
        {"name": "Agra", "lat": "27.1767", "lon": "78.0081", "display": "Agra"},
        {"name": "Varanasi", "lat": "25.3176", "lon": "82.9739", "display": "Varanasi"},
        {"name": "Amritsar", "lat": "31.6340", "lon": "74.8723", "display": "Amritsar"},
        {"name": "Chandigarh", "lat": "30.7333", "lon": "76.7794", "display": "Chandigarh"},
        {"name": "Guwahati", "lat": "26.1445", "lon": "91.7362", "display": "Guwahati"},
        {"name": "Bhubaneswar", "lat": "20.2961", "lon": "85.8245", "display": "Bhubaneswar"},
        {"name": "Ranchi", "lat": "23.3441", "lon": "85.3096", "display": "Ranchi"},
        {"name": "Noida", "lat": "28.5355", "lon": "77.3910", "display": "Noida"},
    ],
}


@router.get(
    "/cities",
    summary="Get available cities for location selection",
    description="Get organized list of Indian cities with coordinates (Karnataka first, then South India, then major cities)",
)
def get_available_cities():
    """Get available cities organized by region"""
    return {
        "success": True,
        "data": CITY_COORDINATES,
        "message": "Cities organized by region: karnataka, south_india, major_cities",
    }
