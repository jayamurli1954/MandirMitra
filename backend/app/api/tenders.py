"""
Tender Management API Endpoints
Optional feature for transparent procurement
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.audit import log_action, get_entity_dict
from app.models.asset import Tender, TenderBid
from app.models.vendor import Vendor
from app.models.user import User
from app.models.temple import Temple
from app.schemas.tender import (
    TenderCreate, TenderUpdate, TenderResponse,
    TenderBidCreate, TenderBidUpdate, TenderBidResponse,
    TenderEvaluationRequest, TenderAwardRequest
)

router = APIRouter(prefix="/api/v1/tenders", tags=["tenders"])


# ===== TENDER MANAGEMENT =====

@router.post("/", response_model=TenderResponse, status_code=status.HTTP_201_CREATED)
def create_tender(
    tender_data: TenderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new tender"""
    # Generate tender number
    year = datetime.now().year
    prefix = f"TND/{year}/"
    
    last_tender = db.query(Tender).filter(
        Tender.temple_id == current_user.temple_id,
        Tender.tender_number.like(f"{prefix}%")
    ).order_by(Tender.id.desc()).first()
    
    if last_tender:
        try:
            last_num = int(last_tender.tender_number.split('/')[-1])
            new_num = last_num + 1
        except:
            new_num = 1
    else:
        new_num = 1
    
    tender_number = f"{prefix}{new_num:04d}"
    
    # Create tender
    tender = Tender(
        temple_id=current_user.temple_id,
        tender_number=tender_number,
        title=tender_data.title,
        description=tender_data.description,
        tender_type=tender_data.tender_type,
        estimated_value=tender_data.estimated_value,
        tender_issue_date=tender_data.tender_issue_date,
        last_date_submission=tender_data.last_date_submission,
        opening_date=tender_data.opening_date,
        terms_conditions=tender_data.terms_conditions,
        status="draft",
        created_by=current_user.id
    )
    
    db.add(tender)
    db.commit()
    db.refresh(tender)
    
    # Audit log
    log_action(
        db=db,
        user=current_user,
        action="CREATE_TENDER",
        entity_type="Tender",
        entity_id=tender.id,
        new_values=get_entity_dict(tender),
        description=f"Created tender: {tender.tender_number} - {tender.title}"
    )
    
    return tender


@router.get("/", response_model=List[TenderResponse])
def list_tenders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
    tender_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of tenders"""
    query = db.query(Tender).filter(
        Tender.temple_id == current_user.temple_id
    )
    
    if status_filter:
        query = query.filter(Tender.status == status_filter)
    
    if tender_type:
        query = query.filter(Tender.tender_type == tender_type)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Tender.title.ilike(search_filter),
                Tender.tender_number.ilike(search_filter),
                Tender.description.ilike(search_filter)
            )
        )
    
    tenders = query.order_by(Tender.tender_issue_date.desc()).offset(skip).limit(limit).all()
    
    # Add bids count
    result = []
    for tender in tenders:
        tender_dict = {
            **{k: v for k, v in tender.__dict__.items() if not k.startswith('_')},
            'bids_count': db.query(TenderBid).filter(TenderBid.tender_id == tender.id).count()
        }
        result.append(TenderResponse(**tender_dict))
    
    return result


@router.get("/{tender_id}", response_model=TenderResponse)
def get_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tender details"""
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.temple_id == current_user.temple_id
    ).first()
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    tender_dict = {
        **{k: v for k, v in tender.__dict__.items() if not k.startswith('_')},
        'bids_count': db.query(TenderBid).filter(TenderBid.tender_id == tender.id).count()
    }
    
    return TenderResponse(**tender_dict)


@router.put("/{tender_id}", response_model=TenderResponse)
def update_tender(
    tender_id: int,
    tender_data: TenderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update tender"""
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.temple_id == current_user.temple_id
    ).first()
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    # Update fields
    update_data = tender_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tender, field, value)
    
    tender.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(tender)
    
    # Audit log
    log_action(
        db=db,
        user=current_user,
        action="UPDATE_TENDER",
        entity_type="Tender",
        entity_id=tender.id,
        new_values=update_data,
        description=f"Updated tender: {tender.tender_number}"
    )
    
    tender_dict = {
        **{k: v for k, v in tender.__dict__.items() if not k.startswith('_')},
        'bids_count': db.query(TenderBid).filter(TenderBid.tender_id == tender.id).count()
    }
    
    return TenderResponse(**tender_dict)


@router.post("/{tender_id}/publish", response_model=TenderResponse)
def publish_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publish tender (change status to published)"""
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.temple_id == current_user.temple_id
    ).first()
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    if tender.status != "draft":
        raise HTTPException(status_code=400, detail=f"Cannot publish tender with status: {tender.status}")
    
    tender.status = "published"
    tender.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(tender)
    
    log_action(
        db=db,
        user=current_user,
        action="PUBLISH_TENDER",
        entity_type="Tender",
        entity_id=tender.id,
        description=f"Published tender: {tender.tender_number}"
    )
    
    tender_dict = {
        **{k: v for k, v in tender.__dict__.items() if not k.startswith('_')},
        'bids_count': db.query(TenderBid).filter(TenderBid.tender_id == tender.id).count()
    }
    
    return TenderResponse(**tender_dict)


