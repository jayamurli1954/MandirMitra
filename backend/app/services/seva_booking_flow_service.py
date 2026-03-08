from datetime import date, datetime, timedelta
from typing import Callable, Optional

from fastapi import HTTPException
from sqlalchemy import MetaData, Table, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import column_exists
from app.models.seva import SevaAvailability, SevaBooking, SevaBookingStatus
from app.schemas.seva import SevaBookingCreate, SevaBookingUpdate
from app.services.notification_service import notification_service


def list_bookings(
    db: Session,
    current_user,
    seva_id: Optional[int] = None,
    devotee_id: Optional[int] = None,
    booking_date: Optional[date] = None,
    status: Optional[SevaBookingStatus] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(SevaBooking).options(
        joinedload(SevaBooking.seva),
        joinedload(SevaBooking.devotee),
        joinedload(SevaBooking.priest),
    )

    if current_user.role != "admin":
        query = query.filter(SevaBooking.user_id == current_user.id)

    if seva_id:
        query = query.filter(SevaBooking.seva_id == seva_id)
    if devotee_id:
        query = query.filter(SevaBooking.devotee_id == devotee_id)
    if booking_date:
        query = query.filter(SevaBooking.booking_date == booking_date)
    if status:
        query = query.filter(SevaBooking.status == status)

    return query.offset(skip).limit(limit).all()


def get_booking(db: Session, booking_id: int, current_user):
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")

    return booking


def create_booking(
    db: Session,
    booking_data: SevaBookingCreate,
    current_user,
    get_seva_safely_fn: Callable,
    post_seva_to_accounting_fn: Callable,
):
    seva = get_seva_safely_fn(db, seva_id=booking_data.seva_id, filter_conditions={"is_active": True})
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found or inactive")

    if seva.advance_booking_days is not None and seva.advance_booking_days > 0:
        max_date = date.today() + timedelta(days=seva.advance_booking_days)
        if booking_data.booking_date > max_date:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot book more than {seva.advance_booking_days} days in advance",
            )

    day_of_week = (booking_data.booking_date.weekday() + 1) % 7
    if seva.availability == SevaAvailability.SPECIFIC_DAY and day_of_week != seva.specific_day:
        raise HTTPException(status_code=400, detail="Seva not available on this day")
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
            day_names = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            excluded_day_names = [day_names[d] for d in except_days_list]
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Seva not available on {day_names[day_of_week]}. "
                    f"This seva is not performed on: {', '.join(excluded_day_names)}"
                ),
            )

    if seva.max_bookings_per_day:
        existing_bookings = (
            db.query(SevaBooking)
            .filter(
                SevaBooking.seva_id == seva.id,
                SevaBooking.booking_date == booking_data.booking_date,
                SevaBooking.status.in_([SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED]),
            )
            .count()
        )

        if existing_bookings >= seva.max_bookings_per_day:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No slots available for this date. "
                    f"Maximum {seva.max_bookings_per_day} booking(s) allowed per day. "
                    f"Already booked: {existing_bookings}/{seva.max_bookings_per_day}"
                ),
            )

    receipt_prefix = "SEV"
    selected_payment_account_id = booking_data.payment_account_id
    booking_status = SevaBookingStatus.PENDING if seva.requires_approval else SevaBookingStatus.CONFIRMED

    booking_columns = {
        "seva_id": booking_data.seva_id,
        "devotee_id": booking_data.devotee_id,
        "user_id": current_user.id,
        "booking_date": booking_data.booking_date,
        "booking_time": booking_data.booking_time,
        "status": booking_status.name if hasattr(booking_status, "name") else str(booking_status),
        "amount_paid": booking_data.amount_paid,
        "payment_method": booking_data.payment_method,
        "payment_reference": booking_data.payment_reference,
        "devotee_names": booking_data.devotee_names,
        "gotra": booking_data.gotra,
        "nakshatra": booking_data.nakshatra,
        "rashi": booking_data.rashi,
        "special_request": booking_data.special_request,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    optional_booking_columns = {
        "sender_upi_id": booking_data.sender_upi_id,
        "upi_reference_number": booking_data.upi_reference_number,
        "cheque_number": booking_data.cheque_number,
        "cheque_date": booking_data.cheque_date,
        "cheque_bank_name": booking_data.cheque_bank_name,
        "cheque_branch": booking_data.cheque_branch,
        "utr_number": booking_data.utr_number,
        "payer_name": booking_data.payer_name,
        "priest_id": booking_data.priest_id,
    }

    for column_name, column_value in optional_booking_columns.items():
        if column_exists(db, "seva_bookings", column_name):
            booking_columns[column_name] = column_value

    try:
        bookings_table = Table("seva_bookings", MetaData(), autoload_with=db.get_bind())
        safe_insert_payload = {
            key: value for key, value in booking_columns.items() if key in bookings_table.c
        }

        status_column = bookings_table.c.get("status")
        enum_labels = getattr(getattr(status_column, "type", None), "enums", None)
        if enum_labels and "status" in safe_insert_payload:
            status_candidates = [
                str(booking_status.name) if hasattr(booking_status, "name") else None,
                str(booking_status.value) if hasattr(booking_status, "value") else None,
                str(booking_status).upper(),
                str(booking_status).lower(),
            ]
            normalized_map = {label.lower(): label for label in enum_labels}
            chosen_status = None
            for candidate in status_candidates:
                if candidate and candidate.lower() in normalized_map:
                    chosen_status = normalized_map[candidate.lower()]
                    break
            if chosen_status:
                safe_insert_payload["status"] = chosen_status

        insert_result = db.execute(bookings_table.insert().values(**safe_insert_payload))
        booking_id = None
        if insert_result.inserted_primary_key:
            booking_id = insert_result.inserted_primary_key[0]
        if not booking_id:
            booking_id = getattr(insert_result, "lastrowid", None)
        if not booking_id:
            booking_lookup = (
                db.execute(select(bookings_table.c.id).order_by(bookings_table.c.id.desc()).limit(1))
                .fetchone()
            )
            booking_id = int(booking_lookup[0]) if booking_lookup else None

        if not booking_id:
            raise ValueError("Failed to resolve newly created booking ID")

        receipt_number = f"{receipt_prefix}{str(int(booking_id)).zfill(6)}"
        if "receipt_number" in bookings_table.c:
            final_receipt_number = receipt_number
            existing_receipt = (
                db.execute(
                    select(bookings_table.c.id)
                    .where(
                        bookings_table.c.receipt_number == final_receipt_number,
                        bookings_table.c.id != booking_id,
                    )
                    .limit(1)
                )
                .fetchone()
            )
            if existing_receipt:
                final_receipt_number = (
                    f"{receipt_prefix}{str(int(booking_id)).zfill(6)}-{int(datetime.utcnow().timestamp())}"
                )

            db.execute(
                bookings_table.update()
                .where(bookings_table.c.id == booking_id)
                .values(receipt_number=final_receipt_number)
            )
            receipt_number = final_receipt_number

        booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Failed to load newly created booking ID {booking_id}")
    except Exception as e:
        db.rollback()
        print(f"Error creating seva booking: {str(e)}")
        print(f"   Booking data: {booking_data.dict()}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")

    if current_user and current_user.temple_id:
        try:
            post_seva_to_accounting_fn(
                db,
                booking,
                current_user.temple_id,
                payment_account_id=selected_payment_account_id,
            )
        except Exception as e:
            db.rollback()
            print(f"Failed to post Seva to accounting: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Accounting Entry Failed: {str(e)}. Please correct the Chart of Accounts.",
            )

    db.commit()
    db.refresh(booking)

    try:
        if booking.devotee and (
            (booking.devotee.receive_sms and booking.devotee.phone)
            or (booking.devotee.receive_email and booking.devotee.email)
        ):
            notification_service.send_seva_booking_confirmation(
                {
                    "devotee_name": booking.devotee.name,
                    "phone": booking.devotee.phone,
                    "email": booking.devotee.email,
                    "receipt_number": booking.receipt_number,
                    "seva_name": seva.name_english if seva else "Seva",
                    "booking_date": booking.booking_date.strftime("%d-%m-%Y") if booking.booking_date else "",
                    "booking_time": booking.booking_time or "All Day",
                    "amount": booking.amount_paid or 0,
                }
            )
    except Exception as e:
        print(f"Failed to send booking confirmation: {str(e)}")

    return booking


def update_booking(
    db: Session,
    booking_id: int,
    booking_data: SevaBookingUpdate,
    current_user,
):
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this booking")

    for key, value in booking_data.dict(exclude_unset=True).items():
        setattr(booking, key, value)

    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(
    db: Session,
    booking_id: int,
    reason: Optional[str],
    current_user,
):
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

    booking.status = SevaBookingStatus.CANCELLED
    booking.cancelled_at = datetime.utcnow()
    booking.cancellation_reason = reason
    db.commit()

    try:
        if booking.devotee and booking.devotee.receive_sms and booking.devotee.phone:
            pass
        if booking.devotee and booking.devotee.receive_email and booking.devotee.email:
            pass
    except Exception as e:
        print(f"Failed to send cancellation notification: {str(e)}")

    return {"message": "Booking cancelled successfully"}
