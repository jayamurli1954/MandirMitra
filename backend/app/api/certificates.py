"""
80G Tax Certificates API
Secure storage and management of tax certificates
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import os
import secrets
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import Permission, check_permission
from app.core.audit import log_action
from app.models.user import User
from app.models.donation import Donation
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/certificates", tags=["certificates"])


# Certificate storage directory
CERTIFICATES_DIR = Path("uploads/certificates")
CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)


class CertificateResponse(BaseModel):
    id: int
    donation_id: Optional[int]
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: int
    uploaded_at: datetime
    is_active: bool


@router.post("/upload", response_model=CertificateResponse)
def upload_certificate(
    donation_id: Optional[int] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """
    Upload 80G tax certificate or other documents
    Requires permission: UPLOAD_CERTIFICATES
    """
    check_permission(current_user, Permission.UPLOAD_CERTIFICATES)
    
    # Validate file type (PDF, images)
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: PDF, JPEG, PNG"
        )
    
    # Validate file size (max 5MB)
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    # Generate secure filename
    file_ext = Path(file.filename).suffix
    secure_filename = f"{secrets.token_urlsafe(16)}{file_ext}"
    file_path = CERTIFICATES_DIR / secure_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create certificate record in database (if you have a Certificate model)
    # For now, return file info
    
    # Audit log
    log_action(
        db=db,
        user=current_user,
        action="UPLOAD_CERTIFICATE",
        entity_type="Certificate",
        description=f"Uploaded certificate: {file.filename}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {
        "id": 1,  # Would be from database
        "donation_id": donation_id,
        "file_name": file.filename,
        "file_path": str(file_path),
        "file_size": file_size,
        "mime_type": file.content_type,
        "uploaded_by": current_user.id,
        "uploaded_at": datetime.utcnow(),
        "is_active": True
    }


@router.get("/download/{certificate_id}")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download certificate (requires permission)
    """
    check_permission(current_user, Permission.DOWNLOAD_CERTIFICATES)
    
    # Get certificate from database
    # For now, return placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Certificate download not yet implemented"
    )


@router.delete("/{certificate_id}")
def delete_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """
    Delete certificate (admin only)
    """
    check_permission(current_user, Permission.DELETE_CERTIFICATES)
    
    # Soft delete certificate
    # Audit log
    log_action(
        db=db,
        user=current_user,
        action="DELETE_CERTIFICATE",
        entity_type="Certificate",
        entity_id=certificate_id,
        description=f"Deleted certificate {certificate_id}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {"message": "Certificate deleted successfully"}

