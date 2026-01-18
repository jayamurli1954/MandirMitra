"""
Tender Management API
Handles tender creation, bid submission, evaluation, and award workflow
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.asset import Tender, TenderBid
from app.models.vendor import Vendor

router = APIRouter(prefix="/api/v1/tenders", tags=["tenders"])


# ===== ENUMS =====


class TenderStatus(str):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class TenderType(str):
    ASSET_PROCUREMENT = "asset_procurement"
    INVENTORY_PURCHASE = "inventory_purchase"
    CONSTRUCTION = "construction"
    SERVICE = "service"


class BidStatus(str):
    SUBMITTED = "submitted"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    AWARDED = "awarded"


# ===== SCHEMAS =====


class TenderBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    tender_type: str = Field(
        ..., description="asset_procurement, inventory_purchase, construction, service"
    )
    estimated_value: float = Field(0.0, ge=0)
    tender_issue_date: date
    last_date_submission: date
    opening_date: Optional[date] = None
    terms_conditions: Optional[str] = None


class TenderCreate(TenderBase):
    pass


class TenderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_value: Optional[float] = None
    last_date_submission: Optional[date] = None
    opening_date: Optional[date] = None
    terms_conditions: Optional[str] = None
    status: Optional[str] = None


class TenderBidResponse(BaseModel):
    id: int
    tender_id: int
    vendor_id: int
    vendor_name: str
    bid_amount: float
    bid_date: date
    validity_period_days: int
    status: str
    technical_score: Optional[float]
    financial_score: Optional[float]
    total_score: Optional[float]
    evaluation_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TenderResponse(BaseModel):
    id: int
    temple_id: Optional[int]
    tender_number: str
    title: str
    description: Optional[str]
    tender_type: str
    estimated_value: float
    tender_issue_date: date
    last_date_submission: date
    opening_date: Optional[date]
    award_date: Optional[date]
    status: str
    tender_document_path: Optional[str]
    terms_conditions: Optional[str]
    total_bids: int
    bids: List[TenderBidResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenderBidCreate(BaseModel):
    vendor_id: int
    bid_amount: float = Field(..., gt=0)
    bid_date: date
    validity_period_days: int = Field(90, ge=1, le=365)
    technical_specifications: Optional[str] = None


class TenderBidEvaluation(BaseModel):
    technical_score: float = Field(..., ge=0, le=100)
    financial_score: float = Field(..., ge=0, le=100)
    evaluation_notes: Optional[str] = None
    status: str = Field(..., description="shortlisted, rejected, awarded")


class BidComparisonResponse(BaseModel):
    tender_id: int
    tender_title: str
    total_bids: int
    lowest_bid: Optional[float]
    highest_bid: Optional[float]
    average_bid: Optional[float]
    best_technical_score: Optional[float]
    best_financial_score: Optional[float]
    recommended_bid_id: Optional[int]
    recommended_vendor: Optional[str]
    comparison_details: List[dict] = []


# ===== TENDER ENDPOINTS =====


@router.post("/", response_model=TenderResponse, status_code=status.HTTP_201_CREATED)
def create_tender(
    tender_data: TenderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new tender"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(
            status_code=403, detail="Only admins and accountants can create tenders"
        )

    # Validate dates
    if tender_data.last_date_submission <= tender_data.tender_issue_date:
        raise HTTPException(
            status_code=400, detail="Last date for submission must be after tender issue date"
        )

    # Generate tender number
    year = tender_data.tender_issue_date.year
    prefix = f"TND/{year}/"
    last_tender = (
        db.query(Tender)
        .filter(Tender.tender_number.like(f"{prefix}%"))
        .order_by(Tender.id.desc())
        .first()
    )

    new_num = 1
    if last_tender:
        try:
            last_num = int(last_tender.tender_number.split("/")[-1])
            new_num = last_num + 1
        except:
            pass

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
        created_by=current_user.id,
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)

    return _enrich_tender_response(tender, db)


@router.get("/", response_model=List[TenderResponse])
def list_tenders(
    status: Optional[str] = Query(None),
    tender_type: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all tenders"""
    query = db.query(Tender).filter(Tender.temple_id == current_user.temple_id)

    if status:
        query = query.filter(Tender.status == status)
    if tender_type:
        query = query.filter(Tender.tender_type == tender_type)
    if from_date:
        query = query.filter(Tender.tender_issue_date >= from_date)
    if to_date:
        query = query.filter(Tender.tender_issue_date <= to_date)

    tenders = query.order_by(Tender.tender_issue_date.desc()).all()
    return [_enrich_tender_response(t, db) for t in tenders]


