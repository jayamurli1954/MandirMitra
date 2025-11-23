"""
Seva API Endpoints
Handles temple sevas/poojas/archanas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.seva import Seva, SevaBooking, SevaCategory, SevaAvailability, SevaBookingStatus
from app.models.accounting import Account, JournalEntry, JournalLine
from app.schemas.seva import (
    SevaCreate, SevaUpdate, SevaResponse, SevaListResponse,
    SevaBookingCreate, SevaBookingUpdate, SevaBookingResponse
)
from app.constants.hindu_constants import GOTHRAS, NAKSHATRAS, RASHIS

router = APIRouter(prefix="/api/v1/sevas", tags=["sevas"])


def post_seva_to_accounting(db: Session, booking: SevaBooking, temple_id: int):
    """
    Create journal entry for seva booking in accounting system
    Dr: Cash/Bank Account (based on payment method)
    Cr: Seva Income Account (based on seva type if linked, else default)
    """
    try:
        # Determine debit account (payment method)
        debit_account_code = None
        payment_method = booking.payment_method or 'CASH'

        if payment_method.upper() in ['CASH', 'COUNTER']:
            debit_account_code = '1101'  # Cash in Hand - Counter
        elif payment_method.upper() in ['UPI', 'ONLINE', 'CARD', 'NETBANKING']:
            debit_account_code = '1110'  # Bank - SBI Current Account
        else:
            debit_account_code = '1101'  # Default to cash counter

        # Get debit account
        debit_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == debit_account_code
        ).first()

        # Determine credit account - PRIORITY: Seva-linked account
        credit_account = None

        # First, try to use seva-linked account
        if booking.seva and hasattr(booking.seva, 'account_id') and booking.seva.account_id:
            credit_account = db.query(Account).filter(Account.id == booking.seva.account_id).first()

        # Fallback: Use default Special Pooja account
        if not credit_account:
            credit_account_code = '4208'  # Special Pooja (default)
            credit_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == credit_account_code
            ).first()

        if not debit_account or not credit_account:
            print(f"Warning: Accounts not found for seva booking {booking.receipt_number}")
            return None

        # Create narration
        devotee_name = booking.devotee.name if booking.devotee else 'Unknown'
        seva_name = booking.seva.name_english if booking.seva else 'Seva'
        narration = f"Seva booking - {seva_name} by {devotee_name}"

        # Create journal entry
        journal_entry = JournalEntry(
            temple_id=temple_id,
            entry_date=booking.booking_date,
            entry_number=None,  # Will be generated below
            narration=narration,
            reference_type='SEVA',
            reference_id=booking.id,
            reference_number=booking.receipt_number,
            status='POSTED',
            created_by=booking.user_id
        )
        db.add(journal_entry)
        db.flush()  # Get journal_entry.id

        # Generate entry number
        year = booking.booking_date.year
        last_entry = db.query(JournalEntry).filter(
            JournalEntry.temple_id == temple_id,
            JournalEntry.id < journal_entry.id
        ).order_by(JournalEntry.id.desc()).first()

        seq = 1
        if last_entry and last_entry.entry_number:
            try:
                seq = int(last_entry.entry_number.split('-')[-1]) + 1
            except:
                seq = journal_entry.id

        journal_entry.entry_number = f"JE-{year}-{str(seq).zfill(5)}"

        # Create journal lines
        # Debit: Payment Account (Cash/Bank increases)
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=debit_account.id,
            debit_amount=booking.amount_paid,
            credit_amount=0,
            description=f"Seva booking received via {payment_method}"
        )

        # Credit: Seva Income (Income increases)
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=credit_account.id,
            debit_amount=0,
            credit_amount=booking.amount_paid,
            description=f"Seva income - {seva_name}"
        )

        db.add(debit_line)
        db.add(credit_line)

        return journal_entry

    except Exception as e:
        print(f"Error posting seva to accounting: {str(e)}")
        return None

# ===== SEVA MANAGEMENT =====

@router.get("/", response_model=List[SevaListResponse])
def list_sevas(
    category: Optional[SevaCategory] = None,
    is_active: bool = True,
    for_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """List all sevas with availability check"""
    query = db.query(Seva).filter(Seva.is_active == is_active)

    if category:
        query = query.filter(Seva.category == category)

    sevas = query.all()

    # Add availability check for specific date
    check_date = for_date or date.today()
    day_of_week = check_date.weekday()  # 0=Monday, 6=Sunday
    # Convert to our format (0=Sunday, 6=Saturday)
    day_of_week = (day_of_week + 1) % 7

    result = []
    for seva in sevas:
        seva_dict = SevaListResponse.from_orm(seva).__dict__

        # Check availability
        is_available = True
        if seva.availability == SevaAvailability.SPECIFIC_DAY:
            is_available = (day_of_week == seva.specific_day)
        elif seva.availability == SevaAvailability.EXCEPT_DAY:
            is_available = (day_of_week != seva.except_day)
        elif seva.availability == SevaAvailability.WEEKDAY:
            is_available = (day_of_week >= 1 and day_of_week <= 5)
        elif seva.availability == SevaAvailability.WEEKEND:
            is_available = (day_of_week == 0 or day_of_week == 6)

        seva_dict['is_available_today'] = is_available

        # Check booking availability
        if seva.max_bookings_per_day:
            bookings_count = db.query(SevaBooking).filter(
                SevaBooking.seva_id == seva.id,
                SevaBooking.booking_date == check_date,
                SevaBooking.status.in_([SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED])
            ).count()
            seva_dict['bookings_available'] = max(0, seva.max_bookings_per_day - bookings_count)

        result.append(SevaListResponse(**seva_dict))

    return result

@router.get("/{seva_id}", response_model=SevaResponse)
def get_seva(
    seva_id: int,
    db: Session = Depends(get_db)
):
    """Get seva details"""
    seva = db.query(Seva).filter(Seva.id == seva_id).first()
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")
    return seva

@router.post("/", response_model=SevaResponse)
def create_seva(
    seva_data: SevaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new seva (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create sevas")

    seva = Seva(**seva_data.dict())
    db.add(seva)
    db.commit()
    db.refresh(seva)
    return seva

@router.put("/{seva_id}", response_model=SevaResponse)
def update_seva(
    seva_id: int,
    seva_data: SevaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update seva (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update sevas")

    seva = db.query(Seva).filter(Seva.id == seva_id).first()
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")

    for key, value in seva_data.dict(exclude_unset=True).items():
        setattr(seva, key, value)

    seva.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(seva)
    return seva

@router.delete("/{seva_id}")
def delete_seva(
    seva_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete seva (soft delete by marking inactive)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete sevas")

    seva = db.query(Seva).filter(Seva.id == seva_id).first()
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")

    seva.is_active = False
    db.commit()
    return {"message": "Seva deleted successfully"}

# ===== SEVA BOOKINGS =====

@router.get("/bookings/", response_model=List[SevaBookingResponse])
def list_bookings(
    seva_id: Optional[int] = None,
    devotee_id: Optional[int] = None,
    booking_date: Optional[date] = None,
    status: Optional[SevaBookingStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List seva bookings"""
    query = db.query(SevaBooking)

    # Non-admin users can only see their own bookings
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

    bookings = query.offset(skip).limit(limit).all()
    return bookings

