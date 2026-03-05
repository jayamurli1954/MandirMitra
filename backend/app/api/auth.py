"""
Authentication API endpoints

⚠️ LOGIN MODULE - PART OF FROZEN AUTHENTICATION SYSTEM ⚠️
==========================================================
This file contains the login endpoint that uses verify_password() from security.py.
DO NOT modify the login logic without thorough testing.

See: backend/LOGIN_MODULE_FROZEN.md for full documentation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any
from datetime import datetime, timedelta, timezone
import secrets
import hashlib

from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.audit import log_action
from app.core.rate_limiting import check_rate_limit, rate_limiter, get_client_identifier
from app.core.config import settings
from app.core.password_policy import default_policy
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.services.notification_service import notification_service
from app.schemas.token import Token
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["Authentication"])


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
        f"Use this link to reset your password (valid for 30 minutes):\n{reset_link}\n\n"
        "If you did not request this, you can ignore this email.\n"
    )
    notification_service.send_email(user.email, subject, body)

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
