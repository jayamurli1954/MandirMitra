"""
Purchase Order, GRN, GIN API
Handles Purchase Orders, Goods Receipt Notes, and Goods Issue Notes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vendor import Vendor
from app.models.inventory import Item, Store, StockBalance, StockMovement, StockMovementType
from app.models.purchase_order import (
    PurchaseOrder, PurchaseOrderItem, GRN, GRNItem, GIN, GINItem,
    POStatus, GRNStatus, GINStatus
)
from app.schemas.purchase_order import (
    POCreate, POUpdate, POResponse, POItemResponse, POApprovalRequest,
    GRNCreate, GRNResponse, GRNItemResponse,
    GINCreate, GINUpdate, GINResponse, GINItemResponse, GINApprovalRequest
)
from app.api.inventory import post_inventory_purchase_to_accounting, post_inventory_issue_to_accounting

router = APIRouter(prefix="/api/v1/purchase-orders", tags=["purchase-orders"])


# ===== PURCHASE ORDER ENDPOINTS =====

@router.post("/", response_model=POResponse, status_code=201)
def create_purchase_order(
    po_data: POCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new Purchase Order"""
    # Verify vendor
    vendor = db.query(Vendor).filter(
        Vendor.id == po_data.vendor_id,
        Vendor.temple_id == current_user.temple_id
    ).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Generate PO number
    year = po_data.po_date.year
    prefix = f"PO/{year}/"
    last_po = db.query(PurchaseOrder).filter(
        PurchaseOrder.po_number.like(f"{prefix}%")
    ).order_by(PurchaseOrder.id.desc()).first()
    
    new_num = 1
    if last_po:
        try:
            last_num = int(last_po.po_number.split('/')[-1])
            new_num = last_num + 1
        except:
            pass
    
    po_number = f"{prefix}{new_num:04d}"
    
    # Calculate totals
    total_amount = sum(item.ordered_quantity * item.unit_price for item in po_data.items)
    tax_amount = 0.0  # Can be calculated based on GST
    grand_total = total_amount + tax_amount
    
    # Create PO
    po = PurchaseOrder(
        temple_id=current_user.temple_id,
        po_number=po_number,
        po_date=po_data.po_date,
        vendor_id=po_data.vendor_id,
        status=POStatus.DRAFT,
        requested_by=current_user.id,
        total_amount=total_amount,
        tax_amount=tax_amount,
        grand_total=grand_total,
        expected_delivery_date=po_data.expected_delivery_date,
        delivery_address=po_data.delivery_address,
        notes=po_data.notes
    )
    db.add(po)
    db.flush()
    
    # Create PO items
    for item_data in po_data.items:
        # Verify item and store
        item = db.query(Item).filter(Item.id == item_data.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_data.item_id} not found")
        
        store = db.query(Store).filter(Store.id == item_data.store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail=f"Store {item_data.store_id} not found")
        
        po_item = PurchaseOrderItem(
            po_id=po.id,
            item_id=item_data.item_id,
            ordered_quantity=item_data.ordered_quantity,
            received_quantity=0.0,
            pending_quantity=item_data.ordered_quantity,
            unit_price=item_data.unit_price,
            total_amount=item_data.ordered_quantity * item_data.unit_price,
            store_id=item_data.store_id,
            notes=item_data.notes
        )
        db.add(po_item)
    
    db.commit()
    db.refresh(po)
    
    return _enrich_po_response(po, db)


@router.get("/", response_model=List[POResponse])
def get_purchase_orders(
    status: Optional[POStatus] = Query(None),
    vendor_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all Purchase Orders"""
    query = db.query(PurchaseOrder).filter(PurchaseOrder.temple_id == current_user.temple_id)
    
    if status:
        query = query.filter(PurchaseOrder.status == status)
    if vendor_id:
        query = query.filter(PurchaseOrder.vendor_id == vendor_id)
    if from_date:
        query = query.filter(PurchaseOrder.po_date >= from_date)
    if to_date:
        query = query.filter(PurchaseOrder.po_date <= to_date)
    
    pos = query.order_by(PurchaseOrder.po_date.desc()).all()
    return [_enrich_po_response(po, db) for po in pos]


@router.get("/{po_id}", response_model=POResponse)
def get_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific Purchase Order"""
    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.temple_id == current_user.temple_id
    ).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    
    return _enrich_po_response(po, db)


