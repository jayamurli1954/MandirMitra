from datetime import date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from app.core.temple_context import require_system_roles
from app.models.seva import Seva, SevaAvailability, SevaBooking, SevaBookingStatus


def validate_reschedule_target_date(
    db: Session,
    booking: SevaBooking,
    new_date: date,
    check_advance_limit: bool = True,
):
    if new_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Reschedule date must be today or a future date.",
        )

    seva = db.query(Seva).filter(Seva.id == booking.seva_id).first()
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found for this booking")

    if check_advance_limit and seva.advance_booking_days is not None and seva.advance_booking_days > 0:
        max_date = date.today() + timedelta(days=seva.advance_booking_days)
        if new_date > max_date:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"This seva can be booked/rescheduled only up to "
                    f"{seva.advance_booking_days} day(s) in advance."
                ),
            )

    day_of_week = (new_date.weekday() + 1) % 7
    if seva.availability == SevaAvailability.SPECIFIC_DAY and day_of_week != seva.specific_day:
        raise HTTPException(status_code=400, detail="Seva not available on requested date")
    elif seva.availability == SevaAvailability.EXCEPT_DAY:
        except_days_list = []
        if seva.except_days:
            import json

            if isinstance(seva.except_days, str):
                try:
                    except_days_list = json.loads(seva.except_days)
                except json.JSONDecodeError:
                    except_days_list = []
            elif isinstance(seva.except_days, list):
                except_days_list = seva.except_days

        if seva.except_day is not None and seva.except_day not in except_days_list:
            except_days_list.append(seva.except_day)

        if day_of_week in except_days_list:
            raise HTTPException(status_code=400, detail="Seva not available on requested date")

    if seva.max_bookings_per_day:
        existing_bookings = (
            db.query(SevaBooking)
            .filter(
                SevaBooking.seva_id == booking.seva_id,
                SevaBooking.booking_date == new_date,
                SevaBooking.id != booking.id,
                SevaBooking.status.in_([SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED]),
            )
            .count()
        )
        if existing_bookings >= seva.max_bookings_per_day:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"No slots available on requested date. "
                    f"Maximum {seva.max_bookings_per_day} booking(s) allowed."
                ),
            )


def request_reschedule(
    db: Session,
    booking_id: int,
    new_date: date,
    reason: str,
    current_user,
):
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reschedule this booking")

    today = date.today()
    if booking.booking_date < today:
        raise HTTPException(
            status_code=400,
            detail="Cannot reschedule a completed seva. Only today's and future bookings can be rescheduled.",
        )

    if new_date == booking.booking_date:
        raise HTTPException(status_code=400, detail="New date must be different from current date")

    validate_reschedule_target_date(db, booking, new_date, check_advance_limit=True)

    if not booking.original_booking_date:
        booking.original_booking_date = booking.booking_date

    booking.reschedule_requested_date = new_date
    booking.reschedule_reason = reason
    booking.reschedule_approved = None
    booking.reschedule_approved_by = None
    booking.reschedule_approved_at = None

    db.commit()
    db.refresh(booking)

    return {
        "message": "Reschedule request submitted. Waiting for admin approval.",
        "booking_id": booking.id,
        "original_date": booking.original_booking_date,
        "requested_date": new_date,
        "status": "pending_approval",
    }


def get_pending_reschedule_requests(db: Session, current_user):
    require_system_roles(
        current_user,
        {"admin", "temple_manager"},
        detail="Only admins and temple managers can view pending reschedule requests",
    )

    pending_filter = or_(
        SevaBooking.reschedule_approved.is_(None),
        and_(
            SevaBooking.reschedule_approved == False,  # noqa: E712
            SevaBooking.reschedule_approved_at.is_(None),
        ),
    )

    return (
        db.query(SevaBooking)
        .options(
            joinedload(SevaBooking.seva),
            joinedload(SevaBooking.devotee),
            joinedload(SevaBooking.priest),
        )
        .filter(
            pending_filter,
            SevaBooking.reschedule_requested_date.isnot(None),
        )
        .all()
    )


def approve_reschedule(
    db: Session,
    booking_id: int,
    approve: bool,
    current_user,
):
    require_system_roles(
        current_user,
        {"admin", "temple_manager"},
        detail=(
            "Only admins and temple managers can approve reschedule requests. "
            f"Current role: {current_user.role}"
        ),
    )

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    is_legacy_pending_false = booking.reschedule_approved is False and booking.reschedule_approved_at is None
    if booking.reschedule_approved is not None and not is_legacy_pending_false:
        raise HTTPException(status_code=400, detail="Reschedule request already processed")

    if not booking.reschedule_requested_date:
        raise HTTPException(status_code=400, detail="No reschedule request found")

    if approve:
        validate_reschedule_target_date(
            db,
            booking,
            booking.reschedule_requested_date,
            check_advance_limit=False,
        )

        booking.booking_date = booking.reschedule_requested_date
        booking.reschedule_approved = True
        booking.reschedule_approved_by = current_user.id
        booking.reschedule_approved_at = datetime.utcnow()

        db.commit()
        return {
            "message": "Reschedule approved. Booking date updated.",
            "new_date": booking.booking_date,
            "original_date": booking.original_booking_date,
        }

    booking.reschedule_approved = False
    booking.reschedule_approved_by = current_user.id
    booking.reschedule_approved_at = datetime.utcnow()

    db.commit()
    return {
        "message": "Reschedule request rejected.",
        "booking_date": booking.booking_date,
    }
