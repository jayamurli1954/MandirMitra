"""
Tender Notification Service
Handles email notifications for tender events
Integrates with existing notification infrastructure
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.asset import Tender, TenderBid
from app.models.vendor import Vendor

router = APIRouter(prefix="/api/v1/tenders", tags=["tenders"])


def send_tender_published_notification(tender: Tender, db: Session):
    """
    Send notification to vendors when tender is published
    In production, this would integrate with email/SMS service
    """
    # Get all active vendors
    vendors = db.query(Vendor).filter(Vendor.is_active == True).all()

    # TODO: Integrate with email service
    # For now, just log the notification
    notification_data = {
        "event": "tender_published",
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "tender_title": tender.title,
        "last_date_submission": tender.last_date_submission.isoformat(),
        "recipients": [
            {"vendor_id": v.id, "vendor_name": v.name, "email": v.email} for v in vendors
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }

    # In production, this would call:
    # - Email service (SendGrid, AWS SES, etc.)
    # - SMS service (Twilio, MSG91, etc.)
    # - Notification queue (Celery, etc.)

    print(f"Tender Published Notification: {notification_data}")
    return notification_data


def send_bid_submission_confirmation(bid: TenderBid, tender: Tender, vendor: Vendor, db: Session):
    """
    Send confirmation email to vendor when bid is submitted
    """
    notification_data = {
        "event": "bid_submitted",
        "bid_id": bid.id,
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "tender_title": tender.title,
        "vendor_id": vendor.id,
        "vendor_name": vendor.name,
        "vendor_email": vendor.email,
        "bid_amount": bid.bid_amount,
        "bid_date": bid.bid_date.isoformat(),
        "timestamp": datetime.utcnow().isoformat(),
    }

    print(f"Bid Submission Confirmation: {notification_data}")
    return notification_data


def send_tender_awarded_notification(
    tender: Tender, winning_bid: TenderBid, vendor: Vendor, db: Session
):
    """
    Send notification to winning vendor when tender is awarded
    """
    notification_data = {
        "event": "tender_awarded",
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "tender_title": tender.title,
        "bid_id": winning_bid.id,
        "vendor_id": vendor.id,
        "vendor_name": vendor.name,
        "vendor_email": vendor.email,
        "awarded_amount": winning_bid.bid_amount,
        "award_date": tender.award_date.isoformat() if tender.award_date else None,
        "timestamp": datetime.utcnow().isoformat(),
    }

    print(f"Tender Awarded Notification: {notification_data}")
    return notification_data


def send_bid_rejected_notification(
    bid: TenderBid, tender: Tender, vendor: Vendor, reason: Optional[str] = None, db: Session = None
):
    """
    Send notification to vendor when bid is rejected
    """
    notification_data = {
        "event": "bid_rejected",
        "bid_id": bid.id,
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "tender_title": tender.title,
        "vendor_id": vendor.id,
        "vendor_name": vendor.name,
        "vendor_email": vendor.email,
        "rejection_reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
    }

    print(f"Bid Rejected Notification: {notification_data}")
    return notification_data
