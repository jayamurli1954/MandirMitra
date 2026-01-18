"""
UPI Payment API Endpoints
Quick logging of UPI payments received via static QR code
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.upi_banking import UpiPayment, UpiPaymentPurpose
from app.models.devotee import Devotee
from app.models.donation import Donation
from app.models.seva import SevaBooking
from app.models.inkind_sponsorship import Sponsorship
from app.models.accounting import (
    Account,
    JournalEntry,
    JournalLine,
    JournalEntryStatus,
    TransactionType,
)
from app.schemas.upi_payment import (
    UpiPaymentCreate,
    UpiPaymentQuickLog,
    UpiPaymentResponse,
    DailyUpiSummary,
)

router = APIRouter(prefix="/api/v1/upi-payments", tags=["upi-payments"])


def generate_receipt_number(db: Session, temple_id: int, purpose: UpiPaymentPurpose) -> str:
    """
    Generate unique receipt number based on purpose
    """
    year = datetime.now().year

    # Get prefix based on purpose
    if purpose == UpiPaymentPurpose.DONATION:
        prefix = f"DON/{year}/"
    elif purpose == UpiPaymentPurpose.SEVA:
        prefix = f"SEVA/{year}/"
    elif purpose == UpiPaymentPurpose.SPONSORSHIP:
        prefix = f"SP/{year}/"
    else:
        prefix = f"UPI/{year}/"

    # Get last receipt number
    last_payment = (
        db.query(UpiPayment)
        .filter(UpiPayment.temple_id == temple_id, UpiPayment.receipt_number.like(f"{prefix}%"))
        .order_by(UpiPayment.id.desc())
        .first()
    )

    if last_payment and last_payment.receipt_number:
        try:
            last_num = int(last_payment.receipt_number.split("/")[-1])
            new_num = last_num + 1
        except:
            new_num = 1
    else:
        new_num = 1

    return f"{prefix}{new_num:04d}"


def post_to_accounts(
    db: Session, temple_id: int, upi_payment: UpiPayment, current_user: User
) -> Optional[JournalEntry]:
    """
    Auto-post UPI payment to accounting
    Dr. Bank Account
       Cr. Income Account (based on purpose)
    """
    try:
        # Get bank account (primary UPI account)
        bank_account = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.account_code.like("111%"),  # Bank accounts
                Account.is_active == True,
            )
            .first()
        )

        if not bank_account:
            print(f"⚠️ Warning: No bank account found for temple {temple_id}")
            return None

        # Get income account based on purpose
        if upi_payment.payment_purpose == UpiPaymentPurpose.DONATION:
            income_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code == "4102",  # Donation - Online/UPI
                    Account.is_active == True,
                )
                .first()
            )
        elif upi_payment.payment_purpose == UpiPaymentPurpose.SEVA:
            income_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code.like("420%"),  # Seva Income
                    Account.is_active == True,
                )
                .first()
            )
        elif upi_payment.payment_purpose == UpiPaymentPurpose.SPONSORSHIP:
            income_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code.like("430%"),  # Sponsorship Income
                    Account.is_active == True,
                )
                .first()
            )
        else:
            # Other income
            income_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code == "4500",  # Other Income
                    Account.is_active == True,
                )
                .first()
            )

        if not income_account:
            print(f"⚠️ Warning: No income account found for purpose {upi_payment.payment_purpose}")
            return None

        # Generate entry number
        entry_number = f"JE/{datetime.now().year}/{upi_payment.id:04d}"

        # Create journal entry
        narration = f"UPI Payment - {upi_payment.payment_purpose.value.title()}"
        if upi_payment.devotee:
            narration += f" from {upi_payment.devotee.name}"

        journal_entry = JournalEntry(
            entry_number=entry_number,
            entry_date=upi_payment.payment_datetime,
            narration=narration,
            reference_type=TransactionType.UPI_PAYMENT,
            reference_id=upi_payment.id,
            temple_id=temple_id,
            total_amount=upi_payment.amount,
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
            debit_amount=upi_payment.amount,
            credit_amount=0.0,
            description=f"UPI payment received",
        )
        db.add(debit_line)

        # Credit: Income Account
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=income_account.id,
            debit_amount=0.0,
            credit_amount=upi_payment.amount,
            description=f"{upi_payment.payment_purpose.value.title()} income",
        )
        db.add(credit_line)

        db.flush()
        return journal_entry

    except Exception as e:
        print(f"❌ Error posting to accounts: {e}")
        return None


@router.post("/quick-log", response_model=UpiPaymentResponse)
def quick_log_payment(
    payment_data: UpiPaymentQuickLog,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Quick log UPI payment (mobile-friendly for admins)
    Called immediately when admin receives SMS about payment
    """
    # Verify devotee exists
    devotee = (
        db.query(Devotee)
        .filter(Devotee.id == payment_data.devotee_id, Devotee.temple_id == current_user.temple_id)
        .first()
    )

    if not devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")

    # Extract UPI ID from phone if not provided
    sender_upi_id = f"{payment_data.sender_phone}@upi"

    # Create UPI payment record
    upi_payment = UpiPayment(
        temple_id=current_user.temple_id,
        devotee_id=payment_data.devotee_id,
        amount=payment_data.amount,
        payment_datetime=datetime.utcnow(),
        sender_upi_id=sender_upi_id,
        sender_phone=payment_data.sender_phone,
        upi_reference_number=payment_data.upi_reference_number,
        payment_purpose=payment_data.payment_purpose,
        notes=payment_data.notes,
        logged_by=current_user.id,
    )

    # If SEVA purpose and seva_id provided, create seva booking
    if payment_data.payment_purpose == UpiPaymentPurpose.SEVA and payment_data.seva_id:
        seva_booking = SevaBooking(
            temple_id=current_user.temple_id,
            devotee_id=payment_data.devotee_id,
            seva_id=payment_data.seva_id,
            booking_date=date.today(),
            amount_paid=payment_data.amount,
            payment_method="upi",
            payment_status="paid",
        )
        db.add(seva_booking)
        db.flush()
        upi_payment.seva_booking_id = seva_booking.id

    # If DONATION purpose, create donation record
    elif payment_data.payment_purpose == UpiPaymentPurpose.DONATION:
        donation = Donation(
            temple_id=current_user.temple_id,
            devotee_id=payment_data.devotee_id,
            amount=payment_data.amount,
            payment_method="upi",
            donation_date=datetime.utcnow(),
        )
        db.add(donation)
        db.flush()
        upi_payment.donation_id = donation.id

    # If SPONSORSHIP purpose
    elif (
        payment_data.payment_purpose == UpiPaymentPurpose.SPONSORSHIP
        and payment_data.sponsorship_id
    ):
        upi_payment.sponsorship_id = payment_data.sponsorship_id

    db.add(upi_payment)
    db.flush()

    # Generate receipt number
    receipt_number = generate_receipt_number(
        db, current_user.temple_id, payment_data.payment_purpose
    )
    upi_payment.receipt_number = receipt_number

    # Post to accounting
    journal_entry = post_to_accounts(db, current_user.temple_id, upi_payment, current_user)
    if journal_entry:
        upi_payment.journal_entry_id = journal_entry.id

    db.commit()
    db.refresh(upi_payment)

    # Populate devotee name
    upi_payment.devotee_name = devotee.name

    return upi_payment


