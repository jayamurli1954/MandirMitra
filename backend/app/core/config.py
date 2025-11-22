"""
Application Configuration
Handles settings for both Standalone and SaaS deployments
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Deployment Mode
    DEPLOYMENT_MODE: str = "standalone"  # standalone or saas
    
    # Application
    APP_NAME: str = "MandirSync"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database Logging
    SQL_ECHO: bool = False  # Set to True to see SQL queries (useful for debugging)
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/temple_db"
    
    # Server
    HOST: str = "0.0.0.0"
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
    SMS_PROVIDER: str = "twilio"
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Email (optional)
    EMAIL_ENABLED: bool = False
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
    BACKUP_PATH: str = "backups"
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


