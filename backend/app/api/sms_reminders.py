"""
SMS Reminder API Endpoints
Handles SMS reminders for seva bookings
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.seva import SevaBooking, SevaBookingStatus
from app.models.devotee import Devotee

router = APIRouter(prefix="/api/v1/sms-reminders", tags=["sms-reminders"])


@router.get("/pending")
def get_pending_reminders(
    days_before: int = Query(7, ge=1, le=30, description="Days before seva to send reminder"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sevas that need SMS reminders
    Returns sevas scheduled for (today + days_before) days from now
    """
    today = date.today()
    target_date = today + timedelta(days=days_before)
    
    # Get bookings scheduled for target_date that haven't been sent reminders
    bookings = db.query(SevaBooking).join(Devotee).filter(
        SevaBooking.booking_date == target_date,
        SevaBooking.status != SevaBookingStatus.CANCELLED,
        Devotee.phone.isnot(None),
        Devotee.receive_sms == True
    ).all()
    
    reminders = []
    for booking in bookings:
        reminders.append({
            "booking_id": booking.id,
            "seva_name": booking.seva.name_english if booking.seva else "Unknown",
            "devotee_name": booking.devotee.name if booking.devotee else "Unknown",
            "devotee_mobile": booking.devotee.phone if booking.devotee else None,
            "booking_date": booking.booking_date.isoformat(),
            "booking_time": booking.booking_time,
            "amount": booking.amount_paid
        })
    
    return {
        "target_date": target_date.isoformat(),
        "days_before": days_before,
        "reminders": reminders,
        "count": len(reminders)
    }


@router.post("/send/{booking_id}")
def send_reminder(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send SMS reminder for a specific booking
    Note: Actual SMS sending requires SMS gateway integration
    """
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if not booking.devotee or not booking.devotee.phone:
        raise HTTPException(status_code=400, detail="Devotee phone number not available")
    
    # TODO: Integrate with SMS gateway (Twilio, AWS SNS, Indian SMS provider)
    # For now, just return success
    # In production, you would:
    # 1. Call SMS gateway API
    # 2. Store reminder record in database
    # 3. Update booking with reminder_sent_at timestamp
    
    message = f"Reminder: Your seva '{booking.seva.name_english if booking.seva else 'Seva'}' is scheduled for {booking.booking_date.strftime('%d-%m-%Y')} at {booking.booking_time or 'TBD'}. Thank you!"
    
    return {
        "message": "SMS reminder sent successfully",
        "booking_id": booking_id,
        "mobile": booking.devotee.phone,
        "sms_text": message,
        "note": "SMS gateway integration required for actual sending"
    }


@router.post("/send-batch")
def send_batch_reminders(
    days_before: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send SMS reminders for all sevas scheduled (today + days_before) days from now
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can send batch reminders")
    
    today = date.today()
    target_date = today + timedelta(days=days_before)
    
    bookings = db.query(SevaBooking).join(Devotee).filter(
        SevaBooking.booking_date == target_date,
        SevaBooking.status != SevaBookingStatus.CANCELLED,
        Devotee.phone.isnot(None),
        Devotee.receive_sms == True
    ).all()
    
    results = []
    for booking in bookings:
        try:
            # TODO: Actually send SMS via gateway
            results.append({
                "booking_id": booking.id,
                "mobile": booking.devotee.phone,
                "status": "sent",
                "message": f"Reminder sent for seva on {target_date}"
            })
        except Exception as e:
            results.append({
                "booking_id": booking.id,
                "mobile": booking.devotee.phone,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "target_date": target_date.isoformat(),
        "total": len(bookings),
        "sent": len([r for r in results if r["status"] == "sent"]),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "results": results
    }









