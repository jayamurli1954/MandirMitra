from datetime import date, datetime, timedelta
from typing import Callable

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


def transfer_advance_booking_to_income(
    db: Session,
    booking_id: int,
    current_user,
):
    if current_user.role not in ["admin", "accountant", "temple_manager"] and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only authorized users can perform this action")

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Seva booking not found")

    if booking.booking_date > date.today():
        raise HTTPException(status_code=400, detail="Cannot transfer advance booking before the actual seva date")

    temple_id = current_user.temple_id
    if not temple_id:
        if booking.devotee and hasattr(booking.devotee, "temple_id"):
            temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id"):
            temple_id = booking.user.temple_id
        else:
            raise HTTPException(status_code=400, detail="User is not associated with a temple.")

    existing_transfer_entry = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.reference_type == TransactionType.ADVANCE_SEVA_TRANSFER,
            JournalEntry.reference_id == booking.id,
        )
        .first()
    )

    if existing_transfer_entry:
        raise HTTPException(status_code=400, detail="Advance booking already transferred to income")

    advance_seva_account = (
        db.query(Account)
        .filter(Account.temple_id == temple_id, Account.account_code == "21003")
        .first()
    )

    seva_income_account = (
        db.query(Account)
        .filter(Account.temple_id == temple_id, Account.account_code == "42002")
        .first()
    )

    if not advance_seva_account:
        raise HTTPException(
            status_code=400,
            detail="Advance Seva Booking account (3003) not found. Please create it in Chart of Accounts.",
        )
    if not seva_income_account:
        raise HTTPException(
            status_code=400,
            detail="Seva Income account (3002) not found. Please create it in Chart of Accounts.",
        )

    narration = f"Transfer of advance seva booking {booking.receipt_number} to Seva Income on seva date"
    entry_date = datetime.combine(booking.booking_date, datetime.min.time())

    year = booking.booking_date.year
    prefix = f"JE/{year}/"
    last_entry = (
        db.query(JournalEntry)
        .filter(JournalEntry.temple_id == temple_id, JournalEntry.entry_number.like(f"{prefix}%"))
        .order_by(JournalEntry.id.desc())
        .first()
    )

    new_num = 1
    if last_entry and last_entry.entry_number:
        try:
            last_num = int(last_entry.entry_number.split("/")[-1])
            new_num = last_num + 1
        except ValueError:
            pass

    entry_number = f"{prefix}{new_num:04d}"

    journal_entry = JournalEntry(
        temple_id=temple_id,
        entry_date=entry_date,
        entry_number=entry_number,
        narration=narration,
        reference_type=TransactionType.ADVANCE_SEVA_TRANSFER,
        reference_id=booking.id,
        total_amount=booking.amount_paid,
        status=JournalEntryStatus.POSTED,
        created_by=current_user.id,
        posted_by=current_user.id,
        posted_at=datetime.utcnow(),
    )
    db.add(journal_entry)
    db.flush()

    debit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=advance_seva_account.id,
        debit_amount=booking.amount_paid,
        credit_amount=0,
        description=f"Transfer from Advance Seva Booking for booking {booking.receipt_number}",
    )

    credit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=seva_income_account.id,
        debit_amount=0,
        credit_amount=booking.amount_paid,
        description=f"Transfer to Seva Income for booking {booking.receipt_number}",
    )

    db.add(debit_line)
    db.add(credit_line)
    db.commit()

    return {
        "message": f"Advance booking {booking.receipt_number} transferred to Seva Income successfully."
    }


