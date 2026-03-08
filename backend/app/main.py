"""
MandirMitra - Temple Management System
FastAPI Main Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
import os

# Monkey patch for passlib 1.7.4 compatibility with bcrypt 4.0.0+
if not hasattr(bcrypt, "__about__"):

    class MockAbout:
        __version__ = bcrypt.__version__

    bcrypt.__about__ = MockAbout()
from app.core.config import settings
from app.core.database import init_db
from app.core.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
    AppException,
)
from app.core.security_headers import SecurityHeadersMiddleware
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import all models to ensure they're registered with SQLAlchemy
# This must happen before init_db() is called
from app.models.temple import Temple
from app.models.user import User
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.seva import Seva, SevaBooking
from app.models.seva_exchange import SevaExchangeRequest
from app.models.accounting import Account, JournalEntry, JournalLine
from app.models.bank_reconciliation import (
    BankStatement,
    BankStatementEntry,
    BankReconciliation,
    ReconciliationOutstandingItem,
)
from app.models.financial_period import FinancialYear, FinancialPeriod, PeriodClosing
from app.models.vendor import Vendor
from app.models.inkind_sponsorship import (
    InKindDonation,
    InKindConsumption,
    Sponsorship,
    SponsorshipPayment,
)
# IMPORTANT: BankReconciliation was moved to app.models.bank_reconciliation
# DO NOT import BankReconciliation from app.models.upi_banking
from app.models.upi_banking import UpiPayment, BankAccount, BankTransaction
from app.models.hundi import HundiOpening, HundiDenominationCount, HundiMaster
from app.models.inventory import Item, StockBalance, StockMovement, Store
from app.models.asset import (
    Asset,
    AssetCategory,
    CapitalWorkInProgress,
)
from app.models.asset_history import (
    AssetTransfer,
    AssetValuationHistory,
    AssetPhysicalVerification,
    AssetInsurance,
    AssetDocument,
)
from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
    GRN,
    GRNItem,
    GIN,
    GINItem,
)

# Note: BankReconciliation is now in app.models.bank_reconciliation (not upi_banking)

# Import routers
from app.api.panchang_display_settings import router as panchang_display_settings_router
from app.api.devotees import router as devotees_router
from app.api.donations import router as donations_router
from app.api.panchang import router as panchang_router
from app.api.auth import router as auth_router
from app.api.sevas import router as sevas_router
from app.api.seva_exchange import router as seva_exchange_router
from app.api.accounts import router as accounts_router
from app.api.journal_entries import router as journal_entries_router
from app.api.vendors import router as vendors_router
from app.api.upi_payments import router as upi_payments_router
from app.api.inkind_donations import router as inkind_donations_router
from app.api.sponsorships import router as sponsorships_router
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router
from app.api.sms_reminders import router as sms_reminders_router
from app.api.users import router as users_router
from app.api.audit_logs import router as audit_logs_router
from app.api.certificates import router as certificates_router
from app.api.bank_reconciliation import router as bank_reconciliation_router
from app.api.bank_accounts import router as bank_accounts_router
from app.api.financial_closing import router as financial_closing_router
from app.api.budget import router as budget_router
from app.api.license import router as license_router
from app.api.printer import router as printer_router
from app.api.temples import router as temples_router
from app.api.pincode import router as pincode_router
from app.api.opening_balances import router as opening_balances_router
from app.api.backup_restore import router as backup_restore_router
from app.api.temple_onboarding import router as temple_onboarding_router
from app.api.account_imports import router as account_imports_router
from app.api.opening_balance_imports import router as opening_balance_imports_router
from app.services.backup_scheduler import start_backup_scheduler, stop_backup_scheduler
from app.api.asset_reports import router as asset_reports_router
from app.api.inventory import router as inventory_router
from app.api.inventory_additional import router as inventory_additional_router
from app.api.inventory_alerts import router as inventory_alerts_router
from app.api.monitoring import router as monitoring_router
from app.api.hr import router as hr_router
from app.api.hundi import router as hundi_router
from app.api.tenders import router as tenders_router
from app.api.purchase_orders import router as purchase_orders_router
from app.api.stock_audit import router as stock_audit_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup + shutdown events"""
    # --- STARTUP ---
    _run_startup()
    yield
    # --- SHUTDOWN (add cleanup here if needed) ---
    stop_backup_scheduler()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Temple Management System API",
    docs_url="/docs" if settings.DEBUG else None,   # Hide Swagger in production
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

