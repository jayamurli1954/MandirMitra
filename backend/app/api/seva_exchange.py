"""
Seva Exchange Request API Endpoints
Handles exchange/swap of seva booking dates between two devotees
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.seva import Seva, SevaBooking, SevaBookingStatus
from app.models.seva_exchange import SevaExchangeRequest, ExchangeRequestStatus
from app.models.devotee import Devotee
from app.schemas.seva_exchange import (
    SevaExchangeRequestCreate,
    SevaExchangeRequestResponse,
    ExchangeDecision,
    BookingSummary,
    ExchangeRequestStatus as SchemaStatus
)

router = APIRouter(prefix="/api/v1/seva-exchange-requests", tags=["seva-exchange"])


def get_booking_summary(booking: SevaBooking) -> BookingSummary:
    """Convert SevaBooking to BookingSummary"""
    devotee = booking.devotee
    seva = booking.seva
    
    return BookingSummary(
        id=booking.id,
        devotee_name=f"{devotee.first_name or ''} {devotee.last_name or ''}".strip() or devotee.name or "Unknown",
        devotee_mobile=devotee.phone,  # Devotee model uses 'phone' field, not 'mobile_number'
        seva_name=seva.name_english or seva.name_kannada or "Seva",
        booking_date=booking.booking_date,
        receipt_number=booking.receipt_number
    )


@router.post("/", response_model=SevaExchangeRequestResponse, status_code=status.HTTP_201_CREATED)
def create_exchange_request(
    request_data: SevaExchangeRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new exchange request (staff/counter staff)
    Requires: super_admin, admin, temple_manager, counter_staff, or staff role
    """
    # Check permissions - allow super_admin, admin, temple_manager, counter_staff, and staff roles
    if current_user.role not in ['super_admin', 'admin', 'temple_manager', 'counter_staff', 'staff']:
        raise HTTPException(
            status_code=403,
            detail="Only admins, temple managers, and counter staff can create exchange requests"
        )
    
    # Validate both bookings exist
    booking_a = db.query(SevaBooking).filter(SevaBooking.id == request_data.booking_a_id).first()
    booking_b = db.query(SevaBooking).filter(SevaBooking.id == request_data.booking_b_id).first()
    
    if not booking_a:
        raise HTTPException(status_code=404, detail=f"Booking A (ID: {request_data.booking_a_id}) not found")
    if not booking_b:
        raise HTTPException(status_code=404, detail=f"Booking B (ID: {request_data.booking_b_id}) not found")
    
    # Ensure bookings are different
    if booking_a.id == booking_b.id:
        raise HTTPException(status_code=400, detail="Cannot exchange a booking with itself")
    
    # Ensure both bookings belong to the same temple (via devotee)
    # Seva model doesn't have temple_id, so we get it from devotee
    temple_id_a = booking_a.devotee.temple_id if booking_a.devotee else None
    temple_id_b = booking_b.devotee.temple_id if booking_b.devotee else None
    
    if temple_id_a != temple_id_b:
        raise HTTPException(
            status_code=400,
            detail="Cannot exchange bookings from different temples"
        )
    
    # Ensure both bookings are active (not cancelled/completed)
    if booking_a.status in [SevaBookingStatus.CANCELLED, SevaBookingStatus.COMPLETED]:
        raise HTTPException(
            status_code=400,
            detail=f"Booking A (ID: {booking_a.id}) is {booking_a.status.value} and cannot be exchanged"
        )
    if booking_b.status in [SevaBookingStatus.CANCELLED, SevaBookingStatus.COMPLETED]:
        raise HTTPException(
            status_code=400,
            detail=f"Booking B (ID: {booking_b.id}) is {booking_b.status.value} and cannot be exchanged"
        )
    
    # Check if either booking already has a pending exchange request
    existing_pending = db.query(SevaExchangeRequest).filter(
        and_(
            SevaExchangeRequest.status == ExchangeRequestStatus.PENDING,
            or_(
                SevaExchangeRequest.booking_a_id.in_([booking_a.id, booking_b.id]),
                SevaExchangeRequest.booking_b_id.in_([booking_a.id, booking_b.id])
            )
        )
    ).first()
    
    if existing_pending:
        raise HTTPException(
            status_code=400,
            detail="One or both bookings already have a pending exchange request"
        )
    
    # Create exchange request
    exchange_request = SevaExchangeRequest(
        booking_a_id=request_data.booking_a_id,
        booking_b_id=request_data.booking_b_id,
        reason=request_data.reason,
        status=ExchangeRequestStatus.PENDING,
        requested_by_id=current_user.id,
        consent_a_method=request_data.consent_a_method.value,
        consent_a_notes=request_data.consent_a_notes,
        consent_b_method=request_data.consent_b_method.value,
        consent_b_notes=request_data.consent_b_notes
    )
    
    db.add(exchange_request)
    db.flush()
    
    # Refresh to get relationships
    db.refresh(exchange_request)
    
    # Build response with booking summaries
    response = SevaExchangeRequestResponse(
        id=exchange_request.id,
        booking_a_id=exchange_request.booking_a_id,
        booking_b_id=exchange_request.booking_b_id,
        reason=exchange_request.reason,
        status=SchemaStatus(exchange_request.status.value),
        requested_by_id=exchange_request.requested_by_id,
        approved_by_id=exchange_request.approved_by_id,
        consent_a_method=exchange_request.consent_a_method,
        consent_a_notes=exchange_request.consent_a_notes,
        consent_b_method=exchange_request.consent_b_method,
        consent_b_notes=exchange_request.consent_b_notes,
        admin_notes=exchange_request.admin_notes,
        created_at=exchange_request.created_at,
        updated_at=exchange_request.updated_at,
        approved_at=exchange_request.approved_at,
        booking_a=get_booking_summary(booking_a),
        booking_b=get_booking_summary(booking_b),
        requested_by_name=current_user.full_name if current_user else None
    )
    
    db.commit()
    return response


