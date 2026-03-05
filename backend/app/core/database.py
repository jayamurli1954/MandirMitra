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
    from sqlalchemy import inspect
    from sqlalchemy.exc import SQLAlchemyError

    try:
        inspector = inspect(db.get_bind())
        columns = inspector.get_columns(table_name)
        return any(col.get("name") == column_name for col in columns)
    except SQLAlchemyError:
        return False


def init_db():
    """
    Initialize database (create tables and optionally create bootstrap admin user)
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
    from app.models.password_reset import PasswordResetToken
    from app.models.budget import Budget
    from app.models.bank_reconciliation import BankReconciliation, BankStatement, BankStatementEntry
    from app.models.financial_period import FinancialPeriod
    from app.models.inkind_sponsorship import InKindDonation, Sponsorship

    # Create all tables (checkfirst=True avoids error if tables already exist, e.g. in tests)
    Base.metadata.create_all(bind=engine, checkfirst=True)

    # Standalone mode (SQLite) admin user is created by setup_wizard.py.
    # For PostgreSQL, bootstrap credentials must be explicitly provided via env vars.
    is_sqlite = db_url.startswith("sqlite")

    if is_sqlite:
        print("[INFO] Standalone mode detected - admin user will be created from config")
        return

    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        bootstrap_email = settings.BOOTSTRAP_ADMIN_EMAIL
        bootstrap_password = settings.BOOTSTRAP_ADMIN_PASSWORD
        if not (bootstrap_email and bootstrap_password):
            print(
                "[INFO] BOOTSTRAP_ADMIN_EMAIL/BOOTSTRAP_ADMIN_PASSWORD not set; "
                "skipping auto-admin creation."
            )
            return
        admin_user = db.query(User).filter(User.email == bootstrap_email).first()
        if not admin_user:
            admin_user = User(
                email=bootstrap_email,
                password_hash=get_password_hash(bootstrap_password),
                full_name="Bootstrap Admin",
                role="temple_manager",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            print("[OK] Bootstrap admin user created")
        else:
            print("[INFO] Bootstrap admin user already exists")
    except Exception as e:
        print(f"[ERROR] Error creating bootstrap admin user: {e}")
        db.rollback()
    finally:
        db.close()
