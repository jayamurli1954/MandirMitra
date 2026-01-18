"""
Vendor API Endpoints
Manage vendors/suppliers for temple services
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse

router = APIRouter(prefix="/api/v1/vendors", tags=["vendors"])


def generate_vendor_code(db: Session, temple_id: int) -> str:
    """
    Generate unique vendor code
    Format: VEND001, VEND002, etc.
    """
    # Get last vendor code for this temple
    last_vendor = (
        db.query(Vendor).filter(Vendor.temple_id == temple_id).order_by(Vendor.id.desc()).first()
    )

    if last_vendor and last_vendor.vendor_code:
        # Extract number and increment
        try:
            last_num = int(last_vendor.vendor_code.replace("VEND", ""))
            new_num = last_num + 1
        except:
            new_num = 1
    else:
        new_num = 1

    return f"VEND{new_num:03d}"


@router.get("/", response_model=List[VendorResponse])
def list_vendors(
    vendor_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_preferred: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get list of vendors with optional filters
    """
    query = db.query(Vendor).filter(Vendor.temple_id == current_user.temple_id)

    if vendor_type:
        query = query.filter(Vendor.vendor_type == vendor_type)

    if is_active is not None:
        query = query.filter(Vendor.is_active == is_active)

    if is_preferred is not None:
        query = query.filter(Vendor.is_preferred == is_preferred)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Vendor.vendor_name.ilike(search_filter))
            | (Vendor.vendor_code.ilike(search_filter))
            | (Vendor.phone.ilike(search_filter))
        )

    vendors = query.order_by(Vendor.vendor_name).limit(limit).offset(offset).all()
    return vendors


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(
    vendor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get vendor by ID
    """
    vendor = (
        db.query(Vendor)
        .filter(Vendor.id == vendor_id, Vendor.temple_id == current_user.temple_id)
        .first()
    )

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return vendor


@router.post("/", response_model=VendorResponse)
def create_vendor(
    vendor_data: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new vendor
    """
    # Verify temple_id matches current user
    if vendor_data.temple_id != current_user.temple_id:
        raise HTTPException(status_code=403, detail="Cannot create vendor for different temple")

    # Generate vendor code
    vendor_code = generate_vendor_code(db, current_user.temple_id)

    # Create vendor
    vendor = Vendor(vendor_code=vendor_code, **vendor_data.dict())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return vendor


@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor(
    vendor_id: int,
    vendor_data: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update vendor
    """
    vendor = (
        db.query(Vendor)
        .filter(Vendor.id == vendor_id, Vendor.temple_id == current_user.temple_id)
        .first()
    )

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Update fields
    update_data = vendor_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vendor, field, value)

    vendor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(vendor)

    return vendor


@router.delete("/{vendor_id}")
def delete_vendor(
    vendor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Delete (deactivate) vendor
    Vendors with transactions are deactivated, not deleted
    """
    vendor = (
        db.query(Vendor)
        .filter(Vendor.id == vendor_id, Vendor.temple_id == current_user.temple_id)
        .first()
    )

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Check if vendor has sponsorships
    has_transactions = len(vendor.sponsorships) > 0

    if has_transactions:
        # Cannot delete, only deactivate
        vendor.is_active = False
        vendor.updated_at = datetime.utcnow()
        db.commit()
        return {"message": "Vendor deactivated (has transaction history)"}
    else:
        # Can safely delete
        db.delete(vendor)
        db.commit()
        return {"message": "Vendor deleted successfully"}


@router.get("/types/list")
def get_vendor_types(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get list of unique vendor types used in the system
    """
    types = (
        db.query(Vendor.vendor_type)
        .filter(Vendor.temple_id == current_user.temple_id, Vendor.vendor_type.isnot(None))
        .distinct()
        .all()
    )

    return [t[0] for t in types if t[0]]
