"""
FCRA (Foreign Contribution Regulation Act) Reporting API
Handles FCRA compliance and FCRA-4 report generation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.donation import Donation
from app.models.devotee import Devotee
from app.models.accounting import Account
from app.models.temple import Temple
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/fcra", tags=["fcra"])


class FCRADonationResponse(BaseModel):
    """FCRA donation details"""

    id: int
    receipt_number: str
    donation_date: date
    devotee_name: str
    devotee_country: Optional[str]
    amount: float
    foreign_currency: Optional[str]
    foreign_amount: Optional[float]
    exchange_rate: Optional[float]
    category_name: str
    payment_mode: Optional[str]

    class Config:
        from_attributes = True


class FCRAReportResponse(BaseModel):
    """FCRA-4 Annual Return Report"""

    financial_year: str
    temple_name: str
    fcra_registration_number: Optional[str]
    report_period_start: date
    report_period_end: date
    total_foreign_contributions: float
    total_contributions_count: int
    contributions_by_currency: dict
    contributions_by_category: List[dict]
    contributions_by_country: List[dict]
    monthly_summary: List[dict]
    donations: List[FCRADonationResponse]

    class Config:
        from_attributes = True


@router.get("/donations", response_model=List[FCRADonationResponse])
def get_fcra_donations(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    financial_year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all FCRA donations (foreign contributions)"""
    query = (
        db.query(Donation)
        .join(Devotee)
        .filter(
            Donation.temple_id == current_user.temple_id,
            Donation.is_fcra_donation == True,
            Donation.is_cancelled == False,
        )
    )

    if from_date:
        query = query.filter(Donation.donation_date >= from_date)
    if to_date:
        query = query.filter(Donation.donation_date <= to_date)
    if financial_year:
        query = query.filter(Donation.financial_year == financial_year)

    donations = query.order_by(Donation.donation_date.desc()).all()

    result = []
    for donation in donations:
        devotee = db.query(Devotee).filter(Devotee.id == donation.devotee_id).first()
        result.append(
            FCRADonationResponse(
                id=donation.id,
                receipt_number=donation.receipt_number,
                donation_date=donation.donation_date,
                devotee_name=devotee.name if devotee else "Unknown",
                devotee_country=devotee.country if devotee else None,
                amount=donation.amount,
                foreign_currency=donation.foreign_currency,
                foreign_amount=donation.foreign_amount,
                exchange_rate=donation.exchange_rate,
                category_name=donation.category.name if donation.category else "Unknown",
                payment_mode=donation.payment_mode,
            )
        )

    return result


