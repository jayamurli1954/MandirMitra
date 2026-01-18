"""
Payment Gateway API Endpoints
Handles online payment processing via Razorpay
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.donation import Donation
from app.models.seva import SevaBooking
from app.models.devotee import Devotee
from app.models.accounting import (
    JournalEntry,
    JournalLine,
    JournalEntryStatus,
    TransactionType,
    Account,
)
from app.services.payment_gateway import payment_gateway_service
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/payments", tags=["payment-gateway"])


# Schemas
class CreatePaymentRequest(BaseModel):
    """Request to create a payment order"""

    amount: float = Field(..., gt=0, description="Amount in rupees")
    purpose: str = Field(..., description="Purpose: donation, seva, sponsorship")
    devotee_id: int = Field(..., description="Devotee ID")
    donation_category_id: Optional[int] = None  # For donations
    seva_id: Optional[int] = None  # For seva bookings
    seva_booking_date: Optional[str] = None  # For seva bookings
    notes: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None


class CreatePaymentResponse(BaseModel):
    """Response after creating payment order"""

    order_id: str
    amount: float
    currency: str
    key_id: str
    receipt: Optional[str] = None
    notes: Optional[Dict[str, str]] = None


class VerifyPaymentRequest(BaseModel):
    """Request to verify payment"""

    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    purpose: str  # donation, seva, sponsorship
    devotee_id: int
    donation_category_id: Optional[int] = None
    seva_id: Optional[int] = None
    seva_booking_date: Optional[str] = None
    notes: Optional[str] = None


class VerifyPaymentResponse(BaseModel):
    """Response after verifying payment"""

    success: bool
    payment_id: str
    order_id: str
    amount: float
    donation_id: Optional[int] = None
    seva_booking_id: Optional[int] = None
    message: str


class PaymentStatusResponse(BaseModel):
    """Payment status response"""

    payment_id: str
    order_id: str
    status: str
    amount: float
    currency: str
    created_at: int
    method: Optional[str] = None
    description: Optional[str] = None


@router.get("/status")
def get_payment_gateway_status():
    """Check if payment gateway is enabled"""
    return {
        "enabled": payment_gateway_service.is_enabled(),
        "gateway": "razorpay" if payment_gateway_service.is_enabled() else None,
    }


@router.post("/create-order", response_model=CreatePaymentResponse)
def create_payment_order(
    request: CreatePaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a Razorpay payment order

    This creates an order in Razorpay and returns order details
    that can be used by the frontend to initiate payment
    """
    if not payment_gateway_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment gateway is not enabled. Please configure Razorpay keys.",
        )

    # Verify devotee exists
    devotee = (
        db.query(Devotee)
        .filter(Devotee.id == request.devotee_id, Devotee.temple_id == current_user.temple_id)
        .first()
    )

    if not devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")

    # Generate receipt number
    year = datetime.now().year
    if request.purpose == "donation":
        receipt_prefix = f"DON/{year}/"
    elif request.purpose == "seva":
        receipt_prefix = f"SEVA/{year}/"
    else:
        receipt_prefix = f"PAY/{year}/"

    # Get last receipt number
    last_donation = (
        db.query(Donation)
        .filter(Donation.receipt_number.like(f"{receipt_prefix}%"))
        .order_by(Donation.id.desc())
        .first()
    )

    if last_donation and last_donation.receipt_number:
        try:
            last_num = int(last_donation.receipt_number.split("/")[-1])
            receipt_number = f"{receipt_prefix}{last_num + 1:04d}"
        except:
            receipt_number = f"{receipt_prefix}0001"
    else:
        receipt_number = f"{receipt_prefix}0001"

    # Prepare notes for Razorpay
    notes = {
        "temple_id": str(current_user.temple_id),
        "devotee_id": str(request.devotee_id),
        "purpose": request.purpose,
        "created_by": str(current_user.id),
    }

    if request.donation_category_id:
        notes["donation_category_id"] = str(request.donation_category_id)
    if request.seva_id:
        notes["seva_id"] = str(request.seva_id)
    if request.seva_booking_date:
        notes["seva_booking_date"] = request.seva_booking_date
    if request.notes:
        notes["notes"] = request.notes

    # Create order in Razorpay
    try:
        order = payment_gateway_service.create_order(
            amount=request.amount,
            currency="INR",
            receipt=receipt_number,
            notes=notes,
            customer_id=str(request.devotee_id),
            customer_name=request.customer_name or devotee.name,
            customer_email=request.customer_email or devotee.email,
            customer_contact=request.customer_phone or devotee.phone,
        )

        return CreatePaymentResponse(
            order_id=order["id"],
            amount=request.amount,
            currency=order.get("currency", "INR"),
            key_id=payment_gateway_service.client.auth[0],  # Razorpay key ID
            receipt=receipt_number,
            notes=notes,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment order: {str(e)}",
        )


