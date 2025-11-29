"""
Token Seva API Endpoints
Handles token-based seva sales, inventory, and reconciliation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.token_seva import TokenInventory, TokenSale, TokenReconciliation, TokenStatus, PaymentMode
from app.models.seva import Seva
from app.models.devotee import Devotee
from app.models.user import User
from app.models.temple import Temple
from app.models.accounting import JournalEntry, JournalLine, Account
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/token-seva", tags=["token-seva"])


# Pydantic Schemas
class TokenInventoryCreate(BaseModel):
    seva_id: int
    token_color: str
    serial_number: str
    token_number: str
    batch_number: Optional[str] = None
    printed_date: Optional[date] = None
    expiry_date: Optional[date] = None


class TokenSaleCreate(BaseModel):
    seva_id: int
    token_serial_number: str
    amount: float
    payment_mode: PaymentMode
    upi_reference: Optional[str] = None
    counter_number: Optional[str] = None
    devotee_id: Optional[int] = None
    devotee_name: Optional[str] = None
    devotee_phone: Optional[str] = None
    notes: Optional[str] = None


class TokenReconciliationCreate(BaseModel):
    reconciliation_date: date
    discrepancy_notes: Optional[str] = None


class TokenSaleResponse(BaseModel):
    id: int
    sale_date: date
    seva_id: int
    seva_name: str
    token_serial_number: str
    amount: float
    payment_mode: str
    counter_number: Optional[str]
    devotee_name: Optional[str]
    
    class Config:
        from_attributes = True


@router.post("/inventory/add", status_code=status.HTTP_201_CREATED)
def add_token_inventory(
    tokens: List[TokenInventoryCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add pre-printed tokens to inventory"""
    temple_id = current_user.temple_id
    
    created_tokens = []
    for token_data in tokens:
        # Verify seva exists and is token seva
        seva = db.query(Seva).filter(
            Seva.id == token_data.seva_id,
            Seva.temple_id == temple_id,
            Seva.is_token_seva == True
        ).first()
        
        if not seva:
            raise HTTPException(
                status_code=404,
                detail=f"Seva {token_data.seva_id} not found or not configured as token seva"
            )
        
        # Check if serial number already exists
        existing = db.query(TokenInventory).filter(
            TokenInventory.serial_number == token_data.serial_number
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Token with serial number {token_data.serial_number} already exists"
            )
        
        # Create token
        token = TokenInventory(
            temple_id=temple_id,
            seva_id=token_data.seva_id,
            token_color=token_data.token_color or seva.token_color,
            serial_number=token_data.serial_number,
            token_number=token_data.token_number,
            batch_number=token_data.batch_number,
            printed_date=token_data.printed_date,
            expiry_date=token_data.expiry_date,
            status=TokenStatus.AVAILABLE
        )
        
        db.add(token)
        created_tokens.append(token)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Added {len(created_tokens)} tokens to inventory",
        "count": len(created_tokens)
    }


