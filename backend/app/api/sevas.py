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
from app.models.accounting import Account, JournalEntry, JournalLine, JournalEntryStatus, TransactionType
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
    Cr: Seva Income Account

    Behaviour:
    - If seva has a specific income account linked -> credit that account
    - Otherwise -> credit 4200 (Seva Income - Main)

    This keeps Trial Balance short (single seva income line),
    while still allowing detailed seva-wise income accounts for temples that link them.
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

        # Fallback: Use Seva Income main account (4200)
        if not credit_account:
            credit_account_code = '4200'  # Seva Income - Main (parent)
            credit_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == credit_account_code
            ).first()

        if not debit_account:
            error_msg = f"Debit account ({debit_account_code}) not found for temple {temple_id}. Please create the account in Chart of Accounts."
            print(f"ERROR: {error_msg}")
            print(f"  - Seva booking: {booking.receipt_number}")
            print(f"  - Payment method: {payment_method}")
            return None
        
        if not credit_account:
            error_msg = f"Credit account not found for seva '{booking.seva.name_english if booking.seva else 'Unknown'}'. Please link an account to the seva or create default seva income accounts."
            print(f"ERROR: {error_msg}")
            print(f"  - Seva booking: {booking.receipt_number}")
            print(f"  - Seva: {booking.seva.name_english if booking.seva else 'None'}")
            print(f"  - Seva account_id: {booking.seva.account_id if booking.seva and hasattr(booking.seva, 'account_id') else 'NO'}")
            return None

        # Create narration
        devotee_name = booking.devotee.name if booking.devotee else 'Unknown'
        seva_name = booking.seva.name_english if booking.seva else 'Seva'
        narration = f"Seva booking - {seva_name} by {devotee_name}"

        # Generate entry number first
        year = booking.booking_date.year
        prefix = f"JE/{year}/"
        
        # Get last entry number for this year
        last_entry = db.query(JournalEntry).filter(
            JournalEntry.temple_id == temple_id,
            JournalEntry.entry_number.like(f"{prefix}%")
        ).order_by(JournalEntry.id.desc()).first()

        if last_entry:
            # Extract number and increment
            try:
                last_num = int(last_entry.entry_number.split('/')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1

        entry_number = f"{prefix}{new_num:04d}"

        # Convert booking_date (date) to datetime for entry_date
        if isinstance(booking.booking_date, date):
            entry_date = datetime.combine(booking.booking_date, datetime.min.time())
        else:
            entry_date = booking.booking_date

        # Create journal entry
        # Note: created_by is required, so use booking.user_id or default to 1
        created_by = booking.user_id if booking.user_id else 1

        journal_entry = JournalEntry(
            temple_id=temple_id,
            entry_date=entry_date,
            entry_number=entry_number,
            narration=narration,
            reference_type=TransactionType.SEVA,
            reference_id=booking.id,
            total_amount=booking.amount_paid,
            status=JournalEntryStatus.POSTED,
            created_by=created_by,
            posted_by=created_by,
            posted_at=datetime.utcnow()
        )
        db.add(journal_entry)
        db.flush()  # Get journal_entry.id

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

# ===== DROPDOWN OPTIONS (Must be before /{seva_id} route) =====

@router.get("/dropdown-options")
def get_dropdown_options():
    """Get dropdown options for Gothra, Nakshatra, and Rashi"""
    try:
        return {
            "gothras": GOTHRAS,
            "nakshatras": NAKSHATRAS,
            "rashis": RASHIS
        }
    except Exception as e:
        print(f"Error in dropdown-options endpoint: {e}")
        # Return empty arrays as fallback
        return {
            "gothras": [],
            "nakshatras": [],
            "rashis": []
        }

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
    try:
        booking = SevaBooking(
            **booking_data.dict(),
            user_id=current_user.id,
            status=SevaBookingStatus.PENDING if seva.requires_approval else SevaBookingStatus.CONFIRMED,
            receipt_number=receipt_number
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating seva booking: {str(e)}")
        print(f"   Booking data: {booking_data.dict()}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create booking: {str(e)}"
        )

    # Post to accounting system (get temple_id from current_user)
    if current_user and current_user.temple_id:
        try:
            journal_entry = post_seva_to_accounting(db, booking, current_user.temple_id)
            if journal_entry:
                db.commit()  # Commit the journal entry
                print(f"✓ Created journal entry {journal_entry.entry_number} for seva booking {booking.receipt_number}")
            else:
                print(f"⚠ WARNING: Failed to create journal entry for seva booking {booking.receipt_number}")
                print(f"  Booking was saved but accounting entry was not created. Check accounts.")
        except Exception as e:
            print(f"⚠ ERROR creating journal entry for seva booking: {str(e)}")
            import traceback
            traceback.print_exc()
            # Don't fail the booking if accounting fails

    # Refresh to get relationships
    db.refresh(booking)
    
    # Manually construct response to handle relationships properly
    response_data = {
        "id": booking.id,
        "seva_id": booking.seva_id,
        "devotee_id": booking.devotee_id,
        "user_id": booking.user_id,
        "priest_id": booking.priest_id,
        "booking_date": booking.booking_date,
        "booking_time": booking.booking_time,
        "status": booking.status.value if hasattr(booking.status, 'value') else str(booking.status),
        "amount_paid": booking.amount_paid,
        "payment_method": booking.payment_method,
        "payment_reference": booking.payment_reference,
        "receipt_number": booking.receipt_number,
        "devotee_names": booking.devotee_names,
        "gotra": booking.gotra,
        "nakshatra": booking.nakshatra,
        "rashi": booking.rashi,
        "special_request": booking.special_request,
        "admin_notes": booking.admin_notes,
        "completed_at": booking.completed_at,
        "cancelled_at": booking.cancelled_at,
        "cancellation_reason": booking.cancellation_reason,
        "original_booking_date": booking.original_booking_date,
        "reschedule_requested_date": booking.reschedule_requested_date,
        "reschedule_reason": booking.reschedule_reason,
        "reschedule_approved": booking.reschedule_approved,
        "reschedule_approved_by": booking.reschedule_approved_by,
        "reschedule_approved_at": booking.reschedule_approved_at,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at,
    }
    
    # Serialize seva relationship
    if booking.seva:
        response_data["seva"] = SevaResponse.from_attributes(booking.seva)
    else:
        response_data["seva"] = None
    
    # Serialize devotee relationship as dict
    if booking.devotee:
        response_data["devotee"] = {
            "id": booking.devotee.id,
            "name": booking.devotee.name,
            "phone": booking.devotee.phone,
            "email": getattr(booking.devotee, 'email', None)
        }
    else:
        response_data["devotee"] = None
    
    # Serialize priest relationship as dict (if exists)
    if booking.priest:
        response_data["priest"] = {
            "id": booking.priest.id,
            "name": getattr(booking.priest, 'name', None) or getattr(booking.priest, 'full_name', None),
            "email": getattr(booking.priest, 'email', None)
        }
    else:
        response_data["priest"] = None
    
    return SevaBookingResponse(**response_data)

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

# ===== SEVA RESCHEDULE (POSTPONE/PREPONE) =====

@router.put("/bookings/{booking_id}/reschedule")
def request_reschedule(
    booking_id: int,
    new_date: date = Query(..., description="New booking date"),
    reason: str = Query(..., description="Reason for reschedule"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Request to reschedule (postpone/prepone) a seva booking
    Requires admin approval
    """
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check permissions - user can request reschedule for their own bookings
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reschedule this booking")

    # Validate new date
    if new_date == booking.booking_date:
        raise HTTPException(status_code=400, detail="New date must be different from current date")

    # Store original date if not already stored
    if not booking.original_booking_date:
        booking.original_booking_date = booking.booking_date

    # Set reschedule request
    booking.reschedule_requested_date = new_date
    booking.reschedule_reason = reason
    booking.reschedule_approved = None  # Pending approval

    db.commit()
    db.refresh(booking)

    return {
        "message": "Reschedule request submitted. Waiting for admin approval.",
        "booking_id": booking.id,
        "original_date": booking.original_booking_date,
        "requested_date": new_date,
        "status": "pending_approval"
    }

@router.post("/bookings/{booking_id}/approve-reschedule")
def approve_reschedule(
    booking_id: int,
    approve: bool = Query(..., description="Approve (true) or reject (false)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve or reject a reschedule request (admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can approve reschedule requests")

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.reschedule_approved is not None:
        raise HTTPException(status_code=400, detail="Reschedule request already processed")

    if not booking.reschedule_requested_date:
        raise HTTPException(status_code=400, detail="No reschedule request found")

    if approve:
        # Approve: Update booking date
        booking.booking_date = booking.reschedule_requested_date
        booking.reschedule_approved = True
        booking.reschedule_approved_by = current_user.id
        booking.reschedule_approved_at = datetime.utcnow()
        
        db.commit()
        return {
            "message": "Reschedule approved. Booking date updated.",
            "new_date": booking.booking_date,
            "original_date": booking.original_booking_date
        }
    else:
        # Reject: Clear reschedule request
        booking.reschedule_approved = False
        booking.reschedule_approved_by = current_user.id
        booking.reschedule_approved_at = datetime.utcnow()
        
        db.commit()
    return {
            "message": "Reschedule request rejected.",
            "booking_date": booking.booking_date  # Unchanged
    }


# ===== PRIEST ASSIGNMENT =====

@router.get("/priests")
def get_priests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of priests (users with role 'priest')"""
    priests = db.query(User).filter(
        User.role == "priest",
        User.is_active == True
    )
    
    # Filter by temple if in multi-tenant mode
    if current_user.temple_id:
        priests = priests.filter(User.temple_id == current_user.temple_id)
    
    priests = priests.all()
    
    return [
        {
            "id": p.id,
            "name": p.full_name,
            "email": p.email,
            "phone": p.phone
        }
        for p in priests
    ]


@router.put("/bookings/{booking_id}/assign-priest")
def assign_priest(
    booking_id: int,
    priest_id: int = Query(..., description="Priest user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Assign a priest to a seva booking
    Only admins or staff can assign priests
    """
    # Check permissions
    if current_user.role not in ["admin", "temple_manager", "staff"]:
        raise HTTPException(status_code=403, detail="Only admins and staff can assign priests")
    
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Verify priest exists and is active
    priest = db.query(User).filter(
        User.id == priest_id,
        User.role == "priest",
        User.is_active == True
    ).first()
    
    if not priest:
        raise HTTPException(status_code=404, detail="Priest not found or inactive")
    
    # Assign priest
    booking.priest_id = priest_id
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    
    return {
        "message": f"Priest {priest.full_name} assigned successfully",
        "booking": SevaBookingResponse.from_orm(booking)
    }


@router.put("/bookings/{booking_id}/remove-priest")
def remove_priest(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove priest assignment from a seva booking
    Only admins or staff can remove priest assignments
    """
    # Check permissions
    if current_user.role not in ["admin", "temple_manager", "staff"]:
        raise HTTPException(status_code=403, detail="Only admins and staff can remove priest assignments")
    
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.priest_id = None
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    
    return {
        "message": "Priest assignment removed successfully",
        "booking": SevaBookingResponse.from_orm(booking)
    }
