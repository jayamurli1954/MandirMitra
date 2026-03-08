from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.coa_bootstrap import ensure_default_coa_for_temple
from app.models.accounting import (
    Account,
    AccountSubType,
    JournalEntry,
    JournalEntryStatus,
    JournalLine,
    TransactionType,
)
from app.models.seva import SevaBooking
from app.models.temple import Temple
from app.models.upi_banking import BankAccount


def get_payment_accounts_for_temple(db: Session, temple_id: Optional[int]) -> dict:
    """Fetch active cash and bank accounts for seva payment selection."""
    # Standalone fallback: resolve first temple when user.temple_id is null.
    if not temple_id:
        first_temple = db.query(Temple.id).order_by(Temple.id.asc()).first()
        temple_id = first_temple.id if first_temple else None
    if not temple_id:
        return {"cash_accounts": [], "bank_accounts": []}

    cash_accounts = (
        db.query(Account)
        .filter(
            Account.temple_id == temple_id,
            Account.is_active == True,
            Account.account_subtype == AccountSubType.CASH_BANK,
            Account.account_code.like("11%"),
        )
        .order_by(Account.account_code.asc())
        .all()
    )
    # Fallback for legacy COA rows without account_subtype.
    if not cash_accounts:
        cash_accounts = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.is_active == True,
                Account.account_code.like("11%"),
            )
            .order_by(Account.account_code.asc())
            .all()
        )

    bank_accounts = (
        db.query(BankAccount)
        .filter(BankAccount.temple_id == temple_id, BankAccount.is_active == True)
        .order_by(BankAccount.is_primary.desc(), BankAccount.account_name.asc())
        .all()
    )

    bank_results = []
    for bank_acc in bank_accounts:
        chart_account = (
            db.query(Account)
            .filter(
                Account.id == bank_acc.chart_account_id,
                Account.temple_id == temple_id,
                Account.is_active == True,
            )
            .first()
        )
        if not chart_account:
            continue
        bank_results.append(
            {
                "id": bank_acc.id,
                "bank_account_id": bank_acc.id,
                "account_id": chart_account.id,
                "account_code": chart_account.account_code,
                "account_name": chart_account.account_name,
                "name": bank_acc.account_name,
                "bank_name": bank_acc.bank_name,
                "account_number": bank_acc.account_number,
                "ifsc_code": bank_acc.ifsc_code,
                "is_primary": bank_acc.is_primary,
            }
        )

    # Fallback: if BankAccount master is not configured, use bank ledgers directly from COA.
    if not bank_results:
        fallback_bank_ledgers = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.is_active == True,
                Account.account_code.like("12%"),
            )
            .order_by(Account.account_code.asc())
            .all()
        )
        for ledger in fallback_bank_ledgers:
            bank_results.append(
                {
                    "id": f"coa-{ledger.id}",
                    "bank_account_id": None,
                    "account_id": ledger.id,
                    "account_code": ledger.account_code,
                    "account_name": ledger.account_name,
                    "name": ledger.account_name,
                    "bank_name": None,
                    "account_number": None,
                    "ifsc_code": None,
                    "is_primary": False,
                }
            )

    cash_results = [
        {
            "account_id": acc.id,
            "account_code": acc.account_code,
            "account_name": acc.account_name,
        }
        for acc in cash_accounts
    ]

    return {"cash_accounts": cash_results, "bank_accounts": bank_results}


