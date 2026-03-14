"""
Database Connection and Session Management
"""

from sqlalchemy import MetaData, Table, create_engine, func, or_, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from datetime import datetime
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


def normalize_nullable_temple_module_flags(db: Session) -> None:
    """Backfill legacy temple rows where newer module flags are NULL."""
    defaults = {
        "module_tender_enabled": False,
        "module_reports_enabled": True,
        "module_token_seva_enabled": True,
    }
    available_columns = [column for column in defaults if column_exists(db, "temples", column)]
    if not available_columns:
        return

    temples_table = Table("temples", MetaData(), autoload_with=db.get_bind())
    values_to_update = {
        column: func.coalesce(getattr(temples_table.c, column), defaults[column])
        for column in available_columns
    }
    null_conditions = [getattr(temples_table.c, column).is_(None) for column in available_columns]
    db.execute(
        temples_table.update().where(or_(*null_conditions)).values(**values_to_update)
    )
    db.commit()


def ensure_seva_tenant_columns(db: Session) -> None:
    """Ensure seva master and booking tables carry tenant context for SaaS mode."""

    def add_integer_column_if_missing(table_name: str, column_name: str) -> bool:
        if column_exists(db, table_name, column_name):
            return False

        dialect = db.get_bind().dialect.name
        if dialect == "sqlite":
            db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} INTEGER"))
        else:
            db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} INTEGER"))
        return True

    sevas_changed = add_integer_column_if_missing("sevas", "temple_id")
    bookings_changed = add_integer_column_if_missing("seva_bookings", "temple_id")

    single_temple = db.execute(
        text("SELECT id FROM temples WHERE is_active = 1 ORDER BY id ASC LIMIT 2")
    ).fetchall()
    single_temple_id = single_temple[0][0] if len(single_temple) == 1 else None

    if column_exists(db, "sevas", "temple_id"):
        if single_temple_id is not None:
            db.execute(
                text("UPDATE sevas SET temple_id = :temple_id WHERE temple_id IS NULL"),
                {"temple_id": single_temple_id},
            )

    if column_exists(db, "seva_bookings", "temple_id"):
        db.execute(
            text(
                """
                UPDATE seva_bookings
                SET temple_id = (
                    SELECT users.temple_id
                    FROM users
                    WHERE users.id = seva_bookings.user_id
                )
                WHERE temple_id IS NULL
                  AND user_id IS NOT NULL
                """
            )
        )
        db.execute(
            text(
                """
                UPDATE seva_bookings
                SET temple_id = (
                    SELECT devotees.temple_id
                    FROM devotees
                    WHERE devotees.id = seva_bookings.devotee_id
                )
                WHERE temple_id IS NULL
                  AND devotee_id IS NOT NULL
                """
            )
        )
        if single_temple_id is not None:
            db.execute(
                text(
                    "UPDATE seva_bookings SET temple_id = :temple_id WHERE temple_id IS NULL"
                ),
                {"temple_id": single_temple_id},
            )

    if sevas_changed or bookings_changed:
        db.commit()
    else:
        db.commit()



def ensure_temple_platform_access_columns(db: Session) -> None:
    """Ensure temple governance columns exist for SaaS platform read-only access."""

    def add_column_if_missing(table_name: str, column_name: str, sql_type: str) -> bool:
        if column_exists(db, table_name, column_name):
            return False

        dialect = db.get_bind().dialect.name
        if dialect == "sqlite":
            db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type}"))
        else:
            db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {sql_type}"))
        return True

    owner_changed = add_column_if_missing("temples", "platform_owner_user_id", "INTEGER")
    writes_changed = add_column_if_missing("temples", "allow_platform_writes", "BOOLEAN")

    if column_exists(db, "temples", "allow_platform_writes"):
        db.execute(text("UPDATE temples SET allow_platform_writes = 0 WHERE allow_platform_writes IS NULL"))

    if owner_changed or writes_changed:
        db.commit()
    else:
        db.commit()


def ensure_audit_log_tenant_column(db: Session) -> None:
    """Ensure audit logs carry tenant context for tenant-safe reporting."""

    if not column_exists(db, "audit_logs", "temple_id"):
        dialect = db.get_bind().dialect.name
        if dialect == "sqlite":
            db.execute(text("ALTER TABLE audit_logs ADD COLUMN temple_id INTEGER"))
        else:
            db.execute(text("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS temple_id INTEGER"))

    db.execute(
        text(
            """
            UPDATE audit_logs
            SET temple_id = (
                SELECT users.temple_id
                FROM users
                WHERE users.id = audit_logs.user_id
            )
            WHERE temple_id IS NULL
            """
        )
    )

    single_temple = db.execute(
        text("SELECT id FROM temples WHERE is_active = 1 ORDER BY id ASC LIMIT 2")
    ).fetchall()
    single_temple_id = single_temple[0][0] if len(single_temple) == 1 else None
    if single_temple_id is not None:
        db.execute(
            text("UPDATE audit_logs SET temple_id = :temple_id WHERE temple_id IS NULL"),
            {"temple_id": single_temple_id},
        )
    db.commit()


