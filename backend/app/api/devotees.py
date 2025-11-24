"""
Devotee API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.data_masking import mask_phone_for_user, mask_address_for_user, mask_email_for_user
from app.models.devotee import Devotee
from app.models.user import User
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/v1/devotees", tags=["devotees"])


# Pydantic Schemas
class DevoteeBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None


class DevoteeCreate(DevoteeBase):
    pass


class DevoteeUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None


class DevoteeResponse(DevoteeBase):
    id: int
    full_name: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_masking(cls, devotee: Devotee, user: User):
        """
        Create response with data masking based on user permissions
        """
        return cls(
            id=devotee.id,
            name=devotee.name,
            phone=mask_phone_for_user(devotee.phone, user),
            email=mask_email_for_user(devotee.email, user),
            address=mask_address_for_user(devotee.address, user),
            city=devotee.city,
            state=devotee.state,
            pincode=devotee.pincode,
            full_name=devotee.full_name,
            created_at=devotee.created_at,
            updated_at=devotee.updated_at
        )


@router.get("/", response_model=List[DevoteeResponse])
def get_devotees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of devotees (with data masking based on permissions)"""
    devotees = db.query(Devotee).offset(skip).limit(limit).all()
    # Apply data masking
    return [DevoteeResponse.from_orm_with_masking(d, current_user) for d in devotees]


@router.get("/search/by-mobile/{mobile}", response_model=Optional[DevoteeResponse])
def search_devotee_by_mobile(
    mobile: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search for a devotee by mobile number"""
    # Clean up mobile number (remove spaces, dashes, etc.)
    clean_mobile = mobile.replace(" ", "").replace("-", "").replace("+91", "")

    # Search for devotee
    devotee = db.query(Devotee).filter(
        Devotee.phone.like(f"%{clean_mobile}%")
    ).first()

    return devotee


@router.get("/{devotee_id}", response_model=DevoteeResponse)
def get_devotee(
    devotee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific devotee (with data masking based on permissions)"""
    devotee = db.query(Devotee).filter(Devotee.id == devotee_id).first()
    if not devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")
    return DevoteeResponse.from_orm_with_masking(devotee, current_user)


@router.post("/", response_model=DevoteeResponse, status_code=status.HTTP_201_CREATED)
def create_devotee(
    devotee: DevoteeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new devotee"""
    # Check if phone already exists
    existing = db.query(Devotee).filter(Devotee.phone == devotee.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already exists")
    
    db_devotee = Devotee(
        name=devotee.name,
        full_name=devotee.name,  # For backward compatibility
        phone=devotee.phone,
        email=devotee.email,
        address=devotee.address,
        city=devotee.city,
        state=devotee.state,
        pincode=devotee.pincode,
        temple_id=current_user.temple_id if current_user else None
    )
    db.add(db_devotee)
    db.commit()
    db.refresh(db_devotee)
    return db_devotee


@router.put("/{devotee_id}", response_model=DevoteeResponse)
def update_devotee(
    devotee_id: int,
    devotee: DevoteeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a devotee"""
    db_devotee = db.query(Devotee).filter(Devotee.id == devotee_id).first()
    if not db_devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")
    
    # Update fields
    update_data = devotee.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_devotee, field, value)
    
    if 'name' in update_data:
        db_devotee.full_name = update_data['name']  # Update full_name too
    
    db_devotee.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(db_devotee)
    return db_devotee


@router.delete("/{devotee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_devotee(
    devotee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a devotee"""
    db_devotee = db.query(Devotee).filter(Devotee.id == devotee_id).first()
    if not db_devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")
    
    db.delete(db_devotee)
    db.commit()
    return None

