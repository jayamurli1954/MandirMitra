from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.accounting import Account, JournalEntry


def generate_entry_number(db: Session, temple_id: Optional[int]) -> str:
    """
    Generate unique journal entry number.
    Format: JE/YYYY/0001.
    For standalone mode (temple_id=None), use 0 as default.
    """
    year = datetime.now().year
    prefix = f"JE/{year}/"

    effective_temple_id = temple_id if temple_id is not None else 0

    last_entry = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.temple_id == effective_temple_id,
            JournalEntry.entry_number.like(f"{prefix}%"),
        )
        .order_by(JournalEntry.id.desc())
        .first()
    )

    if last_entry:
        last_num = int(last_entry.entry_number.split("/")[-1])
        new_num = last_num + 1
    else:
        new_num = 1

    return f"{prefix}{new_num:04d}"


def validate_journal_entry(journal_lines: List, db: Session, temple_id: Optional[int]):
    """
    Validate journal entry:
    - Must have at least 2 lines
    - Total debits must equal total credits
    - All accounts must exist and belong to temple (or any temple in standalone mode)
    - Each line must have either debit or credit (not both)
    """
    if len(journal_lines) < 2:
        raise HTTPException(
            status_code=400, detail="Journal entry must have at least 2 lines (debit and credit)"
        )

    total_debit = sum(line.debit_amount for line in journal_lines)
    total_credit = sum(line.credit_amount for line in journal_lines)

    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(
            status_code=400, detail=f"Debits ({total_debit}) must equal credits ({total_credit})"
        )

    for line in journal_lines:
        if not line.account_id:
            raise HTTPException(
                status_code=400, detail="Account ID is required for all journal lines"
            )

        if not isinstance(line.account_id, int):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid account ID: {line.account_id}. Must be an integer.",
            )

        account_query = db.query(Account).filter(Account.id == line.account_id)
        if temple_id is not None:
            account_query = account_query.filter(Account.temple_id == temple_id)
        account = account_query.first()

        if not account:
            if temple_id is not None:
                account_other_temple = db.query(Account).filter(Account.id == line.account_id).first()
                if account_other_temple:
                    raise HTTPException(
                        status_code=403,
                        detail=(
                            f"Account ID {line.account_id} "
                            f"({account_other_temple.account_code} - "
                            f"{account_other_temple.account_name}) does not belong to your temple"
                        ),
                    )
            raise HTTPException(
                status_code=404,
                detail=f"Account ID {line.account_id} not found. Please select a valid account.",
            )

        if not account.is_active:
            raise HTTPException(
                status_code=400, detail=f"Account '{account.account_name}' is inactive"
            )

        if line.debit_amount > 0 and line.credit_amount > 0:
            raise HTTPException(
                status_code=400, detail="A journal line cannot have both debit and credit amounts"
            )

        if line.debit_amount == 0 and line.credit_amount == 0:
            raise HTTPException(
                status_code=400, detail="A journal line must have either debit or credit amount"
            )

    return total_debit
