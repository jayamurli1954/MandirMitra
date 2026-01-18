"""
Opening Balance API Endpoints
Manage opening balances for balance sheet accounts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.accounting import Account, AccountType, AccountSubType
from app.schemas.accounting import AccountResponse
from sqlalchemy import or_

router = APIRouter(prefix="/api/v1/opening-balances", tags=["opening-balances"])


@router.get("/accounts", response_model=List[AccountResponse])
def get_balance_sheet_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all balance sheet accounts (Assets, Liabilities, Equity)
    These are the accounts that can have opening balances
    """
    if not current_user.temple_id:
        raise HTTPException(status_code=404, detail="Temple not found")
    
    accounts = db.query(Account).filter(
        Account.temple_id == current_user.temple_id,
        or_(
            Account.account_type == AccountType.ASSET,
            Account.account_type == AccountType.LIABILITY,
            Account.account_type == AccountType.EQUITY
        ),
        Account.is_active == True
    ).order_by(Account.account_code).all()
    
    return accounts


@router.put("/accounts/{account_id}")
def update_account_opening_balance(
    account_id: int,
    opening_balance_debit: Optional[float] = None,
    opening_balance_credit: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update opening balance for a balance sheet account
    
    For Assets: Use opening_balance_debit (positive = asset value)
    For Liabilities/Equity: Use opening_balance_credit (positive = liability/equity value)
    
    Alternatively, you can pass a single balance value:
    - Positive for Assets = debit balance
    - Positive for Liabilities/Equity = credit balance
    - Negative reverses the balance
    """
    if not current_user.temple_id:
        raise HTTPException(status_code=404, detail="Temple not found")
    
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.temple_id == current_user.temple_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Only allow balance sheet accounts
    if account.account_type not in [AccountType.ASSET, AccountType.LIABILITY, AccountType.EQUITY]:
        raise HTTPException(
            status_code=400,
            detail="Opening balances can only be set for Assets, Liabilities, or Equity accounts"
        )
    
    # Update opening balance
    if opening_balance_debit is not None:
        account.opening_balance_debit = max(0.0, opening_balance_debit)
    if opening_balance_credit is not None:
        account.opening_balance_credit = max(0.0, opening_balance_credit)
    
    # If both are provided, use them as-is
    # If only one is provided and the other is None, we might want to clear the other
    # But for now, we'll just update what's provided
    
    db.commit()
    db.refresh(account)
    
    return {
        "message": "Opening balance updated successfully",
        "account": {
            "id": account.id,
            "code": account.account_code,
            "name": account.account_name,
            "opening_balance_debit": account.opening_balance_debit,
            "opening_balance_credit": account.opening_balance_credit,
            "net_opening_balance": account.opening_balance_debit - account.opening_balance_credit
        }
    }


@router.put("/bulk-update")
def bulk_update_opening_balances(
    balances: List[dict],  # [{"account_id": 1, "opening_balance_debit": 50000, "opening_balance_credit": 0}]
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk update opening balances for multiple accounts
    
    Request body:
    [
        {
            "account_id": 1,
            "opening_balance_debit": 50000.0,  # For Assets
            "opening_balance_credit": 0.0
        },
        {
            "account_id": 5,
            "opening_balance_debit": 0.0,
            "opening_balance_credit": 100000.0  # For Liabilities/Equity
        }
    ]
    """
    if not current_user.temple_id:
        raise HTTPException(status_code=404, detail="Temple not found")
    
    updated = []
    errors = []
    
    for balance_item in balances:
        account_id = balance_item.get("account_id")
        if not account_id:
            errors.append({"account_id": None, "error": "account_id is required"})
            continue
        
        account = db.query(Account).filter(
            Account.id == account_id,
            Account.temple_id == current_user.temple_id
        ).first()
        
        if not account:
            errors.append({"account_id": account_id, "error": "Account not found"})
            continue
        
        # Only allow balance sheet accounts
        if account.account_type not in [AccountType.ASSET, AccountType.LIABILITY, AccountType.EQUITY]:
            errors.append({
                "account_id": account_id,
                "error": "Only balance sheet accounts can have opening balances"
            })
            continue
        
        # Update balances
        if "opening_balance_debit" in balance_item:
            account.opening_balance_debit = max(0.0, float(balance_item["opening_balance_debit"]))
        if "opening_balance_credit" in balance_item:
            account.opening_balance_credit = max(0.0, float(balance_item["opening_balance_credit"]))
        
        updated.append({
            "account_id": account.id,
            "account_code": account.account_code,
            "account_name": account.account_name
        })
    
    db.commit()
    
    return {
        "message": f"Updated {len(updated)} accounts",
        "updated": updated,
        "errors": errors
    }

















