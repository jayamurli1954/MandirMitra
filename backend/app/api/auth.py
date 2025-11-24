from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any
from datetime import datetime

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.core.audit import log_action
from app.core.rate_limiting import check_rate_limit, rate_limiter, get_client_identifier
from app.core.password_policy import default_policy
from app.models.user import User
from app.schemas.token import Token

router = APIRouter(prefix="/api/v1", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Tracks login attempts and updates last_login_at.
    Rate limited to prevent brute force attacks.
    """
    # Rate limiting for login (stricter: 5 attempts per 15 minutes)
    check_rate_limit(request, max_requests=5, window_seconds=900)
    
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        # Log failed login attempt
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            db.commit()
            
            # Audit log failed login
            log_action(
                db=db,
                user=user,
                action="LOGIN_FAILED",
                entity_type="User",
                entity_id=user.id,
                description=f"Failed login attempt for {user.email}",
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow().isoformat()
    user.failed_login_attempts = 0  # Reset on successful login
    db.commit()
    
    # Clear rate limit on successful login
    identifier = get_client_identifier(request, user)
    rate_limiter.clear_identifier(identifier)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email}
    )
    
    # Audit log successful login
    log_action(
        db=db,
        user=user,
        action="LOGIN_SUCCESS",
        entity_type="User",
        entity_id=user.id,
        description=f"Successful login for {user.email}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