def post_seva_to_accounting(
    db: Session,
    booking: SevaBooking,
    temple_id: int,
    payment_account_id: Optional[int] = None,
):
    """
    Create journal entry for seva booking in accounting system.

    Accounting Rules:
    - If booking_date == today: Dr Cash/Bank, Cr Seva Income (42002)
    - If booking_date > today: Dr Cash/Bank, Cr Advance Seva Booking (21003)
    """
    try:
        # Ensure base COA exists before posting entries.
        seed_result = ensure_default_coa_for_temple(db, temple_id, raise_on_error=False)
        if seed_result.get("created", 0) > 0:
            print(
                f"  INFO: Initialized {seed_result['created']} default COA account(s) for temple {temple_id}"
            )
        if seed_result.get("error"):
            print(
                f"  WARNING: Could not auto-initialize COA for temple {temple_id}: {seed_result['error']}"
            )

        from app.core.bank_account_helper import (
            get_bank_account_for_payment,
            get_cash_account_for_payment,
        )

        payment_method = booking.payment_method or "CASH"
        payment_method_upper = payment_method.strip().upper()
        bank_payment_modes = {"UPI", "ONLINE", "CARD", "NETBANKING", "BANK", "CHEQUE", "DD"}
        debit_account = None

        # First priority: explicitly selected chart account from UI.
        if payment_account_id:
            selected_account = (
                db.query(Account)
                .filter(
                    Account.id == payment_account_id,
                    Account.temple_id == temple_id,
                    Account.is_active == True,
                )
                .first()
            )
            if not selected_account:
                raise ValueError(f"Selected payment account {payment_account_id} was not found.")

            is_cash_mode = payment_method_upper in {"CASH", "COUNTER"} or "HUNDI" in payment_method_upper
            is_bank_mode = payment_method_upper in bank_payment_modes
            if is_cash_mode and not selected_account.account_code.startswith("11"):
                raise ValueError(
                    "Selected payment account is not a cash account (expected code starting with 11)."
                )
            if is_bank_mode and not selected_account.account_code.startswith("12"):
                raise ValueError(
                    "Selected payment account is not a bank account (expected code starting with 12)."
                )

            debit_account = selected_account
            print(
                f"  Using selected payment account: {debit_account.account_code} - {debit_account.account_name}"
            )

        if not debit_account and payment_method_upper in ["CASH", "COUNTER"]:
            debit_account = get_cash_account_for_payment(db, temple_id, payment_method_upper, hundi=False)
            if not debit_account:
                debit_account = (
                    db.query(Account)
                    .filter(
                        Account.temple_id == temple_id,
                        Account.account_code == "11001",
                    )
                    .first()
                )
        elif not debit_account and payment_method_upper in bank_payment_modes:
            debit_account, fallback_code = get_bank_account_for_payment(
                db,
                temple_id,
                payment_method_upper,
                bank_account_id=getattr(booking, "bank_account_id", None),
            )
            if not debit_account and fallback_code:
                debit_account = (
                    db.query(Account)
                    .filter(Account.temple_id == temple_id, Account.account_code == fallback_code)
                    .first()
                )
            if not debit_account:
                print(
                    f"  WARNING: No bank account found for payment method {payment_method}. Please create a bank account in Bank Account Management."
                )
        elif not debit_account:
            debit_account = get_cash_account_for_payment(db, temple_id, payment_method_upper, hundi=False)
            if not debit_account:
                debit_account = (
                    db.query(Account)
                    .filter(Account.temple_id == temple_id, Account.account_code == "11001")
                    .first()
                )

        today = date.today()
        is_advance_booking = booking.booking_date > today

        credit_account = None

        if is_advance_booking:
            credit_account_code = "21003"
            credit_account = (
                db.query(Account)
                .filter(Account.temple_id == temple_id, Account.account_code == credit_account_code)
                .first()
            )
            if credit_account:
                print(
                    f"  Using advance seva booking account: {credit_account.account_code} - {credit_account.account_name}"
                )
            else:
                print(
                    f"  ERROR: Advance Seva Booking account {credit_account_code} not found. Please create '21003 - Advance Seva Booking' in Chart of Accounts."
                )
        else:
            if booking.seva and hasattr(booking.seva, "account_id") and booking.seva.account_id:
                credit_account = db.query(Account).filter(Account.id == booking.seva.account_id).first()

            if not credit_account:
                credit_account_code = "42002"
                credit_account = (
                    db.query(Account)
                    .filter(
                        Account.temple_id == temple_id,
                        Account.account_code == credit_account_code,
                    )
                    .first()
                )
                if credit_account:
                    print(
                        f"  Using default seva income account: {credit_account.account_code} - {credit_account.account_name}"
                    )
                else:
                    print(
                        f"  ERROR: Default seva income account {credit_account_code} not found. Please ensure '42002 - Seva Income - General' exists in Chart of Accounts."
                    )

        if not debit_account:
            raise ValueError(
                f"Debit account not found for temple {temple_id}. Please create the account in Chart of Accounts."
            )

        if not credit_account:
            if is_advance_booking:
                raise ValueError(
                    f"Advance Seva Booking account (3003) not found for temple {temple_id}. Please create '3003 - Advance Seva Booking' in Chart of Accounts."
                )
            raise ValueError(
                f"Credit account not found for seva '{booking.seva.name_english if booking.seva else 'Unknown'}'. Please link an account to the seva or create default seva income account (account code 3002)."
            )

        devotee_name = booking.devotee.name if booking.devotee else "Unknown"
        seva_name = booking.seva.name_english if booking.seva else "Seva"
        receipt_date = (
            booking.created_at.date()
            if hasattr(booking, "created_at") and booking.created_at
            else today
        )
        if is_advance_booking:
            narration = (
                f"Advance seva booking - {seva_name} by {devotee_name} "
                f"(Receipt: {receipt_date.strftime('%d-%m-%Y')}, Seva date: {booking.booking_date.strftime('%d-%m-%Y')})"
            )
        else:
            narration = (
                f"Seva booking - {seva_name} by {devotee_name} "
                f"(Seva date: {booking.booking_date.strftime('%d-%m-%Y')})"
            )

        year = booking.booking_date.year
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

        receipt_date = (
            booking.created_at.date() if hasattr(booking.created_at, "date") else booking.created_at
        )
        if isinstance(receipt_date, date):
            entry_date = datetime.combine(receipt_date, datetime.min.time())
        else:
            entry_date = datetime.combine(today, datetime.min.time())

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
            posted_at=datetime.utcnow(),
        )
        db.add(journal_entry)
        db.flush()

        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=debit_account.id,
            debit_amount=booking.amount_paid,
            credit_amount=0,
            description=f"Seva booking received via {payment_method}",
        )
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=credit_account.id,
            debit_amount=0,
            credit_amount=booking.amount_paid,
            description=f"Seva income - {seva_name}",
        )

        db.add(debit_line)
        db.add(credit_line)

        return journal_entry

    except Exception as e:
        print(f"Error posting seva to accounting: {str(e)}")
        raise e