def transfer_advance_bookings_batch_internal(
    db: Session,
    temple_id: int,
    created_by_user_id: int,
):
    today = date.today()
    yesterday = today - timedelta(days=1)

    bookings_yesterday = (
        db.query(SevaBooking)
        .filter(
            SevaBooking.booking_date == yesterday,
            SevaBooking.status != SevaBookingStatus.CANCELLED,
        )
        .all()
    )

    transferred_count = 0
    errors = []
    skipped_count = 0

    for booking in bookings_yesterday:
        existing_transfer = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.reference_type == TransactionType.ADVANCE_SEVA_TRANSFER,
                JournalEntry.reference_id == booking.id,
            )
            .first()
        )

        if existing_transfer:
            skipped_count += 1
            continue

        seva_entry = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.reference_type == TransactionType.SEVA,
                JournalEntry.reference_id == booking.id,
            )
            .first()
        )

        if not seva_entry:
            skipped_count += 1
            continue

        credit_line = (
            db.query(JournalLine)
            .join(Account)
            .filter(
                JournalLine.journal_entry_id == seva_entry.id,
                JournalLine.credit_amount > 0,
                Account.account_code == "21003",
            )
            .first()
        )

        if not credit_line:
            skipped_count += 1
            continue

        booking_temple_id = temple_id
        if booking.devotee and hasattr(booking.devotee, "temple_id") and booking.devotee.temple_id:
            booking_temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id") and booking.user.temple_id:
            booking_temple_id = booking.user.temple_id

        advance_seva_account = (
            db.query(Account)
            .filter(Account.temple_id == booking_temple_id, Account.account_code == "21003")
            .first()
        )

        seva_income_account = (
            db.query(Account)
            .filter(Account.temple_id == booking_temple_id, Account.account_code == "42002")
            .first()
        )

        if not advance_seva_account or not seva_income_account:
            errors.append(f"Booking {booking.receipt_number}: Accounts not found for temple {booking_temple_id}")
            continue

        try:
            narration = f"Transfer of advance seva booking {booking.receipt_number} to Seva Income on seva date"
            entry_date = datetime.combine(booking.booking_date, datetime.min.time())

            year = booking.booking_date.year
            prefix = f"JE/{year}/"
            from sqlalchemy.orm import load_only

            last_entry = (
                db.query(JournalEntry)
                .options(load_only(JournalEntry.id, JournalEntry.entry_number, JournalEntry.temple_id))
                .filter(
                    JournalEntry.temple_id == booking_temple_id,
                    JournalEntry.entry_number.like(f"{prefix}%"),
                )
                .order_by(JournalEntry.id.desc())
                .first()
            )

            new_num = 1
            if last_entry and last_entry.entry_number:
                try:
                    last_num = int(last_entry.entry_number.split("/")[-1])
                    new_num = last_num + 1
                except ValueError:
                    pass

            entry_number = f"{prefix}{new_num:04d}"

            journal_entry = JournalEntry(
                temple_id=booking_temple_id,
                entry_date=entry_date,
                entry_number=entry_number,
                narration=narration,
                reference_type=TransactionType.ADVANCE_SEVA_TRANSFER,
                reference_id=booking.id,
                total_amount=booking.amount_paid,
                status=JournalEntryStatus.POSTED,
                created_by=created_by_user_id,
                posted_by=created_by_user_id,
                posted_at=datetime.utcnow(),
            )
            db.add(journal_entry)
            db.flush()

            debit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=advance_seva_account.id,
                debit_amount=booking.amount_paid,
                credit_amount=0,
                description=f"Transfer from Advance Seva Booking for booking {booking.receipt_number}",
            )

            credit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=seva_income_account.id,
                debit_amount=0,
                credit_amount=booking.amount_paid,
                description=f"Transfer to Seva Income for booking {booking.receipt_number}",
            )

            db.add(debit_line)
            db.add(credit_line)
            transferred_count += 1
        except Exception as e:
            errors.append(f"Booking {booking.receipt_number}: {str(e)}")
            db.rollback()
            continue

    return {
        "message": (
            f"Transferred {transferred_count} advance booking(s) to Seva Income. "
            f"Skipped {skipped_count} booking(s) (not advance bookings or already transferred)."
        ),
        "transferred_count": transferred_count,
        "skipped_count": skipped_count,
        "errors": errors if errors else None,
    }


