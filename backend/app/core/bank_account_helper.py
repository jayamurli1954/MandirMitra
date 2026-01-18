"""
Helper functions for bank account operations
Gets bank accounts from BankAccount model and returns the associated chart of accounts entry
"""

from sqlalchemy.orm import Session
from app.models.upi_banking import BankAccount
from app.models.accounting import Account
from typing import Optional, Tuple


def get_bank_account_for_payment(
    db: Session, 
    temple_id: int, 
    payment_mode: str,
    bank_account_id: Optional[int] = None
) -> Tuple[Optional[Account], str]:
    """
    Get the appropriate bank account for a payment mode
    
    Priority:
    1. If bank_account_id is provided, use that specific bank account
    2. If payment is bank-related, use primary bank account
    3. If no primary, use any active bank account
    4. Return None if no bank account found (caller should handle fallback)
    
    Args:
        db: Database session
        temple_id: Temple ID
        payment_mode: Payment mode (CASH, CARD, UPI, BANK, CHEQUE, ONLINE, etc.)
        bank_account_id: Optional specific bank account ID to use
    
    Returns:
        Tuple of (Account object or None, account_code for fallback)
    """
    # Bank-related payment modes
    bank_payment_modes = ['BANK', 'CARD', 'UPI', 'ONLINE', 'NETBANKING', 'CHEQUE', 'DD']
    
    # Check if this is a bank-related payment
    is_bank_payment = payment_mode.upper() in bank_payment_modes
    
    if not is_bank_payment:
        return None, None
    
    # If specific bank_account_id is provided, use that
    if bank_account_id:
        bank_account = db.query(BankAccount).filter(
            BankAccount.id == bank_account_id,
            BankAccount.temple_id == temple_id,
            BankAccount.is_active == True
        ).first()
        
        if bank_account and bank_account.chart_account_id:
            account = db.query(Account).filter(
                Account.id == bank_account.chart_account_id,
                Account.temple_id == temple_id
            ).first()
            if account:
                return account, account.account_code
    
    # Try primary bank account
    primary_bank = db.query(BankAccount).filter(
        BankAccount.temple_id == temple_id,
        BankAccount.is_active == True,
        BankAccount.is_primary == True
    ).first()
    
    if primary_bank and primary_bank.chart_account_id:
        account = db.query(Account).filter(
            Account.id == primary_bank.chart_account_id,
            Account.temple_id == temple_id
        ).first()
        if account:
            return account, account.account_code
    
    # Fallback: Any active bank account
    any_bank = db.query(BankAccount).filter(
        BankAccount.temple_id == temple_id,
        BankAccount.is_active == True
    ).order_by(BankAccount.is_primary.desc(), BankAccount.created_at.desc()).first()
    
    if any_bank and any_bank.chart_account_id:
        account = db.query(Account).filter(
            Account.id == any_bank.chart_account_id,
            Account.temple_id == temple_id
        ).first()
        if account:
            return account, account.account_code
    
    # No bank account found
    return None, None


def get_cash_account_for_payment(
    db: Session,
    temple_id: int,
    payment_mode: str,
    hundi: bool = False
) -> Optional[Account]:
    """
    Get cash account for payment
    
    Args:
        db: Database session
        temple_id: Temple ID
        payment_mode: Payment mode
        hundi: Whether this is for hundi (uses 11002 instead of 11001)
    
    Returns:
        Account object or None
    """
    if hundi or (payment_mode and 'HUNDI' in payment_mode.upper()):
        account_code = '11002'  # Cash in Hand - Hundi (no leading zero)
    else:
        account_code = '11001'  # Cash in Hand - Counter (no leading zero)
    
    account = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == account_code
    ).first()
    
    return account


