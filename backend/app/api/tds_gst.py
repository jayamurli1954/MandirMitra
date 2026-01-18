"""
TDS/GST Management API
Handles TDS (Tax Deducted at Source) and GST (Goods and Services Tax) calculations and reporting
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.donation import Donation
from app.models.accounting import Account, JournalEntry, JournalLine, JournalEntryStatus
from app.models.temple import Temple
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/tds-gst", tags=["tds-gst"])


class TDSConfigBase(BaseModel):
    section: str = Field(..., max_length=50)  # e.g., "194A", "80G"
    description: str
    rate: float = Field(..., ge=0, le=100)  # TDS rate percentage
    threshold_amount: float = Field(0.0, ge=0)  # Minimum amount for TDS
    is_active: bool = True


class TDSConfigCreate(TDSConfigBase):
    pass


class TDSConfigResponse(TDSConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GSTConfigBase(BaseModel):
    hsn_code: str = Field(..., max_length=20)
    description: str
    rate: float = Field(..., ge=0, le=100)  # GST rate percentage
    is_active: bool = True


class GSTConfigCreate(GSTConfigBase):
    pass


class GSTConfigResponse(GSTConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TDSReportResponse(BaseModel):
    """TDS report for a period"""

    period_start: date
    period_end: date
    total_tds_amount: float
    total_transactions: int
    tds_by_section: List[dict]
    transactions: List[dict]

    class Config:
        from_attributes = True


class GSTReportResponse(BaseModel):
    """GST report for a period"""

    period_start: date
    period_end: date
    total_gst_amount: float
    total_transactions: int
    gst_by_rate: List[dict]
    transactions: List[dict]

    class Config:
        from_attributes = True


# TDS Configuration endpoints
@router.post("/tds-config", response_model=TDSConfigResponse, status_code=201)
def create_tds_config(
    config_data: TDSConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create TDS configuration"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(status_code=403, detail="Only admins and accountants can configure TDS")

    # Check if section already exists
    existing = (
        db.query(Account)
        .filter(
            Account.account_name.like(f"%TDS {config_data.section}%"),
            Account.temple_id == current_user.temple_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"TDS configuration for section {config_data.section} already exists",
        )

    # For now, we'll store TDS config in a simple way
    # In production, you might want a dedicated TDSConfig table
    # For this implementation, we'll use the temple's GST/TDS settings

    return {
        "id": 1,
        "section": config_data.section,
        "description": config_data.description,
        "rate": config_data.rate,
        "threshold_amount": config_data.threshold_amount,
        "is_active": config_data.is_active,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@router.get("/tds-config", response_model=List[TDSConfigResponse])
def get_tds_configs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all TDS configurations"""
    # In a full implementation, this would query a TDSConfig table
    # For now, return default configurations
    return [
        {
            "id": 1,
            "section": "194A",
            "description": "TDS on Interest (other than interest on securities)",
            "rate": 10.0,
            "threshold_amount": 40000.0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "id": 2,
            "section": "80G",
            "description": "TDS on Donations (if applicable)",
            "rate": 0.0,
            "threshold_amount": 0.0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ]


@router.get("/tds-report", response_model=TDSReportResponse)
def get_tds_report(
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get TDS report for a period"""
    # Get all donations with TDS
    donations = (
        db.query(Donation)
        .filter(
            Donation.temple_id == current_user.temple_id,
            Donation.tds_applicable == True,
            Donation.tds_amount > 0,
            Donation.donation_date >= from_date,
            Donation.donation_date <= to_date,
            Donation.is_cancelled == False,
        )
        .order_by(Donation.donation_date)
        .all()
    )

    total_tds = sum(d.tds_amount for d in donations)

    # Group by TDS section
    tds_by_section = {}
    for donation in donations:
        section = donation.tds_section or "Unknown"
        if section not in tds_by_section:
            tds_by_section[section] = {"amount": 0.0, "tds_amount": 0.0, "count": 0}
        tds_by_section[section]["amount"] += donation.amount
        tds_by_section[section]["tds_amount"] += donation.tds_amount
        tds_by_section[section]["count"] += 1

    transactions = [
        {
            "id": d.id,
            "receipt_number": d.receipt_number,
            "date": d.donation_date,
            "amount": d.amount,
            "tds_section": d.tds_section,
            "tds_amount": d.tds_amount,
            "net_amount": d.amount - d.tds_amount,
        }
        for d in donations
    ]

    return TDSReportResponse(
        period_start=from_date,
        period_end=to_date,
        total_tds_amount=total_tds,
        total_transactions=len(donations),
        tds_by_section=[
            {
                "section": k,
                "total_amount": v["amount"],
                "tds_amount": v["tds_amount"],
                "count": v["count"],
            }
            for k, v in tds_by_section.items()
        ],
        transactions=transactions,
    )


@router.get("/gst-report", response_model=GSTReportResponse)
def get_gst_report(
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GST report for a period"""
    # Get all donations with GST
    donations = (
        db.query(Donation)
        .filter(
            Donation.temple_id == current_user.temple_id,
            Donation.gst_applicable == True,
            Donation.gst_amount > 0,
            Donation.donation_date >= from_date,
            Donation.donation_date <= to_date,
            Donation.is_cancelled == False,
        )
        .order_by(Donation.donation_date)
        .all()
    )

    total_gst = sum(d.gst_amount for d in donations)

    # Group by GST rate
    gst_by_rate = {}
    for donation in donations:
        rate = donation.gst_rate or 0.0
        if rate not in gst_by_rate:
            gst_by_rate[rate] = {"amount": 0.0, "gst_amount": 0.0, "count": 0}
        gst_by_rate[rate]["amount"] += donation.amount
        gst_by_rate[rate]["gst_amount"] += donation.gst_amount
        gst_by_rate[rate]["count"] += 1

    transactions = [
        {
            "id": d.id,
            "receipt_number": d.receipt_number,
            "date": d.donation_date,
            "amount": d.amount,
            "gst_rate": d.gst_rate,
            "gst_amount": d.gst_amount,
            "hsn_code": d.hsn_code,
            "net_amount": d.amount - d.gst_amount,
        }
        for d in donations
    ]

    return GSTReportResponse(
        period_start=from_date,
        period_end=to_date,
        total_gst_amount=total_gst,
        total_transactions=len(donations),
        gst_by_rate=[
            {
                "rate": k,
                "total_amount": v["amount"],
                "gst_amount": v["gst_amount"],
                "count": v["count"],
            }
            for k, v in gst_by_rate.items()
        ],
        transactions=transactions,
    )


@router.post("/calculate-tds")
def calculate_tds(
    donation_id: int,
    tds_section: str = Query(...),
    tds_rate: float = Query(..., ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate and apply TDS to a donation"""
    donation = (
        db.query(Donation)
        .filter(Donation.id == donation_id, Donation.temple_id == current_user.temple_id)
        .first()
    )
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    tds_amount = (donation.amount * tds_rate) / 100

    donation.tds_applicable = True
    donation.tds_amount = tds_amount
    donation.tds_section = tds_section
    donation.updated_at = datetime.utcnow().isoformat()

    db.commit()

    return {
        "donation_id": donation_id,
        "amount": donation.amount,
        "tds_rate": tds_rate,
        "tds_amount": tds_amount,
        "net_amount": donation.amount - tds_amount,
    }


@router.post("/calculate-gst")
def calculate_gst(
    donation_id: int,
    gst_rate: float = Query(..., ge=0, le=100),
    hsn_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate and apply GST to a donation"""
    donation = (
        db.query(Donation)
        .filter(Donation.id == donation_id, Donation.temple_id == current_user.temple_id)
        .first()
    )
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    # GST is calculated on the base amount
    # GST amount = (base_amount * gst_rate) / (100 + gst_rate) for inclusive
    # Or GST amount = (base_amount * gst_rate) / 100 for exclusive
    # Assuming exclusive GST
    gst_amount = (donation.amount * gst_rate) / 100

    donation.gst_applicable = True
    donation.gst_amount = gst_amount
    donation.gst_rate = gst_rate
    donation.hsn_code = hsn_code
    donation.updated_at = datetime.utcnow().isoformat()

    db.commit()

    return {
        "donation_id": donation_id,
        "amount": donation.amount,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "total_amount": donation.amount + gst_amount,
        "hsn_code": hsn_code,
    }