def transfer_advance_bookings_batch(
    db: Session,
    current_user,
):
    if current_user.role not in ["admin", "accountant", "temple_manager"] and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only authorized users can perform this action")

    temple_id = current_user.temple_id
    if not temple_id:
        raise HTTPException(status_code=400, detail="User is not associated with a temple.")

    today = date.today()
    yesterday = today - timedelta(days=1)

    bookings_yesterday = (
        db.query(SevaBooking)
        .filter(
            SevaBooking.booking_date == yesterday,
            SevaBooking.status != SevaBookingStatus.CANCELLED,
        )
        .all()
    )

    transferred_count = 0
    errors = []
    skipped_count = 0

    for booking in bookings_yesterday:
        existing_transfer = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.reference_type == TransactionType.ADVANCE_SEVA_TRANSFER,
                JournalEntry.reference_id == booking.id,
            )
            .first()
        )

        if existing_transfer:
            skipped_count += 1
            continue

        seva_entry = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.reference_type == TransactionType.SEVA,
                JournalEntry.reference_id == booking.id,
            )
            .first()
        )

        if not seva_entry:
            skipped_count += 1
            continue

        credit_line = (
            db.query(JournalLine)
            .join(Account)
            .filter(
                JournalLine.journal_entry_id == seva_entry.id,
                JournalLine.credit_amount > 0,
                Account.account_code == "21003",
            )
            .first()
        )

        if not credit_line:
            skipped_count += 1
            continue

        booking_temple_id = temple_id
        if booking.devotee and hasattr(booking.devotee, "temple_id") and booking.devotee.temple_id:
            booking_temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id") and booking.user.temple_id:
            booking_temple_id = booking.user.temple_id

        advance_seva_account = (
            db.query(Account)
            .filter(Account.temple_id == booking_temple_id, Account.account_code == "21003")
            .first()
        )

        seva_income_account = (
            db.query(Account)
            .filter(Account.temple_id == booking_temple_id, Account.account_code == "42002")
            .first()
        )

        if not advance_seva_account or not seva_income_account:
            errors.append(f"Booking {booking.receipt_number}: Accounts not found for temple {booking_temple_id}")
            continue

        try:
            narration = f"Transfer of advance seva booking {booking.receipt_number} to Seva Income on seva date"
            entry_date = datetime.combine(booking.booking_date, datetime.min.time())

            year = booking.booking_date.year
            prefix = f"JE/{year}/"
            from sqlalchemy.orm import load_only

            last_entry = (
                db.query(JournalEntry)
                .options(load_only(JournalEntry.id, JournalEntry.entry_number, JournalEntry.temple_id))
                .filter(
                    JournalEntry.temple_id == booking_temple_id,
                    JournalEntry.entry_number.like(f"{prefix}%"),
                )
                .order_by(JournalEntry.id.desc())
                .first()
            )

            new_num = 1
            if last_entry and last_entry.entry_number:
                try:
                    last_num = int(last_entry.entry_number.split("/")[-1])
                    new_num = last_num + 1
                except ValueError:
                    pass

            entry_number = f"{prefix}{new_num:04d}"

            journal_entry = JournalEntry(
                temple_id=booking_temple_id,
                entry_date=entry_date,
                entry_number=entry_number,
                narration=narration,
                reference_type=TransactionType.ADVANCE_SEVA_TRANSFER,
                reference_id=booking.id,
                total_amount=booking.amount_paid,
                status=JournalEntryStatus.POSTED,
                created_by=current_user.id,
                posted_by=current_user.id,
                posted_at=datetime.utcnow(),
            )
            db.add(journal_entry)
            db.flush()

            debit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=advance_seva_account.id,
                debit_amount=booking.amount_paid,
                credit_amount=0,
                description=f"Transfer from Advance Seva Booking for booking {booking.receipt_number}",
            )

            credit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=seva_income_account.id,
                debit_amount=0,
                credit_amount=booking.amount_paid,
                description=f"Transfer to Seva Income for booking {booking.receipt_number}",
            )

            db.add(debit_line)
            db.add(credit_line)
            transferred_count += 1
        except Exception as e:
            errors.append(f"Booking {booking.receipt_number}: {str(e)}")
            db.rollback()
            continue

    db.commit()

    return {
        "message": f"Transferred {transferred_count} advance booking(s) to Seva Income.",
        "transferred_count": transferred_count,
        "errors": errors if errors else None,
    }


def create_accounting_for_booking(
    db: Session,
    booking_id: int,
    current_user,
    post_seva_to_accounting_fn: Callable,
):
    if current_user.role not in ["admin", "accountant", "temple_manager"] and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only authorized users can perform this action")

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Seva booking not found")

    existing_entry = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.reference_type == TransactionType.SEVA,
            JournalEntry.reference_id == booking.id,
        )
        .first()
    )

    if existing_entry:
        raise HTTPException(
            status_code=400,
            detail=f"Accounting entry already exists for this booking (Entry: {existing_entry.entry_number})",
        )

    temple_id = current_user.temple_id
    if not temple_id:
        if booking.devotee and hasattr(booking.devotee, "temple_id"):
            temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id"):
            temple_id = booking.user.temple_id
        else:
            raise HTTPException(status_code=400, detail="Could not determine temple_id for this booking")

    try:
        journal_entry = post_seva_to_accounting_fn(db, booking, temple_id)
        db.commit()

        return {
            "status": "success",
            "message": f"Accounting entry created for booking {booking.receipt_number}",
            "entry_number": journal_entry.entry_number,
            "entry_date": journal_entry.entry_date.isoformat(),
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create accounting entry: {str(e)}")
