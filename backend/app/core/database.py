"""
Database Connection and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.SQL_ECHO,  # Log SQL queries (controlled by SQL_ECHO setting)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    Use with FastAPI Depends()
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database (create tables and create default admin user)
    Called on application startup
    """
    # Import all models to ensure relationships are properly configured
    # This must be done before creating tables or querying
    from app.models.user import User
    from app.models.temple import Temple
    from app.models.donation import Donation, DonationCategory
    from app.models.devotee import Devotee
    from app.models.seva import Seva, SevaBooking
    from app.models.accounting import Account, JournalEntry, JournalLine
    from app.models.panchang_display_settings import PanchangDisplaySettings
    
    from app.core.security import get_password_hash

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create default admin user if not exists
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == "admin@temple.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@temple.com",
                password_hash=get_password_hash("admin123"),
                full_name="Admin User",
                role="temple_manager",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Default admin user created: admin@temple.com / admin123")
        else:
            print("ℹ️  Admin user already exists")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


