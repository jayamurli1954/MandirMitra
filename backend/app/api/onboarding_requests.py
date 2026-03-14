from datetime import datetime
import re
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.database import get_db
from app.core.password_policy import default_policy
from app.core.security import get_current_user, get_password_hash
from app.models.onboarding_request import OnboardingRequest
from app.models.temple import Temple
from app.models.user import User
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/v1/onboarding-requests", tags=["onboarding-requests"])


class PublicOnboardingRequestCreate(BaseModel):
    temple_name: str | None = Field(default=None, max_length=200)
    temple_slug: str | None = Field(default=None, max_length=100)
    trust_name: str | None = Field(default=None, max_length=200)
    primary_deity: str | None = Field(default="Lord Ganesha", max_length=100)
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=20)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    admin_full_name: str = Field(min_length=2, max_length=200)
    admin_email: EmailStr
    admin_phone: str | None = Field(default=None, max_length=20)


class OnboardingRequestSummary(BaseModel):
    id: int
    status: str
    temple_name: str | None = None
    trust_name: str | None = None
    temple_slug: str | None = None
    primary_deity: str | None = None
    city: str | None = None
    state: str | None = None
    phone: str | None = None
    email: str | None = None
    admin_full_name: str
    admin_email: str
    admin_phone: str | None = None
    review_notes: str | None = None
    approved_temple_id: int | None = None
    approved_admin_user_id: int | None = None
    created_at: str
    reviewed_at: str | None = None

    class Config:
        from_attributes = True


class ApproveOnboardingRequest(BaseModel):
    temporary_password: str | None = Field(default=None, min_length=8, max_length=128)
    platform_demo_temple: bool = False
    review_notes: str | None = Field(default=None, max_length=500)


class RejectOnboardingRequest(BaseModel):
    review_notes: str = Field(min_length=3, max_length=500)


class ApproveOnboardingResponse(BaseModel):
    message: str
    request_id: int
    temple_id: int
    temple_name: str
    admin_user_id: int
    admin_email: str
    temporary_password: str
    email_sent: bool


def _require_platform_admin(current_user: User) -> None:
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform super admins can manage onboarding requests",
        )


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "temple"