@router.post("/{po_id}/submit", response_model=POResponse)
def submit_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit PO for approval"""
    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.temple_id == current_user.temple_id
    ).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    
    if po.status != POStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft POs can be submitted")
    
    po.status = POStatus.PENDING_APPROVAL
    po.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(po)
    
    return _enrich_po_response(po, db)


@router.post("/{po_id}/approve", response_model=POResponse)
def approve_purchase_order(
    po_id: int,
    approval_data: POApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject a Purchase Order"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can approve POs")
    
    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.temple_id == current_user.temple_id
    ).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    
    if po.status != POStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail="Only pending POs can be approved/rejected")
    
    if approval_data.approve:
        po.status = POStatus.APPROVED
        po.approved_by = current_user.id
        po.approved_at = datetime.utcnow()
        po.rejection_reason = None
    else:
        po.status = POStatus.REJECTED
        po.rejection_reason = approval_data.rejection_reason
    
    po.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(po)
    
    return _enrich_po_response(po, db)


# ===== GRN ENDPOINTS =====

@router.post("/grn", response_model=GRNResponse, status_code=201)
def create_grn(
    grn_data: GRNCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a Goods Receipt Note"""
    # Verify vendor
    vendor = db.query(Vendor).filter(
        Vendor.id == grn_data.vendor_id,
        Vendor.temple_id == current_user.temple_id
    ).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Generate GRN number
    year = grn_data.grn_date.year
    prefix = f"GRN/{year}/"
    last_grn = db.query(GRN).filter(
        GRN.grn_number.like(f"{prefix}%")
    ).order_by(GRN.id.desc()).first()
    
    new_num = 1
    if last_grn:
        try:
            last_num = int(last_grn.grn_number.split('/')[-1])
            new_num = last_num + 1
        except:
            pass
    
    grn_number = f"{prefix}{new_num:04d}"
    
    # Calculate total
    total_amount = sum(item.accepted_quantity * item.unit_price for item in grn_data.items)
    
    # Create GRN
    grn = GRN(
        temple_id=current_user.temple_id,
        grn_number=grn_number,
        grn_date=grn_data.grn_date,
        po_id=grn_data.po_id,
        vendor_id=grn_data.vendor_id,
        status=GRNStatus.PENDING,
        bill_number=grn_data.bill_number,
        bill_date=grn_data.bill_date,
        total_amount=total_amount,
        notes=grn_data.notes
    )
    db.add(grn)
    db.flush()
    
    # Create GRN items and stock movements
    for item_data in grn_data.items:
        item = db.query(Item).filter(Item.id == item_data.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_data.item_id} not found")
        
        grn_item = GRNItem(
            grn_id=grn.id,
            po_item_id=item_data.po_item_id,
            item_id=item_data.item_id,
            ordered_quantity=item_data.ordered_quantity,
            received_quantity=item_data.received_quantity,
            accepted_quantity=item_data.accepted_quantity,
            rejected_quantity=item_data.rejected_quantity,
            unit_price=item_data.unit_price,
            total_amount=item_data.accepted_quantity * item_data.unit_price,
            store_id=item_data.store_id,
            expiry_date=item_data.expiry_date,
            batch_number=item_data.batch_number,
            quality_checked=item_data.quality_checked,
            quality_notes=item_data.quality_notes,
            notes=item_data.notes
        )
        db.add(grn_item)
        db.flush()
        
        # Create stock movement for accepted quantity
        if item_data.accepted_quantity > 0:
            year = grn_data.grn_date.year
            prefix = f"PUR/{year}/"
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
                movement_type=StockMovementType.PURCHASE,
                movement_number=movement_number,
                movement_date=grn_data.grn_date,
                item_id=item_data.item_id,
                store_id=item_data.store_id,
                quantity=item_data.accepted_quantity,
                unit_price=item_data.unit_price,
                total_value=item_data.accepted_quantity * item_data.unit_price,
                reference_number=grn_data.bill_number,
                vendor_id=grn_data.vendor_id,
                grn_id=grn.id,
                expiry_date=item_data.expiry_date,
                batch_number=item_data.batch_number,
                notes=f"GRN: {grn_number}",
                temple_id=current_user.temple_id,
                created_by=current_user.id
            )
            db.add(movement)
            db.flush()
            
            # Update stock balance
            stock_balance = db.query(StockBalance).filter(
                StockBalance.item_id == item_data.item_id,
                StockBalance.store_id == item_data.store_id
            ).first()
            
            if not stock_balance:
                stock_balance = StockBalance(
                    item_id=item_data.item_id,
                    store_id=item_data.store_id,
                    quantity=0.0,
                    value=0.0,
                    temple_id=current_user.temple_id
                )
                db.add(stock_balance)
                db.flush()
            
            stock_balance.quantity += item_data.accepted_quantity
            stock_balance.value += item_data.accepted_quantity * item_data.unit_price
            stock_balance.last_movement_date = grn_data.grn_date
            stock_balance.last_movement_id = movement.id
            
            # Update expiry tracking
            if item_data.expiry_date:
                if not stock_balance.earliest_expiry_date or item_data.expiry_date < stock_balance.earliest_expiry_date:
                    stock_balance.earliest_expiry_date = item_data.expiry_date
            
            # Post to accounting
            journal_entry = post_inventory_purchase_to_accounting(db, movement, current_user.temple_id)
            if journal_entry:
                movement.journal_entry_id = journal_entry.id
        
        # Update PO item received quantity if linked
        if item_data.po_item_id:
            po_item = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.id == item_data.po_item_id).first()
            if po_item:
                po_item.received_quantity += item_data.accepted_quantity
                po_item.pending_quantity = po_item.ordered_quantity - po_item.received_quantity
    
    # Update PO status if all items received
    if grn_data.po_id:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == grn_data.po_id).first()
        if po:
            all_received = all(
                item.received_quantity >= item.ordered_quantity
                for item in po.po_items
            )
            if all_received:
                po.status = POStatus.RECEIVED
            else:
                po.status = POStatus.PARTIALLY_RECEIVED
    
    grn.status = GRNStatus.RECEIVED
    grn.received_by = current_user.id
    grn.received_at = datetime.utcnow()
    
    db.commit()
    db.refresh(grn)
    
    return _enrich_grn_response(grn, db)


