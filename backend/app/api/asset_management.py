"""
Asset Management Advanced Features API
Handles asset transfer, valuation history, physical verification, insurance, and disposal workflow
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.asset import Asset, AssetDisposal, AssetRevaluation, DisposalType, AssetStatus
from app.models.asset_history import (
    AssetTransfer,
    AssetValuationHistory,
    AssetPhysicalVerification,
    AssetInsurance,
    AssetDocument,
    VerificationStatus,
)

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


# ===== SCHEMAS =====


class AssetTransferCreate(BaseModel):
    transfer_date: date
    to_location: str = Field(..., max_length=200)
    transfer_reason: Optional[str] = None
    notes: Optional[str] = None


class AssetTransferResponse(BaseModel):
    id: int
    asset_id: int
    asset_number: str
    asset_name: str
    transfer_date: date
    from_location: Optional[str]
    to_location: str
    transfer_reason: Optional[str]
    transferred_by: int
    transferred_by_name: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AssetValuationHistoryResponse(BaseModel):
    id: int
    asset_id: int
    valuation_date: date
    valuation_type: str
    valuation_amount: float
    valuation_method: Optional[str]
    valuer_name: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PhysicalVerificationCreate(BaseModel):
    verification_date: date
    verified_location: str = Field(..., max_length=200)
    condition: str = Field(..., max_length=50)  # GOOD, FAIR, POOR, DAMAGED
    condition_notes: Optional[str] = None
    verified_by_second: Optional[int] = None
    notes: Optional[str] = None


class PhysicalVerificationResponse(BaseModel):
    id: int
    verification_number: str
    verification_date: date
    asset_id: int
    asset_number: str
    asset_name: str
    status: VerificationStatus
    verified_location: str
    condition: str
    condition_notes: Optional[str]
    verified_by: int
    verified_by_name: Optional[str]
    verified_by_second: Optional[int]
    verified_by_second_name: Optional[str]
    approved_by: Optional[int]
    has_discrepancy: bool
    discrepancy_details: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AssetInsuranceCreate(BaseModel):
    policy_number: str = Field(..., max_length=100)
    insurance_company: str = Field(..., max_length=200)
    policy_start_date: date
    policy_end_date: date
    premium_amount: float = Field(0.0, ge=0)
    insured_value: float = Field(..., gt=0)
    coverage_type: Optional[str] = None
    coverage_details: Optional[str] = None
    auto_renewal: bool = False
    renewal_reminder_days: int = Field(30, ge=1, le=365)
    agent_name: Optional[str] = None
    agent_contact: Optional[str] = None
    notes: Optional[str] = None


class AssetInsuranceResponse(BaseModel):
    id: int
    asset_id: int
    asset_number: str
    asset_name: str
    policy_number: str
    insurance_company: str
    policy_start_date: date
    policy_end_date: date
    days_until_expiry: int
    premium_amount: float
    insured_value: float
    coverage_type: Optional[str]
    is_active: bool
    auto_renewal: bool
    renewal_reminder_days: int
    agent_name: Optional[str]
    agent_contact: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AssetDisposalRequest(BaseModel):
    disposal_date: date
    disposal_type: DisposalType
    disposal_reason: str = Field(..., min_length=1)
    disposal_proceeds: float = Field(0.0, ge=0)
    buyer_name: Optional[str] = None
    disposal_document_number: Optional[str] = None
    notes: Optional[str] = None


class AssetDisposalResponse(BaseModel):
    id: int
    asset_id: int
    asset_number: str
    asset_name: str
    disposal_date: date
    disposal_type: DisposalType
    disposal_reason: str
    book_value_at_disposal: float
    accumulated_depreciation_at_disposal: float
    disposal_proceeds: float
    gain_loss_amount: float
    buyer_name: Optional[str]
    disposal_document_number: Optional[str]
    status: str  # pending, approved, rejected
    requested_by: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== ASSET TRANSFER ENDPOINTS =====


@router.post("/{asset_id}/transfer", response_model=AssetTransferResponse, status_code=201)
def transfer_asset(
    asset_id: int,
    transfer_data: AssetTransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Transfer asset to a new location"""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.status != AssetStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Only active assets can be transferred")

    # Get current location
    from_location = asset.location

    # Create transfer record
    transfer = AssetTransfer(
        temple_id=current_user.temple_id,
        asset_id=asset_id,
        transfer_date=transfer_data.transfer_date,
        from_location=from_location,
        to_location=transfer_data.to_location,
        transfer_reason=transfer_data.transfer_reason,
        transferred_by=current_user.id,
        notes=transfer_data.notes,
    )
    db.add(transfer)

    # Update asset location
    asset.location = transfer_data.to_location
    asset.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(transfer)

    return _enrich_transfer_response(transfer, db)