@router.post("/{tender_id}/close", response_model=TenderResponse)
def close_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close tender (change status to closed)"""
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.temple_id == current_user.temple_id
    ).first()
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    tender.status = "closed"
    tender.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(tender)
    
    log_action(
        db=db,
        user=current_user,
        action="CLOSE_TENDER",
        entity_type="Tender",
        entity_id=tender.id,
        description=f"Closed tender: {tender.tender_number}"
    )
    
    tender_dict = {
        **{k: v for k, v in tender.__dict__.items() if not k.startswith('_')},
        'bids_count': db.query(TenderBid).filter(TenderBid.tender_id == tender.id).count()
    }
    
    return TenderResponse(**tender_dict)


# ===== TENDER BID MANAGEMENT =====

@router.post("/{tender_id}/bids", response_model=TenderBidResponse, status_code=status.HTTP_201_CREATED)
def submit_bid(
    tender_id: int,
    bid_data: TenderBidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a bid for a tender"""
    # Verify tender exists and is published
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.temple_id == current_user.temple_id
    ).first()
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    if tender.status != "published":
        raise HTTPException(status_code=400, detail=f"Cannot submit bid. Tender status is: {tender.status}")
    
    if tender.last_date_submission < date.today():
        raise HTTPException(status_code=400, detail="Tender submission deadline has passed")
    
    # Verify vendor exists
    vendor = db.query(Vendor).filter(
        Vendor.id == bid_data.vendor_id,
        Vendor.temple_id == current_user.temple_id
    ).first()
    
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Check if vendor already submitted a bid
    existing_bid = db.query(TenderBid).filter(
        TenderBid.tender_id == tender_id,
        TenderBid.vendor_id == bid_data.vendor_id
    ).first()
    
    if existing_bid:
        raise HTTPException(status_code=400, detail="Vendor has already submitted a bid for this tender")
    
    # Create bid
    bid = TenderBid(
        tender_id=tender_id,
        vendor_id=bid_data.vendor_id,
        bid_amount=bid_data.bid_amount,
        bid_date=bid_data.bid_date,
        validity_period_days=bid_data.validity_period_days,
        technical_specifications=bid_data.technical_specifications,
        status="submitted"
    )
    
    db.add(bid)
    db.commit()
    db.refresh(bid)
    
    # Add vendor name to response
    bid_dict = {
        **{k: v for k, v in bid.__dict__.items() if not k.startswith('_')},
        'vendor_name': vendor.name
    }
    
    log_action(
        db=db,
        user=current_user,
        action="SUBMIT_TENDER_BID",
        entity_type="TenderBid",
        entity_id=bid.id,
        new_values=get_entity_dict(bid),
        description=f"Submitted bid for tender {tender.tender_number} from vendor {vendor.name}"
    )
    
    return TenderBidResponse(**bid_dict)


@router.get("/{tender_id}/bids", response_model=List[TenderBidResponse])
def list_tender_bids(
    tender_id: int,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of bids for a tender"""
    # Verify tender exists
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.temple_id == current_user.temple_id
    ).first()
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    query = db.query(TenderBid).filter(TenderBid.tender_id == tender_id)
    
    if status_filter:
        query = query.filter(TenderBid.status == status_filter)
    
    bids = query.order_by(TenderBid.bid_amount.asc()).all()
    
    # Add vendor names
    result = []
    for bid in bids:
        vendor = db.query(Vendor).filter(Vendor.id == bid.vendor_id).first()
        bid_dict = {
            **{k: v for k, v in bid.__dict__.items() if not k.startswith('_')},
            'vendor_name': vendor.name if vendor else None
        }
        result.append(TenderBidResponse(**bid_dict))
    
    return result


@router.get("/{tender_id}/bids/{bid_id}", response_model=TenderBidResponse)
def get_tender_bid(
    tender_id: int,
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tender bid details"""
    # Verify tender exists
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.temple_id == current_user.temple_id
    ).first()
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    bid = db.query(TenderBid).filter(
        TenderBid.id == bid_id,
        TenderBid.tender_id == tender_id
    ).first()
    
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    vendor = db.query(Vendor).filter(Vendor.id == bid.vendor_id).first()
    bid_dict = {
        **{k: v for k, v in bid.__dict__.items() if not k.startswith('_')},
        'vendor_name': vendor.name if vendor else None
    }
    
    return TenderBidResponse(**bid_dict)


