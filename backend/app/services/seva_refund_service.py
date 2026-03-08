from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.accounting import (
    Account,
    JournalEntry,
    JournalEntryStatus,
    JournalLine,
    TransactionType,
)
from app.models.seva import SevaBooking, SevaBookingStatus
from app.schemas.seva import SevaBookingResponse


def process_refund(
    db: Session,
    booking_id: int,
    current_user,
    refund_amount: Optional[float] = None,
    refund_method: str = "original",
    refund_reference: Optional[str] = None,
):
    if current_user.role not in ["admin", "accountant", "temple_manager"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can process refunds")

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != SevaBookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Booking must be cancelled before processing refund")

    if hasattr(booking, "refund_processed") and booking.refund_processed:
        raise HTTPException(status_code=400, detail="Refund already processed for this booking")

    if refund_amount is None:
        refund_amount = booking.amount_paid * 0.9
    elif refund_amount > booking.amount_paid:
        raise HTTPException(status_code=400, detail="Refund amount cannot exceed booking amount")

    processing_fee = booking.amount_paid - refund_amount

    refund_note = (
        f"Refund processed: Rs.{refund_amount:.2f} via {refund_method}. "
        f"Processing fee: Rs.{processing_fee:.2f}. Reference: {refund_reference or 'N/A'}"
    )

    if booking.admin_notes:
        booking.admin_notes += f"\n{refund_note}"
    else:
        booking.admin_notes = refund_note

    if hasattr(booking, "refund_processed"):
        booking.refund_processed = True
    if hasattr(booking, "refund_amount"):
        booking.refund_amount = refund_amount
    if hasattr(booking, "refund_method"):
        booking.refund_method = refund_method
    if hasattr(booking, "refund_reference"):
        booking.refund_reference = refund_reference
    if hasattr(booking, "refund_processed_at"):
        booking.refund_processed_at = datetime.utcnow()
    if hasattr(booking, "refund_processed_by"):
        booking.refund_processed_by = current_user.id

    temple_id = current_user.temple_id if current_user else None
    if temple_id:
        try:
            seva = booking.seva
            credit_account = None
            if seva and hasattr(seva, "account_id") and seva.account_id:
                credit_account = db.query(Account).filter(Account.id == seva.account_id).first()

            if not credit_account:
                credit_account = (
                    db.query(Account)
                    .filter(
                        Account.temple_id == temple_id,
                        Account.account_code == "42002",
                    )
                    .first()
                )

            if refund_method.upper() in ["CASH", "COUNTER"]:
                debit_account_code = "11001"
            elif refund_method.upper() in ["BANK_TRANSFER", "ONLINE"]:
                debit_account_code = "12001"
            else:
                debit_account_code = "11001"

            debit_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code == debit_account_code,
                )
                .first()
            )

            if debit_account and credit_account:
                year = datetime.now().year
                prefix = f"JE/{year}/"
                from sqlalchemy.orm import load_only

                last_entry = (
                    db.query(JournalEntry)
                    .options(load_only(JournalEntry.id, JournalEntry.entry_number, JournalEntry.temple_id))
                    .filter(
                        JournalEntry.temple_id == temple_id,
                        JournalEntry.entry_number.like(f"{prefix}%"),
                    )
                    .order_by(JournalEntry.id.desc())
                    .first()
                )

                if last_entry:
                    try:
                        last_num = int(last_entry.entry_number.split("/")[-1])
                        new_num = last_num + 1
                    except Exception:
                        new_num = 1
                else:
                    new_num = 1

                entry_number = f"{prefix}{new_num:04d}"

                refund_entry = JournalEntry(
                    temple_id=temple_id,
                    entry_date=datetime.now().date(),
                    entry_number=entry_number,
                    narration=(
                        f"Refund for booking {booking.receipt_number} - "
                        f"{seva.name_english if seva else 'Seva'}"
                    ),
                    reference_type=TransactionType.SEVA_BOOKING,
                    reference_id=booking.id,
                    total_amount=refund_amount,
                    status=JournalEntryStatus.POSTED,
                    created_by=current_user.id,
                    posted_by=current_user.id,
                    posted_at=datetime.utcnow(),
                )
                db.add(refund_entry)
                db.flush()

                db.add(
                    JournalLine(
                        journal_entry_id=refund_entry.id,
                        account_id=credit_account.id,
                        debit_amount=refund_amount,
                        credit_amount=0,
                        description=f"Refund reversal for booking {booking.receipt_number}",
                    )
                )

                db.add(
                    JournalLine(
                        journal_entry_id=refund_entry.id,
                        account_id=debit_account.id,
                        debit_amount=0,
                        credit_amount=refund_amount,
                        description=f"Refund payment for booking {booking.receipt_number}",
                    )
                )

                db.commit()
        except Exception as e:
            print(f"Failed to create refund accounting entry: {str(e)}")

    db.commit()
    db.refresh(booking)

    return {
        "message": "Refund processed successfully",
        "refund_amount": refund_amount,
        "processing_fee": processing_fee,
        "booking": SevaBookingResponse.from_orm(booking),
    }


def get_refund_status(
    db: Session,
    booking_id: int,
):
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    refund_processed = hasattr(booking, "refund_processed") and booking.refund_processed
    refund_amount = getattr(booking, "refund_amount", None)
    refund_method = getattr(booking, "refund_method", None)
    refund_reference = getattr(booking, "refund_reference", None)

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
        "refund_processed_at": getattr(booking, "refund_processed_at", None),
        "is_cancelled": booking.status == SevaBookingStatus.CANCELLED,
    }
