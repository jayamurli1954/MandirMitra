"""
Seva API Endpoints
Handles temple sevas/poojas/archanas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.seva import Seva, SevaBooking, SevaCategory, SevaAvailability, SevaBookingStatus
from app.models.devotee import Devotee
from app.models.accounting import Account, JournalEntry, JournalLine, JournalEntryStatus, TransactionType
from app.schemas.seva import (
    SevaCreate, SevaUpdate, SevaResponse, SevaListResponse,
    SevaBookingCreate, SevaBookingUpdate, SevaBookingResponse
)
from app.constants.hindu_constants import GOTHRAS, NAKSHATRAS, RASHIS

router = APIRouter(prefix="/api/v1/sevas", tags=["sevas"])


def get_seva_safely(db: Session, seva_id: int = None, filter_conditions: dict = None):
    """
    Safely query Seva model, handling missing materials_required column
    Returns Seva object or None (single) or list of Seva objects
    """
    from sqlalchemy import text
    
    # Check if materials_required column exists
    column_check = db.execute(
        text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'sevas' AND column_name = 'materials_required'
        """)
    ).fetchone()
    
    has_materials_column = column_check is not None
    
    if not has_materials_column:
        # Use raw SQL
        sql = """
            SELECT id, name_english, name_kannada, name_sanskrit, description, category, 
                   amount, min_amount, max_amount, availability, specific_day, except_day, 
                   time_slot, max_bookings_per_day, advance_booking_days, requires_approval,
                   is_active, is_token_seva, token_color, token_threshold, account_id,
                   benefits, instructions, duration_minutes, created_at, updated_at
            FROM sevas
            WHERE 1=1
        """
        params = {}
        
        if seva_id:
            sql += " AND id = :seva_id"
            params["seva_id"] = seva_id
        
        if filter_conditions:
            for key, value in filter_conditions.items():
                sql += f" AND {key} = :{key}"
                params[key] = value
        
        result = db.execute(text(sql), params)
        rows = result.fetchall()
        
        if not rows:
            return None if seva_id else []
        
        class SevaProxy:
            def __init__(self, row_data):
                self.id = row_data[0]
                self.name_english = row_data[1]
                self.name_kannada = row_data[2]
                self.name_sanskrit = row_data[3]
                self.description = row_data[4]
                self.category = row_data[5]
                self.amount = row_data[6]
                self.min_amount = row_data[7]
                self.max_amount = row_data[8]
                self.availability = row_data[9]
                self.specific_day = row_data[10]
                self.except_day = row_data[11]
                self.time_slot = row_data[12]
                self.max_bookings_per_day = row_data[13]
                self.advance_booking_days = row_data[14]
                self.requires_approval = row_data[15]
                self.is_active = row_data[16]
                self.is_token_seva = row_data[17]
                self.token_color = row_data[18]
                self.token_threshold = row_data[19]
                self.account_id = row_data[20]
                self.benefits = row_data[21]
                self.instructions = row_data[22]
                self.duration_minutes = row_data[23]
                self.created_at = row_data[24]
                self.updated_at = row_data[25]
                self.materials_required = None
        
        if seva_id:
            return SevaProxy(rows[0]) if rows else None
        else:
            return [SevaProxy(r) for r in rows]
    else:
        # Use normal ORM
        query = db.query(Seva)
        if seva_id:
            query = query.filter(Seva.id == seva_id)
        if filter_conditions:
            for key, value in filter_conditions.items():
                query = query.filter(getattr(Seva, key) == value)
        return query.first() if seva_id else query.all()


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
    from sqlalchemy import text
    
    # Check if materials_required column exists in database
    column_check = db.execute(
        text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'sevas' AND column_name = 'materials_required'
        """)
    ).fetchone()
    
    has_materials_column = column_check is not None
    
    # Build query using raw SQL if column doesn't exist, otherwise use ORM
    if not has_materials_column:
        # Use raw SQL to select only existing columns
        sql = """
            SELECT id, name_english, name_kannada, name_sanskrit, description, category, 
                   amount, min_amount, max_amount, availability, specific_day, except_day, 
                   time_slot, max_bookings_per_day, advance_booking_days, requires_approval,
                   is_active, is_token_seva, token_color, token_threshold, account_id,
                   benefits, instructions, duration_minutes, created_at, updated_at
            FROM sevas
            WHERE is_active = :is_active
        """
        params = {"is_active": is_active}
        
        if category:
            sql += " AND category = :category"
            params["category"] = category.value
        
        result = db.execute(text(sql), params)
        rows = result.fetchall()
        
        # Convert rows to Seva-like objects
        class SevaProxy:
            def __init__(self, row_data):
                self.id = row_data[0]
                self.name_english = row_data[1]
                self.name_kannada = row_data[2]
                self.name_sanskrit = row_data[3]
                self.description = row_data[4]
                self.category = row_data[5]
                self.amount = row_data[6]
                self.min_amount = row_data[7]
                self.max_amount = row_data[8]
                self.availability = row_data[9]
                self.specific_day = row_data[10]
                self.except_day = row_data[11]
                self.time_slot = row_data[12]
                self.max_bookings_per_day = row_data[13]
                self.advance_booking_days = row_data[14]
                self.requires_approval = row_data[15]
                self.is_active = row_data[16]
                self.is_token_seva = row_data[17]
                self.token_color = row_data[18]
                self.token_threshold = row_data[19]
                self.account_id = row_data[20]
                self.benefits = row_data[21]
                self.instructions = row_data[22]
                self.duration_minutes = row_data[23]
                self.created_at = row_data[24]
                self.updated_at = row_data[25]
                self.materials_required = None  # Set to None since column doesn't exist
        
        sevas = [SevaProxy(row) for row in rows]
    else:
        # Use normal ORM query
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
        # Convert enum values to lowercase for Pydantic schema
        # Database may have uppercase values (SPECIAL, SPECIFIC_DAY) but schema expects lowercase
        # Handle both enum objects and string values from database
        def normalize_enum(value):
            """Convert enum or string to lowercase string"""
            if value is None:
                return None
            if hasattr(value, 'value'):
                # It's an enum object
                return value.value.lower()
            # It's a string (from raw SQL query)
            return str(value).lower()
        
        seva_data = {
            'id': seva.id,
            'name_english': seva.name_english,
            'name_kannada': seva.name_kannada,
            'name_sanskrit': seva.name_sanskrit,
            'description': seva.description,
            'category': normalize_enum(seva.category),
            'amount': seva.amount,
            'min_amount': seva.min_amount,
            'max_amount': seva.max_amount,
            'availability': normalize_enum(seva.availability),
            'specific_day': seva.specific_day,
            'except_day': seva.except_day,
            'time_slot': seva.time_slot,
            'is_active': seva.is_active,
        }
        seva_dict = SevaListResponse(**seva_data).__dict__

        # Check availability
        # Normalize availability for comparison (handle both enum and string)
        availability_str = normalize_enum(seva.availability)
        is_available = True
        if availability_str == 'specific_day':
            is_available = (day_of_week == seva.specific_day)
        elif availability_str == 'except_day':
            is_available = (day_of_week != seva.except_day)
        elif availability_str == 'weekday':
            is_available = (day_of_week >= 1 and day_of_week <= 5)
        elif availability_str == 'weekend':
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
    seva = get_seva_safely(db, seva_id=seva_id)
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")
    return seva

@router.post("/", response_model=SevaResponse)
def create_seva(
    seva_data: SevaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Create new seva (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create sevas")

    seva = Seva(**seva_data.dict())
    seva.temple_id = current_user.temple_id if current_user else None
    db.add(seva)
    db.flush()  # Get seva.id for audit log
    
    # Create audit log
    try:
        from app.core.audit import log_action, get_entity_dict
        log_action(
            db=db,
            user=current_user,
            action="CREATE",
            entity_type="Seva",
            entity_id=seva.id,
            new_values=get_entity_dict(seva),
            description=f"Created seva: {seva.name_english}",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
    except Exception as e:
        print(f"Warning: Failed to create audit log: {e}")
        # Don't fail seva creation if audit log fails
    
    db.commit()
    db.refresh(seva)
    return seva

@router.put("/{seva_id}", response_model=SevaResponse)
def update_seva(
    seva_id: int,
    seva_data: SevaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Update seva (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update sevas")

    seva = get_seva_safely(db, seva_id=seva_id)
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")

    # Get old values for audit log
    old_values = get_entity_dict(seva) if hasattr(seva, '__table__') else {}

    # Update fields
    for key, value in seva_data.dict(exclude_unset=True).items():
        setattr(seva, key, value)

    seva.updated_at = datetime.utcnow()
    db.flush()
    
    # Create audit log
    try:
        from app.core.audit import log_action, get_entity_dict
        new_values = get_entity_dict(seva) if hasattr(seva, '__table__') else {}
        log_action(
            db=db,
            user=current_user,
            action="UPDATE",
            entity_type="Seva",
            entity_id=seva.id,
            old_values=old_values,
            new_values=new_values,
            description=f"Updated seva: {seva.name_english}",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
    except Exception as e:
        print(f"Warning: Failed to create audit log: {e}")
        # Don't fail seva update if audit log fails
    
    db.commit()
    db.refresh(seva)
    return seva

@router.delete("/{seva_id}")
def delete_seva(
    seva_id: int,
    reason: Optional[str] = Query(None, description="Reason for deletion (required)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Delete seva (soft delete by marking inactive)
    
    Requirements:
    - Admin approval required
    - Cannot delete if there are future bookings
    - Reason must be provided
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete sevas")
    
    if not reason or not reason.strip():
        raise HTTPException(
            status_code=400,
            detail="Reason for deletion is required. Please provide a reason for audit trail."
        )

    seva = get_seva_safely(db, seva_id=seva_id)
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")

    # Check for future bookings
    future_bookings = db.query(SevaBooking).filter(
        SevaBooking.seva_id == seva_id,
        SevaBooking.booking_date >= date.today(),
        SevaBooking.status.in_([SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED])
    ).count()
    
    if future_bookings > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete seva. There are {future_bookings} future booking(s). Please cancel or complete all future bookings first."
        )

    # Get old values for audit log
    old_values = get_entity_dict(seva) if hasattr(seva, '__table__') else {}

    # Soft delete by marking inactive
    seva.is_active = False
    seva.updated_at = datetime.utcnow()
    db.flush()
    
    # Create audit log with reason
    try:
        from app.core.audit import log_action, get_entity_dict
        new_values = get_entity_dict(seva) if hasattr(seva, '__table__') else {}
        log_action(
            db=db,
            user=current_user,
            action="DELETE",
            entity_type="Seva",
            entity_id=seva.id,
            old_values=old_values,
            new_values=new_values,
            description=f"Deleted seva: {seva.name_english}. Reason: {reason}",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
    except Exception as e:
        print(f"Warning: Failed to create audit log: {e}")
        # Don't fail seva deletion if audit log fails
    
    db.commit()
    return {"message": "Seva deleted successfully"}

# ===== SEVA AVAILABILITY & BOOKING HELPERS =====

@router.get("/{seva_id}/available-dates")
def get_available_dates(
    seva_id: int,
    weeks_ahead: int = Query(12, ge=1, le=52, description="Number of weeks to look ahead"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available booking dates for a seva
    
    Returns list of dates with:
    - Date
    - Day of week
    - Available slots (max_bookings_per_day - current_bookings)
    - Is available (boolean)
    """
    seva = get_seva_safely(db, seva_id=seva_id)
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")
    
    if not seva.is_active:
        raise HTTPException(status_code=400, detail="Seva is not active")
    
    # Normalize availability
    availability_str = str(seva.availability).lower()
    if hasattr(seva.availability, 'value'):
        availability_str = seva.availability.value.lower()
    
    # Calculate date range
    start_date = date.today()
    end_date = start_date + timedelta(weeks=weeks_ahead)
    
    available_dates = []
    current_date = start_date
    
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    while current_date <= end_date:
        day_of_week = (current_date.weekday() + 1) % 7  # 0=Sunday, 6=Saturday
        
        # Check if seva is available on this day
        is_available_day = True
        if availability_str == 'specific_day':
            is_available_day = (day_of_week == seva.specific_day)
        elif availability_str == 'except_day':
            is_available_day = (day_of_week != seva.except_day)
        elif availability_str == 'weekday':
            is_available_day = (day_of_week >= 1 and day_of_week <= 5)
        elif availability_str == 'weekend':
            is_available_day = (day_of_week == 0 or day_of_week == 6)
        # 'daily' and 'festival_only' are always available (subject to max bookings)
        
        if is_available_day:
            # Check advance booking limit
            days_ahead = (current_date - start_date).days
            if days_ahead <= seva.advance_booking_days:
                # Count existing bookings for this date
                existing_bookings = db.query(SevaBooking).filter(
                    SevaBooking.seva_id == seva_id,
                    SevaBooking.booking_date == current_date,
                    SevaBooking.status.in_([SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED])
                ).count()
                
                max_bookings = seva.max_bookings_per_day if seva.max_bookings_per_day else 999
                available_slots = max(0, max_bookings - existing_bookings)
                is_available = available_slots > 0
                
                available_dates.append({
                    "date": current_date.isoformat(),
                    "day_of_week": day_names[day_of_week],
                    "day_number": day_of_week,
                    "available_slots": available_slots,
                    "max_slots": max_bookings,
                    "booked_slots": existing_bookings,
                    "is_available": is_available,
                    "time_slot": seva.time_slot
                })
        
        current_date += timedelta(days=1)
    
    return {
        "seva_id": seva_id,
        "seva_name": seva.name_english,
        "availability_type": availability_str,
        "specific_day": seva.specific_day,
        "max_bookings_per_day": seva.max_bookings_per_day,
        "advance_booking_days": seva.advance_booking_days,
        "available_dates": available_dates
    }

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
    seva = get_seva_safely(db, seva_id=booking_data.seva_id, filter_conditions={"is_active": True})
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
            available_slots = seva.max_bookings_per_day - existing_bookings
            raise HTTPException(
                status_code=400,
                detail=f"No slots available for this date. Maximum {seva.max_bookings_per_day} booking(s) allowed per day. Already booked: {existing_bookings}/{seva.max_bookings_per_day}"
            )

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

    # Auto-send SMS/Email confirmation (if enabled and devotee preferences allow)
    try:
        if booking.devotee and booking.devotee.receive_sms and booking.devotee.phone:
            # Send SMS booking confirmation (async - don't block response)
            # TODO: Implement SMS service integration
            pass
        if booking.devotee and booking.devotee.receive_email and booking.devotee.email:
            # Send Email booking confirmation (async - don't block response)
            # TODO: Implement Email service integration
            pass
    except Exception as e:
        # Don't fail booking creation if SMS/Email fails
        print(f"Failed to send booking confirmation: {str(e)}")

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
        try:
            # Try from_orm first (Pydantic v1), then model_validate (Pydantic v2)
            if hasattr(SevaResponse, 'from_orm'):
                response_data["seva"] = SevaResponse.from_orm(booking.seva)
            else:
                response_data["seva"] = SevaResponse.model_validate(booking.seva)
        except Exception as e:
            print(f"Error serializing seva: {e}")
            # Fallback to manual dict construction
            response_data["seva"] = {
                "id": booking.seva.id,
                "name_english": booking.seva.name_english,
                "name_kannada": getattr(booking.seva, 'name_kannada', None),
                "name_sanskrit": getattr(booking.seva, 'name_sanskrit', None),
                "category": str(booking.seva.category) if hasattr(booking.seva, 'category') else None,
                "amount": booking.seva.amount
            }
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

    # Auto-send SMS/Email notification (if enabled and devotee preferences allow)
    try:
        if booking.devotee and booking.devotee.receive_sms and booking.devotee.phone:
            # Send SMS cancellation notification (async - don't block response)
            # TODO: Implement SMS service integration
            pass
        if booking.devotee and booking.devotee.receive_email and booking.devotee.email:
            # Send Email cancellation notification (async - don't block response)
            # TODO: Implement Email service integration
            pass
    except Exception as e:
        # Don't fail cancellation if SMS/Email fails
        print(f"Failed to send cancellation notification: {str(e)}")

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


@router.post("/bookings/{booking_id}/process-refund", response_model=dict)
def process_refund(
    booking_id: int,
    refund_amount: Optional[float] = Query(None, description="Refund amount (default: 90% of booking amount)"),
    refund_method: str = Query("original", description="Refund method: original, cash, bank_transfer"),
    refund_reference: Optional[str] = Query(None, description="Transaction reference for refund"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process refund for a cancelled booking
    Business rule: 90% refund (10% processing fee)
    Only admins or accountants can process refunds
    """
    # Check permissions
    if current_user.role not in ["admin", "accountant", "temple_manager"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can process refunds")
    
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != SevaBookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Booking must be cancelled before processing refund")
    
    # Check if refund already processed
    if hasattr(booking, 'refund_processed') and booking.refund_processed:
        raise HTTPException(status_code=400, detail="Refund already processed for this booking")
    
    # Calculate refund amount (90% of booking amount, 10% processing fee)
    if refund_amount is None:
        refund_amount = booking.amount_paid * 0.9  # 90% refund
    else:
        # Validate refund amount doesn't exceed booking amount
        if refund_amount > booking.amount_paid:
            raise HTTPException(status_code=400, detail="Refund amount cannot exceed booking amount")
    
    processing_fee = booking.amount_paid - refund_amount
    
    # Create refund record (add refund fields to booking model if not exists)
    # For now, store in admin_notes or create separate refund table
    refund_note = f"Refund processed: ₹{refund_amount:.2f} via {refund_method}. Processing fee: ₹{processing_fee:.2f}. Reference: {refund_reference or 'N/A'}"
    
    if booking.admin_notes:
        booking.admin_notes += f"\n{refund_note}"
    else:
        booking.admin_notes = refund_note
    
    # Mark refund as processed (if field exists)
    if hasattr(booking, 'refund_processed'):
        booking.refund_processed = True
    if hasattr(booking, 'refund_amount'):
        booking.refund_amount = refund_amount
    if hasattr(booking, 'refund_method'):
        booking.refund_method = refund_method
    if hasattr(booking, 'refund_reference'):
        booking.refund_reference = refund_reference
    if hasattr(booking, 'refund_processed_at'):
        booking.refund_processed_at = datetime.utcnow()
    if hasattr(booking, 'refund_processed_by'):
        booking.refund_processed_by = current_user.id
    
    # Create accounting entry for refund
    # Dr: Seva Income (reversal), Cr: Cash/Bank (refund payment)
    temple_id = current_user.temple_id if current_user else None
    if temple_id:
        try:
            # Get seva income account
            seva = booking.seva
            credit_account = None
            if seva and hasattr(seva, 'account_id') and seva.account_id:
                credit_account = db.query(Account).filter(Account.id == seva.account_id).first()
            
            if not credit_account:
                credit_account_code = '4200'  # Seva Income - Main
                credit_account = db.query(Account).filter(
                    Account.temple_id == temple_id,
                    Account.account_code == credit_account_code
                ).first()
            
            # Get debit account (refund payment method)
            debit_account_code = None
            if refund_method.upper() in ['CASH', 'COUNTER']:
                debit_account_code = '1101'  # Cash in Hand - Counter
            elif refund_method.upper() in ['BANK_TRANSFER', 'ONLINE']:
                debit_account_code = '1110'  # Bank Account
            else:
                debit_account_code = '1101'  # Default to cash
            
            debit_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == debit_account_code
            ).first()
            
            if debit_account and credit_account:
                # Generate entry number
                year = datetime.now().year
                prefix = f"JE/{year}/"
                last_entry = db.query(JournalEntry).filter(
                    JournalEntry.temple_id == temple_id,
                    JournalEntry.entry_number.like(f"{prefix}%")
                ).order_by(JournalEntry.id.desc()).first()
                
                if last_entry:
                    try:
                        last_num = int(last_entry.entry_number.split('/')[-1])
                        new_num = last_num + 1
                    except:
                        new_num = 1
                else:
                    new_num = 1
                
                entry_number = f"{prefix}{new_num:04d}"
                
                # Create journal entry for refund
                refund_entry = JournalEntry(
                    temple_id=temple_id,
                    entry_date=datetime.now().date(),
                    entry_number=entry_number,
                    narration=f"Refund for booking {booking.receipt_number} - {seva.name_english if seva else 'Seva'}",
                    reference_type=TransactionType.SEVA_BOOKING,
                    reference_id=booking.id,
                    total_amount=refund_amount,
                    status=JournalEntryStatus.POSTED,
                    created_by=current_user.id,
                    posted_by=current_user.id,
                    posted_at=datetime.utcnow()
                )
                db.add(refund_entry)
                db.flush()
                
                # Create journal lines
                # Dr: Seva Income (reversal - reduce income)
                db.add(JournalLine(
                    journal_entry_id=refund_entry.id,
                    account_id=credit_account.id,
                    debit_amount=refund_amount,
                    credit_amount=0,
                    description=f"Refund reversal for booking {booking.receipt_number}"
                ))
                
                # Cr: Cash/Bank (refund payment)
                db.add(JournalLine(
                    journal_entry_id=refund_entry.id,
                    account_id=debit_account.id,
                    debit_amount=0,
                    credit_amount=refund_amount,
                    description=f"Refund payment for booking {booking.receipt_number}"
                ))
                
                db.commit()
        except Exception as e:
            print(f"Failed to create refund accounting entry: {str(e)}")
            # Don't fail refund if accounting fails
    
    db.commit()
    db.refresh(booking)
    
    return {
        "message": "Refund processed successfully",
        "refund_amount": refund_amount,
        "processing_fee": processing_fee,
        "booking": SevaBookingResponse.from_orm(booking)
    }


@router.get("/bookings/{booking_id}/refund-status", response_model=dict)
def get_refund_status(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get refund status for a cancelled booking"""
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    refund_processed = hasattr(booking, 'refund_processed') and booking.refund_processed
    refund_amount = getattr(booking, 'refund_amount', None)
    refund_method = getattr(booking, 'refund_method', None)
    refund_reference = getattr(booking, 'refund_reference', None)
    
    # Calculate expected refund (90% of booking amount)
    expected_refund = booking.amount_paid * 0.9
    processing_fee = booking.amount_paid * 0.1
    
    return {
        "booking_id": booking.id,
        "receipt_number": booking.receipt_number,
        "booking_amount": booking.amount_paid,
        "expected_refund": expected_refund,
        "processing_fee": processing_fee,
        "refund_processed": refund_processed,
        "refund_amount": refund_amount,
        "refund_method": refund_method,
        "refund_reference": refund_reference,
        "refund_processed_at": getattr(booking, 'refund_processed_at', None),
        "is_cancelled": booking.status == SevaBookingStatus.CANCELLED
    }
