"""
Panchang API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.services.panchang_service import PanchangService

router = APIRouter(prefix="/api/v1/panchang", tags=["panchang"])

# Initialize Panchang Service
panchang_service = PanchangService()


@router.get("/today")
def get_today_panchang(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get today's panchang data using Swiss Ephemeris with Lahiri Ayanamsa
    Provides accurate Vedic Panchang calculations based on temple's location
    """
    # Get current date and time
    now = datetime.now()

    # Get temple's panchang settings for location
    panchang_settings = db.query(PanchangDisplaySettings).filter(
        PanchangDisplaySettings.temple_id == current_user.temple_id
    ).first()

    # Default to Bangalore if settings not found
    if panchang_settings and panchang_settings.latitude and panchang_settings.longitude:
        lat = float(panchang_settings.latitude)
        lon = float(panchang_settings.longitude)
        city = panchang_settings.city_name or "Bengaluru"
    else:
        # Fallback to Bangalore
        lat = 12.9716
        lon = 77.5946
        city = "Bengaluru"

    # Calculate real panchang using Swiss Ephemeris with temple's location
    panchang_data = panchang_service.calculate_panchang(now, lat, lon, city)

    # Return calculated panchang data
    return panchang_data