@router.put("/{tender_id}/bids/{bid_id}", response_model=TenderBidResponse)
def update_tender_bid(
    tender_id: int,
    bid_id: int,
    bid_data: TenderBidUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update tender bid (for evaluation)"""
    # Verify tender exists
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.temple_id == current_user.temple_id
    ).first()
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    bid = db.query(TenderBid).filter(
        TenderBid.id == bid_id,
        TenderBid.tender_id == tender_id
    ).first()
    
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    # Update fields
    update_data = bid_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bid, field, value)
    
    # If scores are provided, calculate total score
    if bid.technical_score is not None and bid.financial_score is not None:
        # Weighted average: 40% technical, 60% financial
        bid.total_score = (bid.technical_score * 0.4) + (bid.financial_score * 0.6)
    
    if 'technical_score' in update_data or 'financial_score' in update_data:
        bid.evaluated_at = datetime.utcnow()
        bid.evaluated_by = current_user.id
    
    db.commit()
    db.refresh(bid)
    
    vendor = db.query(Vendor).filter(Vendor.id == bid.vendor_id).first()
    bid_dict = {
        **{k: v for k, v in bid.__dict__.items() if not k.startswith('_')},
        'vendor_name': vendor.name if vendor else None
    }
    
    log_action(
        db=db,
        user=current_user,
        action="UPDATE_TENDER_BID",
        entity_type="TenderBid",
        entity_id=bid.id,
        new_values=update_data,
        description=f"Updated bid evaluation for tender {tender.tender_number}"
    )
    
    return TenderBidResponse(**bid_dict)


@router.post("/{tender_id}/bids/{bid_id}/evaluate", response_model=TenderBidResponse)
def evaluate_bid(
    tender_id: int,
    bid_id: int,
    evaluation: TenderEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Evaluate a tender bid"""
    if bid_id != evaluation.bid_id:
        raise HTTPException(status_code=400, detail="Bid ID mismatch")
    
    # Verify tender exists
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.temple_id == current_user.temple_id
    ).first()
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    bid = db.query(TenderBid).filter(
        TenderBid.id == bid_id,
        TenderBid.tender_id == tender_id
    ).first()
    
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    # Update evaluation
    bid.technical_score = evaluation.technical_score
    bid.financial_score = evaluation.financial_score
    bid.total_score = (evaluation.technical_score * 0.4) + (evaluation.financial_score * 0.6)
    bid.evaluation_notes = evaluation.evaluation_notes
    bid.evaluated_at = datetime.utcnow()
    bid.evaluated_by = current_user.id
    
    db.commit()
    db.refresh(bid)
    
    vendor = db.query(Vendor).filter(Vendor.id == bid.vendor_id).first()
    bid_dict = {
        **{k: v for k, v in bid.__dict__.items() if not k.startswith('_')},
        'vendor_name': vendor.name if vendor else None
    }
    
    log_action(
        db=db,
        user=current_user,
        action="EVALUATE_TENDER_BID",
        entity_type="TenderBid",
        entity_id=bid.id,
        description=f"Evaluated bid for tender {tender.tender_number}: Technical={evaluation.technical_score}, Financial={evaluation.financial_score}"
    )
    
    return TenderBidResponse(**bid_dict)


@router.post("/{tender_id}/award", response_model=TenderResponse)
def award_tender(
    tender_id: int,
    award_data: TenderAwardRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Award tender to a bid"""
    # Verify tender exists
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.temple_id == current_user.temple_id
    ).first()
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    if tender.status == "awarded":
        raise HTTPException(status_code=400, detail="Tender has already been awarded")
    
    # Verify bid exists and belongs to this tender
    bid = db.query(TenderBid).filter(
        TenderBid.id == award_data.bid_id,
        TenderBid.tender_id == tender_id
    ).first()
    
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    # Update bid status to awarded
    bid.status = "awarded"
    bid.evaluated_at = datetime.utcnow()
    bid.evaluated_by = current_user.id
    
    # Update all other bids to rejected
    db.query(TenderBid).filter(
        TenderBid.tender_id == tender_id,
        TenderBid.id != award_data.bid_id
    ).update({"status": "rejected"})
    
    # Update tender status
    tender.status = "awarded"
    tender.award_date = award_data.award_date
    tender.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(tender)
    
    log_action(
        db=db,
        user=current_user,
        action="AWARD_TENDER",
        entity_type="Tender",
        entity_id=tender.id,
        description=f"Awarded tender {tender.tender_number} to bid {award_data.bid_id}"
    )
    
    tender_dict = {
        **{k: v for k, v in tender.__dict__.items() if not k.startswith('_')},
        'bids_count': db.query(TenderBid).filter(TenderBid.tender_id == tender.id).count()
    }
    
    return TenderResponse(**tender_dict)