@router.get("/bookings/{booking_id}", response_model=SevaBookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get booking details"""
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check permissions
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")

    return booking

@router.post("/bookings/", response_model=SevaBookingResponse)
def create_booking(
    booking_data: SevaBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new seva booking"""
    # Validate seva exists and is active
    seva = db.query(Seva).filter(Seva.id == booking_data.seva_id, Seva.is_active == True).first()
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found or inactive")

    # Check advance booking limit
    max_date = date.today() + timedelta(days=seva.advance_booking_days)
    if booking_data.booking_date > max_date:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot book more than {seva.advance_booking_days} days in advance"
        )

    # Check availability for the day
    day_of_week = (booking_data.booking_date.weekday() + 1) % 7
    if seva.availability == SevaAvailability.SPECIFIC_DAY and day_of_week != seva.specific_day:
        raise HTTPException(status_code=400, detail="Seva not available on this day")
    elif seva.availability == SevaAvailability.EXCEPT_DAY and day_of_week == seva.except_day:
        raise HTTPException(status_code=400, detail="Seva not available on this day")

    # Check max bookings per day
    if seva.max_bookings_per_day:
        existing_bookings = db.query(SevaBooking).filter(
            SevaBooking.seva_id == seva.id,
            SevaBooking.booking_date == booking_data.booking_date,
            SevaBooking.status.in_([SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED])
        ).count()

        if existing_bookings >= seva.max_bookings_per_day:
            raise HTTPException(status_code=400, detail="No slots available for this date")

    # Generate receipt number
    receipt_number = f"SEV{datetime.now().strftime('%Y%m%d%H%M%S')}{booking_data.seva_id}"

    # Create booking
    booking = SevaBooking(
        **booking_data.dict(),
        user_id=current_user.id,
        status=SevaBookingStatus.PENDING if seva.requires_approval else SevaBookingStatus.CONFIRMED,
        receipt_number=receipt_number
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Post to accounting system (get temple_id from current_user)
    if current_user and current_user.temple_id:
        journal_entry = post_seva_to_accounting(db, booking, current_user.temple_id)
        if journal_entry:
            db.commit()  # Commit the journal entry

    return booking

@router.put("/bookings/{booking_id}", response_model=SevaBookingResponse)
def update_booking(
    booking_id: int,
    booking_data: SevaBookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update booking"""
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check permissions
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this booking")

    for key, value in booking_data.dict(exclude_unset=True).items():
        setattr(booking, key, value)

    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel booking"""
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check permissions
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

    booking.status = SevaBookingStatus.CANCELLED
    booking.cancelled_at = datetime.utcnow()
    booking.cancellation_reason = reason
    db.commit()

    return {"message": "Booking cancelled successfully"}

# ===== DROPDOWN OPTIONS =====

@router.get("/dropdown-options")
def get_dropdown_options():
    """Get dropdown options for Gothra, Nakshatra, and Rashi"""
    return {
        "gothras": GOTHRAS,
        "nakshatras": NAKSHATRAS,
        "rashis": RASHIS
    }