def normalize_saas_superuser_flags(db: Session) -> None:
    """Keep SaaS platform-admin semantics aligned with role == super_admin."""
    if settings.DEPLOYMENT_MODE.lower() != 'saas':
        return

    users_table = Table('users', MetaData(), autoload_with=db.get_bind())
    email_column = getattr(users_table.c, 'email', None)
    role_column = getattr(users_table.c, 'role', None)
    is_superuser_column = getattr(users_table.c, 'is_superuser', None)
    updated_at_column = getattr(users_table.c, 'updated_at', None)

    if email_column is None or role_column is None or is_superuser_column is None:
        return

    now_value = datetime.utcnow().isoformat() if updated_at_column is not None else None
    bootstrap_email = (settings.BOOTSTRAP_ADMIN_EMAIL or '').strip().lower()

    if bootstrap_email:
        promote_values = {'role': 'super_admin', 'is_superuser': True}
        if updated_at_column is not None:
            promote_values['updated_at'] = now_value
        db.execute(
            users_table.update()
            .where(func.lower(email_column) == bootstrap_email)
            .values(**promote_values)
        )

    demote_values = {'is_superuser': False}
    if updated_at_column is not None:
        demote_values['updated_at'] = now_value

    demote_query = users_table.update().where(
        role_column != 'super_admin',
        is_superuser_column == True,
    )
    if bootstrap_email:
        demote_query = demote_query.where(func.lower(email_column) != bootstrap_email)
    db.execute(demote_query.values(**demote_values))

    promote_super_admin_values = {'is_superuser': True}
    if updated_at_column is not None:
        promote_super_admin_values['updated_at'] = now_value
    db.execute(
        users_table.update()
        .where(role_column == 'super_admin', is_superuser_column != True)
        .values(**promote_super_admin_values)
    )
    db.commit()

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
    from app.models.role_permission import RolePermissionProfile, UserRoleAssignment
    from app.models.budget import Budget
    from app.models.bank_reconciliation import BankReconciliation, BankStatement, BankStatementEntry
    from app.models.financial_period import FinancialPeriod
    from app.models.inkind_sponsorship import InKindDonation, Sponsorship

    # Create all tables (checkfirst=True avoids error if tables already exist, e.g. in tests)
    Base.metadata.create_all(bind=engine, checkfirst=True)

    db = SessionLocal()
    try:
        normalize_nullable_temple_module_flags(db)
        ensure_seva_tenant_columns(db)
        ensure_temple_platform_access_columns(db)
        ensure_audit_log_tenant_column(db)
        normalize_saas_superuser_flags(db)
    finally:
        db.close()

    # Standalone mode (SQLite) admin user is created by setup_wizard.py.
    # For PostgreSQL, bootstrap credentials must be explicitly provided via env vars.
    is_sqlite = db_url.startswith("sqlite")

    if is_sqlite:
        if settings.is_standalone:
            print("[INFO] Standalone mode detected - admin user will be created from config")
        else:
            print("[INFO] Local SQLite database detected in SaaS mode - skipping bootstrap admin auto-creation")
        return

    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        bootstrap_email = (settings.BOOTSTRAP_ADMIN_EMAIL or '').strip().lower()
        bootstrap_password = settings.BOOTSTRAP_ADMIN_PASSWORD
        legacy_bootstrap_email = 'admin@temple.com'

        if not bootstrap_email and not bootstrap_password:
            print(
                "[INFO] BOOTSTRAP_ADMIN_EMAIL/BOOTSTRAP_ADMIN_PASSWORD not set; "
                "skipping auto-admin creation."
            )
            return

        admin_user = None
        if bootstrap_email:
            admin_user = db.query(User).filter(func.lower(User.email) == bootstrap_email).first()

            if not admin_user:
                legacy_admin_user = (
                    db.query(User)
                    .filter(
                        func.lower(User.email) == legacy_bootstrap_email,
                        User.is_superuser == True,
                    )
                    .first()
                )
                if legacy_admin_user:
                    legacy_admin_user.email = bootstrap_email
                    legacy_admin_user.updated_at = datetime.utcnow().isoformat()
                    db.commit()
                    admin_user = legacy_admin_user
                    print(f"[OK] Legacy bootstrap admin email updated to {bootstrap_email}")

        if not admin_user and bootstrap_email and bootstrap_password:
            admin_user = User(
                email=bootstrap_email,
                password_hash=get_password_hash(bootstrap_password),
                full_name="Bootstrap Admin",
                role="super_admin",
                is_active=True,
                is_superuser=True,
            )
            db.add(admin_user)
            db.commit()
            print("[OK] Bootstrap admin user created")
        elif admin_user:
            updated_bootstrap_flags = False
            if admin_user.role != "super_admin":
                admin_user.role = "super_admin"
                updated_bootstrap_flags = True
            if not bool(admin_user.is_superuser):
                admin_user.is_superuser = True
                updated_bootstrap_flags = True
            if not bool(admin_user.is_active):
                admin_user.is_active = True
                updated_bootstrap_flags = True
            if updated_bootstrap_flags:
                admin_user.updated_at = datetime.utcnow().isoformat()
                db.commit()
                print(f"[OK] Bootstrap admin privileges enforced for {bootstrap_email}")
            else:
                print("[INFO] Bootstrap admin user already exists")
        else:
            print(
                "[INFO] BOOTSTRAP_ADMIN_EMAIL is set but BOOTSTRAP_ADMIN_PASSWORD is missing; "
                "skipping auto-admin creation."
            )
    except Exception as e:
        print(f"[ERROR] Error creating bootstrap admin user: {e}")
        db.rollback()
    finally:
        db.close()
