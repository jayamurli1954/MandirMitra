"""
Devotee API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.data_masking import mask_phone_for_user, mask_address_for_user, mask_email_for_user
from app.models.devotee import Devotee
from app.models.user import User
from app.models.donation import Donation
from app.models.seva import SevaBooking
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
    country: Optional[str] = "India"
    date_of_birth: Optional[date] = None
    gothra: Optional[str] = None
    nakshatra: Optional[str] = None
    family_head_id: Optional[int] = None
    preferred_language: Optional[str] = "en"
    receive_sms: Optional[bool] = True
    receive_email: Optional[bool] = True
    tags: Optional[List[str]] = None


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
    country: Optional[str] = None
    date_of_birth: Optional[date] = None
    gothra: Optional[str] = None
    nakshatra: Optional[str] = None
    family_head_id: Optional[int] = None
    preferred_language: Optional[str] = None
    receive_sms: Optional[bool] = None
    receive_email: Optional[bool] = None
    tags: Optional[List[str]] = None


class DevoteeResponse(DevoteeBase):
    id: int
    full_name: Optional[str] = None
    created_at: str
    updated_at: str
    family_head_name: Optional[str] = None
    family_members_count: Optional[int] = 0
    total_donations: Optional[float] = 0.0
    donation_count: Optional[int] = 0
    booking_count: Optional[int] = 0
    last_visit_date: Optional[date] = None
    is_vip: Optional[bool] = False
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_masking(cls, devotee: Devotee, user: User, db: Session = None):
        """
        Create response with data masking based on user permissions
        """
        # Parse tags from JSON string
        tags = []
        if devotee.tags:
            try:
                tags = json.loads(devotee.tags) if isinstance(devotee.tags, str) else devotee.tags
            except:
                tags = []
        
        # Get family info
        family_head_name = None
        if devotee.family_head_id:
            family_head = db.query(Devotee).filter(Devotee.id == devotee.family_head_id).first() if db else None
            family_head_name = family_head.name if family_head else None
        
        # Count family members
        family_members_count = 0
        if db:
            family_members_count = db.query(Devotee).filter(Devotee.family_head_id == devotee.id).count()
        
        # Get donation stats
        total_donations = 0.0
        donation_count = 0
        if db:
            donations = db.query(Donation).filter(Donation.devotee_id == devotee.id).all()
            donation_count = len(donations)
            total_donations = sum(d.amount for d in donations)
        
        # Get booking count
        booking_count = 0
        if db:
            booking_count = db.query(SevaBooking).filter(SevaBooking.devotee_id == devotee.id).count()
        
        # Check if VIP (has VIP tag)
        is_vip = "VIP" in tags or "Patron" in tags if tags else False
        
        return cls(
            id=devotee.id,
            name=devotee.name,
            phone=mask_phone_for_user(devotee.phone, user),
            email=mask_email_for_user(devotee.email, user),
            address=mask_address_for_user(devotee.address, user),
            city=devotee.city,
            state=devotee.state,
            pincode=devotee.pincode,
            country=devotee.country,
            date_of_birth=devotee.date_of_birth,
            gothra=devotee.gothra,
            nakshatra=devotee.nakshatra,
            family_head_id=devotee.family_head_id,
            preferred_language=devotee.preferred_language,
            receive_sms=devotee.receive_sms,
            receive_email=devotee.receive_email,
            tags=tags,
            full_name=devotee.full_name,
            created_at=devotee.created_at,
            updated_at=devotee.updated_at,
            family_head_name=family_head_name,
            family_members_count=family_members_count,
            total_donations=total_donations,
            donation_count=donation_count,
            booking_count=booking_count,
            is_vip=is_vip
        )


@router.get("/", response_model=List[DevoteeResponse])
def get_devotees(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search by name, phone, or email"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    is_vip: Optional[bool] = Query(None, description="Filter VIP devotees"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of devotees (with data masking based on permissions)"""
    query = db.query(Devotee)
    
    # Apply temple filter
    if current_user.temple_id:
        query = query.filter(Devotee.temple_id == current_user.temple_id)
    
    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Devotee.name.ilike(search_term),
                Devotee.phone.ilike(search_term),
                Devotee.email.ilike(search_term)
            )
        )
    
    # Tag filter
    if tag:
        query = query.filter(Devotee.tags.contains(f'"{tag}"'))
    
    # VIP filter
    if is_vip is not None:
        if is_vip:
            query = query.filter(
                or_(
                    Devotee.tags.contains('"VIP"'),
                    Devotee.tags.contains('"Patron"')
                )
            )
    
    devotees = query.offset(skip).limit(limit).all()
    # Apply data masking
    return [DevoteeResponse.from_orm_with_masking(d, current_user, db) for d in devotees]


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

    if devotee:
        return DevoteeResponse.from_orm_with_masking(devotee, current_user, db)
    return None


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
    return DevoteeResponse.from_orm_with_masking(devotee, current_user, db)


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
    
    # Convert tags list to JSON string
    tags_json = json.dumps(devotee.tags) if devotee.tags else None
    
    db_devotee = Devotee(
        name=devotee.name,
        full_name=devotee.name,  # For backward compatibility
        phone=devotee.phone,
        email=devotee.email,
        address=devotee.address,
        city=devotee.city,
        state=devotee.state,
        pincode=devotee.pincode,
        country=devotee.country or "India",
        date_of_birth=devotee.date_of_birth,
        gothra=devotee.gothra,
        nakshatra=devotee.nakshatra,
        family_head_id=devotee.family_head_id,
        preferred_language=devotee.preferred_language or "en",
        receive_sms=devotee.receive_sms if devotee.receive_sms is not None else True,
        receive_email=devotee.receive_email if devotee.receive_email is not None else True,
        tags=tags_json,
        temple_id=current_user.temple_id if current_user else None
    )
    db.add(db_devotee)
    db.commit()
    db.refresh(db_devotee)
    return DevoteeResponse.from_orm_with_masking(db_devotee, current_user, db)


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
    
    # Handle tags separately (convert list to JSON)
    if 'tags' in update_data:
        tags_json = json.dumps(update_data['tags']) if update_data['tags'] else None
        db_devotee.tags = tags_json
        del update_data['tags']
    
    for field, value in update_data.items():
        setattr(db_devotee, field, value)
    
    if 'name' in update_data:
        db_devotee.full_name = update_data['name']  # Update full_name too
    
    db_devotee.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(db_devotee)
    return DevoteeResponse.from_orm_with_masking(db_devotee, current_user, db)


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


