"""
Dashboard API Endpoints
Provides statistics for dashboard display
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, datetime, timedelta
from typing import Dict

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.donation import Donation
from app.models.seva import SevaBooking, SevaBookingStatus
from app.models.devotee import Devotee
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.services.ready_reckoner_service import ReadyReckonerService

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get dashboard statistics:
    - Today's donations and cumulative (month/year)
    - Today's sevas and cumulative (month/year)
    """
    # For standalone mode, if temple_id is None, get the first temple or use None
    temple_id = current_user.temple_id
    if temple_id is None:
        # In standalone mode, get all donations (temple_id can be None)
        temple_id = None

    today = date.today()
    current_month = today.month
    current_year = today.year

    # Calculate month start and end dates
    month_start = date(current_year, current_month, 1)
    if current_month == 12:
        month_end = date(current_year + 1, 1, 1)
    else:
        month_end = date(current_year, current_month + 1, 1)

    # Calculate year start and end dates
    year_start = date(current_year, 4, 1)  # Financial year starts April
    if today.month >= 4:
        year_end = date(current_year + 1, 4, 1)
    else:
        year_start = date(current_year - 1, 4, 1)
        year_end = date(current_year, 4, 1)

    # ===== DONATIONS =====

    # Today's donations
    today_filter = [Donation.donation_date == today, Donation.is_cancelled == False]
    if temple_id is not None:
        today_filter.append(Donation.temple_id == temple_id)

    today_donations_query = (
        db.query(func.sum(Donation.amount).label("total"), func.count(Donation.id).label("count"))
        .filter(*today_filter)
        .first()
    )

    today_donations = float(today_donations_query.total or 0) if today_donations_query else 0
    today_donations_count = int(today_donations_query.count or 0) if today_donations_query else 0

    # Month cumulative donations
    month_filter = [
        Donation.donation_date >= month_start,
        Donation.donation_date < month_end,
        Donation.is_cancelled == False,
    ]
    if temple_id is not None:
        month_filter.append(Donation.temple_id == temple_id)

    month_donations_query = (
        db.query(func.sum(Donation.amount).label("total"), func.count(Donation.id).label("count"))
        .filter(*month_filter)
        .first()
    )

    month_donations = float(month_donations_query.total or 0) if month_donations_query else 0
    month_donations_count = int(month_donations_query.count or 0) if month_donations_query else 0

    # Year cumulative donations
    year_filter = [
        Donation.donation_date >= year_start,
        Donation.donation_date < year_end,
        Donation.is_cancelled == False,
    ]
    if temple_id is not None:
        year_filter.append(Donation.temple_id == temple_id)

    year_donations_query = (
        db.query(func.sum(Donation.amount).label("total"), func.count(Donation.id).label("count"))
        .filter(*year_filter)
        .first()
    )

    year_donations = float(year_donations_query.total or 0) if year_donations_query else 0
    year_donations_count = int(year_donations_query.count or 0) if year_donations_query else 0

    # ===== SEVAS =====
    # Count based on when booking was created (payment date), not when seva is performed
    # This includes advance bookings in today/month/year totals since money is collected at booking time

    # Today's sevas (bookings created today, regardless of seva date)
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    today_sevas_query = (
        db.query(
            func.sum(SevaBooking.amount_paid).label("total"),
            func.count(SevaBooking.id).label("count"),
        )
        .filter(
            SevaBooking.created_at >= today_start,
            SevaBooking.created_at <= today_end,
            SevaBooking.status != SevaBookingStatus.CANCELLED,
        )
        .first()
    )

    today_sevas = float(today_sevas_query.total or 0) if today_sevas_query else 0
    today_sevas_count = int(today_sevas_query.count or 0) if today_sevas_query else 0

    # Month cumulative sevas (bookings created this month)
    month_start_dt = datetime.combine(month_start, datetime.min.time())
    month_end_dt = datetime.combine(month_end, datetime.min.time())

    month_sevas_query = (
        db.query(
            func.sum(SevaBooking.amount_paid).label("total"),
            func.count(SevaBooking.id).label("count"),
        )
        .filter(
            SevaBooking.created_at >= month_start_dt,
            SevaBooking.created_at < month_end_dt,
            SevaBooking.status != SevaBookingStatus.CANCELLED,
        )
        .first()
    )

    month_sevas = float(month_sevas_query.total or 0) if month_sevas_query else 0
    month_sevas_count = int(month_sevas_query.count or 0) if month_sevas_query else 0

    # Year cumulative sevas (bookings created this financial year)
    year_start_dt = datetime.combine(year_start, datetime.min.time())
    year_end_dt = datetime.combine(year_end, datetime.min.time())

    year_sevas_query = (
        db.query(
            func.sum(SevaBooking.amount_paid).label("total"),
            func.count(SevaBooking.id).label("count"),
        )
        .filter(
            SevaBooking.created_at >= year_start_dt,
            SevaBooking.created_at < year_end_dt,
            SevaBooking.status != SevaBookingStatus.CANCELLED,
        )
        .first()
    )

    year_sevas = float(year_sevas_query.total or 0) if year_sevas_query else 0
    year_sevas_count = int(year_sevas_query.count or 0) if year_sevas_query else 0

    return {
        "donations": {
            "today": {"amount": today_donations, "count": today_donations_count},
            "month": {"amount": month_donations, "count": month_donations_count},
            "year": {"amount": year_donations, "count": year_donations_count},
        },
        "sevas": {
            "today": {"amount": today_sevas, "count": today_sevas_count},
            "month": {"amount": month_sevas, "count": month_sevas_count},
            "year": {"amount": year_sevas, "count": year_sevas_count},
        },
        "period": {
            "today": today.isoformat(),
            "month_start": month_start.isoformat(),
            "month_end": (month_end).isoformat(),
            "year_start": year_start.isoformat(),
            "year_end": year_end.isoformat(),
        },
    }


