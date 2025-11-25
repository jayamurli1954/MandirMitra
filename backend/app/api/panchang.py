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


@router.post("/kundli/generate")
def generate_kundli(
    birth_datetime: str,
    latitude: float,
    longitude: float,
    name: str = "Devotee",
    temple_name: Optional[str] = None,
    temple_logo_url: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate complete Kundli (Birth Chart) with:
    - Rasi Chart (D1) - South Indian style
    - Navamsa Chart (D9)
    - Vimshottari Dasha Table (120 years)
    - Returns HTML ready for PDF conversion
    
    birth_datetime: ISO format "YYYY-MM-DDTHH:MM:SS" (IST)
    """
    try:
        # Parse birth datetime
        dt_birth = datetime.fromisoformat(birth_datetime.replace('Z', '+05:30'))
        
        # Get temple name if not provided
        if not temple_name:
            from app.models.temple import Temple
            temple = db.query(Temple).filter(Temple.id == current_user.temple_id).first()
            temple_name = temple.name if temple else "MandirSync Temple"
        
        # Generate Kundli data
        kundli_data = panchang_service.generate_kundli_pdf_data(
            dt_birth=dt_birth,
            lat=latitude,
            lon=longitude,
            name=name,
            temple_name=temple_name,
            temple_logo_url=temple_logo_url or ""
        )
        
        return {
            "success": True,
            "kundli": kundli_data,
            "message": "Kundli generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating Kundli: {str(e)}")