@router.get("/report/fcra4", response_model=FCRAReportResponse)
def get_fcra4_report(
    financial_year: str = Query(..., description="Financial year (e.g., '2024-25')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate FCRA-4 Annual Return Report"""
    # Get temple details
    temple = db.query(Temple).filter(Temple.id == current_user.temple_id).first()
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    if not temple.fcra_applicable:
        raise HTTPException(status_code=400, detail="FCRA is not applicable for this temple")

    # Get financial year dates (assuming April to March)
    year_parts = financial_year.split("-")
    if len(year_parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid financial year format. Use 'YYYY-YY'")

    start_year = int(year_parts[0])
    report_start = date(start_year, 4, 1)
    report_end = date(start_year + 1, 3, 31)

    # Get all FCRA donations for the financial year
    donations = (
        db.query(Donation)
        .join(Devotee)
        .filter(
            Donation.temple_id == current_user.temple_id,
            Donation.is_fcra_donation == True,
            Donation.is_cancelled == False,
            Donation.donation_date >= report_start,
            Donation.donation_date <= report_end,
        )
        .order_by(Donation.donation_date)
        .all()
    )

    # Calculate totals
    total_contributions = sum(d.amount for d in donations)
    total_count = len(donations)

    # Contributions by currency
    contributions_by_currency = {}
    for donation in donations:
        currency = donation.foreign_currency or "INR"
        if currency not in contributions_by_currency:
            contributions_by_currency[currency] = {"amount": 0.0, "count": 0}
        contributions_by_currency[currency]["amount"] += donation.amount
        contributions_by_currency[currency]["count"] += 1

    # Contributions by category
    contributions_by_category = {}
    for donation in donations:
        category_name = donation.category.name if donation.category else "Unknown"
        if category_name not in contributions_by_category:
            contributions_by_category[category_name] = {"amount": 0.0, "count": 0}
        contributions_by_category[category_name]["amount"] += donation.amount
        contributions_by_category[category_name]["count"] += 1

    # Contributions by country
    contributions_by_country = {}
    for donation in donations:
        devotee = db.query(Devotee).filter(Devotee.id == donation.devotee_id).first()
        country = devotee.country if devotee and devotee.country else "Unknown"
        if country not in contributions_by_country:
            contributions_by_country[country] = {"amount": 0.0, "count": 0}
        contributions_by_country[country]["amount"] += donation.amount
        contributions_by_country[country]["count"] += 1

    # Monthly summary
    monthly_summary = {}
    for donation in donations:
        month_key = donation.donation_date.strftime("%Y-%m")
        if month_key not in monthly_summary:
            monthly_summary[month_key] = {"amount": 0.0, "count": 0}
        monthly_summary[month_key]["amount"] += donation.amount
        monthly_summary[month_key]["count"] += 1

    monthly_list = [
        {"month": k, "amount": v["amount"], "count": v["count"]}
        for k, v in sorted(monthly_summary.items())
    ]

    # Format donations
    donations_response = []
    for donation in donations:
        devotee = db.query(Devotee).filter(Devotee.id == donation.devotee_id).first()
        donations_response.append(
            FCRADonationResponse(
                id=donation.id,
                receipt_number=donation.receipt_number,
                donation_date=donation.donation_date,
                devotee_name=devotee.name if devotee else "Unknown",
                devotee_country=devotee.country if devotee else None,
                amount=donation.amount,
                foreign_currency=donation.foreign_currency,
                foreign_amount=donation.foreign_amount,
                exchange_rate=donation.exchange_rate,
                category_name=donation.category.name if donation.category else "Unknown",
                payment_mode=donation.payment_mode,
            )
        )

    return FCRAReportResponse(
        financial_year=financial_year,
        temple_name=temple.name,
        fcra_registration_number=temple.fcra_registration_number,
        report_period_start=report_start,
        report_period_end=report_end,
        total_foreign_contributions=total_contributions,
        total_contributions_count=total_count,
        contributions_by_currency=contributions_by_currency,
        contributions_by_category=[
            {"category": k, "amount": v["amount"], "count": v["count"]}
            for k, v in contributions_by_category.items()
        ],
        contributions_by_country=[
            {"country": k, "amount": v["amount"], "count": v["count"]}
            for k, v in contributions_by_country.items()
        ],
        monthly_summary=monthly_list,
        donations=donations_response,
    )


@router.put("/donations/{donation_id}/mark-fcra")
def mark_donation_as_fcra(
    donation_id: int,
    is_fcra: bool = Query(True),
    foreign_currency: Optional[str] = Query(None),
    foreign_amount: Optional[float] = Query(None),
    exchange_rate: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a donation as FCRA (foreign contribution)"""
    donation = (
        db.query(Donation)
        .filter(Donation.id == donation_id, Donation.temple_id == current_user.temple_id)
        .first()
    )
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    donation.is_fcra_donation = is_fcra
    if is_fcra:
        donation.foreign_currency = foreign_currency
        donation.foreign_amount = foreign_amount
        donation.exchange_rate = exchange_rate

    donation.updated_at = datetime.utcnow().isoformat()
    db.commit()

    return {"message": "Donation FCRA status updated successfully"}


@router.get("/summary", response_model=dict)
def get_fcra_summary(
    financial_year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get FCRA summary statistics"""
    query = db.query(Donation).filter(
        Donation.temple_id == current_user.temple_id,
        Donation.is_fcra_donation == True,
        Donation.is_cancelled == False,
    )

    if financial_year:
        query = query.filter(Donation.financial_year == financial_year)

    donations = query.all()

    total_amount = sum(d.amount for d in donations)
    total_count = len(donations)

    # Get unique countries
    devotee_ids = [d.devotee_id for d in donations]
    devotees = db.query(Devotee).filter(Devotee.id.in_(devotee_ids)).all()
    countries = set(d.country for d in devotees if d.country and d.country != "India")

    # Get currencies
    currencies = set(d.foreign_currency for d in donations if d.foreign_currency)

    return {
        "total_foreign_contributions": total_amount,
        "total_contributions_count": total_count,
        "unique_countries": len(countries),
        "countries": list(countries),
        "currencies": list(currencies),
        "financial_year": financial_year,
    }
