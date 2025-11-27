"""
Budget Management API
Handles budget creation, approval, and Budget vs Actual reports
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.accounting import Account, JournalEntry, JournalLine, JournalEntryStatus, AccountType
from app.models.financial_period import FinancialYear
from app.models.budget import Budget, BudgetItem, BudgetRevision, BudgetStatus, BudgetType
from app.schemas.budget import (
    BudgetCreate, BudgetUpdate, BudgetResponse, BudgetItemCreate, BudgetItemUpdate,
    BudgetItemResponse, BudgetApprovalRequest, BudgetVsActualResponse
)
from app.api.journal_entries import generate_entry_number

router = APIRouter(prefix="/api/v1/budget", tags=["budget"])


@router.post("/", response_model=BudgetResponse, status_code=201)
def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new budget"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can create budgets")
    
    # Verify financial year exists
    financial_year = db.query(FinancialYear).filter(
        FinancialYear.id == budget_data.financial_year_id,
        FinancialYear.temple_id == current_user.temple_id
    ).first()
    if not financial_year:
        raise HTTPException(status_code=404, detail="Financial year not found")
    
    # Calculate total budgeted amount
    total_budgeted = sum(item.budgeted_amount for item in budget_data.budget_items)
    
    # Create budget
    budget = Budget(
        temple_id=current_user.temple_id,
        financial_year_id=budget_data.financial_year_id,
        budget_name=budget_data.budget_name,
        budget_type=budget_data.budget_type,
        budget_period_start=budget_data.budget_period_start,
        budget_period_end=budget_data.budget_period_end,
        total_budgeted_amount=total_budgeted,
        status=BudgetStatus.DRAFT,
        notes=budget_data.notes,
        created_by=current_user.id
    )
    db.add(budget)
    db.flush()
    
    # Create budget items
    for item_data in budget_data.budget_items:
        # Verify account exists
        account = db.query(Account).filter(
            Account.id == item_data.account_id,
            Account.temple_id == current_user.temple_id
        ).first()
        if not account:
            raise HTTPException(status_code=404, detail=f"Account {item_data.account_id} not found")
        
        budget_item = BudgetItem(
            budget_id=budget.id,
            account_id=item_data.account_id,
            budgeted_amount=item_data.budgeted_amount,
            notes=item_data.notes
        )
        db.add(budget_item)
    
    db.commit()
    db.refresh(budget)
    
    return _enrich_budget_response(budget, db, current_user.temple_id)


@router.get("/", response_model=List[BudgetResponse])
def get_budgets(
    financial_year_id: Optional[int] = Query(None),
    status: Optional[BudgetStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all budgets"""
    query = db.query(Budget).filter(Budget.temple_id == current_user.temple_id)
    
    if financial_year_id:
        query = query.filter(Budget.financial_year_id == financial_year_id)
    if status:
        query = query.filter(Budget.status == status)
    
    budgets = query.order_by(Budget.budget_period_start.desc()).all()
    return [_enrich_budget_response(b, db, current_user.temple_id) for b in budgets]


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.temple_id == current_user.temple_id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return _enrich_budget_response(budget, db, current_user.temple_id)


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.temple_id == current_user.temple_id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget.status == BudgetStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Cannot update approved budget. Create a revision instead.")
    
    # Update fields
    update_data = budget_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(budget, field, value)
    
    budget.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(budget)
    
    return _enrich_budget_response(budget, db, current_user.temple_id)


@router.post("/{budget_id}/submit", response_model=BudgetResponse)
def submit_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit budget for approval"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.temple_id == current_user.temple_id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget.status != BudgetStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft budgets can be submitted")
    
    budget.status = BudgetStatus.SUBMITTED
    budget.submitted_by = current_user.id
    budget.submitted_at = datetime.utcnow()
    budget.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(budget)
    
    return _enrich_budget_response(budget, db, current_user.temple_id)


@router.post("/{budget_id}/approve", response_model=BudgetResponse)
def approve_budget(
    budget_id: int,
    approval_data: BudgetApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject a budget"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can approve budgets")
    
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.temple_id == current_user.temple_id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget.status != BudgetStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Only submitted budgets can be approved/rejected")
    
    if approval_data.approve:
        budget.status = BudgetStatus.APPROVED
        budget.approved_by = current_user.id
        budget.approved_at = datetime.utcnow()
        budget.rejection_reason = None
    else:
        budget.status = BudgetStatus.REJECTED
        budget.rejection_reason = approval_data.rejection_reason
    
    budget.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(budget)
    
    return _enrich_budget_response(budget, db, current_user.temple_id)


