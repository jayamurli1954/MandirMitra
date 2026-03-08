from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.donation import Donation, DonationCategory


def build_daily_report(db: Session, report_date: Optional[str]):
    from datetime import date as date_class

    effective_date = report_date if report_date else date_class.today().isoformat()
    donations = db.query(Donation).filter(Donation.donation_date == effective_date).all()

    total = sum(d.amount for d in donations)
    by_category = {}
    for donation in donations:
        cat_name = donation.category.name if donation.category else "Unknown"
        if cat_name not in by_category:
            by_category[cat_name] = {"amount": 0, "count": 0}
        by_category[cat_name]["amount"] += donation.amount
        by_category[cat_name]["count"] += 1

    return {
        "date": effective_date,
        "total": total,
        "count": len(donations),
        "by_category": [
            {"category": key, "amount": value["amount"], "count": value["count"]}
            for key, value in by_category.items()
        ],
    }


def build_monthly_report(db: Session, month: int, year: int, temple_id: Optional[int]):
    donations = (
        db.query(Donation)
        .filter(
            Donation.temple_id == temple_id,
            func.extract("year", Donation.donation_date) == year,
            func.extract("month", Donation.donation_date) == month,
            Donation.is_cancelled == False,
        )
        .all()
    )

    total = sum(d.amount for d in donations)
    by_category = {}
    for donation in donations:
        cat_name = donation.category.name if donation.category else "Unknown"
        if cat_name not in by_category:
            by_category[cat_name] = {"amount": 0, "count": 0}
        by_category[cat_name]["amount"] += donation.amount
        by_category[cat_name]["count"] += 1

    return {
        "month": month,
        "year": year,
        "total": total,
        "count": len(donations),
        "by_category": [
            {"category": key, "amount": value["amount"], "count": value["count"]}
            for key, value in by_category.items()
        ],
    }


def build_category_wise_report(
    db: Session,
    date_from: Optional[str],
    date_to: Optional[str],
    temple_id: Optional[int],
):
    from datetime import date as date_class

    effective_date_from = date_from if date_from else date_class.today().isoformat()
    effective_date_to = date_to if date_to else effective_date_from

    start_date = datetime.strptime(effective_date_from, "%Y-%m-%d").date()
    end_date = datetime.strptime(effective_date_to, "%Y-%m-%d").date()

    donations = (
        db.query(Donation)
        .filter(
            Donation.temple_id == temple_id,
            Donation.donation_date >= start_date,
            Donation.donation_date <= end_date,
            Donation.is_cancelled == False,
        )
        .all()
    )

    total = sum(d.amount for d in donations)
    by_category = {}
    for donation in donations:
        cat_name = donation.category.name if donation.category else "Unknown"
        if cat_name not in by_category:
            by_category[cat_name] = {"amount": 0, "count": 0}
        by_category[cat_name]["amount"] += donation.amount
        by_category[cat_name]["count"] += 1

    return {
        "date_from": effective_date_from,
        "date_to": effective_date_to,
        "total": total,
        "count": len(donations),
        "by_category": [
            {"category": key, "amount": value["amount"], "count": value["count"]}
            for key, value in sorted(by_category.items(), key=lambda item: item[1]["amount"], reverse=True)
        ],
    }


def build_detailed_donation_report(
    db: Session,
    temple_id: Optional[int],
    date_from: Optional[str],
    date_to: Optional[str],
    category: Optional[str],
    payment_mode: Optional[str],
):
    query = db.query(Donation).filter(Donation.temple_id == temple_id, Donation.is_cancelled == False)

    if date_from:
        start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        query = query.filter(Donation.donation_date >= start_date)

    if date_to:
        end_date = datetime.strptime(date_to, "%Y-%m-%d").date()
        query = query.filter(Donation.donation_date <= end_date)

    if category:
        query = query.join(DonationCategory).filter(DonationCategory.name == category)

    if payment_mode:
        query = query.filter(Donation.payment_mode.ilike(f"%{payment_mode}%"))

    donations = query.order_by(Donation.donation_date.desc(), Donation.id.desc()).all()

    result = []
    for donation in donations:
        result.append(
            {
                "id": donation.id,
                "receipt_number": donation.receipt_number,
                "date": donation.donation_date.isoformat() if donation.donation_date else None,
                "devotee_name": donation.devotee.name if donation.devotee else "Anonymous",
                "mobile_number": donation.devotee.phone if donation.devotee else None,
                "category": donation.category.name if donation.category else "Unknown",
                "payment_mode": donation.payment_mode,
                "amount": float(donation.amount),
                "transaction_id": donation.transaction_id,
                "notes": donation.notes,
            }
        )

    return {
        "date_from": date_from,
        "date_to": date_to,
        "filters": {"category": category, "payment_mode": payment_mode},
        "total": sum(d.amount for d in donations),
        "count": len(donations),
        "donations": result,
    }