@router.get("/grn", response_model=List[GRNResponse])
def get_grns(
    po_id: Optional[int] = Query(None),
    vendor_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all GRNs"""
    query = db.query(GRN).filter(GRN.temple_id == current_user.temple_id)
    
    if po_id:
        query = query.filter(GRN.po_id == po_id)
    if vendor_id:
        query = query.filter(GRN.vendor_id == vendor_id)
    if from_date:
        query = query.filter(GRN.grn_date >= from_date)
    if to_date:
        query = query.filter(GRN.grn_date <= to_date)
    
    grns = query.order_by(GRN.grn_date.desc()).all()
    return [_enrich_grn_response(grn, db) for grn in grns]


# ===== GIN ENDPOINTS =====

@router.post("/gin", response_model=GINResponse, status_code=201)
def create_gin(
    gin_data: GINCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a Goods Issue Note"""
    # Verify store
    store = db.query(Store).filter(
        Store.id == gin_data.issued_from_store_id,
        Store.temple_id == current_user.temple_id
    ).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Generate GIN number
    year = gin_data.gin_date.year
    prefix = f"GIN/{year}/"
    last_gin = db.query(GIN).filter(
        GIN.gin_number.like(f"{prefix}%")
    ).order_by(GIN.id.desc()).first()
    
    new_num = 1
    if last_gin:
        try:
            last_num = int(last_gin.gin_number.split('/')[-1])
            new_num = last_num + 1
        except:
            pass
    
    gin_number = f"{prefix}{new_num:04d}"
    
    # Create GIN
    gin = GIN(
        temple_id=current_user.temple_id,
        gin_number=gin_number,
        gin_date=gin_data.gin_date,
        status=GINStatus.DRAFT,
        issued_from_store_id=gin_data.issued_from_store_id,
        issued_to=gin_data.issued_to,
        purpose=gin_data.purpose,
        requested_by=current_user.id,
        notes=gin_data.notes
    )
    db.add(gin)
    db.flush()
    
    # Create GIN items
    for item_data in gin_data.items:
        item = db.query(Item).filter(Item.id == item_data.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_data.item_id} not found")
        
        # Check stock availability
        stock_balance = db.query(StockBalance).filter(
            StockBalance.item_id == item_data.item_id,
            StockBalance.store_id == gin_data.issued_from_store_id
        ).first()
        
        if not stock_balance or stock_balance.quantity < item_data.issued_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {item.name}. Available: {stock_balance.quantity if stock_balance else 0.0} {item.unit.value}"
            )
        
        # Calculate cost
        unit_cost = item.standard_cost
        if unit_cost == 0 and stock_balance.quantity > 0:
            unit_cost = stock_balance.value / stock_balance.quantity
        
        total_cost = item_data.issued_quantity * unit_cost
        
        gin_item = GINItem(
            gin_id=gin.id,
            item_id=item_data.item_id,
            requested_quantity=item_data.requested_quantity,
            issued_quantity=item_data.issued_quantity,
            unit_cost=unit_cost,
            total_cost=total_cost,
            notes=item_data.notes
        )
        db.add(gin_item)
        db.flush()
        
        # Create stock movement
        year = gin_data.gin_date.year
        prefix = f"ISS/{year}/"
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
            movement_type=StockMovementType.ISSUE,
            movement_number=movement_number,
            movement_date=gin_data.gin_date,
            item_id=item_data.item_id,
            store_id=gin_data.issued_from_store_id,
            quantity=item_data.issued_quantity,
            unit_price=unit_cost,
            total_value=total_cost,
            issued_to=gin_data.issued_to,
            purpose=gin_data.purpose,
            gin_id=gin.id,
            notes=f"GIN: {gin_number}",
            temple_id=current_user.temple_id,
            created_by=current_user.id
        )
        db.add(movement)
        db.flush()
        
        # Update stock balance
        stock_balance.quantity -= item_data.issued_quantity
        stock_balance.value -= total_cost
        stock_balance.last_movement_date = gin_data.gin_date
        stock_balance.last_movement_id = movement.id
        
        # Post to accounting
        journal_entry = post_inventory_issue_to_accounting(db, movement, current_user.temple_id)
        if journal_entry:
            movement.journal_entry_id = journal_entry.id
    
    gin.status = GINStatus.ISSUED
    gin.issued_by = current_user.id
    gin.issued_at = datetime.utcnow()
    
    db.commit()
    db.refresh(gin)
    
    return _enrich_gin_response(gin, db)


