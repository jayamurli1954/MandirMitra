"""
Application Configuration
Handles settings for both Standalone and SaaS deployments
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import tempfile


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Deployment Mode
    DEPLOYMENT_MODE: str = "standalone"  # standalone or saas

    # Application
    APP_NAME: str = "MandirMitra"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database Logging
    SQL_ECHO: bool = False  # Set to True to see SQL queries (useful for debugging)

    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Data Encryption
    ENCRYPTION_KEY: Optional[str] = None  # Set in .env for production

    # Password Policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # Account Lockout (brute-force protection)
    ACCOUNT_LOCKOUT_ENABLED: bool = True
    ACCOUNT_LOCKOUT_ATTEMPTS: int = 5      # Max failed attempts before lockout
    ACCOUNT_LOCKOUT_DURATION: int = 15     # Lockout duration in minutes

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # Requests per window
    RATE_LIMIT_WINDOW: int = 60     # Seconds
    # Stricter limits for auth endpoints
    AUTH_RATE_LIMIT_REQUESTS: int = 10
    AUTH_RATE_LIMIT_WINDOW: int = 60

    # Session Security
    SESSION_TIMEOUT_MINUTES: int = 120
    FORCE_HTTPS: bool = False  # Set to True in production

    # Database
    # Default to PostgreSQL, but will be overridden to SQLite for standalone packages
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/temple_db"
    BOOTSTRAP_ADMIN_EMAIL: Optional[str] = None
    BOOTSTRAP_ADMIN_PASSWORD: Optional[str] = None

    # Server
    HOST: str = "0.0.0.0"  # nosec B104
    PORT: int = 8000

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10 MB

    # SMS (optional)
    SMS_ENABLED: bool = False
    SMS_API_KEY: Optional[str] = None
    SMS_SENDER_ID: Optional[str] = None
    SMS_TEMPLATE_ID: Optional[str] = None
    SMS_PROVIDER: str = "MSG91"  # MSG91, INFOBIP, Twilio, etc.
    INFOBIP_BASE_URL: str = "https://api.infobip.com"
    SMS_TEST_MODE: bool = False
    SMS_TEST_RECIPIENT: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # Email (optional)
    EMAIL_ENABLED: bool = False
    EMAIL_API_KEY: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_PROVIDER: str = "SMTP"  # SMTP, SendGrid, AWS SES
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None

    # Payment (optional)
    PAYMENT_ENABLED: bool = False
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None

    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_PATH: str = os.path.join(tempfile.gettempdir(), "mandirmitra", "backups")
    BACKUP_RETENTION_DAYS: int = 30

    # Deployment mode helpers
    @property
    def is_standalone(self) -> bool:
        """Check if running in standalone mode"""
        return self.DEPLOYMENT_MODE.lower() == "standalone"

    @property
    def is_saas(self) -> bool:
        """Check if running in SaaS mode"""
        return self.DEPLOYMENT_MODE.lower() == "saas"

    @property
    def is_production(self) -> bool:
        """Check if running in production (non-debug) mode"""
        return not self.DEBUG

    @property
    def multi_tenant(self) -> bool:
        """Check if multi-tenancy is enabled"""
        return self.is_saas

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
