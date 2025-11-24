"""
Global Error Handlers for FastAPI
Provides consistent error responses across the application
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging
import traceback

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppException):
    """Resource not found"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f" with id: {identifier}"
        super().__init__(message, status_code=404)


class AppValidationError(AppException):
    """Application validation error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=422, details=details)


class UnauthorizedError(AppException):
    """Unauthorized access"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppException):
    """Forbidden access"""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, status_code=403)


async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions"""
    logger.warning(
        f"Application error: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.__class__.__name__,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error: {errors}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "message": "Validation error",
                "code": "VALIDATION_ERROR",
                "details": {
                    "errors": errors
                }
            }
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    # Check for integrity errors (duplicate keys, foreign key violations)
    if isinstance(exc, IntegrityError):
        error_msg = "Database integrity error"
        if "duplicate key" in str(exc.orig).lower():
            error_msg = "This record already exists"
        elif "foreign key" in str(exc.orig).lower():
            error_msg = "Cannot delete: record is referenced by other records"
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "message": error_msg,
                    "code": "DATABASE_ERROR",
                    "details": {}
                }
            }
        )
    
    # Generic database error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "message": "Database error occurred",
                "code": "DATABASE_ERROR",
                "details": {}
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )
    
    # Don't expose internal errors in production
    error_message = "An unexpected error occurred"
    if hasattr(exc, "__class__"):
        error_message = f"Error: {exc.__class__.__name__}"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "message": error_message,
                "code": "INTERNAL_ERROR",
                "details": {}
            }
        }
    )