@router.get("/duplicates", response_model=List[dict])
def find_duplicate_devotees(
    threshold: float = Query(0.8, description="Similarity threshold (0-1)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Find potential duplicate devotees based on phone, name, or email similarity
    """
    query = db.query(Devotee)
    if current_user.temple_id:
        query = query.filter(Devotee.temple_id == current_user.temple_id)
    
    all_devotees = query.all()
    duplicates = []
    processed = set()
    
    for i, devotee1 in enumerate(all_devotees):
        if devotee1.id in processed:
            continue
        
        group = [devotee1]
        
        for devotee2 in all_devotees[i+1:]:
            if devotee2.id in processed:
                continue
            
            # Check for duplicates
            is_duplicate = False
            
            # Same phone (exact match)
            if devotee1.phone == devotee2.phone:
                is_duplicate = True
            
            # Similar name and same city
            elif devotee1.name.lower() == devotee2.name.lower() and devotee1.city == devotee2.city:
                is_duplicate = True
            
            # Same email
            elif devotee1.email and devotee2.email and devotee1.email == devotee2.email:
                is_duplicate = True
            
            if is_duplicate:
                group.append(devotee2)
                processed.add(devotee2.id)
        
        if len(group) > 1:
            duplicates.append({
                "group": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "phone": d.phone,
                        "email": d.email,
                        "city": d.city
                    } for d in group
                ],
                "count": len(group)
            })
            processed.add(devotee1.id)
    
    return duplicates


@router.post("/merge", response_model=DevoteeResponse)
def merge_devotees(
    primary_id: int = Query(..., description="ID of devotee to keep"),
    duplicate_ids: List[int] = Query(..., description="IDs of devotees to merge into primary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Merge duplicate devotees into one primary devotee
    Transfers all donations and bookings to primary devotee
    """
    primary = db.query(Devotee).filter(Devotee.id == primary_id).first()
    if not primary:
        raise HTTPException(status_code=404, detail="Primary devotee not found")
    
    duplicates = db.query(Devotee).filter(Devotee.id.in_(duplicate_ids)).all()
    if len(duplicates) != len(duplicate_ids):
        raise HTTPException(status_code=404, detail="Some duplicate devotees not found")
    
    # Merge data: keep non-null values from duplicates
    for dup in duplicates:
        if not primary.email and dup.email:
            primary.email = dup.email
        if not primary.address and dup.address:
            primary.address = dup.address
        if not primary.city and dup.city:
            primary.city = dup.city
        if not primary.state and dup.state:
            primary.state = dup.state
        if not primary.pincode and dup.pincode:
            primary.pincode = dup.pincode
        if not primary.date_of_birth and dup.date_of_birth:
            primary.date_of_birth = dup.date_of_birth
        if not primary.gothra and dup.gothra:
            primary.gothra = dup.gothra
        if not primary.nakshatra and dup.nakshatra:
            primary.nakshatra = dup.nakshatra
        
        # Merge tags
        primary_tags = json.loads(primary.tags) if primary.tags else []
        dup_tags = json.loads(dup.tags) if dup.tags else []
        merged_tags = list(set(primary_tags + dup_tags))
        primary.tags = json.dumps(merged_tags) if merged_tags else None
        
        # Transfer donations
        db.query(Donation).filter(Donation.devotee_id == dup.id).update({Donation.devotee_id: primary.id})
        
        # Transfer bookings
        db.query(SevaBooking).filter(SevaBooking.devotee_id == dup.id).update({SevaBooking.devotee_id: primary.id})
        
        # Transfer family relationships
        db.query(Devotee).filter(Devotee.family_head_id == dup.id).update({Devotee.family_head_id: primary.id})
        
        # Delete duplicate
        db.delete(dup)
    
    primary.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(primary)
    
    return DevoteeResponse.from_orm_with_masking(primary, current_user, db)


@router.get("/birthdays", response_model=List[DevoteeResponse])
def get_upcoming_birthdays(
    days: int = Query(30, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get devotees with birthdays in the next N days"""
    today = date.today()
    end_date = today + timedelta(days=days)
    
    query = db.query(Devotee).filter(
        Devotee.date_of_birth.isnot(None)
    )
    
    if current_user.temple_id:
        query = query.filter(Devotee.temple_id == current_user.temple_id)
    
    all_devotees = query.all()
    upcoming_birthdays = []
    
    for devotee in all_devotees:
        if not devotee.date_of_birth:
            continue
        
        # Calculate this year's birthday
        this_year_birthday = devotee.date_of_birth.replace(year=today.year)
        if this_year_birthday < today:
            # Birthday already passed this year, check next year
            this_year_birthday = devotee.date_of_birth.replace(year=today.year + 1)
        
        if today <= this_year_birthday <= end_date:
            upcoming_birthdays.append(devotee)
    
    # Sort by birthday date
    upcoming_birthdays.sort(key=lambda d: d.date_of_birth.replace(year=today.year) if d.date_of_birth.replace(year=today.year) >= today else d.date_of_birth.replace(year=today.year + 1))
    
    return [DevoteeResponse.from_orm_with_masking(d, current_user, db) for d in upcoming_birthdays]


@router.get("/analytics", response_model=dict)
def get_devotee_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get devotee analytics and metrics"""
    query = db.query(Devotee)
    if current_user.temple_id:
        query = query.filter(Devotee.temple_id == current_user.temple_id)
    
    total_devotees = query.count()
    active_devotees = query.filter(Devotee.is_active == True).count()
    
    # VIP count
    vip_count = query.filter(
        or_(
            Devotee.tags.contains('"VIP"'),
            Devotee.tags.contains('"Patron"')
        )
    ).count()
    
    # Devotees with donations
    devotees_with_donations = db.query(func.count(func.distinct(Donation.devotee_id))).filter(
        Donation.temple_id == current_user.temple_id if current_user.temple_id else True
    ).scalar() or 0
    
    # Top donors
    top_donors_query = db.query(
        Devotee.id,
        Devotee.name,
        func.sum(Donation.amount).label('total')
    ).join(Donation).group_by(Devotee.id, Devotee.name)
    
    if current_user.temple_id:
        top_donors_query = top_donors_query.filter(Donation.temple_id == current_user.temple_id)
    
    top_donors = top_donors_query.order_by(func.sum(Donation.amount).desc()).limit(10).all()
    
    # Family groups
    family_groups_count = db.query(func.count(func.distinct(Devotee.family_head_id))).filter(
        Devotee.family_head_id.isnot(None)
    )
    if current_user.temple_id:
        family_groups_count = family_groups_count.filter(Devotee.temple_id == current_user.temple_id)
    family_groups_count = family_groups_count.scalar() or 0
    
    return {
        "total_devotees": total_devotees,
        "active_devotees": active_devotees,
        "vip_count": vip_count,
        "devotees_with_donations": devotees_with_donations,
        "family_groups": family_groups_count,
        "top_donors": [
            {
                "id": d.id,
                "name": d.name,
                "total_donated": float(d.total)
            } for d in top_donors
        ]
    }


@router.put("/{devotee_id}/link-family", response_model=DevoteeResponse)
def link_family_member(
    devotee_id: int,
    family_head_id: int = Query(..., description="ID of family head"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Link a devotee to a family head"""
    devotee = db.query(Devotee).filter(Devotee.id == devotee_id).first()
    if not devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")
    
    family_head = db.query(Devotee).filter(Devotee.id == family_head_id).first()
    if not family_head:
        raise HTTPException(status_code=404, detail="Family head not found")
    
    devotee.family_head_id = family_head_id
    devotee.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(devotee)
    
    return DevoteeResponse.from_orm_with_masking(devotee, current_user, db)


@router.put("/{devotee_id}/tags", response_model=DevoteeResponse)
def update_devotee_tags(
    devotee_id: int,
    tags: List[str] = Query(..., description="List of tags"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update devotee tags"""
    devotee = db.query(Devotee).filter(Devotee.id == devotee_id).first()
    if not devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")
    
    devotee.tags = json.dumps(tags) if tags else None
    devotee.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(devotee)
    
    return DevoteeResponse.from_orm_with_masking(devotee, current_user, db)


@router.get("/{devotee_id}/family", response_model=List[DevoteeResponse])
def get_family_members(
    devotee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all family members of a devotee"""
    devotee = db.query(Devotee).filter(Devotee.id == devotee_id).first()
    if not devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")
    
    # Get family head
    family_head_id = devotee.family_head_id if devotee.family_head_id else devotee.id
    
    # Get all family members
    family_members = db.query(Devotee).filter(
        or_(
            Devotee.family_head_id == family_head_id,
            Devotee.id == family_head_id
        )
    ).all()
    
    return [DevoteeResponse.from_orm_with_masking(d, current_user, db) for d in family_members]

