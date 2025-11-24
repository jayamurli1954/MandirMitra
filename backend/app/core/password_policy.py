"""
Password Policy
Enforce strong password requirements
"""

import re
from typing import Tuple, Optional


class PasswordPolicy:
    """
    Password policy configuration
    """
    
    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = True,
        max_length: int = 128,
        prevent_common: bool = True
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.max_length = max_length
        self.prevent_common = prevent_common
        
        # Common weak passwords
        self.common_passwords = {
            "password", "12345678", "password123", "admin123",
            "qwerty", "abc123", "letmein", "welcome", "monkey"
        }
    
    def validate(self, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password against policy
        
        Returns:
            (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters long"
        
        if len(password) > self.max_length:
            return False, f"Password must be at most {self.max_length} characters long"
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if self.require_digits and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character (!@#$%^&*(), etc.)"
        
        if self.prevent_common and password.lower() in self.common_passwords:
            return False, "Password is too common. Please choose a stronger password"
        
        # Check for repeated characters (e.g., "aaaaaa")
        if re.search(r'(.)\1{3,}', password):
            return False, "Password contains too many repeated characters"
        
        return True, None


# Default password policy
default_policy = PasswordPolicy(
    min_length=8,
    require_uppercase=True,
    require_lowercase=True,
    require_digits=True,
    require_special=True
)