@router.post("/sale", status_code=status.HTTP_201_CREATED)
def record_token_sale(
    sale_data: TokenSaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a token sale"""
    temple_id = current_user.temple_id
    
    # Find available token
    token = db.query(TokenInventory).filter(
        TokenInventory.serial_number == sale_data.token_serial_number,
        TokenInventory.temple_id == temple_id,
        TokenInventory.status == TokenStatus.AVAILABLE
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=404,
            detail=f"Token {sale_data.token_serial_number} not found or not available"
        )
    
    # Verify seva matches
    if token.seva_id != sale_data.seva_id:
        raise HTTPException(
            status_code=400,
            detail="Token seva_id does not match sale seva_id"
        )
    
    seva = db.query(Seva).filter(Seva.id == sale_data.seva_id).first()
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")
    
    # Get or create devotee if provided
    devotee_id = sale_data.devotee_id
    if sale_data.devotee_phone and not devotee_id:
        devotee = db.query(Devotee).filter(Devotee.phone == sale_data.devotee_phone).first()
        if devotee:
            devotee_id = devotee.id
        elif sale_data.devotee_name:
            # Create new devotee
            devotee = Devotee(
                name=sale_data.devotee_name,
                full_name=sale_data.devotee_name,
                phone=sale_data.devotee_phone,
                temple_id=temple_id
            )
            db.add(devotee)
            db.flush()
            devotee_id = devotee.id
    
    # Create token sale record
    sale = TokenSale(
        temple_id=temple_id,
        seva_id=sale_data.seva_id,
        sale_date=date.today(),
        sale_time=datetime.utcnow(),
        token_id=token.id,
        token_serial_number=sale_data.token_serial_number,
        amount=sale_data.amount,
        payment_mode=sale_data.payment_mode,
        upi_reference=sale_data.upi_reference,
        counter_number=sale_data.counter_number or f"COUNTER-{current_user.id}",
        sold_by=current_user.id,
        devotee_id=devotee_id,
        devotee_name=sale_data.devotee_name,
        devotee_phone=sale_data.devotee_phone,
        notes=sale_data.notes
    )
    
    # Update token status
    token.status = TokenStatus.SOLD
    token.sold_at = datetime.utcnow()
    token.sold_by = current_user.id
    token.counter_number = sale.counter_number
    
    db.add(sale)
    db.flush()
    
    # Post to accounting if configured
    if seva.account_id:
        try:
            _post_token_sale_to_accounting(db, sale, seva, temple_id)
        except Exception as e:
            print(f"Error posting token sale to accounting: {str(e)}")
            # Don't fail the sale if accounting fails
    
    db.commit()
    db.refresh(sale)
    
    return {
        "success": True,
        "message": "Token sale recorded successfully",
        "sale": {
            "id": sale.id,
            "token_serial_number": sale.token_serial_number,
            "amount": sale.amount,
            "payment_mode": sale.payment_mode.value,
            "sale_date": sale.sale_date.isoformat()
        }
    }


def _post_token_sale_to_accounting(db: Session, sale: TokenSale, seva: Seva, temple_id: int):
    """Post token sale to accounting system"""
    # Get cash/bank account based on payment mode
    if sale.payment_mode == PaymentMode.CASH:
        cash_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code.like("1.1.1%")  # Cash account
        ).first()
        if not cash_account:
            return  # No cash account configured
        debit_account_id = cash_account.id
    else:  # UPI
        bank_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code.like("1.1.2%")  # Bank account
        ).first()
        if not bank_account:
            return  # No bank account configured
        debit_account_id = bank_account.id
    
    # Credit account from seva
    credit_account_id = seva.account_id
    
    if not credit_account_id:
        return  # No account configured for seva
    
    # Create journal entry
    journal_entry = JournalEntry(
        temple_id=temple_id,
        entry_date=sale.sale_date,
        entry_type="receipt",
        reference_number=f"TOKEN-{sale.token_serial_number}",
        narration=f"Token sale - {seva.name_english}",
        created_by=sale.sold_by
    )
    db.add(journal_entry)
    db.flush()
    
    # Create debit line
    debit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=debit_account_id,
        debit_amount=sale.amount,
        credit_amount=0,
        narration=f"Token sale - {sale.token_serial_number}"
    )
    
    # Create credit line
    credit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=credit_account_id,
        debit_amount=0,
        credit_amount=sale.amount,
        narration=f"Token sale - {seva.name_english}"
    )
    
    db.add(debit_line)
    db.add(credit_line)
    
    # Link sale to journal entry
    sale.journal_entry_id = journal_entry.id
    
    db.flush()


@router.get("/sales", response_model=List[TokenSaleResponse])
def get_token_sales(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    seva_id: Optional[int] = Query(None),
    counter_number: Optional[str] = Query(None),
    payment_mode: Optional[PaymentMode] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get token sales with filters"""
    temple_id = current_user.temple_id
    
    query = db.query(TokenSale).filter(TokenSale.temple_id == temple_id)
    
    if start_date:
        query = query.filter(TokenSale.sale_date >= start_date)
    if end_date:
        query = query.filter(TokenSale.sale_date <= end_date)
    if seva_id:
        query = query.filter(TokenSale.seva_id == seva_id)
    if counter_number:
        query = query.filter(TokenSale.counter_number == counter_number)
    if payment_mode:
        query = query.filter(TokenSale.payment_mode == payment_mode)
    
    sales = query.order_by(TokenSale.sale_date.desc(), TokenSale.sale_time.desc()).all()
    
    result = []
    for sale in sales:
        seva = db.query(Seva).filter(Seva.id == sale.seva_id).first()
        result.append(TokenSaleResponse(
            id=sale.id,
            sale_date=sale.sale_date,
            seva_id=sale.seva_id,
            seva_name=seva.name_english if seva else "Unknown",
            token_serial_number=sale.token_serial_number,
            amount=sale.amount,
            payment_mode=sale.payment_mode.value,
            counter_number=sale.counter_number,
            devotee_name=sale.devotee_name
        ))
    
    return result


@router.get("/inventory/status")
def get_token_inventory_status(
    seva_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get token inventory status by seva"""
    temple_id = current_user.temple_id
    
    query = db.query(
        TokenInventory.seva_id,
        TokenInventory.status,
        func.count(TokenInventory.id).label('count')
    ).filter(
        TokenInventory.temple_id == temple_id
    )
    
    if seva_id:
        query = query.filter(TokenInventory.seva_id == seva_id)
    
    results = query.group_by(TokenInventory.seva_id, TokenInventory.status).all()
    
    # Format results
    status_by_seva = {}
    for seva_id, status, count in results:
        if seva_id not in status_by_seva:
            seva = db.query(Seva).filter(Seva.id == seva_id).first()
            status_by_seva[seva_id] = {
                "seva_id": seva_id,
                "seva_name": seva.name_english if seva else "Unknown",
                "token_color": seva.token_color if seva else None,
                "statuses": {}
            }
        status_by_seva[seva_id]["statuses"][status.value] = count
    
    return list(status_by_seva.values())


@router.post("/reconcile", status_code=status.HTTP_201_CREATED)
def create_reconciliation(
    reconciliation_data: TokenReconciliationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create daily token reconciliation"""
    temple_id = current_user.temple_id
    recon_date = reconciliation_data.reconciliation_date
    
    # Check if reconciliation already exists
    existing = db.query(TokenReconciliation).filter(
        TokenReconciliation.temple_id == temple_id,
        TokenReconciliation.reconciliation_date == recon_date
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Reconciliation for {recon_date} already exists"
        )
    
    # Get all token sales for the date
    sales = db.query(TokenSale).filter(
        TokenSale.temple_id == temple_id,
        TokenSale.sale_date == recon_date
    ).all()
    
    # Calculate totals
    total_tokens_sold = len(sales)
    total_amount_cash = sum(s.amount for s in sales if s.payment_mode == PaymentMode.CASH)
    total_amount_upi = sum(s.amount for s in sales if s.payment_mode == PaymentMode.UPI)
    total_amount = total_amount_cash + total_amount_upi
    
    # Get token counts by seva
    token_counts = {}
    for sale in sales:
        if sale.seva_id not in token_counts:
            token_counts[sale.seva_id] = {"sold": 0, "amount": 0}
        token_counts[sale.seva_id]["sold"] += 1
        token_counts[sale.seva_id]["amount"] += sale.amount
    
    # Get counter-wise summary
    counter_summary = {}
    for sale in sales:
        counter = sale.counter_number or "UNKNOWN"
        if counter not in counter_summary:
            counter_summary[counter] = {
                "tokens_sold": 0,
                "cash": 0.0,
                "upi": 0.0,
                "total": 0.0
            }
        counter_summary[counter]["tokens_sold"] += 1
        if sale.payment_mode == PaymentMode.CASH:
            counter_summary[counter]["cash"] += sale.amount
        else:
            counter_summary[counter]["upi"] += sale.amount
        counter_summary[counter]["total"] += sale.amount
    
    # Get inventory status counts
    inventory_status = db.query(
        TokenInventory.seva_id,
        TokenInventory.status,
        func.count(TokenInventory.id).label('count')
    ).filter(
        TokenInventory.temple_id == temple_id
    ).group_by(
        TokenInventory.seva_id,
        TokenInventory.status
    ).all()
    
    # Add inventory counts to token_counts
    for seva_id, status, count in inventory_status:
        if seva_id not in token_counts:
            token_counts[seva_id] = {}
        token_counts[seva_id][status.value] = count
    
    # Create reconciliation record
    reconciliation = TokenReconciliation(
        temple_id=temple_id,
        reconciliation_date=recon_date,
        token_counts=json.dumps(token_counts),
        total_tokens_sold=total_tokens_sold,
        total_amount_cash=total_amount_cash,
        total_amount_upi=total_amount_upi,
        total_amount=total_amount,
        counter_summary=json.dumps(counter_summary),
        discrepancy_notes=reconciliation_data.discrepancy_notes,
        is_reconciled=False
    )
    
    db.add(reconciliation)
    db.commit()
    db.refresh(reconciliation)
    
    return {
        "success": True,
        "message": "Reconciliation created successfully",
        "reconciliation": {
            "id": reconciliation.id,
            "date": reconciliation.reconciliation_date.isoformat(),
            "total_tokens_sold": total_tokens_sold,
            "total_amount": total_amount,
            "total_cash": total_amount_cash,
            "total_upi": total_amount_upi
        }
    }


@router.put("/reconcile/{reconciliation_id}/approve")
def approve_reconciliation(
    reconciliation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve/reconcile a daily reconciliation"""
    reconciliation = db.query(TokenReconciliation).filter(
        TokenReconciliation.id == reconciliation_id,
        TokenReconciliation.temple_id == current_user.temple_id
    ).first()
    
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    
    if reconciliation.is_reconciled:
        raise HTTPException(status_code=400, detail="Reconciliation already approved")
    
    reconciliation.is_reconciled = True
    reconciliation.reconciled_by = current_user.id
    reconciliation.reconciled_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": "Reconciliation approved successfully"
    }


@router.get("/reconcile/{date}")
def get_reconciliation(
    date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reconciliation for a specific date"""
    reconciliation = db.query(TokenReconciliation).filter(
        TokenReconciliation.temple_id == current_user.temple_id,
        TokenReconciliation.reconciliation_date == date
    ).first()
    
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    
    return {
        "id": reconciliation.id,
        "date": reconciliation.reconciliation_date.isoformat(),
        "total_tokens_sold": reconciliation.total_tokens_sold,
        "total_amount": reconciliation.total_amount,
        "total_amount_cash": reconciliation.total_amount_cash,
        "total_amount_upi": reconciliation.total_amount_upi,
        "is_reconciled": reconciliation.is_reconciled,
        "token_counts": json.loads(reconciliation.token_counts) if reconciliation.token_counts else {},
        "counter_summary": json.loads(reconciliation.counter_summary) if reconciliation.counter_summary else {},
        "discrepancy_notes": reconciliation.discrepancy_notes
    }






