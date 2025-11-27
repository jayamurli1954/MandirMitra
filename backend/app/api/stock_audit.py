"""
Stock Audit and Wastage API
Handles stock audit workflow and wastage recording
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.inventory import Item, Store, StockBalance, StockMovement, StockMovementType
from app.models.stock_audit import (
    StockAudit, StockAuditItem, StockWastage,
    AuditStatus, WastageReason
)
from app.models.accounting import JournalEntry, JournalLine, JournalEntryStatus, TransactionType

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


# ===== SCHEMAS =====

class StockAuditItemCreate(BaseModel):
    item_id: int
    physical_quantity: float = Field(..., gt=0)
    discrepancy_reason: Optional[str] = None
    notes: Optional[str] = None


class StockAuditCreate(BaseModel):
    audit_date: date
    store_id: int
    notes: Optional[str] = None


class StockAuditItemResponse(BaseModel):
    id: int
    item_id: int
    item_code: str
    item_name: str
    book_quantity: float
    book_value: float
    physical_quantity: float
    physical_value: float
    quantity_discrepancy: float
    value_discrepancy: float
    discrepancy_reason: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class StockAuditResponse(BaseModel):
    id: int
    audit_number: str
    audit_date: date
    store_id: int
    store_name: str
    status: AuditStatus
    total_items_audited: int
    items_with_discrepancy: int
    total_discrepancy_value: float
    conducted_by: int
    verified_by: Optional[int]
    approved_by: Optional[int]
    notes: Optional[str]
    created_at: datetime
    audit_items: List[StockAuditItemResponse] = []
    
    class Config:
        from_attributes = True


class StockWastageCreate(BaseModel):
    wastage_date: date
    item_id: int
    store_id: int
    quantity: float = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0)
    reason: WastageReason
    reason_details: Optional[str] = None
    notes: Optional[str] = None


class StockWastageResponse(BaseModel):
    id: int
    wastage_number: str
    wastage_date: date
    item_id: int
    item_code: str
    item_name: str
    store_id: int
    store_name: str
    quantity: float
    unit_cost: float
    total_value: float
    reason: WastageReason
    reason_details: Optional[str]
    recorded_by: int
    approved_by: Optional[int]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== STOCK AUDIT ENDPOINTS =====

@router.post("/audits", response_model=StockAuditResponse, status_code=201)
def create_stock_audit(
    audit_data: StockAuditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new stock audit"""
    # Verify store exists
    store = db.query(Store).filter(
        Store.id == audit_data.store_id,
        Store.temple_id == current_user.temple_id
    ).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Generate audit number
    year = audit_data.audit_date.year
    prefix = f"AUD/{year}/"
    last_audit = db.query(StockAudit).filter(
        StockAudit.audit_number.like(f"{prefix}%")
    ).order_by(StockAudit.id.desc()).first()
    
    new_num = 1
    if last_audit:
        try:
            last_num = int(last_audit.audit_number.split('/')[-1])
            new_num = last_num + 1
        except:
            pass
    
    audit_number = f"{prefix}{new_num:04d}"
    
    # Create audit
    audit = StockAudit(
        temple_id=current_user.temple_id,
        audit_number=audit_number,
        audit_date=audit_data.audit_date,
        store_id=audit_data.store_id,
        status=AuditStatus.DRAFT,
        conducted_by=current_user.id,
        started_at=datetime.utcnow(),
        notes=audit_data.notes
    )
    db.add(audit)
    db.flush()
    
    db.commit()
    db.refresh(audit)
    
    return _enrich_audit_response(audit, db)