@router.post("/verify", response_model=VerifyPaymentResponse)
def verify_payment(
    request: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Verify Razorpay payment and create donation/seva booking

    This endpoint is called after payment is successful
    """
    if not payment_gateway_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment gateway is not enabled"
        )

    # Verify payment signature
    is_valid = payment_gateway_service.verify_payment(
        razorpay_order_id=request.razorpay_order_id,
        razorpay_payment_id=request.razorpay_payment_id,
        razorpay_signature=request.razorpay_signature,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment signature"
        )

    # Get payment details from Razorpay
    try:
        payment_details = payment_gateway_service.get_payment(request.razorpay_payment_id)
        order_details = payment_gateway_service.get_order(request.razorpay_order_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment details: {str(e)}",
        )

    # Verify devotee
    devotee = (
        db.query(Devotee)
        .filter(Devotee.id == request.devotee_id, Devotee.temple_id == current_user.temple_id)
        .first()
    )

    if not devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")

    amount = payment_details.get("amount", 0) / 100  # Convert from paise to rupees
    donation_id = None
    seva_booking_id = None

    # Create donation or seva booking based on purpose
    if request.purpose == "donation":
        if not request.donation_category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="donation_category_id is required for donation payments",
            )

        # Create donation
        donation = Donation(
            temple_id=current_user.temple_id,
            devotee_id=request.devotee_id,
            category_id=request.donation_category_id,
            receipt_number=order_details.get("receipt", ""),
            amount=amount,
            payment_mode="online",
            transaction_id=request.razorpay_payment_id,
            donation_date=datetime.utcnow().date(),
            notes=request.notes,
            created_by=current_user.id,
        )
        db.add(donation)
        db.flush()
        donation_id = donation.id

    elif request.purpose == "seva":
        if not request.seva_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="seva_id is required for seva payments",
            )

        # Parse booking date
        booking_date = datetime.utcnow().date()
        if request.seva_booking_date:
            try:
                booking_date = datetime.strptime(request.seva_booking_date, "%Y-%m-%d").date()
            except:
                pass

        # Create seva booking
        seva_booking = SevaBooking(
            temple_id=current_user.temple_id,
            devotee_id=request.devotee_id,
            seva_id=request.seva_id,
            booking_date=booking_date,
            amount_paid=amount,
            payment_method="online",
            payment_status="paid",
            transaction_id=request.razorpay_payment_id,
            notes=request.notes,
            created_by=current_user.id,
        )
        db.add(seva_booking)
        db.flush()
        seva_booking_id = seva_booking.id

    # Post to accounting
    journal_entry = None
    if request.purpose == "donation" and donation_id:
        # Post donation to accounting
        donation = db.query(Donation).filter(Donation.id == donation_id).first()
        if donation:
            # Get bank account (for online payments)
            bank_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == current_user.temple_id,
                    Account.account_code.like("12%"),  # Bank accounts (12000-12999)
                    Account.is_active == True,
                )
                .first()
            )

            # Get income account from donation category
            income_account = None
            if donation.category and donation.category.account_id:
                income_account = (
                    db.query(Account)
                    .filter(Account.id == donation.category.account_id, Account.is_active == True)
                    .first()
                )

            if not income_account:
                # Default donation income account
                income_account = (
                    db.query(Account)
                    .filter(
                        Account.temple_id == current_user.temple_id,
                        Account.account_code == "44001",  # General Donations
                        Account.is_active == True,
                    )
                    .first()
                )

            if bank_account and income_account:
                # Create journal entry
                entry_number = f"JE/{datetime.now().year}/{donation.id:04d}"
                narration = f"Online donation via Razorpay - {devotee.name}"

                journal_entry = JournalEntry(
                    entry_number=entry_number,
                    entry_date=datetime.utcnow(),
                    narration=narration,
                    reference_type=TransactionType.DONATION,
                    reference_id=donation.id,
                    temple_id=current_user.temple_id,
                    total_amount=amount,
                    status=JournalEntryStatus.POSTED,
                    created_by=current_user.id,
                    posted_by=current_user.id,
                    posted_at=datetime.utcnow(),
                )
                db.add(journal_entry)
                db.flush()

                # Debit: Bank Account
                debit_line = JournalLine(
                    journal_entry_id=journal_entry.id,
                    account_id=bank_account.id,
                    debit_amount=amount,
                    credit_amount=0.0,
                    description="Online payment received via Razorpay",
                )
                db.add(debit_line)

                # Credit: Income Account
                credit_line = JournalLine(
                    journal_entry_id=journal_entry.id,
                    account_id=income_account.id,
                    debit_amount=0.0,
                    credit_amount=amount,
                    description=f"Donation income - {donation.category.name if donation.category else 'General'}",
                )
                db.add(credit_line)

                donation.journal_entry_id = journal_entry.id

    elif request.purpose == "seva" and seva_booking_id:
        # Post seva booking to accounting
        seva_booking = db.query(SevaBooking).filter(SevaBooking.id == seva_booking_id).first()
        if seva_booking:
            # Get bank account
            bank_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == current_user.temple_id,
                    Account.account_code.like("12%"),  # Bank accounts (12000-12999)
                    Account.is_active == True,
                )
                .first()
            )

            # Get seva income account
            seva_income_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == current_user.temple_id,
                    Account.account_code.like("420%"),  # Seva Income (42000-42999)
                    Account.is_active == True,
                )
                .first()
            )

            if bank_account and seva_income_account:
                # Create journal entry
                entry_number = f"JE/{datetime.now().year}/{seva_booking.id:04d}"
                narration = f"Seva booking payment via Razorpay - {devotee.name}"

                journal_entry = JournalEntry(
                    entry_number=entry_number,
                    entry_date=datetime.utcnow(),
                    narration=narration,
                    reference_type=TransactionType.SEVA_BOOKING,
                    reference_id=seva_booking.id,
                    temple_id=current_user.temple_id,
                    total_amount=amount,
                    status=JournalEntryStatus.POSTED,
                    created_by=current_user.id,
                    posted_by=current_user.id,
                    posted_at=datetime.utcnow(),
                )
                db.add(journal_entry)
                db.flush()

                # Debit: Bank Account
                debit_line = JournalLine(
                    journal_entry_id=journal_entry.id,
                    account_id=bank_account.id,
                    debit_amount=amount,
                    credit_amount=0.0,
                    description="Seva booking payment via Razorpay",
                )
                db.add(debit_line)

                # Credit: Seva Income Account
                credit_line = JournalLine(
                    journal_entry_id=journal_entry.id,
                    account_id=seva_income_account.id,
                    debit_amount=0.0,
                    credit_amount=amount,
                    description=f"Seva income - {seva_booking.seva.name_english if seva_booking.seva else 'Seva'}",
                )
                db.add(credit_line)

                seva_booking.journal_entry_id = journal_entry.id

    db.commit()

    return VerifyPaymentResponse(
        success=True,
        payment_id=request.razorpay_payment_id,
        order_id=request.razorpay_order_id,
        amount=amount,
        donation_id=donation_id,
        seva_booking_id=seva_booking_id,
        message="Payment verified and transaction created successfully",
    )


@router.get("/status/{payment_id}", response_model=PaymentStatusResponse)
def get_payment_status(
    payment_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get payment status from Razorpay"""
    if not payment_gateway_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment gateway is not enabled"
        )

    try:
        payment = payment_gateway_service.get_payment(payment_id)

        return PaymentStatusResponse(
            payment_id=payment.get("id", ""),
            order_id=payment.get("order_id", ""),
            status=payment.get("status", ""),
            amount=payment.get("amount", 0) / 100,  # Convert from paise
            currency=payment.get("currency", "INR"),
            created_at=payment.get("created_at", 0),
            method=payment.get("method", ""),
            description=payment.get("description", ""),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment status: {str(e)}",
        )


