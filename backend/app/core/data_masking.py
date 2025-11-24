"""
Data Masking Utilities
Mask sensitive data in responses based on user permissions
"""

from typing import Optional
from app.core.permissions import Permission, has_permission
from app.models.user import User


def mask_phone_for_user(phone: Optional[str], user: User) -> str:
    """
    Mask phone number based on user permissions
    """
    if not phone:
        return ""
    
    if has_permission(user, Permission.VIEW_DEVOTEE_PHONE):
        return phone
    else:
        # Mask phone: 9876543210 -> 98765*****
        if len(phone) < 6:
            return "******"
        return phone[:5] + "*" * (len(phone) - 5)


def mask_address_for_user(address: Optional[str], user: User) -> str:
    """
    Mask address based on user permissions
    """
    if not address:
        return ""
    
    if has_permission(user, Permission.VIEW_DEVOTEE_ADDRESS):
        return address
    else:
        # Show only first few characters
        if len(address) <= 10:
            return "*" * len(address)
        return address[:10] + "..." + "*" * 10


def mask_email_for_user(email: Optional[str], user: User) -> str:
    """
    Mask email based on user permissions
    """
    if not email:
        return ""
    
    # Only admins can see full emails
    if user.role == "admin":
        return email
    
    # Mask email: user@example.com -> u***@example.com
    if "@" not in email:
        return "******"
    
    local, domain = email.split("@", 1)
    if len(local) <= 1:
        masked_local = "*"
    else:
        masked_local = local[0] + "*" * (len(local) - 1)
    
    return f"{masked_local}@{domain}"


def mask_pan_for_user(pan: Optional[str], user: User) -> str:
    """
    Mask PAN number (only show last 4 digits to non-admins)
    """
    if not pan:
        return ""
    
    if user.role == "admin":
        return pan
    
    # PAN format: ABCDE1234F -> ABCDE****F
    if len(pan) >= 6:
        return pan[:5] + "*" * (len(pan) - 6) + pan[-1]
    return "*" * len(pan)


def mask_aadhaar_for_user(aadhaar: Optional[str], user: User) -> str:
    """
    Mask Aadhaar number (only show last 4 digits to non-admins)
    """
    if not aadhaar:
        return ""
    
    if user.role == "admin":
        return aadhaar
    
    # Aadhaar format: 1234 5678 9012 -> **** **** 9012
    if len(aadhaar) >= 4:
        return "*" * (len(aadhaar) - 4) + aadhaar[-4:]
    return "*" * len(aadhaar)