@router.get("/{tender_id}", response_model=TenderResponse)
def get_tender(
    tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get tender details"""
    tender = (
        db.query(Tender)
        .filter(Tender.id == tender_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    return _enrich_tender_response(tender, db)


@router.put("/{tender_id}", response_model=TenderResponse)
def update_tender(
    tender_id: int,
    tender_data: TenderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a tender"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(
            status_code=403, detail="Only admins and accountants can update tenders"
        )

    tender = (
        db.query(Tender)
        .filter(Tender.id == tender_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    if tender.status == "awarded":
        raise HTTPException(status_code=400, detail="Cannot update awarded tender")

    # Update fields
    for key, value in tender_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(tender, key, value)

    tender.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tender)

    return _enrich_tender_response(tender, db)


@router.post("/{tender_id}/publish", response_model=TenderResponse)
def publish_tender(
    tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Publish a tender (change status from draft to published)"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(
            status_code=403, detail="Only admins and accountants can publish tenders"
        )

    tender = (
        db.query(Tender)
        .filter(Tender.id == tender_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    if tender.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft tenders can be published")

    tender.status = "published"
    tender.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tender)

    # Send email notifications to vendors
    from app.api.tender_notifications import send_tender_published_notification

    send_tender_published_notification(tender, db)

    return _enrich_tender_response(tender, db)


@router.post("/{tender_id}/close", response_model=TenderResponse)
def close_tender(
    tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Close a tender (stop accepting bids)"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can close tenders")

    tender = (
        db.query(Tender)
        .filter(Tender.id == tender_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    if tender.status not in ["published", "draft"]:
        raise HTTPException(status_code=400, detail="Only published or draft tenders can be closed")

    tender.status = "closed"
    tender.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tender)

    return _enrich_tender_response(tender, db)


@router.post("/{tender_id}/documents", response_model=dict)
async def upload_tender_document(
    tender_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload tender document"""
    tender = (
        db.query(Tender)
        .filter(Tender.id == tender_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    # In production, save file to storage (S3, local filesystem, etc.)
    # For now, create placeholder path
    file_path = f"/uploads/tenders/{tender_id}/{file.filename}"

    tender.tender_document_path = file_path
    tender.updated_at = datetime.utcnow()
    db.commit()

    return {
        "tender_id": tender_id,
        "document_path": file_path,
        "filename": file.filename,
        "uploaded_at": datetime.utcnow(),
    }


# ===== BID ENDPOINTS =====


@router.post(
    "/{tender_id}/bids", response_model=TenderBidResponse, status_code=status.HTTP_201_CREATED
)
def submit_bid(
    tender_id: int,
    bid_data: TenderBidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a bid for a tender"""
    tender = (
        db.query(Tender)
        .filter(Tender.id == tender_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    if tender.status != "published":
        raise HTTPException(
            status_code=400, detail="Bids can only be submitted for published tenders"
        )

    if date.today() > tender.last_date_submission:
        raise HTTPException(status_code=400, detail="Submission deadline has passed")

    # Check if vendor exists
    vendor = db.query(Vendor).filter(Vendor.id == bid_data.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Check if vendor already submitted a bid
    existing_bid = (
        db.query(TenderBid)
        .filter(TenderBid.tender_id == tender_id, TenderBid.vendor_id == bid_data.vendor_id)
        .first()
    )

    if existing_bid:
        raise HTTPException(
            status_code=400, detail="Vendor has already submitted a bid for this tender"
        )

    # Create bid
    bid = TenderBid(
        tender_id=tender_id,
        vendor_id=bid_data.vendor_id,
        bid_amount=bid_data.bid_amount,
        bid_date=bid_data.bid_date,
        validity_period_days=bid_data.validity_period_days,
        technical_specifications=bid_data.technical_specifications,
        status="submitted",
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)

    # Send confirmation email to vendor
    from app.api.tender_notifications import send_bid_submission_confirmation

    send_bid_submission_confirmation(bid, tender, vendor, db)

    return _enrich_bid_response(bid, db)


@router.get("/{tender_id}/bids", response_model=List[TenderBidResponse])
def get_tender_bids(
    tender_id: int,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all bids for a tender"""
    tender = (
        db.query(Tender)
        .filter(Tender.id == tender_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    query = db.query(TenderBid).filter(TenderBid.tender_id == tender_id)
    if status:
        query = query.filter(TenderBid.status == status)

    bids = query.order_by(TenderBid.bid_amount.asc()).all()
    return [_enrich_bid_response(b, db) for b in bids]


@router.post("/bids/{bid_id}/evaluate", response_model=TenderBidResponse)
def evaluate_bid(
    bid_id: int,
    evaluation: TenderBidEvaluation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evaluate a bid (technical + financial scoring)"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can evaluate bids")

    bid = (
        db.query(TenderBid)
        .join(Tender)
        .filter(TenderBid.id == bid_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # Calculate total score (weighted: 40% technical, 60% financial)
    technical_weight = 0.4
    financial_weight = 0.6
    total_score = (evaluation.technical_score * technical_weight) + (
        evaluation.financial_score * financial_weight
    )

    # Update bid
    bid.technical_score = evaluation.technical_score
    bid.financial_score = evaluation.financial_score
    bid.total_score = total_score
    bid.evaluation_notes = evaluation.evaluation_notes
    bid.status = evaluation.status
    bid.evaluated_at = datetime.utcnow()
    bid.evaluated_by = current_user.id

    db.commit()
    db.refresh(bid)

    return _enrich_bid_response(bid, db)


@router.post("/bids/{bid_id}/documents", response_model=dict)
async def upload_bid_document(
    bid_id: int,
    file: UploadFile = File(...),
    document_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload bid document (technical proposal, financial proposal, certificates, etc.)"""
    bid = (
        db.query(TenderBid)
        .join(Tender)
        .filter(TenderBid.id == bid_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # In production, save file to storage
    import os
    from pathlib import Path

    # Create upload directory structure
    upload_dir = Path(f"uploads/tenders/bids/{bid_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = upload_dir / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Store relative path in database
    relative_path = f"/uploads/tenders/bids/{bid_id}/{file.filename}"

    # Update bid document path (could be enhanced to support multiple documents)
    bid.bid_document_path = relative_path
    db.commit()

    return {
        "bid_id": bid_id,
        "document_path": relative_path,
        "filename": file.filename,
        "file_size": len(content),
        "mime_type": file.content_type,
        "document_type": document_type or "main",
        "uploaded_at": datetime.utcnow(),
    }


@router.post("/{tender_id}/award", response_model=TenderResponse)
def award_tender(
    tender_id: int,
    bid_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Award tender to a bid"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can award tenders")

    tender = (
        db.query(Tender)
        .filter(Tender.id == tender_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    if tender.status != "closed":
        raise HTTPException(status_code=400, detail="Tender must be closed before awarding")

    bid = (
        db.query(TenderBid).filter(TenderBid.id == bid_id, TenderBid.tender_id == tender_id).first()
    )

    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # Update bid status
    bid.status = "awarded"

    # Update tender
    tender.status = "awarded"
    tender.award_date = date.today()
    tender.updated_at = datetime.utcnow()

    # Reject all other bids
    db.query(TenderBid).filter(
        TenderBid.tender_id == tender_id, TenderBid.id != bid_id, TenderBid.status != "rejected"
    ).update({"status": "rejected"})

    db.commit()
    db.refresh(tender)

    # Send email notification to awarded vendor
    from app.api.tender_notifications import send_tender_awarded_notification

    vendor = db.query(Vendor).filter(Vendor.id == bid.vendor_id).first()
    if vendor:
        send_tender_awarded_notification(tender, bid, vendor, db)

    # Send rejection notifications to other vendors
    from app.api.tender_notifications import send_bid_rejected_notification

    rejected_bids = (
        db.query(TenderBid)
        .filter(
            TenderBid.tender_id == tender_id, TenderBid.id != bid_id, TenderBid.status == "rejected"
        )
        .all()
    )
    for rejected_bid in rejected_bids:
        rejected_vendor = db.query(Vendor).filter(Vendor.id == rejected_bid.vendor_id).first()
        if rejected_vendor:
            send_bid_rejected_notification(
                rejected_bid, tender, rejected_vendor, "Another bid was selected", db
            )

    return _enrich_tender_response(tender, db)


# ===== BID COMPARISON ENDPOINTS =====


@router.get("/{tender_id}/compare-bids", response_model=BidComparisonResponse)
def compare_bids(
    tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Automated bid comparison for a tender"""
    tender = (
        db.query(Tender)
        .filter(Tender.id == tender_id, Tender.temple_id == current_user.temple_id)
        .first()
    )

    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    # Get all evaluated bids
    bids = (
        db.query(TenderBid)
        .filter(TenderBid.tender_id == tender_id, TenderBid.total_score.isnot(None))
        .order_by(TenderBid.total_score.desc())
        .all()
    )

    if not bids:
        return BidComparisonResponse(
            tender_id=tender_id,
            tender_title=tender.title,
            total_bids=0,
            lowest_bid=None,
            highest_bid=None,
            average_bid=None,
            best_technical_score=None,
            best_financial_score=None,
            recommended_bid_id=None,
            recommended_vendor=None,
            comparison_details=[],
        )

    # Calculate statistics
    bid_amounts = [b.bid_amount for b in bids]
    lowest_bid = min(bid_amounts)
    highest_bid = max(bid_amounts)
    average_bid = sum(bid_amounts) / len(bid_amounts)

    # Find best scores
    best_technical = max([b.technical_score for b in bids if b.technical_score], default=None)
    best_financial = max([b.financial_score for b in bids if b.financial_score], default=None)

    # Recommend bid with highest total score
    recommended_bid = bids[0] if bids else None
    recommended_vendor = None
    if recommended_bid:
        vendor = db.query(Vendor).filter(Vendor.id == recommended_bid.vendor_id).first()
        recommended_vendor = vendor.name if vendor else None

    # Create comparison details
    comparison_details = []
    for bid in bids:
        vendor = db.query(Vendor).filter(Vendor.id == bid.vendor_id).first()
        comparison_details.append(
            {
                "bid_id": bid.id,
                "vendor_name": vendor.name if vendor else "Unknown",
                "bid_amount": bid.bid_amount,
                "technical_score": bid.technical_score,
                "financial_score": bid.financial_score,
                "total_score": bid.total_score,
                "status": bid.status,
            }
        )

    return BidComparisonResponse(
        tender_id=tender_id,
        tender_title=tender.title,
        total_bids=len(bids),
        lowest_bid=lowest_bid,
        highest_bid=highest_bid,
        average_bid=average_bid,
        best_technical_score=best_technical,
        best_financial_score=best_financial,
        recommended_bid_id=recommended_bid.id if recommended_bid else None,
        recommended_vendor=recommended_vendor,
        comparison_details=comparison_details,
    )


# ===== HELPER FUNCTIONS =====


def _enrich_tender_response(tender: Tender, db: Session) -> TenderResponse:
    """Enrich tender response with related data"""
    bids = db.query(TenderBid).filter(TenderBid.tender_id == tender.id).all()
    bid_responses = [_enrich_bid_response(b, db) for b in bids]

    return TenderResponse(
        id=tender.id,
        temple_id=tender.temple_id,
        tender_number=tender.tender_number,
        title=tender.title,
        description=tender.description,
        tender_type=tender.tender_type,
        estimated_value=tender.estimated_value,
        tender_issue_date=tender.tender_issue_date,
        last_date_submission=tender.last_date_submission,
        opening_date=tender.opening_date,
        award_date=tender.award_date,
        status=tender.status,
        tender_document_path=tender.tender_document_path,
        terms_conditions=tender.terms_conditions,
        total_bids=len(bids),
        bids=bid_responses,
        created_at=tender.created_at,
        updated_at=tender.updated_at,
    )


def _enrich_bid_response(bid: TenderBid, db: Session) -> TenderBidResponse:
    """Enrich bid response with vendor data"""
    vendor = db.query(Vendor).filter(Vendor.id == bid.vendor_id).first()

    return TenderBidResponse(
        id=bid.id,
        tender_id=bid.tender_id,
        vendor_id=bid.vendor_id,
        vendor_name=vendor.name if vendor else "Unknown",
        bid_amount=bid.bid_amount,
        bid_date=bid.bid_date,
        validity_period_days=bid.validity_period_days,
        status=bid.status,
        technical_score=bid.technical_score,
        financial_score=bid.financial_score,
        total_score=bid.total_score,
        evaluation_notes=bid.evaluation_notes,
        created_at=bid.created_at,
    )
