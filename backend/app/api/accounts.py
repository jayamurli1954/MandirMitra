"""
Chart of Accounts API Endpoints
Manage accounts in the accounting system
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.accounting import Account, AccountType, JournalLine
from app.schemas.accounting import (
    AccountCreate, AccountUpdate, AccountResponse,
    AccountBalance, AccountHierarchy
)

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


# ===== HELPER FUNCTIONS =====

def build_account_hierarchy(accounts: List[Account], parent_id: Optional[int] = None) -> List[dict]:
    """
    Recursively build account hierarchy tree
    """
    result = []
    for account in accounts:
        if account.parent_account_id == parent_id:
            account_dict = {
                "id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_name_kannada": account.account_name_kannada,
                "description": account.description,
                "account_type": account.account_type,
                "account_subtype": account.account_subtype,
                "parent_account_id": account.parent_account_id,
                "temple_id": account.temple_id,
                "is_active": account.is_active,
                "is_system_account": account.is_system_account,
                "allow_manual_entry": account.allow_manual_entry,
                "opening_balance_debit": account.opening_balance_debit,
                "opening_balance_credit": account.opening_balance_credit,
                "created_at": account.created_at,
                "updated_at": account.updated_at,
                "sub_accounts": build_account_hierarchy(accounts, account.id)
            }
            result.append(account_dict)
    return result


def get_account_balance(db: Session, account_id: int, as_of_date: Optional[date] = None) -> dict:
    """
    Calculate account balance from journal lines
    """
    query = db.query(
        func.sum(JournalLine.debit_amount).label('total_debit'),
        func.sum(JournalLine.credit_amount).label('total_credit')
    ).filter(JournalLine.account_id == account_id)

    if as_of_date:
        # Filter by entry date if specified
        query = query.join(JournalLine.journal_entry).filter(
            func.date(JournalEntry.entry_date) <= as_of_date
        )

    result = query.first()

    total_debit = float(result.total_debit or 0)
    total_credit = float(result.total_credit or 0)
    balance = total_debit - total_credit

    return {
        "total_debit": total_debit,
        "total_credit": total_credit,
        "balance": abs(balance),
        "balance_type": "debit" if balance >= 0 else "credit"
    }


# ===== ACCOUNT CRUD =====

@router.get("/", response_model=List[AccountResponse])
def list_accounts(
    account_type: Optional[AccountType] = None,
    is_active: Optional[bool] = None,
    parent_account_id: Optional[int] = Query(None, description="Filter by parent account (use 0 for root accounts)"),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of accounts with optional filters
    """
    query = db.query(Account).filter(Account.temple_id == current_user.temple_id)

    if account_type:
        query = query.filter(Account.account_type == account_type)

    if is_active is not None:
        query = query.filter(Account.is_active == is_active)

    if parent_account_id is not None:
        if parent_account_id == 0:
            # Root accounts (no parent)
            query = query.filter(Account.parent_account_id == None)
        else:
            query = query.filter(Account.parent_account_id == parent_account_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Account.account_name.ilike(search_filter)) |
            (Account.account_code.ilike(search_filter))
        )

    accounts = query.order_by(Account.account_code).all()
    return accounts


@router.get("/hierarchy", response_model=List[AccountHierarchy])
def get_account_hierarchy(
    account_type: Optional[AccountType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get accounts in hierarchical tree structure
    """
    query = db.query(Account).filter(
        Account.temple_id == current_user.temple_id,
        Account.is_active == True
    )

    if account_type:
        query = query.filter(Account.account_type == account_type)

    accounts = query.order_by(Account.account_code).all()
    hierarchy = build_account_hierarchy(accounts)
    return hierarchy


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get account by ID
    """
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.temple_id == current_user.temple_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.post("/", response_model=AccountResponse)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new account
    Only admin users can create accounts
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create accounts"
        )

    # Verify temple_id matches current user
    if account_data.temple_id != current_user.temple_id:
        raise HTTPException(status_code=403, detail="Cannot create account for different temple")

    # Check if account code already exists
    existing = db.query(Account).filter(
        Account.account_code == account_data.account_code,
        Account.temple_id == current_user.temple_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Account code '{account_data.account_code}' already exists"
        )

    # Verify parent account exists (if specified)
    if account_data.parent_account_id:
        parent = db.query(Account).filter(
            Account.id == account_data.parent_account_id,
            Account.temple_id == current_user.temple_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent account not found")

    # Create account
    account = Account(**account_data.dict())
    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update account
    Only admin users can update accounts
    System accounts cannot be modified
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update accounts"
        )

    account = db.query(Account).filter(
        Account.id == account_id,
        Account.temple_id == current_user.temple_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.is_system_account:
        raise HTTPException(
            status_code=400,
            detail="System accounts cannot be modified"
        )

    # Update fields
    update_data = account_data.dict(exclude_unset=True)

    # Verify parent account if being changed
    if 'parent_account_id' in update_data and update_data['parent_account_id']:
        parent = db.query(Account).filter(
            Account.id == update_data['parent_account_id'],
            Account.temple_id == current_user.temple_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent account not found")

        # Cannot set self as parent
        if update_data['parent_account_id'] == account_id:
            raise HTTPException(status_code=400, detail="Account cannot be its own parent")

    for field, value in update_data.items():
        setattr(account, field, value)

    account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(account)

    return account


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete (deactivate) account
    Only admin users can delete accounts
    System accounts cannot be deleted
    Accounts with transactions cannot be deleted (only deactivated)
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete accounts"
        )

    account = db.query(Account).filter(
        Account.id == account_id,
        Account.temple_id == current_user.temple_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.is_system_account:
        raise HTTPException(
            status_code=400,
            detail="System accounts cannot be deleted"
        )

    # Check if account has transactions
    has_transactions = db.query(JournalLine).filter(
        JournalLine.account_id == account_id
    ).first() is not None

    if has_transactions:
        # Cannot delete, only deactivate
        account.is_active = False
        account.updated_at = datetime.utcnow()
        db.commit()
        return {"message": "Account deactivated (has transaction history)"}
    else:
        # Can safely delete
        db.delete(account)
        db.commit()
        return {"message": "Account deleted successfully"}


@router.get("/{account_id}/balance", response_model=AccountBalance)
def get_balance(
    account_id: int,
    as_of_date: Optional[date] = Query(None, description="Calculate balance as of specific date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current balance for an account
    """
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.temple_id == current_user.temple_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    balance_data = get_account_balance(db, account_id, as_of_date)

    return {
        "account_id": account.id,
        "account_code": account.account_code,
        "account_name": account.account_name,
        "account_type": account.account_type,
        **balance_data
    }
