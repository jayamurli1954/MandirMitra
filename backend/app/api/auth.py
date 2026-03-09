"""
Authentication API endpoints

⚠️ LOGIN MODULE - PART OF FROZEN AUTHENTICATION SYSTEM ⚠️
==========================================================
This file contains the login endpoint that uses verify_password() from security.py.
DO NOT modify the login logic without thorough testing.

See: backend/LOGIN_MODULE_FROZEN.md for full documentation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, Optional
from datetime import datetime, timedelta, timezone
import logging
import secrets
import hashlib
import re

from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.audit import log_action
from app.core.rate_limiting import check_rate_limit, rate_limiter, get_client_identifier
from app.core.config import settings
from app.core.password_policy import default_policy
from app.models.user import User
from app.models.temple import Temple
from app.models.password_reset import PasswordResetToken
from app.services.notification_service import notification_service
from app.schemas.token import Token
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(prefix="/api/v1", tags=["Authentication"])
logger = logging.getLogger(__name__)


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseModel):
    message: str
    debug_reset_link: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str


def _parse_locked_until(locked_until_value: str) -> datetime | None:
    if not locked_until_value:
        return None
    try:
        parsed = datetime.fromisoformat(locked_until_value)
    except ValueError:
        return None

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def _hash_reset_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _get_frontend_base_url() -> str:
    if settings.ALLOWED_ORIGINS:
        first_origin = settings.ALLOWED_ORIGINS.split(",")[0].strip()
        if first_origin:
            return first_origin.rstrip("/")
    return "http://localhost:3000"


@router.post("/login", response_model=Token)
def login_for_access_token(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Tracks login attempts and updates last_login_at.
    Rate limited to prevent brute force attacks.

    ⚠️ FROZEN: Uses verify_password() from security.py
    Do not modify password verification logic here - it's handled in security.py
    """
    # Rate limiting for login (stricter: 5 attempts per 15 minutes)
    check_rate_limit(request, max_requests=5, window_seconds=900)

    user = db.query(User).filter(User.email == username).first()
    now = datetime.utcnow()

    if user and settings.ACCOUNT_LOCKOUT_ENABLED and user.locked_until:
        locked_until = _parse_locked_until(user.locked_until)
        if locked_until and now < locked_until:
            remaining_seconds = int((locked_until - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=(
                    "Account is temporarily locked due to too many failed login attempts. "
                    f"Try again in {max(1, remaining_seconds)} seconds."
                ),
            )
        # Clear stale lock
        user.locked_until = None
        user.failed_login_attempts = 0
        db.commit()

    if not user or not verify_password(password, user.password_hash):
        # Log failed login attempt
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

            if (
                settings.ACCOUNT_LOCKOUT_ENABLED
                and user.failed_login_attempts >= settings.ACCOUNT_LOCKOUT_ATTEMPTS
            ):
                lock_until = now + timedelta(minutes=settings.ACCOUNT_LOCKOUT_DURATION)
                user.locked_until = lock_until.isoformat()

            db.commit()

            # Audit log failed login
            log_action(
                db=db,
                user=user,
                action="LOGIN_FAILED",
                entity_type="User",
                entity_id=user.id,
                description=f"Failed login attempt for {user.email}",
                ip_address=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None,
            )

            if (
                settings.ACCOUNT_LOCKOUT_ENABLED
                and user.failed_login_attempts >= settings.ACCOUNT_LOCKOUT_ATTEMPTS
            ):
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=(
                        "Account is temporarily locked due to too many failed login attempts. "
                        f"Try again in {settings.ACCOUNT_LOCKOUT_DURATION} minutes."
                    ),
                    headers={"WWW-Authenticate": "Bearer"},
                )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    # Update last login
    user.last_login_at = now.isoformat()
    user.failed_login_attempts = 0  # Reset on successful login
    user.locked_until = None
    db.commit()

    # Clear rate limit on successful login
    identifier = get_client_identifier(request, user)
    rate_limiter.clear_identifier(identifier)

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    # Audit log successful login
    log_action(
        db=db,
        user=user,
        action="LOGIN_SUCCESS",
        entity_type="User",
        entity_id=user.id,
        description=f"Successful login for {user.email}",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )

    return {"access_token": access_token, "token_type": "bearer"}


class BootstrapSetupRequest(BaseModel):
    temple_name: str = Field(min_length=2, max_length=200)
    temple_slug: Optional[str] = Field(default=None, max_length=100)
    primary_deity: Optional[str] = Field(default="Lord Ganesha", max_length=100)
    admin_full_name: str = Field(min_length=2, max_length=200)
    admin_email: EmailStr
    admin_password: str = Field(min_length=8, max_length=128)


class BootstrapSetupResponse(BaseModel):
    message: str
    temple_id: int
    temple_name: str
    temple_slug: str
    admin_user_id: int
    admin_email: EmailStr


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


