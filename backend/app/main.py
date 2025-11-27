"""
MandirSync - Temple Management System
FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.core.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
    AppException
)
from app.core.security_headers import SecurityHeadersMiddleware
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import RequestValidationError

# Import all models to ensure they're registered with SQLAlchemy
# This must happen before init_db() is called
from app.models.temple import Temple
from app.models.user import User
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine
from app.models.bank_reconciliation import BankStatement, BankStatementEntry, BankReconciliation, ReconciliationOutstandingItem
from app.models.financial_period import FinancialYear, FinancialPeriod, PeriodClosing
from app.models.vendor import Vendor
from app.models.token_seva import TokenInventory, TokenSale, TokenReconciliation
from app.models.inkind_sponsorship import (
    InKindDonation, InKindConsumption,
    Sponsorship, SponsorshipPayment
)
from app.models.upi_banking import (
    UpiPayment, BankAccount, BankTransaction
)
from app.models.inventory import (
    Store, Item, StockBalance, StockMovement
)
from app.models.asset import (
    Asset, AssetCategory, CapitalWorkInProgress, AssetExpense,
    DepreciationSchedule, AssetRevaluation, AssetDisposal, AssetMaintenance,
    Tender, TenderBid
)
from app.models.hr import (
    Employee, Department, Designation, SalaryComponent, SalaryStructure,
    SalaryStructureComponent, Payroll, PayrollComponent, LeaveType, LeaveApplication
)
# Note: BankReconciliation is now in app.models.bank_reconciliation (not upi_banking)

# Import routers
from app.api.panchang_display_settings import router as panchang_display_settings_router
from app.api.devotees import router as devotees_router
from app.api.donations import router as donations_router
from app.api.panchang import router as panchang_router
from app.api.auth import router as auth_router
from app.api.sevas import router as sevas_router
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
from app.api.financial_closing import router as financial_closing_router
from app.api.token_seva import router as token_seva_router
from app.api.inventory import router as inventory_router
from app.api.asset import router as asset_router
from app.api.cwip import router as cwip_router
from app.api.depreciation import router as depreciation_router
from app.api.revaluation import router as revaluation_router
from app.api.disposal import router as disposal_router
from app.api.asset_reports import router as asset_reports_router
from app.api.tenders import router as tenders_router
from app.api.temples import router as temples_router
from app.api.hr import router as hr_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Temple Management System API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security headers middleware (add first)
app.add_middleware(SecurityHeadersMiddleware)

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

# Include routers
app.include_router(auth_router)
app.include_router(panchang_display_settings_router)
app.include_router(devotees_router)
app.include_router(donations_router)
app.include_router(panchang_router)
app.include_router(sevas_router)
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
app.include_router(financial_closing_router)
app.include_router(token_seva_router)
app.include_router(inventory_router)
app.include_router(asset_router)
app.include_router(cwip_router)
app.include_router(depreciation_router)
app.include_router(revaluation_router)
app.include_router(disposal_router)
app.include_router(asset_reports_router)
app.include_router(tenders_router)
app.include_router(temples_router)
app.include_router(hr_router)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    init_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