@router.get("/gin", response_model=List[GINResponse])
def get_gins(
    store_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all GINs"""
    query = db.query(GIN).filter(GIN.temple_id == current_user.temple_id)
    
    if store_id:
        query = query.filter(GIN.issued_from_store_id == store_id)
    if from_date:
        query = query.filter(GIN.gin_date >= from_date)
    if to_date:
        query = query.filter(GIN.gin_date <= to_date)
    
    gins = query.order_by(GIN.gin_date.desc()).all()
    return [_enrich_gin_response(gin, db) for gin in gins]


# ===== HELPER FUNCTIONS =====

def _enrich_po_response(po: PurchaseOrder, db: Session) -> POResponse:
    """Enrich PO response with related data"""
    vendor = db.query(Vendor).filter(Vendor.id == po.vendor_id).first()
    items = []
    for po_item in po.po_items:
        item = db.query(Item).filter(Item.id == po_item.item_id).first()
        items.append(POItemResponse(
            id=po_item.id,
            po_id=po_item.po_id,
            item_id=po_item.item_id,
            item_code=item.code if item else None,
            item_name=item.name if item else None,
            unit=item.unit.value if item else None,
            ordered_quantity=po_item.ordered_quantity,
            received_quantity=po_item.received_quantity,
            pending_quantity=po_item.pending_quantity,
            unit_price=po_item.unit_price,
            total_amount=po_item.total_amount,
            store_id=po_item.store_id,
            notes=po_item.notes
        ))
    
    return POResponse(
        id=po.id,
        temple_id=po.temple_id,
        po_number=po.po_number,
        po_date=po.po_date,
        vendor_id=po.vendor_id,
        vendor_name=vendor.name if vendor else None,
        status=po.status,
        total_amount=po.total_amount,
        tax_amount=po.tax_amount,
        grand_total=po.grand_total,
        expected_delivery_date=po.expected_delivery_date,
        delivery_address=po.delivery_address,
        notes=po.notes,
        requested_by=po.requested_by,
        approved_by=po.approved_by,
        approved_at=po.approved_at,
        rejection_reason=po.rejection_reason,
        created_at=po.created_at,
        updated_at=po.updated_at,
        items=items
    )


def _enrich_grn_response(grn: GRN, db: Session) -> GRNResponse:
    """Enrich GRN response with related data"""
    vendor = db.query(Vendor).filter(Vendor.id == grn.vendor_id).first()
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == grn.po_id).first() if grn.po_id else None
    items = []
    for grn_item in grn.grn_items:
        item = db.query(Item).filter(Item.id == grn_item.item_id).first()
        items.append(GRNItemResponse(
            id=grn_item.id,
            grn_id=grn_item.grn_id,
            item_id=grn_item.item_id,
            item_code=item.code if item else None,
            item_name=item.name if item else None,
            unit=item.unit.value if item else None,
            ordered_quantity=grn_item.ordered_quantity,
            received_quantity=grn_item.received_quantity,
            accepted_quantity=grn_item.accepted_quantity,
            rejected_quantity=grn_item.rejected_quantity,
            unit_price=grn_item.unit_price,
            total_amount=grn_item.total_amount,
            store_id=grn_item.store_id,
            expiry_date=grn_item.expiry_date,
            batch_number=grn_item.batch_number,
            quality_checked=grn_item.quality_checked,
            quality_notes=grn_item.quality_notes,
            notes=grn_item.notes
        ))
    
    return GRNResponse(
        id=grn.id,
        temple_id=grn.temple_id,
        grn_number=grn.grn_number,
        grn_date=grn.grn_date,
        po_id=grn.po_id,
        po_number=po.po_number if po else None,
        vendor_id=grn.vendor_id,
        vendor_name=vendor.name if vendor else None,
        status=grn.status,
        bill_number=grn.bill_number,
        bill_date=grn.bill_date,
        total_amount=grn.total_amount,
        received_by=grn.received_by,
        received_at=grn.received_at,
        notes=grn.notes,
        created_at=grn.created_at,
        updated_at=grn.updated_at,
        items=items
    )


def _enrich_gin_response(gin: GIN, db: Session) -> GINResponse:
    """Enrich GIN response with related data"""
    store = db.query(Store).filter(Store.id == gin.issued_from_store_id).first()
    items = []
    for gin_item in gin.gin_items:
        item = db.query(Item).filter(Item.id == gin_item.item_id).first()
        items.append(GINItemResponse(
            id=gin_item.id,
            gin_id=gin_item.gin_id,
            item_id=gin_item.item_id,
            item_code=item.code if item else None,
            item_name=item.name if item else None,
            unit=item.unit.value if item else None,
            requested_quantity=gin_item.requested_quantity,
            issued_quantity=gin_item.issued_quantity,
            unit_cost=gin_item.unit_cost,
            total_cost=gin_item.total_cost,
            notes=gin_item.notes
        ))
    
    return GINResponse(
        id=gin.id,
        temple_id=gin.temple_id,
        gin_number=gin.gin_number,
        gin_date=gin.gin_date,
        status=gin.status,
        issued_from_store_id=gin.issued_from_store_id,
        store_name=store.name if store else None,
        issued_to=gin.issued_to,
        purpose=gin.purpose,
        requested_by=gin.requested_by,
        approved_by=gin.approved_by,
        approved_at=gin.approved_at,
        issued_by=gin.issued_by,
        issued_at=gin.issued_at,
        notes=gin.notes,
        created_at=gin.created_at,
        updated_at=gin.updated_at,
        items=items
    )