@router.post("/audits/{audit_id}/items", response_model=StockAuditItemResponse)
def add_audit_item(
    audit_id: int,
    item_data: StockAuditItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add an item to stock audit"""
    audit = db.query(StockAudit).filter(
        StockAudit.id == audit_id,
        StockAudit.temple_id == current_user.temple_id
    ).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if audit.status != AuditStatus.DRAFT and audit.status != AuditStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Cannot add items to completed audit")
    
    # Get item
    item = db.query(Item).filter(Item.id == item_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Get book balance
    stock_balance = db.query(StockBalance).filter(
        StockBalance.item_id == item_data.item_id,
        StockBalance.store_id == audit.store_id
    ).first()
    
    book_quantity = stock_balance.quantity if stock_balance else 0.0
    book_value = stock_balance.value if stock_balance else 0.0
    
    # Calculate physical value
    unit_cost = item.standard_cost if item.standard_cost > 0 else (book_value / book_quantity if book_quantity > 0 else 0)
    physical_value = item_data.physical_quantity * unit_cost
    
    # Calculate discrepancy
    quantity_discrepancy = item_data.physical_quantity - book_quantity
    value_discrepancy = physical_value - book_value
    
    # Check if item already exists in audit
    existing = db.query(StockAuditItem).filter(
        StockAuditItem.audit_id == audit_id,
        StockAuditItem.item_id == item_data.item_id
    ).first()
    
    if existing:
        # Update existing
        existing.physical_quantity = item_data.physical_quantity
        existing.physical_value = physical_value
        existing.quantity_discrepancy = quantity_discrepancy
        existing.value_discrepancy = value_discrepancy
        existing.discrepancy_reason = item_data.discrepancy_reason
        existing.notes = item_data.notes
        audit_item = existing
    else:
        # Create new
        audit_item = StockAuditItem(
            audit_id=audit_id,
            item_id=item_data.item_id,
            book_quantity=book_quantity,
            book_value=book_value,
            physical_quantity=item_data.physical_quantity,
            physical_value=physical_value,
            quantity_discrepancy=quantity_discrepancy,
            value_discrepancy=value_discrepancy,
            discrepancy_reason=item_data.discrepancy_reason,
            notes=item_data.notes
        )
        db.add(audit_item)
    
    # Update audit status
    if audit.status == AuditStatus.DRAFT:
        audit.status = AuditStatus.IN_PROGRESS
    
    db.commit()
    db.refresh(audit_item)
    
    return StockAuditItemResponse(
        id=audit_item.id,
        item_id=item.id,
        item_code=item.code,
        item_name=item.name,
        book_quantity=audit_item.book_quantity,
        book_value=audit_item.book_value,
        physical_quantity=audit_item.physical_quantity,
        physical_value=audit_item.physical_value,
        quantity_discrepancy=audit_item.quantity_discrepancy,
        value_discrepancy=audit_item.value_discrepancy,
        discrepancy_reason=audit_item.discrepancy_reason,
        notes=audit_item.notes
    )


@router.post("/audits/{audit_id}/complete", response_model=StockAuditResponse)
def complete_stock_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete stock audit and calculate summary"""
    audit = db.query(StockAudit).filter(
        StockAudit.id == audit_id,
        StockAudit.temple_id == current_user.temple_id
    ).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if audit.status == AuditStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Audit already completed")
    
    # Get all audit items
    audit_items = db.query(StockAuditItem).filter(StockAuditItem.audit_id == audit_id).all()
    
    # Calculate summary
    total_items = len(audit_items)
    items_with_discrepancy = sum(1 for item in audit_items if abs(item.quantity_discrepancy) > 0.01)
    total_discrepancy_value = sum(abs(item.value_discrepancy) for item in audit_items)
    
    # Update audit
    audit.status = AuditStatus.COMPLETED
    audit.completed_at = datetime.utcnow()
    audit.total_items_audited = total_items
    audit.items_with_discrepancy = items_with_discrepancy
    audit.total_discrepancy_value = total_discrepancy_value
    
    if items_with_discrepancy > 0:
        audit.status = AuditStatus.DISCREPANCY
    
    db.commit()
    db.refresh(audit)
    
    return _enrich_audit_response(audit, db)


@router.get("/audits", response_model=List[StockAuditResponse])
def get_stock_audits(
    store_id: Optional[int] = Query(None),
    status: Optional[AuditStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all stock audits"""
    query = db.query(StockAudit).filter(StockAudit.temple_id == current_user.temple_id)
    
    if store_id:
        query = query.filter(StockAudit.store_id == store_id)
    if status:
        query = query.filter(StockAudit.status == status)
    if from_date:
        query = query.filter(StockAudit.audit_date >= from_date)
    if to_date:
        query = query.filter(StockAudit.audit_date <= to_date)
    
    audits = query.order_by(StockAudit.audit_date.desc()).all()
    return [_enrich_audit_response(audit, db) for audit in audits]


@router.get("/audits/{audit_id}", response_model=StockAuditResponse)
def get_stock_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific stock audit"""
    audit = db.query(StockAudit).filter(
        StockAudit.id == audit_id,
        StockAudit.temple_id == current_user.temple_id
    ).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return _enrich_audit_response(audit, db)


# ===== WASTAGE ENDPOINTS =====

@router.post("/wastages", response_model=StockWastageResponse, status_code=201)
def create_stock_wastage(
    wastage_data: StockWastageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record stock wastage"""
    # Verify item and store
    item = db.query(Item).filter(Item.id == wastage_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    store = db.query(Store).filter(
        Store.id == wastage_data.store_id,
        Store.temple_id == current_user.temple_id
    ).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Check stock availability
    stock_balance = db.query(StockBalance).filter(
        StockBalance.item_id == wastage_data.item_id,
        StockBalance.store_id == wastage_data.store_id
    ).first()
    
    if not stock_balance or stock_balance.quantity < wastage_data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {stock_balance.quantity if stock_balance else 0}"
        )
    
    # Generate wastage number
    year = wastage_data.wastage_date.year
    prefix = f"WST/{year}/"
    last_wastage = db.query(StockWastage).filter(
        StockWastage.wastage_number.like(f"{prefix}%")
    ).order_by(StockWastage.id.desc()).first()
    
    new_num = 1
    if last_wastage:
        try:
            last_num = int(last_wastage.wastage_number.split('/')[-1])
            new_num = last_num + 1
        except:
            pass
    
    wastage_number = f"{prefix}{new_num:04d}"
    total_value = wastage_data.quantity * wastage_data.unit_cost
    
    # Create wastage record
    wastage = StockWastage(
        temple_id=current_user.temple_id,
        wastage_number=wastage_number,
        wastage_date=wastage_data.wastage_date,
        item_id=wastage_data.item_id,
        store_id=wastage_data.store_id,
        quantity=wastage_data.quantity,
        unit_cost=wastage_data.unit_cost,
        total_value=total_value,
        reason=wastage_data.reason,
        reason_details=wastage_data.reason_details,
        recorded_by=current_user.id,
        notes=wastage_data.notes
    )
    db.add(wastage)
    db.flush()
    
    # Update stock balance
    stock_balance.quantity -= wastage_data.quantity
    stock_balance.value -= total_value
    
    # Create stock movement (adjustment)
    # Generate movement number
    year = wastage_data.wastage_date.year
    prefix = f"ADJ/{year}/"
    last_movement = db.query(StockMovement).filter(
        StockMovement.movement_number.like(f"{prefix}%")
    ).order_by(StockMovement.id.desc()).first()
    
    new_num = 1
    if last_movement:
        try:
            last_num = int(last_movement.movement_number.split('/')[-1])
            new_num = last_num + 1
        except:
            pass
    
    movement_number = f"{prefix}{new_num:04d}"
    
    movement = StockMovement(
        temple_id=current_user.temple_id,
        movement_type=StockMovementType.ADJUSTMENT,
        movement_number=movement_number,
        movement_date=wastage_data.wastage_date,
        item_id=wastage_data.item_id,
        store_id=wastage_data.store_id,
        quantity=-wastage_data.quantity,  # Negative for reduction
        unit_price=wastage_data.unit_cost,
        total_value=-total_value,
        reference_number=wastage_number,
        notes=f"Wastage - {wastage_data.reason.value}: {wastage_data.reason_details}",
        created_by=current_user.id
    )
    db.add(movement)
    
    # Post to accounting (if needed)
    # Dr: Wastage Expense, Cr: Inventory
    
    db.commit()
    db.refresh(wastage)
    
    return _enrich_wastage_response(wastage, db)


@router.get("/wastages", response_model=List[StockWastageResponse])
def get_stock_wastages(
    item_id: Optional[int] = Query(None),
    store_id: Optional[int] = Query(None),
    reason: Optional[WastageReason] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all stock wastages"""
    query = db.query(StockWastage).filter(StockWastage.temple_id == current_user.temple_id)
    
    if item_id:
        query = query.filter(StockWastage.item_id == item_id)
    if store_id:
        query = query.filter(StockWastage.store_id == store_id)
    if reason:
        query = query.filter(StockWastage.reason == reason)
    if from_date:
        query = query.filter(StockWastage.wastage_date >= from_date)
    if to_date:
        query = query.filter(StockWastage.wastage_date <= to_date)
    
    wastages = query.order_by(StockWastage.wastage_date.desc()).all()
    return [_enrich_wastage_response(w, db) for w in wastages]


def _enrich_audit_response(audit: StockAudit, db: Session) -> StockAuditResponse:
    """Enrich audit response with related data"""
    store = db.query(Store).filter(Store.id == audit.store_id).first()
    
    # Get audit items
    audit_items = db.query(StockAuditItem).filter(StockAuditItem.audit_id == audit.id).all()
    items_response = []
    for item in audit_items:
        item_master = db.query(Item).filter(Item.id == item.item_id).first()
        items_response.append(StockAuditItemResponse(
            id=item.id,
            item_id=item.item_id,
            item_code=item_master.code if item_master else "",
            item_name=item_master.name if item_master else "",
            book_quantity=item.book_quantity,
            book_value=item.book_value,
            physical_quantity=item.physical_quantity,
            physical_value=item.physical_value,
            quantity_discrepancy=item.quantity_discrepancy,
            value_discrepancy=item.value_discrepancy,
            discrepancy_reason=item.discrepancy_reason,
            notes=item.notes
        ))
    
    return StockAuditResponse(
        id=audit.id,
        audit_number=audit.audit_number,
        audit_date=audit.audit_date,
        store_id=audit.store_id,
        store_name=store.name if store else "",
        status=audit.status,
        total_items_audited=audit.total_items_audited,
        items_with_discrepancy=audit.items_with_discrepancy,
        total_discrepancy_value=audit.total_discrepancy_value,
        conducted_by=audit.conducted_by,
        verified_by=audit.verified_by,
        approved_by=audit.approved_by,
        notes=audit.notes,
        created_at=audit.created_at,
        audit_items=items_response
    )


def _enrich_wastage_response(wastage: StockWastage, db: Session) -> StockWastageResponse:
    """Enrich wastage response with related data"""
    item = db.query(Item).filter(Item.id == wastage.item_id).first()
    store = db.query(Store).filter(Store.id == wastage.store_id).first()
    
    return StockWastageResponse(
        id=wastage.id,
        wastage_number=wastage.wastage_number,
        wastage_date=wastage.wastage_date,
        item_id=wastage.item_id,
        item_code=item.code if item else "",
        item_name=item.name if item else "",
        store_id=wastage.store_id,
        store_name=store.name if store else "",
        quantity=wastage.quantity,
        unit_cost=wastage.unit_cost,
        total_value=wastage.total_value,
        reason=wastage.reason,
        reason_details=wastage.reason_details,
        recorded_by=wastage.recorded_by,
        approved_by=wastage.approved_by,
        notes=wastage.notes,
        created_at=wastage.created_at
    )