def _build_unique_slug(db: Session, base_slug: str) -> str:
    slug = base_slug
    counter = 2
    while db.query(Temple.id).filter(Temple.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def _generate_temporary_password() -> str:
    alphabet = string.ascii_letters + string.digits + "@#$_!"
    for _ in range(10):
        candidate = "Mm@" + "".join(secrets.choice(alphabet) for _ in range(10))
        is_valid, _ = default_policy.validate(candidate)
        if is_valid:
            return candidate
    return "Mandir@12345X"


def _serialize_request(row: OnboardingRequest) -> dict:
    return {
        "id": row.id,
        "status": row.status,
        "temple_name": row.temple_name,
        "trust_name": row.trust_name,
        "temple_slug": row.temple_slug,
        "primary_deity": row.primary_deity,
        "city": row.city,
        "state": row.state,
        "phone": row.phone,
        "email": row.email,
        "admin_full_name": row.admin_full_name,
        "admin_email": row.admin_email,
        "admin_phone": row.admin_phone,
        "review_notes": row.review_notes,
        "approved_temple_id": row.approved_temple_id,
        "approved_admin_user_id": row.approved_admin_user_id,
        "created_at": row.created_at,
        "reviewed_at": row.reviewed_at,
    }


@router.post('/register', response_model=OnboardingRequestSummary, status_code=status.HTTP_201_CREATED)
def create_public_onboarding_request(
    payload: PublicOnboardingRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    temple_name = (payload.temple_name or '').strip()
    trust_name = (payload.trust_name or '').strip()
    admin_full_name = (payload.admin_full_name or '').strip()
    admin_email = str(payload.admin_email).strip().lower()

    if not temple_name and not trust_name:
        raise HTTPException(status_code=400, detail='Fill Temple Name or Trust Name')
    if not admin_full_name:
        raise HTTPException(status_code=400, detail='Admin full name cannot be empty')

    duplicate_user = db.query(User.id).filter(func.lower(User.email) == admin_email).first()
    if duplicate_user:
        raise HTTPException(status_code=400, detail='Admin email already exists')

    duplicate_request = (
        db.query(OnboardingRequest.id)
        .filter(
            func.lower(OnboardingRequest.admin_email) == admin_email,
            OnboardingRequest.status == 'pending',
        )
        .first()
    )
    if duplicate_request:
        raise HTTPException(status_code=400, detail='A pending onboarding request already exists for this admin email')

    request_row = OnboardingRequest(
        status='pending',
        temple_name=temple_name or None,
        temple_slug=(payload.temple_slug or '').strip() or None,
        trust_name=trust_name or None,
        primary_deity=(payload.primary_deity or 'Lord Ganesha').strip() or 'Lord Ganesha',
        address=(payload.address or '').strip() or None,
        city=(payload.city or '').strip() or None,
        state=(payload.state or '').strip() or None,
        pincode=(payload.pincode or '').strip() or None,
        phone=(payload.phone or '').strip() or None,
        email=str(payload.email).strip().lower() if payload.email else None,
        admin_full_name=admin_full_name,
        admin_email=admin_email,
        admin_phone=(payload.admin_phone or '').strip() or None,
    )
    db.add(request_row)
    db.commit()
    db.refresh(request_row)

    try:
        log_action(
            db=db,
            user=None,
            action='CREATE_PUBLIC_ONBOARDING_REQUEST',
            entity_type='OnboardingRequest',
            entity_id=request_row.id,
            description=f"Public onboarding request submitted for {admin_email}",
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get('user-agent') if request else None,
        )
    except Exception:
        pass

    return _serialize_request(request_row)


@router.get('/', response_model=list[OnboardingRequestSummary])
def list_onboarding_requests(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_platform_admin(current_user)
    query = db.query(OnboardingRequest)
    if status_filter:
        query = query.filter(OnboardingRequest.status == status_filter)
    rows = query.order_by(OnboardingRequest.created_at.desc()).all()
    return [_serialize_request(row) for row in rows]


@router.post('/{request_id}/approve', response_model=ApproveOnboardingResponse)
def approve_onboarding_request(
    request_id: int,
    payload: ApproveOnboardingRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_platform_admin(current_user)
    row = db.query(OnboardingRequest).filter(OnboardingRequest.id == request_id).first()
    if not row:
        raise HTTPException(status_code=404, detail='Onboarding request not found')
    if row.status != 'pending':
        raise HTTPException(status_code=400, detail='Only pending requests can be approved')

    existing_admin = db.query(User.id).filter(func.lower(User.email) == row.admin_email.lower()).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail='Admin email already exists')

    resolved_name = (row.temple_name or '').strip() or (row.trust_name or '').strip()
    if not resolved_name:
        raise HTTPException(status_code=400, detail='Request is missing temple or trust name')

    temporary_password = (payload.temporary_password or '').strip() or _generate_temporary_password()
    is_valid, error_msg = default_policy.validate(temporary_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    requested_slug = (row.temple_slug or '').strip() or resolved_name
    final_slug = _build_unique_slug(db, _slugify(requested_slug))

    temple = Temple(
        name=(row.temple_name or '').strip() or (row.trust_name or '').strip(),
        slug=final_slug,
        trust_name=(row.trust_name or '').strip() or None,
        primary_deity=(row.primary_deity or 'Lord Ganesha').strip() or 'Lord Ganesha',
        address=(row.address or '').strip() or None,
        city=(row.city or '').strip() or None,
        state=(row.state or '').strip() or None,
        pincode=(row.pincode or '').strip() or None,
        phone=(row.phone or '').strip() or None,
        email=(row.email or '').strip().lower() or None,
        is_active=True,
        platform_owner_user_id=current_user.id,
        allow_platform_writes=bool(payload.platform_demo_temple),
    )
    db.add(temple)
    db.flush()

    admin_user = User(
        temple_id=temple.id,
        email=row.admin_email.strip().lower(),
        password_hash=get_password_hash(temporary_password),
        full_name=row.admin_full_name.strip(),
        phone=(row.admin_phone or '').strip() or None,
        role='admin',
        is_active=True,
        is_superuser=False,
        must_change_password=True,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
    )
    db.add(admin_user)
    db.flush()

    row.status = 'approved'
    row.review_notes = (payload.review_notes or '').strip() or None
    row.reviewed_at = datetime.utcnow().isoformat()
    row.reviewed_by_user_id = current_user.id
    row.approved_temple_id = temple.id
    row.approved_admin_user_id = admin_user.id
    row.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(row)
    db.refresh(temple)
    db.refresh(admin_user)

    login_url = f"{request.base_url.scheme}://{request.base_url.netloc}" if request else ''
    frontend_login_url = f"{login_url}/login" if login_url else '/login'
    email_result = notification_service.send_email(
        admin_user.email,
        f"MandirMitra onboarding approved for {temple.name}",
        (
            f"Dear {admin_user.full_name},\n\n"
            f"Your temple/trust onboarding request for {temple.name} has been approved.\n"
            f"Login URL: {frontend_login_url}\n"
            f"Login ID: {admin_user.email}\n"
            f"Temporary Password: {temporary_password}\n\n"
            "You must change this password immediately after your first login.\n"
        ),
    )

    log_action(
        db=db,
        user=current_user,
        action='APPROVE_ONBOARDING_REQUEST',
        entity_type='OnboardingRequest',
        entity_id=row.id,
        description=f"Approved onboarding request for {admin_user.email} and created temple {temple.name}",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get('user-agent') if request else None,
    )

    return {
        'message': 'Onboarding request approved successfully',
        'request_id': row.id,
        'temple_id': temple.id,
        'temple_name': temple.name,
        'admin_user_id': admin_user.id,
        'admin_email': admin_user.email,
        'temporary_password': temporary_password,
        'email_sent': bool(email_result.get('success')),
    }


@router.post('/{request_id}/reject', response_model=OnboardingRequestSummary)
def reject_onboarding_request(
    request_id: int,
    payload: RejectOnboardingRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_platform_admin(current_user)
    row = db.query(OnboardingRequest).filter(OnboardingRequest.id == request_id).first()
    if not row:
        raise HTTPException(status_code=404, detail='Onboarding request not found')
    if row.status != 'pending':
        raise HTTPException(status_code=400, detail='Only pending requests can be rejected')

    row.status = 'rejected'
    row.review_notes = payload.review_notes.strip()
    row.reviewed_at = datetime.utcnow().isoformat()
    row.reviewed_by_user_id = current_user.id
    row.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(row)

    log_action(
        db=db,
        user=current_user,
        action='REJECT_ONBOARDING_REQUEST',
        entity_type='OnboardingRequest',
        entity_id=row.id,
        description=f"Rejected onboarding request for {row.admin_email}",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get('user-agent') if request else None,
    )

    return _serialize_request(row)
