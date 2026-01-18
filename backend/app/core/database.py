"""
Database Connection and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

from app.core.config import settings
from app.core.auto_setup import is_standalone_mode, setup_standalone_database

# Auto-setup SQLite for standalone packages
if is_standalone_mode():
    db_url = setup_standalone_database()
else:
    db_url = os.environ.get("DATABASE_URL", settings.DATABASE_URL)

# Create database engine with SQLite-specific settings
if db_url.startswith("sqlite"):
    # SQLite doesn't support pool_pre_ping, and we want to create the database file
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},  # SQLite requirement
        echo=settings.SQL_ECHO,
    )
else:
    # PostgreSQL settings
    engine = create_engine(
        db_url,
        pool_pre_ping=True,  # Verify connections before using
        echo=settings.SQL_ECHO,
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


def column_exists(db: Session, table_name: str, column_name: str) -> bool:
    """
    Check if a column exists in a table (works with both SQLite and PostgreSQL)
    """
    from sqlalchemy import text
    is_sqlite = db_url.startswith("sqlite")
    
    if is_sqlite:
        # SQLite uses PRAGMA table_info
        result = db.execute(
            text(f"PRAGMA table_info({table_name})")
        ).fetchall()
        # Check if column_name is in the results
        return any(row[1] == column_name for row in result)
    else:
        # PostgreSQL uses information_schema
        result = db.execute(
            text(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name AND column_name = :column_name
                """
            ),
            {"table_name": table_name, "column_name": column_name}
        ).fetchone()
        return result is not None


def init_db():
    """
    Initialize database (create tables and create default admin user)
    Called on application startup
    """
    # For SQLite, ensure the database file directory exists
    if db_url.startswith("sqlite"):
        from pathlib import Path

        db_path = Path(db_url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)
    # Import all models to ensure relationships are properly configured
    # This must be done before creating tables or querying
    from app.models.user import User
    from app.models.temple import Temple
    from app.models.donation import Donation, DonationCategory
    from app.models.devotee import Devotee
    from app.models.seva import Seva, SevaBooking
    from app.models.accounting import Account, JournalEntry, JournalLine
    from app.models.panchang_display_settings import PanchangDisplaySettings

    from app.models.inventory import Store, Item, StockBalance, StockMovement
    from app.models.asset import Asset
    from app.models.asset_history import (
        AssetTransfer,
        AssetValuationHistory,
        AssetPhysicalVerification,
        AssetInsurance,
        AssetDocument,
    )
    from app.models.hundi import HundiOpening, HundiMaster, HundiDenominationCount
    from app.models.hr import (
        Employee,
        Department,
        Designation,
        SalaryComponent,
        SalaryStructure,
        Payroll,
        LeaveType,
        LeaveApplication,
    )
    from app.models.vendor import Vendor
    from app.models.purchase_order import PurchaseOrder
    from app.models.upi_banking import BankAccount, UpiPayment, BankTransaction
    from app.models.token_seva import TokenInventory, TokenSale, TokenReconciliation
    from app.models.budget import Budget
    from app.models.bank_reconciliation import BankReconciliation, BankStatement, BankStatementEntry
    from app.models.financial_period import FinancialPeriod
    from app.models.inkind_sponsorship import InKindDonation, Sponsorship

    from app.core.security import get_password_hash

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create default admin user if not exists (only if not in standalone mode)
    # In standalone mode (SQLite), admin user will be created by setup_wizard.py
    # Standalone mode uses SQLite, so skip default admin creation for SQLite databases
    is_sqlite = db_url.startswith("sqlite")

    # Only create default admin for PostgreSQL (non-standalone mode)
    if not is_sqlite:
        db = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.email == "admin@temple.com").first()
            if not admin_user:
                admin_user = User(
                    email="admin@temple.com",
                    password_hash=get_password_hash("admin123"),
                    full_name="Admin User",
                    role="temple_manager",
                    is_active=True,
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
    else:
        print("ℹ️  Standalone mode detected - admin user will be created from config")