@router.get("/sacred-events")
def get_sacred_events(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get upcoming sacred events for Ready Reckoner widget
    Returns pre-calculated dates for Nakshatra, Ekadashi, Pradosha, etc.
    """
    temple_id = current_user.temple_id

    # Get temple's panchang settings for location
    panchang_settings = (
        db.query(PanchangDisplaySettings)
        .filter(PanchangDisplaySettings.temple_id == temple_id)
        .first()
    )

    # Default location (will be used if cache doesn't exist, but cache should have location)
    lat = 12.9716
    lon = 77.5946
    city = "Bengaluru"

    if panchang_settings and panchang_settings.latitude and panchang_settings.longitude:
        lat = float(panchang_settings.latitude)
        lon = float(panchang_settings.longitude)
        city = panchang_settings.city_name or "Bengaluru"

    # Initialize service
    service = ReadyReckonerService(db)

    # Get dashboard data (this reads from cache)
    result = service.get_dashboard_data(temple_id=temple_id)

    return result


@router.post("/sacred-events/pre-calculate")
def trigger_pre_calculation(
    days_ahead: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    Trigger pre-calculation of sacred events cache
    Admin/Manager only - Should be called via daily cron job

    Args:
        days_ahead: Number of days to calculate ahead (default: 30)
    """
    # Check permissions
    if current_user.role not in ["admin", "temple_manager"] and not current_user.is_superuser:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Only admins can trigger pre-calculation")

    temple_id = current_user.temple_id

    # Get temple's panchang settings for location
    panchang_settings = (
        db.query(PanchangDisplaySettings)
        .filter(PanchangDisplaySettings.temple_id == temple_id)
        .first()
    )

    # Default to Bangalore if settings not found
    lat = 12.9716
    lon = 77.5946
    city = "Bengaluru"

    if panchang_settings and panchang_settings.latitude and panchang_settings.longitude:
        lat = float(panchang_settings.latitude)
        lon = float(panchang_settings.longitude)
        city = panchang_settings.city_name or "Bengaluru"

    # Calculate date range
    start_date = date.today()
    end_date = start_date + timedelta(days=days_ahead)

    # Initialize service and pre-calculate
    service = ReadyReckonerService(db)
    result = service.pre_calculate_dates(
        temple_id=temple_id, start_date=start_date, end_date=end_date, lat=lat, lon=lon, city=city
    )

    return result


@router.get("/sacred-events/nakshatra/{nakshatra_name}")
def find_nakshatra_dates(
    nakshatra_name: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    Find next occurrences of a specific nakshatra (birth star)

    This helps counter clerks quickly find dates when a devotee's birth star occurs.

    Args:
        nakshatra_name: Name of the nakshatra (e.g., "Rohini", "Pushya", "Anuradha")
        limit: Number of upcoming occurrences to return (default: 5)

    Returns:
        Dict with nakshatra info and next occurrence dates
    """
    temple_id = current_user.temple_id

    # Get temple's panchang settings for location
    panchang_settings = (
        db.query(PanchangDisplaySettings)
        .filter(PanchangDisplaySettings.temple_id == temple_id)
        .first()
    )

    # Default location
    lat = 12.9716
    lon = 77.5946
    city = "Bengaluru"

    if panchang_settings and panchang_settings.latitude and panchang_settings.longitude:
        lat = float(panchang_settings.latitude)
        lon = float(panchang_settings.longitude)
        city = panchang_settings.city_name or "Bengaluru"

    # Initialize service
    service = ReadyReckonerService(db)

    # Find nakshatra dates (this reads from cache)
    result = service.find_next_nakshatra(
        temple_id=temple_id, nakshatra_name=nakshatra_name, limit=limit
    )

    return result
