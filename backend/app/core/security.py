"""
Security utilities: Password hashing, JWT tokens

⚠️ CRITICAL: LOGIN MODULE - FROZEN VERSION ⚠️
=============================================
This module contains the core authentication logic that has been tested and verified.
DO NOT modify the following functions without thorough testing:
- verify_password() - Critical for login authentication
- get_password_hash() - Used for password creation/updates
- hash_password() - Used for password hashing

Last verified working: 2024-12-XX
Login credentials: admin@temple.com / admin123

IMPORTANT NOTES:
- Bcrypt has a 72-byte password limit
- Passlib's internal bug detection can cause issues, so we use bcrypt directly as fallback
- All password functions truncate to 72 bytes to prevent errors
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    Bcrypt has a 72-byte limit, so truncate if necessary

    ⚠️ FROZEN: Do not modify without testing login functionality
    """
    # Ensure password is a string and encode to bytes to check length
    if isinstance(password, bytes):
        password = password.decode("utf-8", errors="ignore")
    # Truncate to 72 bytes to avoid bcrypt error
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    Bcrypt has a 72-byte limit, so truncate if necessary
    Uses bcrypt directly as fallback if passlib fails

    ⚠️ FROZEN: CRITICAL FUNCTION - Do not modify without thorough testing
    This function is essential for login authentication.
    It includes fallback to direct bcrypt verification to handle passlib's bug detection.

    Test before modifying:
    1. Login with admin@temple.com / admin123
    2. Verify existing users can still log in
    3. Verify new password hashes work correctly
    """
    try:
        # Ensure password is a string and encode to bytes to check length
        if isinstance(plain_password, bytes):
            plain_password = plain_password.decode("utf-8", errors="ignore")
        # Truncate to 72 bytes to avoid bcrypt error
        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > 72:
            plain_password = password_bytes[:72].decode("utf-8", errors="ignore")

        # Try passlib first
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except (ValueError, AttributeError) as e:
            # If passlib fails due to bug detection or other issues, try bcrypt directly
            if "password cannot be longer than 72 bytes" in str(e) or "has no attribute" in str(e):
                # Fallback to direct bcrypt verification
                import bcrypt

                try:
                    return bcrypt.checkpw(
                        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
                    )
                except Exception:
                    return False
            raise
    except Exception as e:
        # Final fallback: try direct bcrypt verification
        try:
            import bcrypt

            if isinstance(plain_password, bytes):
                plain_password = plain_password.decode("utf-8", errors="ignore")
            password_bytes = plain_password.encode("utf-8")
            if len(password_bytes) > 72:
                plain_password = password_bytes[:72].decode("utf-8", errors="ignore")
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False


def get_password_hash(password: str) -> str:
    """
    Hash a password
    Bcrypt has a 72-byte limit, so truncate if necessary

    ⚠️ FROZEN: Do not modify without testing password creation/updates
    """
    # Ensure password is a string and encode to bytes to check length
    if isinstance(password, bytes):
        password = password.decode("utf-8", errors="ignore")
    # Truncate to 72 bytes to avoid bcrypt error
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "sub": str(data.get("sub"))})

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    FastAPI dependency to get current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user
