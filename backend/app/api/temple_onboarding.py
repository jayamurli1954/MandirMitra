from datetime import datetime
import re

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.database import get_db
from app.core.password_policy import default_policy
from app.core.security import get_current_user, get_password_hash
from app.models.temple import Temple
from app.models.user import User

router = APIRouter(prefix="/api/v1/temples", tags=["temples"])


class TempleOnboardingRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=200)
    temple_name: str | None = Field(default=None, max_length=200)
    temple_slug: str | None = Field(default=None, max_length=100)
    trust_name: str | None = Field(default=None, max_length=200)
    primary_deity: str | None = Field(default="Lord Ganesha", max_length=100)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    admin_full_name: str = Field(min_length=2, max_length=200)
    admin_email: EmailStr
    admin_password: str = Field(min_length=8, max_length=128)


class TempleOnboardingResponse(BaseModel):
    message: str
    temple_id: int
    temple_name: str
    temple_slug: str
    trust_name: str | None = None
    admin_user_id: int
    admin_email: EmailStr
    admin_role: str


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


def _require_platform_admin(current_user: User) -> None:
    allowed_roles = {"admin", "super_admin", "temple_manager"}
    if current_user.role not in allowed_roles and not bool(current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can onboard temples",
        )


@router.post("/onboard", response_model=TempleOnboardingResponse, status_code=status.HTTP_201_CREATED)
def onboard_temple_with_admin(
    payload: TempleOnboardingRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new temple/trust and assign an admin user for that temple."""
    _require_platform_admin(current_user)

    existing_admin = (
        db.query(User.id)
        .filter(func.lower(User.email) == str(payload.admin_email).strip().lower())
        .first()
    )
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin email already exists")

    is_valid, error_msg = default_policy.validate(payload.admin_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    display_name = (
        (payload.display_name or '').strip()
        or (payload.temple_name or '').strip()
        or (payload.trust_name or '').strip()
    )
    admin_full_name = payload.admin_full_name.strip()
    if not display_name:
        admin_seed = str(payload.admin_email).split('@', 1)[0].replace('.', ' ').replace('_', ' ').strip()
        display_name = f"{admin_seed.title() or 'Organization'} Organization"
    if not admin_full_name:
        raise HTTPException(status_code=400, detail="Admin full name cannot be empty")

    requested_slug = payload.temple_slug.strip() if payload.temple_slug else display_name
    final_slug = _build_unique_slug(db, _slugify(requested_slug))

    try:
        temple = Temple(
            name=display_name,
            slug=final_slug,
            trust_name=(payload.trust_name or "").strip() or None,
            primary_deity=(payload.primary_deity or "Lord Ganesha").strip() or "Lord Ganesha",
            city=(payload.city or "").strip() or None,
            state=(payload.state or "").strip() or None,
            phone=(payload.phone or "").strip() or None,
            email=str(payload.email).strip().lower() if payload.email else None,
            is_active=True,
        )
        db.add(temple)
        db.flush()

        admin_user = User(
            temple_id=temple.id,
            email=str(payload.admin_email).strip().lower(),
            password_hash=get_password_hash(payload.admin_password),
            full_name=admin_full_name,
            role="admin",
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )
        db.add(admin_user)
        db.commit()
        db.refresh(temple)
        db.refresh(admin_user)

        log_action(
            db=db,
            user=current_user,
            action="CREATE_TEMPLE_ONBOARDING",
            entity_type="Temple",
            entity_id=temple.id,
            description=f"Onboarded temple '{temple.name}' with admin '{admin_user.email}'",
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )

        return {
            "message": "Temple/trust onboarded successfully",
            "temple_id": temple.id,
            "temple_name": temple.name,
            "temple_slug": temple.slug,
            "trust_name": temple.trust_name,
            "admin_user_id": admin_user.id,
            "admin_email": admin_user.email,
            "admin_role": admin_user.role,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to onboard temple/trust")