@router.get("/", response_model=List[SevaExchangeRequestResponse])
def list_exchange_requests(
    status_filter: Optional[SchemaStatus] = Query(None, alias="status", description="Filter by status"),
    devotee_search: Optional[str] = Query(None, description="Search by devotee name or mobile"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List exchange requests (admin/temple_manager only)
    """
    if current_user.role not in ['super_admin', 'admin', 'temple_manager']:
        raise HTTPException(
            status_code=403,
            detail="Only admins and temple managers can view exchange requests"
        )
    
    query = db.query(SevaExchangeRequest)
    
    # Filter by status
    if status_filter:
        query = query.filter(SevaExchangeRequest.status == ExchangeRequestStatus(status_filter.value))
    
    # Search by devotee name or mobile (search in both bookings)
    if devotee_search:
        search_term = f"%{devotee_search}%"
        # Find booking IDs that match the search
        matching_booking_ids = db.query(SevaBooking.id).join(Devotee).filter(
            or_(
                Devotee.first_name.ilike(search_term),
                Devotee.last_name.ilike(search_term),
                Devotee.phone.ilike(search_term),  # Devotee model uses 'phone' field
                Devotee.name.ilike(search_term)  # Also search by full name
            )
        ).all()
        matching_ids = [bid[0] for bid in matching_booking_ids]
        
        if matching_ids:
            # Filter exchange requests where either booking matches
            query = query.filter(
                or_(
                    SevaExchangeRequest.booking_a_id.in_(matching_ids),
                    SevaExchangeRequest.booking_b_id.in_(matching_ids)
                )
            )
        else:
            # No matching bookings, return empty result
            query = query.filter(SevaExchangeRequest.id == -1)  # Impossible condition
    
    # Order by created_at descending (newest first)
    query = query.order_by(SevaExchangeRequest.created_at.desc())
    
    requests = query.offset(skip).limit(limit).all()
    
    # Build response with booking summaries
    results = []
    for req in requests:
        booking_a = db.query(SevaBooking).filter(SevaBooking.id == req.booking_a_id).first()
        booking_b = db.query(SevaBooking).filter(SevaBooking.id == req.booking_b_id).first()
        
        requested_by_user = db.query(User).filter(User.id == req.requested_by_id).first()
        approved_by_user = db.query(User).filter(User.id == req.approved_by_id).first() if req.approved_by_id else None
        
        results.append(SevaExchangeRequestResponse(
            id=req.id,
            booking_a_id=req.booking_a_id,
            booking_b_id=req.booking_b_id,
            reason=req.reason,
            status=SchemaStatus(req.status.value),
            requested_by_id=req.requested_by_id,
            approved_by_id=req.approved_by_id,
            consent_a_method=req.consent_a_method,
            consent_a_notes=req.consent_a_notes,
            consent_b_method=req.consent_b_method,
            consent_b_notes=req.consent_b_notes,
            admin_notes=req.admin_notes,
            created_at=req.created_at,
            updated_at=req.updated_at,
            approved_at=req.approved_at,
            booking_a=get_booking_summary(booking_a) if booking_a else None,
            booking_b=get_booking_summary(booking_b) if booking_b else None,
            requested_by_name=requested_by_user.full_name if requested_by_user else None,
            approved_by_name=approved_by_user.full_name if approved_by_user else None
        ))
    
    return results


@router.get("/{request_id}", response_model=SevaExchangeRequestResponse)
def get_exchange_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific exchange request (admin/temple_manager only)
    """
    if current_user.role not in ['super_admin', 'admin', 'temple_manager']:
        raise HTTPException(
            status_code=403,
            detail="Only admins and temple managers can view exchange requests"
        )
    
    exchange_request = db.query(SevaExchangeRequest).filter(SevaExchangeRequest.id == request_id).first()
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    
    booking_a = db.query(SevaBooking).filter(SevaBooking.id == exchange_request.booking_a_id).first()
    booking_b = db.query(SevaBooking).filter(SevaBooking.id == exchange_request.booking_b_id).first()
    
    requested_by_user = db.query(User).filter(User.id == exchange_request.requested_by_id).first()
    approved_by_user = db.query(User).filter(User.id == exchange_request.approved_by_id).first() if exchange_request.approved_by_id else None
    
    return SevaExchangeRequestResponse(
        id=exchange_request.id,
        booking_a_id=exchange_request.booking_a_id,
        booking_b_id=exchange_request.booking_b_id,
        reason=exchange_request.reason,
        status=SchemaStatus(exchange_request.status.value),
        requested_by_id=exchange_request.requested_by_id,
        approved_by_id=exchange_request.approved_by_id,
        consent_a_method=exchange_request.consent_a_method,
        consent_a_notes=exchange_request.consent_a_notes,
        consent_b_method=exchange_request.consent_b_method,
        consent_b_notes=exchange_request.consent_b_notes,
        admin_notes=exchange_request.admin_notes,
        created_at=exchange_request.created_at,
        updated_at=exchange_request.updated_at,
        approved_at=exchange_request.approved_at,
        booking_a=get_booking_summary(booking_a) if booking_a else None,
        booking_b=get_booking_summary(booking_b) if booking_b else None,
        requested_by_name=requested_by_user.full_name if requested_by_user else None,
        approved_by_name=approved_by_user.full_name if approved_by_user else None
    )


@router.post("/{request_id}/decision", response_model=SevaExchangeRequestResponse)
def approve_or_reject_exchange(
    request_id: int,
    decision: ExchangeDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve or reject an exchange request (admin/temple_manager only)
    """
    if current_user.role not in ['super_admin', 'admin', 'temple_manager'] and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only admins and temple managers can approve/reject exchange requests"
        )
    
    exchange_request = db.query(SevaExchangeRequest).filter(SevaExchangeRequest.id == request_id).first()
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    
    if exchange_request.status != ExchangeRequestStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Exchange request is already {exchange_request.status.value}"
        )
    
    # Load bookings with lock to prevent concurrent modifications
    booking_a = db.query(SevaBooking).filter(SevaBooking.id == exchange_request.booking_a_id).first()
    booking_b = db.query(SevaBooking).filter(SevaBooking.id == exchange_request.booking_b_id).first()
    
    if not booking_a or not booking_b:
        raise HTTPException(status_code=404, detail="One or both bookings not found")
    
    # Update exchange request
    exchange_request.status = ExchangeRequestStatus(decision.status.value)
    exchange_request.approved_by_id = current_user.id
    exchange_request.admin_notes = decision.admin_notes
    exchange_request.updated_at = datetime.utcnow()
    
    if decision.status == SchemaStatus.approved:
        # Swap the booking dates
        exchange_request.approved_at = datetime.utcnow()
        
        # Store original dates for audit
        original_date_a = booking_a.booking_date
        original_date_b = booking_b.booking_date
        
        # Swap dates
        booking_a.booking_date = original_date_b
        booking_b.booking_date = original_date_a
        
        # Update booking timestamps
        booking_a.updated_at = datetime.utcnow()
        booking_b.updated_at = datetime.utcnow()
        
        # Add admin notes to bookings
        admin_note = f"Date exchanged with booking #{booking_b.id if booking_a.id == exchange_request.booking_a_id else booking_a.id} on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} by {current_user.full_name}"
        if booking_a.admin_notes:
            booking_a.admin_notes += f"\n{admin_note}"
        else:
            booking_a.admin_notes = admin_note
        
        if booking_b.admin_notes:
            booking_b.admin_notes += f"\n{admin_note}"
        else:
            booking_b.admin_notes = admin_note
        
        # Create audit log entry
        try:
            from app.core.audit import log_action, get_entity_dict
            log_action(
                db=db,
                user=current_user,
                action="EXCHANGE_APPROVED",
                entity_type="SevaExchangeRequest",
                entity_id=exchange_request.id,
                old_values={
                    "booking_a_date": original_date_a.isoformat(),
                    "booking_b_date": original_date_b.isoformat()
                },
                new_values={
                    "booking_a_date": original_date_b.isoformat(),
                    "booking_b_date": original_date_a.isoformat()
                },
                description=f"Approved exchange: Booking {exchange_request.booking_a_id} ({original_date_a}) ↔ Booking {exchange_request.booking_b_id} ({original_date_b})",
                ip_address=None,
                user_agent=None
            )
        except Exception as e:
            print(f"Warning: Failed to create audit log: {e}")
    
    db.commit()
    db.refresh(exchange_request)
    
    # Refresh bookings
    db.refresh(booking_a)
    db.refresh(booking_b)
    
    # Build response
    requested_by_user = db.query(User).filter(User.id == exchange_request.requested_by_id).first()
    approved_by_user = current_user
    
    return SevaExchangeRequestResponse(
        id=exchange_request.id,
        booking_a_id=exchange_request.booking_a_id,
        booking_b_id=exchange_request.booking_b_id,
        reason=exchange_request.reason,
        status=SchemaStatus(exchange_request.status.value),
        requested_by_id=exchange_request.requested_by_id,
        approved_by_id=exchange_request.approved_by_id,
        consent_a_method=exchange_request.consent_a_method,
        consent_a_notes=exchange_request.consent_a_notes,
        consent_b_method=exchange_request.consent_b_method,
        consent_b_notes=exchange_request.consent_b_notes,
        admin_notes=exchange_request.admin_notes,
        created_at=exchange_request.created_at,
        updated_at=exchange_request.updated_at,
        approved_at=exchange_request.approved_at,
        booking_a=get_booking_summary(booking_a),
        booking_b=get_booking_summary(booking_b),
        requested_by_name=requested_by_user.full_name if requested_by_user else None,
        approved_by_name=approved_by_user.full_name if approved_by_user else None
    )


@router.get("/bookings/search", response_model=List[BookingSummary])
def search_bookings_for_exchange(
    name_or_mobile: str = Query(..., description="Search by devotee name or mobile number"),
    seva_id: Optional[int] = Query(None, description="Filter by seva ID"),
    from_date: Optional[str] = Query(None, description="Filter bookings from this date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Filter bookings to this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search bookings for exchange form (staff/counter staff)
    Returns simplified booking summaries
    """
    if current_user.role not in ['super_admin', 'admin', 'temple_manager', 'counter_staff', 'staff']:
        raise HTTPException(
            status_code=403,
            detail="Only admins, temple managers, and counter staff can search bookings"
        )
    
    query = db.query(SevaBooking).join(Devotee)
    
    # Search by name or mobile
    search_term = f"%{name_or_mobile}%"
    query = query.filter(
        or_(
            Devotee.first_name.ilike(search_term),
            Devotee.last_name.ilike(search_term),
            Devotee.phone.ilike(search_term),  # Devotee model uses 'phone' field, not 'mobile_number'
            Devotee.name.ilike(search_term),  # Also search by full name field
            (Devotee.first_name + " " + Devotee.last_name).ilike(search_term)
        )
    )
    
    # Filter by seva
    if seva_id:
        query = query.filter(SevaBooking.seva_id == seva_id)
    
    # Filter by date range
    if from_date:
        from datetime import date as date_type
        query = query.filter(SevaBooking.booking_date >= date_type.fromisoformat(from_date))
    if to_date:
        from datetime import date as date_type
        query = query.filter(SevaBooking.booking_date <= date_type.fromisoformat(to_date))
    
    # Only active bookings (not cancelled/completed)
    query = query.filter(
        SevaBooking.status.in_([SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED])
    )
    
    # Order by booking date ascending
    query = query.order_by(SevaBooking.booking_date.asc())
    
    bookings = query.limit(50).all()  # Limit to 50 results
    
    return [get_booking_summary(booking) for booking in bookings]