@router.get("/", response_model=List[UpiPaymentResponse])
def list_upi_payments(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    payment_purpose: Optional[UpiPaymentPurpose] = None,
    is_reconciled: Optional[bool] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get list of UPI payments with filters
    """
    query = db.query(UpiPayment).filter(UpiPayment.temple_id == current_user.temple_id)

    if from_date:
        query = query.filter(func.date(UpiPayment.payment_datetime) >= from_date)

    if to_date:
        query = query.filter(func.date(UpiPayment.payment_datetime) <= to_date)

    if payment_purpose:
        query = query.filter(UpiPayment.payment_purpose == payment_purpose)

    if is_reconciled is not None:
        query = query.filter(UpiPayment.is_bank_reconciled == is_reconciled)

    payments = query.order_by(UpiPayment.payment_datetime.desc()).limit(limit).offset(offset).all()

    # Populate devotee names
    for payment in payments:
        if payment.devotee:
            payment.devotee_name = payment.devotee.name

    return payments


@router.get("/daily-summary", response_model=DailyUpiSummary)
def get_daily_summary(
    summary_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get daily summary of UPI payments
    """
    payments = (
        db.query(UpiPayment)
        .filter(
            UpiPayment.temple_id == current_user.temple_id,
            func.date(UpiPayment.payment_datetime) == summary_date,
        )
        .all()
    )

    total_amount = sum(p.amount for p in payments)
    total_count = len(payments)

    # Group by purpose
    by_purpose = {}
    for payment in payments:
        purpose = payment.payment_purpose.value
        if purpose not in by_purpose:
            by_purpose[purpose] = {"amount": 0, "count": 0}
        by_purpose[purpose]["amount"] += payment.amount
        by_purpose[purpose]["count"] += 1

    # Reconciliation counts
    reconciled_count = sum(1 for p in payments if p.is_bank_reconciled)
    unreconciled_count = total_count - reconciled_count

    return DailyUpiSummary(
        date=summary_date.isoformat(),
        total_amount=total_amount,
        total_count=total_count,
        by_purpose=by_purpose,
        reconciled_count=reconciled_count,
        unreconciled_count=unreconciled_count,
    )


@router.get("/{payment_id}", response_model=UpiPaymentResponse)
def get_upi_payment(
    payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get UPI payment by ID
    """
    payment = (
        db.query(UpiPayment)
        .filter(UpiPayment.id == payment_id, UpiPayment.temple_id == current_user.temple_id)
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="UPI payment not found")

    # Populate devotee name
    if payment.devotee:
        payment.devotee_name = payment.devotee.name

    return payment
