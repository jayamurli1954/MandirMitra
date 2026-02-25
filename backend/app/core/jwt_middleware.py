from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt, JWTError
from app.core.config import settings

# Paths that don't depend on JWT validation
EXCLUDED_PATHS = [
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/reset-password",
    "/health",
    "/"
]

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow preflight requests and excluded paths
        if request.method == "OPTIONS" or any(request.url.path.startswith(path) for path in EXCLUDED_PATHS):
            return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # Some APIs might optionally not require authentication so we let them through to be checked by Depends()
            return await call_next(request)
            
        token = auth_header.split(" ")[1]
        try:
            # Structurally validate token signature and expiration
            jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail": "Token expired"})
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Invalid authentication token"})
            
        return await call_next(request)
