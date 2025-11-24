"""
Dashboard API Endpoints
Provides statistics for dashboard display
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, datetime
from typing import Dict

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.donation import Donation
from app.models.seva import SevaBooking, SevaBookingStatus
from app.models.devotee import Devotee

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    
    today_donations_query = db.query(
        func.sum(Donation.amount).label('total'),
        func.count(Donation.id).label('count')
    ).filter(*today_filter).first()
    
    today_donations = float(today_donations_query.total or 0) if today_donations_query else 0
    today_donations_count = int(today_donations_query.count or 0) if today_donations_query else 0
    
    # Month cumulative donations
    month_filter = [
        Donation.donation_date >= month_start,
        Donation.donation_date < month_end,
        Donation.is_cancelled == False
    ]
    if temple_id is not None:
        month_filter.append(Donation.temple_id == temple_id)
    
    month_donations_query = db.query(
        func.sum(Donation.amount).label('total'),
        func.count(Donation.id).label('count')
    ).filter(*month_filter).first()
    
    month_donations = float(month_donations_query.total or 0) if month_donations_query else 0
    month_donations_count = int(month_donations_query.count or 0) if month_donations_query else 0
    
    # Year cumulative donations
    year_filter = [
        Donation.donation_date >= year_start,
        Donation.donation_date < year_end,
        Donation.is_cancelled == False
    ]
    if temple_id is not None:
        year_filter.append(Donation.temple_id == temple_id)
    
    year_donations_query = db.query(
        func.sum(Donation.amount).label('total'),
        func.count(Donation.id).label('count')
    ).filter(*year_filter).first()
    
    year_donations = float(year_donations_query.total or 0) if year_donations_query else 0
    year_donations_count = int(year_donations_query.count or 0) if year_donations_query else 0
    
    # ===== SEVAS =====
    
    # Today's sevas (completed - current date or past)
    today_sevas_query = db.query(
        func.sum(SevaBooking.amount_paid).label('total'),
        func.count(SevaBooking.id).label('count')
    ).filter(
        SevaBooking.booking_date == today,
        SevaBooking.status != SevaBookingStatus.CANCELLED
    ).first()
    
    today_sevas = float(today_sevas_query.total or 0) if today_sevas_query else 0
    today_sevas_count = int(today_sevas_query.count or 0) if today_sevas_query else 0
    
    # Month cumulative sevas
    month_sevas_query = db.query(
        func.sum(SevaBooking.amount_paid).label('total'),
        func.count(SevaBooking.id).label('count')
    ).filter(
        SevaBooking.booking_date >= month_start,
        SevaBooking.booking_date < month_end,
        SevaBooking.status != SevaBookingStatus.CANCELLED
    ).first()
    
    month_sevas = float(month_sevas_query.total or 0) if month_sevas_query else 0
    month_sevas_count = int(month_sevas_query.count or 0) if month_sevas_query else 0
    
    # Year cumulative sevas
    year_sevas_query = db.query(
        func.sum(SevaBooking.amount_paid).label('total'),
        func.count(SevaBooking.id).label('count')
    ).filter(
        SevaBooking.booking_date >= year_start,
        SevaBooking.booking_date < year_end,
        SevaBooking.status != SevaBookingStatus.CANCELLED
    ).first()
    
    year_sevas = float(year_sevas_query.total or 0) if year_sevas_query else 0
    year_sevas_count = int(year_sevas_query.count or 0) if year_sevas_query else 0
    
    return {
        "donations": {
            "today": {
                "amount": today_donations,
                "count": today_donations_count
            },
            "month": {
                "amount": month_donations,
                "count": month_donations_count
            },
            "year": {
                "amount": year_donations,
                "count": year_donations_count
            }
        },
        "sevas": {
            "today": {
                "amount": today_sevas,
                "count": today_sevas_count
            },
            "month": {
                "amount": month_sevas,
                "count": month_sevas_count
            },
            "year": {
                "amount": year_sevas,
                "count": year_sevas_count
            }
        },
        "period": {
            "today": today.isoformat(),
            "month_start": month_start.isoformat(),
            "month_end": (month_end).isoformat(),
            "year_start": year_start.isoformat(),
            "year_end": year_end.isoformat()
        }
    }

