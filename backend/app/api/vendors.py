"""
Vendor API Endpoints
Manage vendors/suppliers for temple services
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.temple_context import require_temple_id_for_user, require_temple_write_access
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse

router = APIRouter(prefix="/api/v1/vendors", tags=["vendors"])


def _resolve_temple_id(db: Session, current_user: User) -> int:
    return require_temple_id_for_user(db, current_user, active_only=False)


def _resolve_write_temple_id(db: Session, current_user: User) -> int:
    return require_temple_write_access(db, current_user, active_only=False)


def generate_vendor_code(db: Session, temple_id: int) -> str:
    """Generate unique vendor code for the active tenant."""
    last_vendor = (
        db.query(Vendor)
        .filter(Vendor.temple_id == temple_id)
        .order_by(Vendor.id.desc())
        .first()
    )

    if last_vendor and last_vendor.vendor_code:
        try:
            new_num = int(last_vendor.vendor_code.replace("VEND", "")) + 1
        except Exception:
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
    temple_id = _resolve_temple_id(db, current_user)
    query = db.query(Vendor).filter(Vendor.temple_id == temple_id)

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

    return query.order_by(Vendor.vendor_name).limit(limit).offset(offset).all()


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(
    vendor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    temple_id = _resolve_temple_id(db, current_user)
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.temple_id == temple_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.post("/", response_model=VendorResponse)
def create_vendor(
    vendor_data: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    temple_id = _resolve_write_temple_id(db, current_user)
    if vendor_data.temple_id is not None and vendor_data.temple_id != temple_id:
        raise HTTPException(status_code=403, detail="Cannot create vendor for different temple")

    vendor_payload = vendor_data.dict()
    vendor_payload["temple_id"] = temple_id
    vendor_payload["vendor_code"] = generate_vendor_code(db, temple_id)

    vendor = Vendor(**vendor_payload)
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
    temple_id = _resolve_write_temple_id(db, current_user)
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.temple_id == temple_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    for field, value in vendor_data.dict(exclude_unset=True).items():
        setattr(vendor, field, value)

    vendor.temple_id = temple_id
    vendor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(vendor)
    return vendor


@router.delete("/{vendor_id}")
def delete_vendor(
    vendor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    temple_id = _resolve_write_temple_id(db, current_user)
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.temple_id == temple_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if len(vendor.sponsorships) > 0:
        vendor.is_active = False
        vendor.updated_at = datetime.utcnow()
        db.commit()
        return {"message": "Vendor deactivated (has transaction history)"}

    db.delete(vendor)
    db.commit()
    return {"message": "Vendor deleted successfully"}


@router.get("/types/list")
def get_vendor_types(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    temple_id = _resolve_temple_id(db, current_user)
    types = (
        db.query(Vendor.vendor_type)
        .filter(Vendor.temple_id == temple_id, Vendor.vendor_type.isnot(None))
        .distinct()
        .all()
    )
    return [value for (value,) in types if value]