@router.post("/setup/bootstrap", response_model=BootstrapSetupResponse, status_code=status.HTTP_201_CREATED)
def bootstrap_temple_and_admin(
    payload: BootstrapSetupRequest,
    request: Request,
    db: Session = Depends(get_db),
    x_setup_token: Optional[str] = Header(default=None, alias="X-Setup-Token"),
) -> Any:
    """
    One-click onboarding endpoint to create Temple + Admin.

    Security:
    - If SETUP_BOOTSTRAP_TOKEN is set, caller must pass matching X-Setup-Token.
    - If SETUP_BOOTSTRAP_TOKEN is not set, endpoint only works when no users exist.
    """
    check_rate_limit(request, max_requests=5, window_seconds=300)

    configured_token = (settings.SETUP_BOOTSTRAP_TOKEN or "").strip()
    supplied_token = (x_setup_token or "").strip()

    if configured_token:
        if supplied_token != configured_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid setup token",
            )
    else:
        existing_user = db.query(User.id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Bootstrap token is not configured. "
                    "Set SETUP_BOOTSTRAP_TOKEN to allow onboarding when users already exist."
                ),
            )

    admin_email = str(payload.admin_email).strip().lower()
    existing_admin = db.query(User.id).filter(func.lower(User.email) == admin_email).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin email already exists",
        )

    is_valid, error_msg = default_policy.validate(payload.admin_password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    temple_name = payload.temple_name.strip()
    full_name = payload.admin_full_name.strip()
    if not temple_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Temple name cannot be empty",
        )
    if not full_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin full name cannot be empty",
        )

    requested_slug = payload.temple_slug.strip() if payload.temple_slug else temple_name
    base_slug = _slugify(requested_slug)
    final_slug = _build_unique_slug(db, base_slug)

    primary_deity = (payload.primary_deity or "Lord Ganesha").strip() or "Lord Ganesha"

    try:
        temple = Temple(
            name=temple_name,
            slug=final_slug,
            primary_deity=primary_deity,
            is_active=True,
        )
        db.add(temple)
        db.flush()

        admin_user = User(
            temple_id=temple.id,
            email=admin_email,
            password_hash=get_password_hash(payload.admin_password),
            full_name=full_name,
            role="temple_manager",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(temple)
        db.refresh(admin_user)

        try:
            log_action(
                db=db,
                user=admin_user,
                action="BOOTSTRAP_TEMPLE_ADMIN",
                entity_type="Temple",
                entity_id=temple.id,
                description=f"Bootstrap onboarding completed for temple '{temple.name}'",
                ip_address=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None,
            )
        except Exception as audit_err:
            logger.warning(
                "Bootstrap onboarding completed but audit log failed for temple_id=%s: %s",
                temple.id,
                audit_err,
            )

        return {
            "message": "Temple and admin created successfully",
            "temple_id": temple.id,
            "temple_name": temple.name,
            "temple_slug": temple.slug,
            "admin_user_id": admin_user.id,
            "admin_email": admin_user.email,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create temple and admin",
        )

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> Any:
    """
    Request a password reset link.
    Always returns a generic success message to avoid account enumeration.
    """
    check_rate_limit(
        request,
        max_requests=settings.AUTH_RATE_LIMIT_REQUESTS,
        window_seconds=settings.AUTH_RATE_LIMIT_WINDOW,
    )

    email = (payload.email or "").strip().lower()
    response_message = (
        "If an account with this email exists, a password reset link has been sent."
    )

    if not email:
        return {"message": response_message}

    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user or not user.is_active:
        return {"message": response_message}

    # Invalidate previous active tokens for this user.
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False,
    ).update(
        {
            PasswordResetToken.is_used: True,
            PasswordResetToken.used_at: datetime.utcnow(),
        },
        synchronize_session=False,
    )

    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_reset_token(raw_token)
    expires_at = datetime.utcnow() + timedelta(minutes=30)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        requested_ip=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    db.add(reset_token)
    db.commit()

    reset_link = f"{_get_frontend_base_url()}/reset-password?token={raw_token}"
    subject = "MandirMitra Password Reset Request"
    body = (
        f"Dear {user.full_name},\n\n"
        "A password reset request was received for your account.\n"
        "Use the Reset Password button in the email, or copy this link into your browser (valid for 30 minutes):\n"
        f"{reset_link}\n\n"
        "If you did not request this, you can ignore this email.\n"
    )
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.6;">
        <p>Dear {user.full_name},</p>
        <p>A password reset request was received for your account.</p>
        <p>Use the button below to reset your password. This link is valid for <strong>30 minutes</strong>.</p>
        <p style="margin: 24px 0;">
          <a href="{reset_link}" style="background: #f97316; color: #ffffff; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 600;">
            Reset Password
          </a>
        </p>
        <p>If the button does not work, copy and paste this link into your browser:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>If you did not request this, you can ignore this email.</p>
      </body>
    </html>
    """
    notification_service.send_email(
        user.email,
        subject,
        body,
        html_body=html_body,
        disable_click_tracking=True,
    )

    # In debug mode, return the link so local environments can complete the flow without email setup.
    if settings.DEBUG:
        return {"message": response_message, "debug_reset_link": reset_link}

    return {"message": response_message}


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> Any:
    """
    Reset password using a valid one-time token.
    """
    check_rate_limit(
        request,
        max_requests=settings.AUTH_RATE_LIMIT_REQUESTS,
        window_seconds=settings.AUTH_RATE_LIMIT_WINDOW,
    )

    token = (payload.token or "").strip()
    if not token:
        raise HTTPException(status_code=400, detail="Reset token is required")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    is_valid, error_msg = default_policy.validate(payload.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    token_hash = _hash_reset_token(token)
    now = datetime.utcnow()

    reset_entry = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.is_used == False,
            PasswordResetToken.expires_at >= now,
        )
        .order_by(PasswordResetToken.id.desc())
        .first()
    )

    if not reset_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.id == reset_entry.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = get_password_hash(payload.new_password)
    user.last_password_change = now.isoformat()
    user.failed_login_attempts = 0
    user.locked_until = None

    reset_entry.is_used = True
    reset_entry.used_at = now

    # Invalidate any remaining unused tokens for safety.
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False,
    ).update(
        {
            PasswordResetToken.is_used: True,
            PasswordResetToken.used_at: now,
        },
        synchronize_session=False,
    )

    db.commit()

    log_action(
        db=db,
        user=user,
        action="PASSWORD_RESET",
        entity_type="User",
        entity_id=user.id,
        description=f"Password reset completed for {user.email}",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )

    return {"message": "Password has been reset successfully. Please log in."}

