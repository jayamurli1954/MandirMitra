"""
Data Encryption Utilities
Encrypt sensitive data at rest (phone numbers, addresses, etc.)
"""

from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import os
from typing import Optional


# Generate or load encryption key
def get_encryption_key() -> bytes:
    """
    Get encryption key from environment or generate one
    In production, this should be stored securely (e.g., AWS Secrets Manager, Azure Key Vault)
    """
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # Generate a key (for development only - should be set in production)
        key = Fernet.generate_key().decode()
        print("⚠️  WARNING: ENCRYPTION_KEY not set. Generated temporary key.")
        print("⚠️  Set ENCRYPTION_KEY in .env file for production!")
    else:
        key = key.encode()
    
    return key


# Initialize Fernet cipher
try:
    _cipher = Fernet(get_encryption_key())
except Exception:
    _cipher = None


def encrypt_sensitive_data(data: str) -> Optional[str]:
    """
    Encrypt sensitive data (phone numbers, addresses, etc.)
    
    Args:
        data: Plain text data to encrypt
    
    Returns:
        Encrypted string (base64 encoded) or None if encryption fails
    """
    if not data or not _cipher:
        return data
    
    try:
        encrypted = _cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    except Exception as e:
        print(f"Error encrypting data: {e}")
        return data  # Return original if encryption fails


def decrypt_sensitive_data(encrypted_data: str) -> Optional[str]:
    """
    Decrypt sensitive data
    
    Args:
        encrypted_data: Encrypted string (base64 encoded)
    
    Returns:
        Decrypted plain text or None if decryption fails
    """
    if not encrypted_data or not _cipher:
        return encrypted_data
    
    try:
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = _cipher.decrypt(decoded)
        return decrypted.decode()
    except Exception as e:
        print(f"Error decrypting data: {e}")
        return encrypted_data  # Return as-is if decryption fails


def mask_phone_number(phone: Optional[str]) -> str:
    """
    Mask phone number for display (e.g., 9876543210 -> 98765*****)
    """
    if not phone or len(phone) < 6:
        return "******"
    
    return phone[:5] + "*" * (len(phone) - 5)


def mask_email(email: Optional[str]) -> str:
    """
    Mask email for display (e.g., user@example.com -> u***@example.com)
    """
    if not email or "@" not in email:
        return "******"
    
    local, domain = email.split("@", 1)
    if len(local) <= 1:
        masked_local = "*"
    else:
        masked_local = local[0] + "*" * (len(local) - 1)
    
    return f"{masked_local}@{domain}"


def mask_address(address: Optional[str]) -> str:
    """
    Mask address for display (show only first few characters)
    """
    if not address:
        return ""
    
    if len(address) <= 10:
        return "*" * len(address)
    
    return address[:10] + "..." + "*" * 10

