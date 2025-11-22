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
    Provides accurate Vedic Panchang calculations
    """
    # Get current date and time
    now = datetime.now()

    # Calculate real panchang using Swiss Ephemeris
    panchang_data = panchang_service.calculate_panchang(now)

    # Return calculated panchang data
    return panchang_data

