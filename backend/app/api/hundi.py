"""
Hundi Management API Endpoints
Handles hundi opening, counting, verification, and bank deposit
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.hundi import HundiOpening, HundiDenominationCount, HundiMaster, HundiStatus
from app.models.accounting import (
    Account,
    JournalEntry,
    JournalLine,
    JournalEntryStatus,
    AccountType,
    AccountSubType,
    TransactionType,
)
from app.schemas.hundi import (
    HundiMasterCreate,
    HundiMasterUpdate,
    HundiMasterResponse,
    HundiOpeningCreate,
    HundiOpeningUpdate,
    HundiOpeningResponse,
    HundiOpeningListResponse,
    DenominationCountCreate,
    DenominationCountResponse,
    StartCountingRequest,
    CompleteCountingRequest,
    VerifyCountingRequest,
    ReportDiscrepancyRequest,
    ResolveDiscrepancyRequest,
    RecordBankDepositRequest,
    ReconcileHundiRequest,
    HundiReportResponse,
)

router = APIRouter(prefix="/api/v1/hundi", tags=["hundi"])


# ===== HUNDI MASTER ENDPOINTS =====


@router.post("/masters", response_model=HundiMasterResponse, status_code=201)
def create_hundi_master(
    hundi_data: HundiMasterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new hundi master"""
    temple_id = current_user.temple_id

    # Check if code already exists
    existing = (
        db.query(HundiMaster)
        .filter(HundiMaster.hundi_code == hundi_data.hundi_code, HundiMaster.temple_id == temple_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Hundi code '{hundi_data.hundi_code}' already exists"
        )

    hundi_master = HundiMaster(temple_id=temple_id, **hundi_data.dict())

    db.add(hundi_master)
    db.commit()
    db.refresh(hundi_master)

    return hundi_master


@router.get("/masters", response_model=List[HundiMasterResponse])
def list_hundi_masters(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all hundi masters"""
    temple_id = current_user.temple_id

    query = db.query(HundiMaster).filter(HundiMaster.temple_id == temple_id)

    if is_active is not None:
        query = query.filter(HundiMaster.is_active == is_active)

    return query.order_by(HundiMaster.hundi_code).all()


@router.get("/masters/{master_id}", response_model=HundiMasterResponse)
def get_hundi_master(
    master_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get hundi master by ID"""
    temple_id = current_user.temple_id

    hundi_master = (
        db.query(HundiMaster)
        .filter(HundiMaster.id == master_id, HundiMaster.temple_id == temple_id)
        .first()
    )

    if not hundi_master:
        raise HTTPException(status_code=404, detail="Hundi master not found")

    return hundi_master


@router.put("/masters/{master_id}", response_model=HundiMasterResponse)
def update_hundi_master(
    master_id: int,
    hundi_data: HundiMasterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update hundi master"""
    temple_id = current_user.temple_id

    hundi_master = (
        db.query(HundiMaster)
        .filter(HundiMaster.id == master_id, HundiMaster.temple_id == temple_id)
        .first()
    )

    if not hundi_master:
        raise HTTPException(status_code=404, detail="Hundi master not found")

    update_data = hundi_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hundi_master, field, value)

    hundi_master.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(hundi_master)

    return hundi_master


# ===== HUNDI OPENING ENDPOINTS =====


def generate_hundi_opening_number(
    db: Session, temple_id: int, hundi_code: str, opening_date: date
) -> str:
    """Generate unique hundi opening number"""
    year = opening_date.year
    prefix = f"HUNDI/{hundi_code}/{year}/"

    last_opening = (
        db.query(HundiOpening)
        .filter(
            HundiOpening.temple_id == temple_id,
            HundiOpening.hundi_code == hundi_code,
            HundiOpening.scheduled_date >= date(year, 1, 1),
            HundiOpening.scheduled_date < date(year + 1, 1, 1),
        )
        .order_by(HundiOpening.id.desc())
        .first()
    )

    if last_opening:
        # Extract number from last opening
        try:
            last_num = (
                int(last_opening.hundi_code.split("/")[-1]) if "/" in last_opening.hundi_code else 0
            )
        except:
            last_num = 0
        new_num = last_num + 1
    else:
        new_num = 1

    return f"{prefix}{new_num:04d}"


@router.post("/openings", response_model=HundiOpeningResponse, status_code=201)
def create_hundi_opening(
    opening_data: HundiOpeningCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Schedule a new hundi opening"""
    temple_id = current_user.temple_id

    # Verify hundi master exists
    hundi_master = (
        db.query(HundiMaster)
        .filter(
            HundiMaster.hundi_code == opening_data.hundi_code,
            HundiMaster.temple_id == temple_id,
            HundiMaster.is_active == True,
        )
        .first()
    )

    if not hundi_master:
        raise HTTPException(
            status_code=404, detail=f"Hundi '{opening_data.hundi_code}' not found or inactive"
        )

    hundi_opening = HundiOpening(
        temple_id=temple_id,
        hundi_name=opening_data.hundi_name or hundi_master.hundi_name,
        hundi_location=opening_data.hundi_location or hundi_master.hundi_location,
        scheduled_date=opening_data.scheduled_date,
        scheduled_time=opening_data.scheduled_time,
        sealed_number=opening_data.sealed_number,
        notes=opening_data.notes,
        status=HundiStatus.SCHEDULED,
        created_by=current_user.id,
    )

    db.add(hundi_opening)
    db.commit()
    db.refresh(hundi_opening)

    return hundi_opening


@router.get("/openings", response_model=List[HundiOpeningListResponse])
def list_hundi_openings(
    hundi_code: Optional[str] = Query(None),
    status: Optional[HundiStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List hundi openings with filters"""
    temple_id = current_user.temple_id

    query = db.query(HundiOpening).filter(HundiOpening.temple_id == temple_id)

    if hundi_code:
        query = query.filter(HundiOpening.hundi_code == hundi_code)
    if status:
        query = query.filter(HundiOpening.status == status)
    if from_date:
        query = query.filter(HundiOpening.scheduled_date >= from_date)
    if to_date:
        query = query.filter(HundiOpening.scheduled_date <= to_date)

    return (
        query.order_by(HundiOpening.scheduled_date.desc(), HundiOpening.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/openings/{opening_id}", response_model=HundiOpeningResponse)
def get_hundi_opening(
    opening_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get hundi opening details with denomination counts"""
    temple_id = current_user.temple_id

    hundi_opening = (
        db.query(HundiOpening)
        .filter(HundiOpening.id == opening_id, HundiOpening.temple_id == temple_id)
        .first()
    )

    if not hundi_opening:
        raise HTTPException(status_code=404, detail="Hundi opening not found")

    # Get denomination counts
    denomination_counts = (
        db.query(HundiDenominationCount)
        .filter(HundiDenominationCount.hundi_opening_id == opening_id)
        .all()
    )

    # Get verifier names
    response_dict = {
        **{k: v for k, v in hundi_opening.__dict__.items() if not k.startswith("_")},
        "denomination_counts": denomination_counts,
        "verified_by_user_1_name": None,
        "verified_by_user_2_name": None,
        "verified_by_user_3_name": None,
    }

    if hundi_opening.verified_by_user_1_id:
        user1 = db.query(User).filter(User.id == hundi_opening.verified_by_user_1_id).first()
        if user1:
            response_dict["verified_by_user_1_name"] = user1.full_name

    if hundi_opening.verified_by_user_2_id:
        user2 = db.query(User).filter(User.id == hundi_opening.verified_by_user_2_id).first()
        if user2:
            response_dict["verified_by_user_2_name"] = user2.full_name

    if hundi_opening.verified_by_user_3_id:
        user3 = db.query(User).filter(User.id == hundi_opening.verified_by_user_3_id).first()
        if user3:
            response_dict["verified_by_user_3_name"] = user3.full_name

    return HundiOpeningResponse(**response_dict)


@router.put("/openings/{opening_id}", response_model=HundiOpeningResponse)
def update_hundi_opening(
    opening_id: int,
    opening_data: HundiOpeningUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update hundi opening"""
    temple_id = current_user.temple_id

    hundi_opening = (
        db.query(HundiOpening)
        .filter(HundiOpening.id == opening_id, HundiOpening.temple_id == temple_id)
        .first()
    )

    if not hundi_opening:
        raise HTTPException(status_code=404, detail="Hundi opening not found")

    update_data = opening_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hundi_opening, field, value)

    hundi_opening.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(hundi_opening)

    return hundi_opening


@router.post("/openings/{opening_id}/open", response_model=HundiOpeningResponse)
def open_hundi(
    opening_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Mark hundi as opened"""
    temple_id = current_user.temple_id

    hundi_opening = (
        db.query(HundiOpening)
        .filter(HundiOpening.id == opening_id, HundiOpening.temple_id == temple_id)
        .first()
    )

    if not hundi_opening:
        raise HTTPException(status_code=404, detail="Hundi opening not found")

    if hundi_opening.status != HundiStatus.SCHEDULED:
        raise HTTPException(
            status_code=400, detail=f"Cannot open hundi in status: {hundi_opening.status}"
        )

    hundi_opening.status = HundiStatus.OPENED
    hundi_opening.actual_opened_date = date.today()
    hundi_opening.actual_opened_time = datetime.now().strftime("%H:%M")
    hundi_opening.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(hundi_opening)

    return hundi_opening


@router.post("/openings/{opening_id}/start-counting", response_model=HundiOpeningResponse)
def start_counting(
    opening_id: int,
    request: StartCountingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start counting process"""
    temple_id = current_user.temple_id

    hundi_opening = (
        db.query(HundiOpening)
        .filter(HundiOpening.id == opening_id, HundiOpening.temple_id == temple_id)
        .first()
    )

    if not hundi_opening:
        raise HTTPException(status_code=404, detail="Hundi opening not found")

    if hundi_opening.status not in [HundiStatus.OPENED, HundiStatus.SCHEDULED]:
        raise HTTPException(
            status_code=400, detail=f"Cannot start counting in status: {hundi_opening.status}"
        )

    hundi_opening.status = HundiStatus.COUNTING
    hundi_opening.counting_started_at = datetime.utcnow()
    hundi_opening.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(hundi_opening)

    return hundi_opening


@router.post("/openings/{opening_id}/complete-counting", response_model=HundiOpeningResponse)
def complete_counting(
    opening_id: int,
    request: CompleteCountingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete counting with denomination-wise details"""
    temple_id = current_user.temple_id

    hundi_opening = (
        db.query(HundiOpening)
        .filter(HundiOpening.id == opening_id, HundiOpening.temple_id == temple_id)
        .first()
    )

    if not hundi_opening:
        raise HTTPException(status_code=404, detail="Hundi opening not found")

    if hundi_opening.status != HundiStatus.COUNTING:
        raise HTTPException(
            status_code=400, detail=f"Cannot complete counting in status: {hundi_opening.status}"
        )

    # Delete existing counts
    db.query(HundiDenominationCount).filter(
        HundiDenominationCount.hundi_opening_id == opening_id
    ).delete()

    # Create new counts
    total_amount = 0.0
    for count_data in request.denomination_counts:
        # Calculate total amount
        count_data.total_amount = count_data.quantity * count_data.denomination_value
        total_amount += count_data.total_amount

        denomination_count = HundiDenominationCount(
            hundi_opening_id=opening_id,
            denomination_value=count_data.denomination_value,
            denomination_type=count_data.denomination_type,
            currency=count_data.currency,
            quantity=count_data.quantity,
            total_amount=count_data.total_amount,
            counted_by_user_id=current_user.id,
            notes=count_data.notes,
        )
        db.add(denomination_count)

    hundi_opening.total_amount = total_amount
    hundi_opening.counting_completed_at = datetime.utcnow()
    hundi_opening.status = HundiStatus.VERIFIED  # Move to verified for verification
    hundi_opening.notes = request.notes
    hundi_opening.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(hundi_opening)

    return hundi_opening


@router.post("/openings/{opening_id}/verify", response_model=HundiOpeningResponse)
def verify_counting(
    opening_id: int,
    request: VerifyCountingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify counting (multi-person verification)"""
    temple_id = current_user.temple_id

    hundi_opening = (
        db.query(HundiOpening)
        .filter(HundiOpening.id == opening_id, HundiOpening.temple_id == temple_id)
        .first()
    )

    if not hundi_opening:
        raise HTTPException(status_code=404, detail="Hundi opening not found")

    if hundi_opening.status != HundiStatus.VERIFIED:
        raise HTTPException(
            status_code=400, detail=f"Cannot verify in status: {hundi_opening.status}"
        )

    # Get hundi master to check verification requirements
    hundi_master = (
        db.query(HundiMaster)
        .filter(
            HundiMaster.hundi_code == hundi_opening.hundi_code, HundiMaster.temple_id == temple_id
        )
        .first()
    )

    min_verifiers = (
        hundi_master.min_verifiers if hundi_master and hundi_master.requires_verification else 2
    )

    # Set verifiers
    if not hundi_opening.verified_by_user_1_id:
        hundi_opening.verified_by_user_1_id = current_user.id
    elif not hundi_opening.verified_by_user_2_id:
        if request.verified_by_user_2_id:
            hundi_opening.verified_by_user_2_id = request.verified_by_user_2_id
        else:
            hundi_opening.verified_by_user_2_id = current_user.id
    elif not hundi_opening.verified_by_user_3_id and min_verifiers >= 3:
        if request.verified_by_user_3_id:
            hundi_opening.verified_by_user_3_id = request.verified_by_user_3_id
        else:
            hundi_opening.verified_by_user_3_id = current_user.id

    # Check if minimum verifiers reached
    verifier_count = sum(
        [
            1 if hundi_opening.verified_by_user_1_id else 0,
            1 if hundi_opening.verified_by_user_2_id else 0,
            1 if hundi_opening.verified_by_user_3_id else 0,
        ]
    )

    if verifier_count >= min_verifiers:
        hundi_opening.verified_at = datetime.utcnow()
        hundi_opening.status = HundiStatus.VERIFIED

    # Mark denomination counts as verified
    db.query(HundiDenominationCount).filter(
        HundiDenominationCount.hundi_opening_id == opening_id
    ).update(
        {"verified": True, "verified_by_user_id": current_user.id, "verified_at": datetime.utcnow()}
    )

    hundi_opening.notes = request.notes or hundi_opening.notes
    hundi_opening.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(hundi_opening)

    return hundi_opening


@router.post("/openings/{opening_id}/report-discrepancy", response_model=HundiOpeningResponse)
def report_discrepancy(
    opening_id: int,
    request: ReportDiscrepancyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Report discrepancy in counting"""
    temple_id = current_user.temple_id

    hundi_opening = (
        db.query(HundiOpening)
        .filter(HundiOpening.id == opening_id, HundiOpening.temple_id == temple_id)
        .first()
    )

    if not hundi_opening:
        raise HTTPException(status_code=404, detail="Hundi opening not found")

    hundi_opening.has_discrepancy = True
    hundi_opening.discrepancy_amount = request.discrepancy_amount
    hundi_opening.discrepancy_reason = request.discrepancy_reason
    hundi_opening.discrepancy_resolved = False
    hundi_opening.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(hundi_opening)

    return hundi_opening


@router.post("/openings/{opening_id}/resolve-discrepancy", response_model=HundiOpeningResponse)
def resolve_discrepancy(
    opening_id: int,
    request: ResolveDiscrepancyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resolve discrepancy"""
    temple_id = current_user.temple_id

    hundi_opening = (
        db.query(HundiOpening)
        .filter(HundiOpening.id == opening_id, HundiOpening.temple_id == temple_id)
        .first()
    )

    if not hundi_opening:
        raise HTTPException(status_code=404, detail="Hundi opening not found")

    if not hundi_opening.has_discrepancy:
        raise HTTPException(status_code=400, detail="No discrepancy to resolve")

    hundi_opening.discrepancy_resolved = True
    hundi_opening.discrepancy_resolved_by = current_user.id
    hundi_opening.discrepancy_resolved_at = datetime.utcnow()
    hundi_opening.notes = (
        hundi_opening.notes or ""
    ) + f"\nDiscrepancy Resolution: {request.resolution_notes}"
    hundi_opening.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(hundi_opening)

    return hundi_opening


@router.post("/openings/{opening_id}/record-deposit", response_model=HundiOpeningResponse)
def record_bank_deposit(
    opening_id: int,
    request: RecordBankDepositRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record bank deposit for hundi"""
    temple_id = current_user.temple_id

    hundi_opening = (
        db.query(HundiOpening)
        .filter(HundiOpening.id == opening_id, HundiOpening.temple_id == temple_id)
        .first()
    )

    if not hundi_opening:
        raise HTTPException(status_code=404, detail="Hundi opening not found")

    if hundi_opening.status != HundiStatus.VERIFIED:
        raise HTTPException(
            status_code=400, detail=f"Cannot record deposit in status: {hundi_opening.status}"
        )

    # Verify bank account
    bank_account = (
        db.query(Account)
        .filter(
            Account.id == request.bank_account_id,
            Account.temple_id == temple_id,
            Account.account_type == AccountType.ASSET,
            Account.account_subtype == AccountSubType.CASH_BANK,
        )
        .first()
    )

    if not bank_account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    # Create journal entry for bank deposit
    from app.api.journal_entries import generate_entry_number

    journal_entry = JournalEntry(
        temple_id=temple_id,
        entry_number=generate_entry_number(db, temple_id),
        entry_date=request.bank_deposit_date,
        narration=f"Hundi deposit - {hundi_opening.hundi_code}",
        reference_type=TransactionType.MANUAL,
        reference_id=opening_id,
        status=JournalEntryStatus.POSTED,
        created_by=current_user.id,
    )
    db.add(journal_entry)
    db.flush()

    # Get cash account (or create debit to cash)
    cash_account = (
        db.query(Account)
        .filter(
            Account.temple_id == temple_id,
            Account.account_code.like("1100%"),  # Cash in Hand (11000-11099)
            Account.is_active == True,
        )
        .first()
    )

    if not cash_account:
        # Use first cash/bank account
        cash_account = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.account_type == AccountType.ASSET,
                Account.account_subtype == AccountSubType.CASH_BANK,
                Account.is_active == True,
            )
            .first()
        )

    if cash_account:
        # Debit: Bank Account
        db.add(
            JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=request.bank_account_id,
                debit_amount=request.bank_deposit_amount,
                credit_amount=0.0,
                description=f"Hundi deposit from {hundi_opening.hundi_code}",
            )
        )

        # Credit: Cash Account (hundi was cash)
        db.add(
            JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=cash_account.id,
                debit_amount=0.0,
                credit_amount=request.bank_deposit_amount,
                description=f"Hundi deposit to bank",
            )
        )

    hundi_opening.bank_account_id = request.bank_account_id
    hundi_opening.bank_deposit_date = request.bank_deposit_date
    hundi_opening.bank_deposit_reference = request.bank_deposit_reference
    hundi_opening.bank_deposit_amount = request.bank_deposit_amount
    hundi_opening.journal_entry_id = journal_entry.id
    hundi_opening.status = HundiStatus.DEPOSITED
    hundi_opening.notes = (hundi_opening.notes or "") + f"\nBank Deposit: {request.notes or ''}"
    hundi_opening.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(hundi_opening)

    return hundi_opening


@router.post("/openings/{opening_id}/reconcile", response_model=HundiOpeningResponse)
def reconcile_hundi(
    opening_id: int,
    request: ReconcileHundiRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reconcile hundi (mark as completed)"""
    temple_id = current_user.temple_id

    hundi_opening = (
        db.query(HundiOpening)
        .filter(HundiOpening.id == opening_id, HundiOpening.temple_id == temple_id)
        .first()
    )

    if not hundi_opening:
        raise HTTPException(status_code=404, detail="Hundi opening not found")

    if hundi_opening.status != HundiStatus.DEPOSITED:
        raise HTTPException(
            status_code=400, detail=f"Cannot reconcile in status: {hundi_opening.status}"
        )

    hundi_opening.reconciled = True
    hundi_opening.reconciled_at = datetime.utcnow()
    hundi_opening.reconciled_by = current_user.id
    hundi_opening.status = HundiStatus.RECONCILED
    hundi_opening.notes = (hundi_opening.notes or "") + f"\nReconciled: {request.notes or ''}"
    hundi_opening.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(hundi_opening)

    return hundi_opening


# ===== REPORTS =====


@router.get("/reports", response_model=HundiReportResponse)
def get_hundi_report(
    from_date: date = Query(...),
    to_date: date = Query(...),
    hundi_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate hundi report"""
    temple_id = current_user.temple_id

    query = db.query(HundiOpening).filter(
        HundiOpening.temple_id == temple_id,
        HundiOpening.scheduled_date >= from_date,
        HundiOpening.scheduled_date <= to_date,
    )

    if hundi_code:
        query = query.filter(HundiOpening.hundi_code == hundi_code)

    openings = query.all()

    total_openings = len(openings)
    total_amount = sum(op.total_amount for op in openings)
    total_deposited = sum(op.bank_deposit_amount or 0 for op in openings if op.bank_deposit_amount)
    total_pending = total_amount - total_deposited

    # Hundi-wise breakdown
    hundi_wise = {}
    for op in openings:
        if op.hundi_code not in hundi_wise:
            hundi_wise[op.hundi_code] = {"count": 0, "amount": 0.0, "deposited": 0.0}
        hundi_wise[op.hundi_code]["count"] += 1
        hundi_wise[op.hundi_code]["amount"] += op.total_amount
        if op.bank_deposit_amount:
            hundi_wise[op.hundi_code]["deposited"] += op.bank_deposit_amount

    hundi_wise_breakdown = [{"hundi_code": code, **data} for code, data in hundi_wise.items()]

    # Daily breakdown
    daily_breakdown = {}
    for op in openings:
        day_key = op.scheduled_date.isoformat()
        if day_key not in daily_breakdown:
            daily_breakdown[day_key] = {"date": day_key, "count": 0, "amount": 0.0}
        daily_breakdown[day_key]["count"] += 1
        daily_breakdown[day_key]["amount"] += op.total_amount

    daily_breakdown_list = list(daily_breakdown.values())

    # Denomination-wise summary
    denomination_summary = {}
    for op in openings:
        counts = (
            db.query(HundiDenominationCount)
            .filter(HundiDenominationCount.hundi_opening_id == op.id)
            .all()
        )
        for count in counts:
            key = f"{count.denomination_value}_{count.denomination_type}"
            if key not in denomination_summary:
                denomination_summary[key] = {
                    "denomination_value": count.denomination_value,
                    "denomination_type": count.denomination_type,
                    "total_quantity": 0,
                    "total_amount": 0.0,
                }
            denomination_summary[key]["total_quantity"] += count.quantity
            denomination_summary[key]["total_amount"] += count.total_amount

    denomination_wise_summary = list(denomination_summary.values())

    return HundiReportResponse(
        from_date=from_date,
        to_date=to_date,
        total_openings=total_openings,
        total_amount=total_amount,
        total_deposited=total_deposited,
        total_pending=total_pending,
        hundi_wise_breakdown=hundi_wise_breakdown,
        daily_breakdown=daily_breakdown_list,
        denomination_wise_summary=denomination_wise_summary,
    )