@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Razorpay webhook events

    This endpoint receives webhook notifications from Razorpay
    about payment status changes, refunds, etc.
    """
    if not payment_gateway_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment gateway is not enabled"
        )

    # Get webhook signature from headers
    signature = request.headers.get("X-Razorpay-Signature")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing webhook signature"
        )

    # Get request body
    body = await request.body()
    payload = body.decode("utf-8")

    # Verify webhook signature
    is_valid = payment_gateway_service.verify_webhook_signature(
        payload=payload, signature=signature
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature"
        )

    # Parse webhook event
    import json

    event = json.loads(payload)

    event_type = event.get("event")
    payload_data = event.get("payload", {}).get("payment", {})
    payment_id = payload_data.get("entity", {}).get("id", "")

    # Handle different event types
    if event_type == "payment.captured":
        # Payment was successfully captured
        # Update donation/seva booking status if needed
        pass
    elif event_type == "payment.failed":
        # Payment failed
        # Log failure, notify user
        pass
    elif event_type == "payment.refunded":
        # Refund was processed
        # Update transaction status
        pass

    # Return success to Razorpay
    return {"status": "success"}


@router.post("/refund")
def create_refund(
    payment_id: str,
    amount: Optional[float] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a refund for a payment

    Args:
        payment_id: Razorpay payment ID
        amount: Refund amount (if None, full refund)
        notes: Refund notes
    """
    if not payment_gateway_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment gateway is not enabled"
        )

    try:
        refund_notes = {}
        if notes:
            refund_notes["reason"] = notes
        refund_notes["refunded_by"] = str(current_user.id)

        refund = payment_gateway_service.refund_payment(
            payment_id=payment_id, amount=amount, notes=refund_notes if refund_notes else None
        )

        return {
            "success": True,
            "refund_id": refund.get("id", ""),
            "amount": refund.get("amount", 0) / 100,  # Convert from paise
            "status": refund.get("status", ""),
            "message": "Refund processed successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process refund: {str(e)}",
        )