@router.get("/{asset_id}/transfers", response_model=List[AssetTransferResponse])
def get_asset_transfers(
    asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get transfer history for an asset"""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    transfers = (
        db.query(AssetTransfer)
        .filter(AssetTransfer.asset_id == asset_id)
        .order_by(AssetTransfer.transfer_date.desc())
        .all()
    )

    return [_enrich_transfer_response(t, db) for t in transfers]


# ===== VALUATION HISTORY ENDPOINTS =====


@router.get("/{asset_id}/valuation-history", response_model=List[AssetValuationHistoryResponse])
def get_asset_valuation_history(
    asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get valuation history for an asset"""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Get from valuation history table
    history = (
        db.query(AssetValuationHistory)
        .filter(AssetValuationHistory.asset_id == asset_id)
        .order_by(AssetValuationHistory.valuation_date.desc())
        .all()
    )

    # Also include purchase as initial valuation
    purchase_valuation = AssetValuationHistoryResponse(
        id=0,
        asset_id=asset_id,
        valuation_date=asset.purchase_date,
        valuation_type="PURCHASE",
        valuation_amount=asset.original_cost,
        valuation_method="COST_BASED",
        valuer_name=None,
        notes="Initial purchase",
        created_at=asset.created_at,
    )

    result = [purchase_valuation]
    result.extend(
        [
            AssetValuationHistoryResponse(
                id=h.id,
                asset_id=h.asset_id,
                valuation_date=h.valuation_date,
                valuation_type=h.valuation_type,
                valuation_amount=h.valuation_amount,
                valuation_method=h.valuation_method,
                valuer_name=h.valuer_name,
                notes=h.notes,
                created_at=h.created_at,
            )
            for h in history
        ]
    )

    return result


# ===== PHYSICAL VERIFICATION ENDPOINTS =====


@router.post(
    "/{asset_id}/physical-verification",
    response_model=PhysicalVerificationResponse,
    status_code=201,
)
def create_physical_verification(
    asset_id: int,
    verification_data: PhysicalVerificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create physical verification record"""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Generate verification number
    year = verification_data.verification_date.year
    prefix = f"VER/{year}/"
    last_verification = (
        db.query(AssetPhysicalVerification)
        .filter(AssetPhysicalVerification.verification_number.like(f"{prefix}%"))
        .order_by(AssetPhysicalVerification.id.desc())
        .first()
    )

    new_num = 1
    if last_verification:
        try:
            last_num = int(last_verification.verification_number.split("/")[-1])
            new_num = last_num + 1
        except:
            pass

    verification_number = f"{prefix}{new_num:04d}"

    # Check for discrepancies
    has_discrepancy = False
    discrepancy_details = None
    if verification_data.verified_location != asset.location:
        has_discrepancy = True
        discrepancy_details = f"Location mismatch: Expected {asset.location}, Found {verification_data.verified_location}"

    status = VerificationStatus.VERIFIED
    if has_discrepancy:
        status = VerificationStatus.DISCREPANCY

    # Create verification
    verification = AssetPhysicalVerification(
        temple_id=current_user.temple_id,
        asset_id=asset_id,
        verification_number=verification_number,
        verification_date=verification_data.verification_date,
        status=status,
        verified_location=verification_data.verified_location,
        condition=verification_data.condition,
        condition_notes=verification_data.condition_notes,
        verified_by=current_user.id,
        verified_by_second=verification_data.verified_by_second,
        has_discrepancy=has_discrepancy,
        discrepancy_details=discrepancy_details,
        verified_at=datetime.utcnow(),
        notes=verification_data.notes,
    )
    db.add(verification)

    # Update asset location if verified and different
    if not has_discrepancy and verification_data.verified_location != asset.location:
        asset.location = verification_data.verified_location
        asset.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(verification)

    return _enrich_verification_response(verification, db)


@router.get("/{asset_id}/physical-verifications", response_model=List[PhysicalVerificationResponse])
def get_physical_verifications(
    asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get physical verification history for an asset"""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    verifications = (
        db.query(AssetPhysicalVerification)
        .filter(AssetPhysicalVerification.asset_id == asset_id)
        .order_by(AssetPhysicalVerification.verification_date.desc())
        .all()
    )

    return [_enrich_verification_response(v, db) for v in verifications]


# ===== INSURANCE ENDPOINTS =====


@router.post("/{asset_id}/insurance", response_model=AssetInsuranceResponse, status_code=201)
def add_asset_insurance(
    asset_id: int,
    insurance_data: AssetInsuranceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add insurance record for an asset"""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Check if active policy already exists
    existing = (
        db.query(AssetInsurance)
        .filter(
            AssetInsurance.asset_id == asset_id,
            AssetInsurance.is_active == True,
            AssetInsurance.policy_end_date >= date.today(),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Active insurance policy already exists (Policy: {existing.policy_number}, Expires: {existing.policy_end_date})",
        )

    # Create insurance record
    insurance = AssetInsurance(
        temple_id=current_user.temple_id,
        asset_id=asset_id,
        policy_number=insurance_data.policy_number,
        insurance_company=insurance_data.insurance_company,
        policy_start_date=insurance_data.policy_start_date,
        policy_end_date=insurance_data.policy_end_date,
        premium_amount=insurance_data.premium_amount,
        insured_value=insurance_data.insured_value,
        coverage_type=insurance_data.coverage_type,
        coverage_details=insurance_data.coverage_details,
        auto_renewal=insurance_data.auto_renewal,
        renewal_reminder_days=insurance_data.renewal_reminder_days,
        agent_name=insurance_data.agent_name,
        agent_contact=insurance_data.agent_contact,
        created_by=current_user.id,
    )
    db.add(insurance)
    db.commit()
    db.refresh(insurance)

    return _enrich_insurance_response(insurance, db)


@router.get("/{asset_id}/insurance", response_model=List[AssetInsuranceResponse])
def get_asset_insurance(
    asset_id: int,
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get insurance records for an asset"""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    query = db.query(AssetInsurance).filter(AssetInsurance.asset_id == asset_id)
    if is_active is not None:
        query = query.filter(AssetInsurance.is_active == is_active)

    insurances = query.order_by(AssetInsurance.policy_end_date.desc()).all()
    return [_enrich_insurance_response(i, db) for i in insurances]


@router.get("/insurance/expiring", response_model=List[AssetInsuranceResponse])
def get_expiring_insurance(
    days_ahead: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get insurance policies expiring within specified days"""
    today = date.today()
    expiry_threshold = today + timedelta(days=days_ahead)

    insurances = (
        db.query(AssetInsurance)
        .filter(
            AssetInsurance.temple_id == current_user.temple_id,
            AssetInsurance.is_active == True,
            AssetInsurance.policy_end_date >= today,
            AssetInsurance.policy_end_date <= expiry_threshold,
        )
        .order_by(AssetInsurance.policy_end_date)
        .all()
    )

    return [_enrich_insurance_response(i, db) for i in insurances]


# ===== DISPOSAL WORKFLOW ENDPOINTS =====


@router.post("/{asset_id}/dispose", response_model=AssetDisposalResponse, status_code=201)
def request_asset_disposal(
    asset_id: int,
    disposal_data: AssetDisposalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request asset disposal (requires approval)"""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if (
        asset.status == AssetStatus.DISPOSED
        or asset.status == AssetStatus.SOLD
        or asset.status == AssetStatus.SCRAPPED
    ):
        raise HTTPException(status_code=400, detail="Asset is already disposed")

    # Check if disposal already exists
    existing = (
        db.query(AssetDisposal)
        .join(Asset)
        .filter(AssetDisposal.asset_id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Disposal request already exists for this asset"
        )

    # Calculate gain/loss
    book_value = asset.current_book_value
    gain_loss = disposal_data.disposal_proceeds - book_value

    # Create disposal record
    disposal = AssetDisposal(
        asset_id=asset_id,
        disposal_date=disposal_data.disposal_date,
        disposal_type=disposal_data.disposal_type,
        disposal_reason=disposal_data.disposal_reason,
        book_value_at_disposal=book_value,
        accumulated_depreciation_at_disposal=asset.accumulated_depreciation,
        disposal_proceeds=disposal_data.disposal_proceeds,
        gain_loss_amount=gain_loss,
        buyer_name=disposal_data.buyer_name,
        disposal_document_number=disposal_data.disposal_document_number,
        created_by=current_user.id,
    )
    db.add(disposal)

    # Update asset status to pending disposal (we'll add this status if needed)
    # For now, keep asset as ACTIVE until approved

    db.commit()
    db.refresh(disposal)

    return _enrich_disposal_response(disposal, db, current_user.temple_id)


@router.post("/disposals/{disposal_id}/approve", response_model=AssetDisposalResponse)
def approve_asset_disposal(
    disposal_id: int,
    approve: bool = Query(True),
    rejection_reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve or reject asset disposal"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(
            status_code=403, detail="Only admins and accountants can approve disposals"
        )

    disposal = (
        db.query(AssetDisposal)
        .join(Asset)
        .filter(AssetDisposal.id == disposal_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not disposal:
        raise HTTPException(status_code=404, detail="Disposal request not found")

    asset = db.query(Asset).filter(Asset.id == disposal.asset_id).first()

    if approve:
        # Update asset status
        if disposal.disposal_type == DisposalType.SALE:
            asset.status = AssetStatus.SOLD
        elif disposal.disposal_type == DisposalType.SCRAP:
            asset.status = AssetStatus.SCRAPPED
        elif disposal.disposal_type == DisposalType.DONATION:
            asset.status = AssetStatus.DONATED
        else:
            asset.status = AssetStatus.DISPOSED

        asset.updated_at = datetime.utcnow()

        # Update disposal approval
        disposal.approved_by = current_user.id
        disposal.approved_at = datetime.utcnow()
        disposal.rejection_reason = None

        # Create journal entry for disposal
        # Dr: Accumulated Depreciation, Dr: Cash/Receivables (if proceeds), Dr: Loss (if loss)
        # Cr: Asset Account, Cr: Gain (if gain)
        # This would be implemented similar to other accounting integrations

        # Add to valuation history
        valuation_history = AssetValuationHistory(
            asset_id=asset.id,
            valuation_date=disposal.disposal_date,
            valuation_type="DISPOSAL",
            valuation_amount=disposal.disposal_proceeds,
            valuation_method="DISPOSAL_PROCEEDS",
            reference_id=disposal.id,
            reference_type="disposal",
            notes=f"Disposal - {disposal.disposal_type.value}",
        )
        db.add(valuation_history)
    else:
        # Rejection - just mark it, asset remains active
        if not rejection_reason:
            raise HTTPException(status_code=400, detail="Rejection reason is required")

        disposal.rejection_reason = rejection_reason
        disposal.approved_by = None
        disposal.approved_at = None

    db.commit()
    db.refresh(disposal)

    return _enrich_disposal_response(disposal, db, current_user.temple_id)


@router.get("/disposals", response_model=List[AssetDisposalResponse])
def get_asset_disposals(
    asset_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get asset disposal records"""
    query = db.query(AssetDisposal).join(Asset).filter(Asset.temple_id == current_user.temple_id)

    if asset_id:
        query = query.filter(AssetDisposal.asset_id == asset_id)
    if from_date:
        query = query.filter(AssetDisposal.disposal_date >= from_date)
    if to_date:
        query = query.filter(AssetDisposal.disposal_date <= to_date)

    disposals = query.order_by(AssetDisposal.disposal_date.desc()).all()
    return [_enrich_disposal_response(d, db, current_user.temple_id) for d in disposals]


# ===== DOCUMENT UPLOAD ENDPOINTS =====


@router.post("/{asset_id}/documents", response_model=dict)
async def upload_asset_document(
    asset_id: int,
    document_type: str = Query(
        ..., description="IMAGE, INVOICE, WARRANTY, MANUAL, CERTIFICATE, OTHER"
    ),
    file: UploadFile = File(...),
    description: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload document/image for an asset"""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # In production, you would:
    # 1. Save file to storage (S3, local filesystem, etc.)
    # 2. Get file URL
    # 3. Store metadata in database

    # For now, we'll create a placeholder
    file_url = f"/uploads/assets/{asset_id}/{file.filename}"  # Placeholder
    file_size = 0  # Would get from uploaded file
    mime_type = file.content_type or "application/octet-stream"

    document = AssetDocument(
        asset_id=asset_id,
        document_type=document_type.upper(),
        document_name=file.filename,
        file_url=file_url,
        file_size=file_size,
        mime_type=mime_type,
        description=description,
        uploaded_by=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "id": document.id,
        "document_type": document.document_type,
        "document_name": document.document_name,
        "file_url": document.file_url,
        "uploaded_at": document.uploaded_at,
    }


@router.get("/{asset_id}/documents", response_model=List[dict])
def get_asset_documents(
    asset_id: int,
    document_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get documents for an asset"""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.temple_id == current_user.temple_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    query = db.query(AssetDocument).filter(AssetDocument.asset_id == asset_id)
    if document_type:
        query = query.filter(AssetDocument.document_type == document_type.upper())

    documents = query.order_by(AssetDocument.uploaded_at.desc()).all()

    return [
        {
            "id": d.id,
            "document_type": d.document_type,
            "document_name": d.document_name,
            "file_url": d.file_url,
            "file_size": d.file_size,
            "mime_type": d.mime_type,
            "description": d.description,
            "uploaded_at": d.uploaded_at,
            "uploaded_by": d.uploaded_by,
        }
        for d in documents
    ]


# ===== HELPER FUNCTIONS =====


def _enrich_transfer_response(transfer: AssetTransfer, db: Session) -> AssetTransferResponse:
    asset = db.query(Asset).filter(Asset.id == transfer.asset_id).first()
    transferred_by_user = db.query(User).filter(User.id == transfer.transferred_by).first()
    approved_by_user = (
        db.query(User).filter(User.id == transfer.approved_by).first()
        if transfer.approved_by
        else None
    )

    return AssetTransferResponse(
        id=transfer.id,
        asset_id=transfer.asset_id,
        asset_number=asset.asset_number if asset else "",
        asset_name=asset.name if asset else "",
        transfer_date=transfer.transfer_date,
        from_location=transfer.from_location,
        to_location=transfer.to_location,
        transfer_reason=transfer.transfer_reason,
        transferred_by=transfer.transferred_by,
        transferred_by_name=transferred_by_user.name if transferred_by_user else None,
        approved_by=transfer.approved_by,
        approved_at=transfer.approved_at,
        notes=transfer.notes,
        created_at=transfer.created_at,
    )


def _enrich_verification_response(
    verification: AssetPhysicalVerification, db: Session
) -> PhysicalVerificationResponse:
    asset = db.query(Asset).filter(Asset.id == verification.asset_id).first()
    verified_by_user = db.query(User).filter(User.id == verification.verified_by).first()
    verified_by_second_user = (
        db.query(User).filter(User.id == verification.verified_by_second).first()
        if verification.verified_by_second
        else None
    )
    approved_by_user = (
        db.query(User).filter(User.id == verification.approved_by).first()
        if verification.approved_by
        else None
    )

    return PhysicalVerificationResponse(
        id=verification.id,
        verification_number=verification.verification_number,
        verification_date=verification.verification_date,
        asset_id=verification.asset_id,
        asset_number=asset.asset_number if asset else "",
        asset_name=asset.name if asset else "",
        status=verification.status,
        verified_location=verification.verified_location,
        condition=verification.condition,
        condition_notes=verification.condition_notes,
        verified_by=verification.verified_by,
        verified_by_name=verified_by_user.name if verified_by_user else None,
        verified_by_second=verification.verified_by_second,
        verified_by_second_name=verified_by_second_user.name if verified_by_second_user else None,
        approved_by=verification.approved_by,
        has_discrepancy=verification.has_discrepancy,
        discrepancy_details=verification.discrepancy_details,
        notes=verification.notes,
        created_at=verification.created_at,
    )


def _enrich_insurance_response(insurance: AssetInsurance, db: Session) -> AssetInsuranceResponse:
    asset = db.query(Asset).filter(Asset.id == insurance.asset_id).first()
    today = date.today()
    days_until_expiry = (insurance.policy_end_date - today).days

    return AssetInsuranceResponse(
        id=insurance.id,
        asset_id=insurance.asset_id,
        asset_number=asset.asset_number if asset else "",
        asset_name=asset.name if asset else "",
        policy_number=insurance.policy_number,
        insurance_company=insurance.insurance_company,
        policy_start_date=insurance.policy_start_date,
        policy_end_date=insurance.policy_end_date,
        days_until_expiry=days_until_expiry,
        premium_amount=insurance.premium_amount,
        insured_value=insurance.insured_value,
        coverage_type=insurance.coverage_type,
        is_active=insurance.is_active,
        auto_renewal=insurance.auto_renewal,
        renewal_reminder_days=insurance.renewal_reminder_days,
        agent_name=insurance.agent_name,
        agent_contact=insurance.agent_contact,
        created_at=insurance.created_at,
    )


def _enrich_disposal_response(
    disposal: AssetDisposal, db: Session, temple_id: int
) -> AssetDisposalResponse:
    asset = db.query(Asset).filter(Asset.id == disposal.asset_id).first()
    requested_by_user = db.query(User).filter(User.id == disposal.created_by).first()
    approved_by_user = (
        db.query(User).filter(User.id == disposal.approved_by).first()
        if hasattr(disposal, "approved_by") and disposal.approved_by
        else None
    )

    # Determine status based on asset status
    status = "pending"
    if asset and asset.status in [
        AssetStatus.DISPOSED,
        AssetStatus.SOLD,
        AssetStatus.SCRAPPED,
        AssetStatus.DONATED,
    ]:
        status = "approved"

    return AssetDisposalResponse(
        id=disposal.id,
        asset_id=disposal.asset_id,
        asset_number=asset.asset_number if asset else "",
        asset_name=asset.name if asset else "",
        disposal_date=disposal.disposal_date,
        disposal_type=disposal.disposal_type,
        disposal_reason=disposal.disposal_reason,
        book_value_at_disposal=disposal.book_value_at_disposal,
        accumulated_depreciation_at_disposal=disposal.accumulated_depreciation_at_disposal,
        disposal_proceeds=disposal.disposal_proceeds,
        gain_loss_amount=disposal.gain_loss_amount,
        buyer_name=disposal.buyer_name,
        disposal_document_number=disposal.disposal_document_number,
        status=status,
        requested_by=disposal.created_by,
        approved_by=approved_by_user.id if approved_by_user else None,
        approved_at=disposal.approved_at if hasattr(disposal, "approved_at") else None,
        rejection_reason=None,  # Would need to add this field
        notes=None,
        created_at=disposal.created_at,
    )