from app.core.jwt_middleware import JWTMiddleware

# Security headers middleware (add first)
app.add_middleware(SecurityHeadersMiddleware)

# JWT authentication middleware
app.add_middleware(JWTMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Serve static files from uploads directory
from fastapi.staticfiles import StaticFiles
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(auth_router)
app.include_router(panchang_display_settings_router)
app.include_router(devotees_router)
app.include_router(donations_router)
app.include_router(panchang_router)
app.include_router(sevas_router)
app.include_router(seva_exchange_router)
app.include_router(accounts_router)
app.include_router(journal_entries_router)
app.include_router(vendors_router)
app.include_router(upi_payments_router)
app.include_router(inkind_donations_router)
app.include_router(sponsorships_router)
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(sms_reminders_router)
app.include_router(users_router)
app.include_router(audit_logs_router)
app.include_router(certificates_router)
app.include_router(bank_reconciliation_router)
app.include_router(bank_accounts_router)
app.include_router(financial_closing_router)
app.include_router(budget_router)
app.include_router(license_router)
app.include_router(asset_reports_router)
app.include_router(printer_router)
app.include_router(temples_router)
app.include_router(pincode_router, prefix="/api/v1/pincode", tags=["pincode"])
app.include_router(opening_balances_router)
app.include_router(backup_restore_router)
app.include_router(temple_onboarding_router)
app.include_router(account_imports_router)
app.include_router(opening_balance_imports_router)
app.include_router(inventory_router)
app.include_router(inventory_additional_router)
app.include_router(inventory_alerts_router)
app.include_router(monitoring_router)
app.include_router(hr_router)
app.include_router(hundi_router)
app.include_router(tenders_router)
app.include_router(purchase_orders_router)
app.include_router(stock_audit_router)


def _validate_startup_security_config():
    """Fail fast for insecure settings in non-standalone/production-like deployments."""
    deployment_mode = (settings.DEPLOYMENT_MODE or "").lower()
    non_standalone_mode = deployment_mode != "standalone"
    issues = []

    if non_standalone_mode and settings.DEBUG:
        issues.append("DEBUG must be False when DEPLOYMENT_MODE is not 'standalone'.")

    # Strict secret checks for SaaS/non-standalone and any explicit non-debug mode.
    if non_standalone_mode or not settings.DEBUG:
        placeholder_values = {
            "your-secret-key-change-this",
            "your-jwt-secret-key-change-this",
            "changeme",
            "change-me",
            "secret",
        }
        secret_key = (settings.SECRET_KEY or "").strip()
        jwt_secret_key = (settings.JWT_SECRET_KEY or "").strip()

        if secret_key in placeholder_values or len(secret_key) < 32:
            issues.append(
                "SECRET_KEY must be set to a strong random value (minimum 32 chars)."
            )
        if jwt_secret_key in placeholder_values or len(jwt_secret_key) < 32:
            issues.append(
                "JWT_SECRET_KEY must be set to a strong random value (minimum 32 chars)."
            )
        if secret_key and jwt_secret_key and secret_key == jwt_secret_key:
            issues.append("SECRET_KEY and JWT_SECRET_KEY must be different values.")

    if issues:
        for issue in issues:
            print(f"[ERROR] {issue}")
        raise RuntimeError(
            "Startup blocked due to insecure configuration. "
            "Set secure secrets and disable DEBUG for production-like deployments."
        )


def _check_backup_path_writable():
    """Warn if configured backup path is not writable."""
    from pathlib import Path
    import uuid

    backup_path = Path(settings.BACKUP_PATH).expanduser()
    probe_file = backup_path / f".write_probe_{uuid.uuid4().hex}.tmp"
    try:
        backup_path.mkdir(parents=True, exist_ok=True)
        probe_file.write_text("ok", encoding="utf-8")
        probe_file.unlink(missing_ok=True)
        print(f"[OK] Backup path writable: {backup_path}")
    except Exception as e:
        print(
            f"[WARNING] BACKUP_PATH is not writable ({backup_path}). "
            f"Backup create/restore may fail. Details: {e}"
        )


def _run_startup():
    """Synchronous startup logic (called from lifespan context manager)"""
    _validate_startup_security_config()
    init_db()
    _check_backup_path_writable()
    if not os.environ.get("PYTEST_CURRENT_TEST"):
        start_backup_scheduler()

    # Run database integrity check (for tampering detection)
    try:
        from app.core.startup_integrity import (
            run_startup_integrity_check,
            print_integrity_check_results,
        )

        all_passed, messages = run_startup_integrity_check()
        print_integrity_check_results(messages)

        # Note: We don't fail startup if integrity check fails
        # This allows admin to investigate while system is running
        # In production, you might want to:
        # - Send email alert to admin
        # - Disable write operations (set READ_ONLY_MODE = True)
        # - Log to separate security log file
    except Exception as e:
        print(f"⚠️  Warning: Could not run integrity check: {str(e)}")
        # Don't fail startup if integrity check fails

    # Create temple from configuration (for standalone packages)
    try:
        from app.core.setup_wizard import create_temple_from_config
        from app.core.database import SessionLocal
        from pathlib import Path
        import sys

        # Get base directory - use STANDALONE_BASE_DIR if set, otherwise calculate
        if os.environ.get("STANDALONE_BASE_DIR"):
            base_dir = Path(os.environ["STANDALONE_BASE_DIR"])
        elif getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).parent.parent

        db = SessionLocal()
        try:
            temple = create_temple_from_config(db, base_dir)
            if temple:
                print(f"[OK] Temple configured: {temple.name}")
        finally:
            db.close()
    except Exception as e:
        print(f"[INFO] Temple configuration: {e}")

    # Apply module configuration from file (for standalone packages)
    try:
        from app.core.module_config_loader import apply_module_config_to_temples

        apply_module_config_to_temples()
    except Exception as e:
        print(f"[INFO] Module configuration: {e}")

    # Check license status on startup
    # NOTE: For development/testing, we completely skip license enforcement
    # so that all modules (seva booking, accounting, etc.) can be tested freely.
    # In production, set DEBUG=False to enable license checks.
    if settings.DEBUG:
        print("ℹ️  License checks are DISABLED in DEBUG mode. All features enabled for testing.")
        return

    from app.licensing import check_trial_status

    try:
        status = check_trial_status()
        if status.get("is_active"):
            print(f"✅ License Active: {status.get('message')}")
            if status.get("is_grace_period"):
                print(f"⚠️  WARNING: Grace period - {status.get('grace_days_left')} days remaining")
        else:
            print(f"⚠️  LICENSE WARNING: {status.get('message')}")
            print("   Some features may be restricted.")
    except Exception as e:
        print(f"ℹ️  No license found. Activate license to enable all features.")

    # Transfer advance seva bookings to income for yesterday's seva date (booking_date == today - 1)
    # This runs on startup to ensure any missed transfers are processed
    # We process yesterday's bookings because the seva date has definitely passed
    try:
        from app.core.database import SessionLocal
        from app.api.sevas import _transfer_advance_bookings_batch_internal
        from app.models.user import User
        from app.models.temple import Temple

        db = SessionLocal()
        try:
            # Process for all temples
            temples = db.query(Temple).all()
            total_transferred = 0

            for temple in temples:
                # Get first admin user for this temple for system-initiated transfer
                admin_user = (
                    db.query(User)
                    .filter(
                        User.temple_id == temple.id,
                        User.role.in_(["admin", "temple_manager", "accountant"]),
                        User.is_active == True,
                    )
                    .first()
                )

                if admin_user:
                    print(
                        f"🔄 Processing advance seva booking transfers for temple {temple.name} (yesterday's bookings)..."
                    )
                    result = _transfer_advance_bookings_batch_internal(db, temple.id, admin_user.id)
                    db.commit()
                    if result.get("transferred_count", 0) > 0:
                        total_transferred += result["transferred_count"]
                        print(
                            f"✅ Transferred {result['transferred_count']} advance booking(s) to Seva Income for {temple.name}"
                        )
                    if result.get("skipped_count", 0) > 0:
                        print(
                            f"ℹ️  Skipped {result.get('skipped_count')} booking(s) (not advance bookings or already transferred)"
                        )

            if total_transferred > 0:
                print(
                    f"✅ Total: Transferred {total_transferred} advance booking(s) to Seva Income across all temples"
                )
        except Exception as e:
            # Don't fail startup if transfer fails - just log it
            print(f"⚠️  Warning: Could not process advance booking transfers on startup: {str(e)}")
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        # Ignore errors in startup transfer - system should still start
        pass


@app.get("/")
@limiter.limit("60/minute")
async def root(request: Request):
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION}
