"""
Rate Limiting
Prevent abuse and brute force attacks
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
from fastapi import HTTPException, status, Request
import time


class RateLimiter:
    """
    Simple in-memory rate limiter
    For production, use Redis-based rate limiting
    """
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.locked_ips: Dict[str, datetime] = {}
    
    def is_rate_limited(
        self, 
        identifier: str, 
        max_requests: int = 10, 
        window_seconds: int = 60,
        lock_duration_seconds: int = 300  # 5 minutes lockout
    ) -> tuple[bool, Optional[str]]:
        """
        Check if identifier is rate limited
        
        Args:
            identifier: IP address, user ID, or email
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            lock_duration_seconds: Lockout duration if exceeded
        
        Returns:
            (is_limited, message)
        """
        now = datetime.utcnow()
        
        # Check if IP is locked
        if identifier in self.locked_ips:
            lock_until = self.locked_ips[identifier]
            if now < lock_until:
                remaining = (lock_until - now).total_seconds()
                return True, f"Too many requests. Locked for {int(remaining)} more seconds."
            else:
                # Lock expired, remove it
                del self.locked_ips[identifier]
        
        # Clean old requests outside the window
        cutoff = now - timedelta(seconds=window_seconds)
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= max_requests:
            # Lock the identifier
            self.locked_ips[identifier] = now + timedelta(seconds=lock_duration_seconds)
            return True, f"Rate limit exceeded. Locked for {lock_duration_seconds} seconds."
        
        # Record this request
        self.requests[identifier].append(now)
        return False, None
    
    def clear_identifier(self, identifier: str):
        """Clear rate limit for an identifier (e.g., after successful login)"""
        if identifier in self.requests:
            del self.requests[identifier]
        if identifier in self.locked_ips:
            del self.locked_ips[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_identifier(request: Request, user: Optional[object] = None) -> str:
    """
    Get unique identifier for rate limiting
    Uses IP address or user ID
    """
    if user and hasattr(user, 'id'):
        return f"user_{user.id}"
    
    # Get IP address
    client_host = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take first IP in chain
        client_host = forwarded_for.split(",")[0].strip()
    
    return f"ip_{client_host}"


def check_rate_limit(
    request: Request,
    max_requests: int = 10,
    window_seconds: int = 60,
    user: Optional[object] = None
):
    """
    Check rate limit and raise exception if exceeded
    """
    identifier = get_client_identifier(request, user)
    is_limited, message = rate_limiter.is_rate_limited(
        identifier, 
        max_requests=max_requests,
        window_seconds=window_seconds
    )
    
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message or "Rate limit exceeded"
        )







