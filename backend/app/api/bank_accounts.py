"""
Bank Account Management API Endpoints
Create and manage bank accounts for the temple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.upi_banking import BankAccount
from app.models.accounting import Account, AccountType, AccountSubType

router = APIRouter(prefix="/api/v1/bank-accounts", tags=["bank-accounts"])


# Pydantic Schemas
class BankAccountBase(BaseModel):
    account_name: str
    bank_name: str
    branch_name: Optional[str] = None
    account_number: str
    ifsc_code: str
    account_type: Optional[str] = "Savings"  # Savings, Current
    is_primary: Optional[bool] = False
    is_active: Optional[bool] = True


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountResponse(BankAccountBase):
    id: int
    temple_id: int
    chart_account_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Convert datetime objects to strings"""
        from datetime import datetime

        data = {
            "id": obj.id,
            "temple_id": obj.temple_id,
            "account_name": obj.account_name,
            "bank_name": obj.bank_name,
            "branch_name": obj.branch_name,
            "account_number": obj.account_number,
            "ifsc_code": obj.ifsc_code,
            "account_type": obj.account_type,
            "is_primary": obj.is_primary,
            "is_active": obj.is_active,
            "chart_account_id": obj.chart_account_id,
            "created_at": obj.created_at.isoformat()
            if obj.created_at and isinstance(obj.created_at, datetime)
            else (str(obj.created_at) if obj.created_at else None),
            "updated_at": obj.updated_at.isoformat()
            if obj.updated_at and isinstance(obj.updated_at, datetime)
            else (str(obj.updated_at) if obj.updated_at else None),
        }
        return cls(**data)


@router.get("/", response_model=List[BankAccountResponse])
def get_bank_accounts(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all bank accounts for the temple"""
    temple_id = current_user.temple_id
    if not temple_id:
        raise HTTPException(status_code=404, detail="Temple not found")

    bank_accounts = (
        db.query(BankAccount)
        .filter(BankAccount.temple_id == temple_id)
        .order_by(BankAccount.is_primary.desc(), BankAccount.created_at.desc())
        .all()
    )

    return [BankAccountResponse.from_orm(acc) for acc in bank_accounts]


@router.post("/", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
def create_bank_account(
    bank_account: BankAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new bank account"""
    temple_id = current_user.temple_id
    if not temple_id:
        raise HTTPException(status_code=404, detail="Temple not found")

    # Check if account number already exists
    existing = (
        db.query(BankAccount)
        .filter(
            BankAccount.account_number == bank_account.account_number,
            BankAccount.temple_id == temple_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Bank account with number {bank_account.account_number} already exists",
        )

    # If this is set as primary, unset other primary accounts
    if bank_account.is_primary:
        db.query(BankAccount).filter(
            BankAccount.temple_id == temple_id, BankAccount.is_primary == True
        ).update({"is_primary": False})

    # Find or create chart of accounts entry
    # Bank accounts are typically under 1110 (Bank Accounts)
    chart_account = (
        db.query(Account)
        .filter(
            Account.temple_id == temple_id,
            Account.account_code == "12001",  # Default bank account code
            Account.account_type == AccountType.ASSET,
            Account.account_subtype == AccountSubType.CASH_BANK,
        )
        .first()
    )

    # No fallback to 01110 - only use 12001
    # If not found, will create new account with code 12001 below

    if not chart_account:
        # Create a default bank account in chart of accounts
        try:
            chart_account = Account(
                temple_id=temple_id,
                account_code="12001",
                account_name="Bank Accounts",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubType.CASH_BANK,
                is_active=True,
            )
            db.add(chart_account)
            db.flush()
        except Exception as e:
            # If account already exists (unique constraint), fetch it
            try:
                db.rollback()
            except:
                pass  # Ignore rollback errors if transaction is already closed
            # Try to find existing account with code 12001
            chart_account = (
                db.query(Account)
                .filter(Account.temple_id == temple_id, Account.account_code == "12001")
                .first()
            )
            if not chart_account:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create or find bank account in chart of accounts: {str(e)}",
                )

    # Create bank account
    try:
        db_bank_account = BankAccount(
            temple_id=temple_id,
            account_name=bank_account.account_name,
            bank_name=bank_account.bank_name,
            branch_name=bank_account.branch_name,
            account_number=bank_account.account_number,
            ifsc_code=bank_account.ifsc_code,
            account_type=bank_account.account_type,
            is_primary=bank_account.is_primary,
            is_active=bank_account.is_active,
            chart_account_id=chart_account.id,
        )

        db.add(db_bank_account)
        db.commit()
        db.refresh(db_bank_account)

        return BankAccountResponse.from_orm(db_bank_account)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create bank account: {str(e)}")


@router.put("/{bank_account_id}", response_model=BankAccountResponse)
def update_bank_account(
    bank_account_id: int,
    bank_account: BankAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a bank account"""
    temple_id = current_user.temple_id
    if not temple_id:
        raise HTTPException(status_code=404, detail="Temple not found")

    db_bank_account = (
        db.query(BankAccount)
        .filter(BankAccount.id == bank_account_id, BankAccount.temple_id == temple_id)
        .first()
    )

    if not db_bank_account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    # If setting as primary, unset other primary accounts
    if bank_account.is_primary and not db_bank_account.is_primary:
        db.query(BankAccount).filter(
            BankAccount.temple_id == temple_id,
            BankAccount.is_primary == True,
            BankAccount.id != bank_account_id,
        ).update({"is_primary": False})

    # Update fields
    db_bank_account.account_name = bank_account.account_name
    db_bank_account.bank_name = bank_account.bank_name
    db_bank_account.branch_name = bank_account.branch_name
    db_bank_account.account_number = bank_account.account_number
    db_bank_account.ifsc_code = bank_account.ifsc_code
    db_bank_account.account_type = bank_account.account_type
    db_bank_account.is_primary = bank_account.is_primary
    db_bank_account.is_active = bank_account.is_active

    db.commit()
    db.refresh(db_bank_account)

    return BankAccountResponse.from_orm(db_bank_account)


@router.delete("/{bank_account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bank_account(
    bank_account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a bank account (soft delete by setting is_active=False)"""
    temple_id = current_user.temple_id
    if not temple_id:
        raise HTTPException(status_code=404, detail="Temple not found")

    db_bank_account = (
        db.query(BankAccount)
        .filter(BankAccount.id == bank_account_id, BankAccount.temple_id == temple_id)
        .first()
    )

    if not db_bank_account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    # Soft delete
    db_bank_account.is_active = False
    db.commit()

    return None
