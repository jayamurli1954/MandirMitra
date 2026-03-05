"""
Chart of Accounts bootstrap helpers.

Provides a single place to ensure default COA accounts exist for a temple.
"""

from typing import Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data.default_coa import DefaultCOA
from app.models.accounting import Account


def ensure_default_coa_for_temple(
    db: Session, temple_id: int, raise_on_error: bool = False
) -> Dict[str, object]:
    """
    Ensure default COA exists for the given temple.
    Safe to call repeatedly: only missing account codes are inserted.
    """
    default_accounts = DefaultCOA.get_default_accounts()
    existing_codes = {
        row[0]
        for row in db.query(Account.account_code).filter(Account.temple_id == temple_id).all()
    }

    created_count = 0
    skipped_count = 0

    for account_data in default_accounts:
        code = account_data["account_code"]
        if code in existing_codes:
            skipped_count += 1
            continue

        db.add(Account(temple_id=temple_id, **account_data))
        existing_codes.add(code)
        created_count += 1

    error = None
    if created_count > 0:
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            error = str(exc)
            if raise_on_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize default accounts: {exc}",
                )
            created_count = 0

    return {
        "created": created_count,
        "skipped": skipped_count,
        "total_defaults": len(default_accounts),
        "error": error,
    }