@router.post("/{budget_id}/activate", response_model=BudgetResponse)
def activate_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate an approved budget"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can activate budgets")
    
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.temple_id == current_user.temple_id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget.status != BudgetStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Only approved budgets can be activated")
    
    # Deactivate other active budgets for the same period
    db.query(Budget).filter(
        Budget.temple_id == current_user.temple_id,
        Budget.financial_year_id == budget.financial_year_id,
        Budget.status == BudgetStatus.ACTIVE,
        Budget.id != budget_id
    ).update({Budget.status: BudgetStatus.CLOSED})
    
    budget.status = BudgetStatus.ACTIVE
    budget.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(budget)
    
    return _enrich_budget_response(budget, db, current_user.temple_id)


@router.get("/{budget_id}/vs-actual", response_model=BudgetVsActualResponse)
def get_budget_vs_actual(
    budget_id: int,
    as_of_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Budget vs Actual comparison report"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.temple_id == current_user.temple_id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Use budget period end if as_of_date not provided
    if not as_of_date:
        as_of_date = budget.budget_period_end
    
    # Get all budget items with actual amounts
    budget_items = db.query(BudgetItem).filter(BudgetItem.budget_id == budget_id).all()
    
    items_response = []
    total_actual = 0.0
    
    for item in budget_items:
        account = db.query(Account).filter(Account.id == item.account_id).first()
        if not account:
            continue
        
        # Calculate actual amount from journal entries
        actual_query = db.query(
            func.sum(JournalLine.debit_amount).label('total_debit'),
            func.sum(JournalLine.credit_amount).label('total_credit')
        ).join(JournalLine.journal_entry).filter(
            JournalLine.account_id == item.account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            func.date(JournalEntry.entry_date) >= budget.budget_period_start,
            func.date(JournalEntry.entry_date) <= as_of_date
        )
        if current_user.temple_id:
            actual_query = actual_query.filter(JournalEntry.temple_id == current_user.temple_id)
        
        actual_result = actual_query.first()
        
        # Determine actual amount based on account type
        if account.account_type == AccountType.INCOME:
            actual_amount = float(actual_result.total_credit or 0)
        elif account.account_type == AccountType.EXPENSE:
            actual_amount = float(actual_result.total_debit or 0)
        else:
            # For asset/liability, use net balance
            actual_amount = float((actual_result.total_debit or 0) - (actual_result.total_credit or 0))
        
        variance = actual_amount - item.budgeted_amount
        variance_percentage = (variance / item.budgeted_amount * 100) if item.budgeted_amount > 0 else 0
        
        total_actual += actual_amount
        
        items_response.append(BudgetItemResponse(
            id=item.id,
            budget_id=item.budget_id,
            account_id=item.account_id,
            account_code=account.account_code,
            account_name=account.account_name,
            budgeted_amount=item.budgeted_amount,
            actual_amount=actual_amount,
            variance=variance,
            variance_percentage=variance_percentage,
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at
        ))
    
    total_variance = total_actual - budget.total_budgeted_amount
    total_variance_percentage = (total_variance / budget.total_budgeted_amount * 100) if budget.total_budgeted_amount > 0 else 0
    
    return BudgetVsActualResponse(
        budget_id=budget.id,
        budget_name=budget.budget_name,
        period_start=budget.budget_period_start,
        period_end=budget.budget_period_end,
        total_budgeted=budget.total_budgeted_amount,
        total_actual=total_actual,
        total_variance=total_variance,
        total_variance_percentage=total_variance_percentage,
        items=items_response
    )


@router.post("/{budget_id}/items", response_model=BudgetItemResponse)
def add_budget_item(
    budget_id: int,
    item_data: BudgetItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add an item to a budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.temple_id == current_user.temple_id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget.status == BudgetStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Cannot add items to approved budget")
    
    # Check if item already exists
    existing = db.query(BudgetItem).filter(
        BudgetItem.budget_id == budget_id,
        BudgetItem.account_id == item_data.account_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Budget item for this account already exists")
    
    budget_item = BudgetItem(
        budget_id=budget_id,
        account_id=item_data.account_id,
        budgeted_amount=item_data.budgeted_amount,
        notes=item_data.notes
    )
    db.add(budget_item)
    
    # Update budget total
    budget.total_budgeted_amount += item_data.budgeted_amount
    budget.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(budget_item)
    
    account = db.query(Account).filter(Account.id == item_data.account_id).first()
    return BudgetItemResponse(
        id=budget_item.id,
        budget_id=budget_item.budget_id,
        account_id=budget_item.account_id,
        account_code=account.account_code if account else None,
        account_name=account.account_name if account else None,
        budgeted_amount=budget_item.budgeted_amount,
        actual_amount=0.0,
        variance=0.0,
        variance_percentage=0.0,
        notes=budget_item.notes,
        created_at=budget_item.created_at,
        updated_at=budget_item.updated_at
    )


@router.put("/{budget_id}/items/{item_id}", response_model=BudgetItemResponse)
def update_budget_item(
    budget_id: int,
    item_id: int,
    item_data: BudgetItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a budget item"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.temple_id == current_user.temple_id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget.status == BudgetStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Cannot update items in approved budget")
    
    budget_item = db.query(BudgetItem).filter(
        BudgetItem.id == item_id,
        BudgetItem.budget_id == budget_id
    ).first()
    if not budget_item:
        raise HTTPException(status_code=404, detail="Budget item not found")
    
    # Update amount and adjust budget total
    if item_data.budgeted_amount is not None:
        old_amount = budget_item.budgeted_amount
        budget.total_budgeted_amount = budget.total_budgeted_amount - old_amount + item_data.budgeted_amount
        budget_item.budgeted_amount = item_data.budgeted_amount
    
    if item_data.notes is not None:
        budget_item.notes = item_data.notes
    
    budget_item.updated_at = datetime.utcnow()
    budget.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(budget_item)
    
    account = db.query(Account).filter(Account.id == budget_item.account_id).first()
    return BudgetItemResponse(
        id=budget_item.id,
        budget_id=budget_item.budget_id,
        account_id=budget_item.account_id,
        account_code=account.account_code if account else None,
        account_name=account.account_name if account else None,
        budgeted_amount=budget_item.budgeted_amount,
        actual_amount=0.0,
        variance=0.0,
        variance_percentage=0.0,
        notes=budget_item.notes,
        created_at=budget_item.created_at,
        updated_at=budget_item.updated_at
    )


@router.delete("/{budget_id}/items/{item_id}", status_code=204)
def delete_budget_item(
    budget_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a budget item"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.temple_id == current_user.temple_id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget.status == BudgetStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Cannot delete items from approved budget")
    
    budget_item = db.query(BudgetItem).filter(
        BudgetItem.id == item_id,
        BudgetItem.budget_id == budget_id
    ).first()
    if not budget_item:
        raise HTTPException(status_code=404, detail="Budget item not found")
    
    # Update budget total
    budget.total_budgeted_amount -= budget_item.budgeted_amount
    budget.updated_at = datetime.utcnow()
    
    db.delete(budget_item)
    db.commit()
    
    return None


def _enrich_budget_response(budget: Budget, db: Session, temple_id: Optional[int]) -> BudgetResponse:
    """Enrich budget response with actual amounts and items"""
    # Get budget items
    items = db.query(BudgetItem).filter(BudgetItem.budget_id == budget.id).all()
    
    items_response = []
    total_actual = 0.0
    
    for item in items:
        account = db.query(Account).filter(Account.id == item.account_id).first()
        if not account:
            continue
        
        # Calculate actual amount
        actual_query = db.query(
            func.sum(JournalLine.debit_amount).label('total_debit'),
            func.sum(JournalLine.credit_amount).label('total_credit')
        ).join(JournalLine.journal_entry).filter(
            JournalLine.account_id == item.account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            func.date(JournalEntry.entry_date) >= budget.budget_period_start,
            func.date(JournalEntry.entry_date) <= budget.budget_period_end
        )
        if temple_id:
            actual_query = actual_query.filter(JournalEntry.temple_id == temple_id)
        
        actual_result = actual_query.first()
        
        if account.account_type == AccountType.INCOME:
            actual_amount = float(actual_result.total_credit or 0)
        elif account.account_type == AccountType.EXPENSE:
            actual_amount = float(actual_result.total_debit or 0)
        else:
            actual_amount = float((actual_result.total_debit or 0) - (actual_result.total_credit or 0))
        
        variance = actual_amount - item.budgeted_amount
        variance_percentage = (variance / item.budgeted_amount * 100) if item.budgeted_amount > 0 else 0
        total_actual += actual_amount
        
        items_response.append(BudgetItemResponse(
            id=item.id,
            budget_id=item.budget_id,
            account_id=item.account_id,
            account_code=account.account_code,
            account_name=account.account_name,
            budgeted_amount=item.budgeted_amount,
            actual_amount=actual_amount,
            variance=variance,
            variance_percentage=variance_percentage,
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at
        ))
    
    return BudgetResponse(
        id=budget.id,
        temple_id=budget.temple_id,
        financial_year_id=budget.financial_year_id,
        budget_name=budget.budget_name,
        budget_type=budget.budget_type,
        budget_period_start=budget.budget_period_start,
        budget_period_end=budget.budget_period_end,
        status=budget.status,
        total_budgeted_amount=budget.total_budgeted_amount,
        total_actual_amount=total_actual,
        total_variance=total_actual - budget.total_budgeted_amount,
        notes=budget.notes,
        submitted_by=budget.submitted_by,
        submitted_at=budget.submitted_at,
        approved_by=budget.approved_by,
        approved_at=budget.approved_at,
        created_by=budget.created_by,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
        budget_items=items_response
    )

