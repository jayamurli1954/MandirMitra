"""
MandirSync - Temple Management System
FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db

# Import all models to ensure they're registered with SQLAlchemy
# This must happen before init_db() is called
from app.models.temple import Temple
from app.models.user import User
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine
from app.models.vendor import Vendor
from app.models.inkind_sponsorship import (
    InKindDonation, InKindConsumption,
    Sponsorship, SponsorshipPayment
)
from app.models.upi_banking import (
    UpiPayment, BankAccount, BankTransaction, BankReconciliation
)
from app.models.financial_period import FinancialYear, FinancialPeriod, PeriodClosing
from app.models.budget import Budget, BudgetItem, BudgetRevision
from app.models.asset import Asset, AssetCategory, AssetDisposal, AssetRevaluation
from app.models.asset_history import AssetTransfer, AssetValuationHistory, AssetPhysicalVerification, AssetInsurance, AssetDocument
from app.models.inventory import Store, Item, StockBalance, StockMovement
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, GRN, GRNItem, GIN, GINItem

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
from app.api.financial_closing import router as financial_closing_router
from app.api.budget import router as budget_router
from app.api.fcra import router as fcra_router
from app.api.tds_gst import router as tds_gst_router
from app.api.inventory import router as inventory_router
from app.api.inventory_alerts import router as inventory_alerts_router
from app.api.stock_audit import router as stock_audit_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Temple Management System API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(financial_closing_router)
app.include_router(budget_router)
app.include_router(fcra_router)
app.include_router(tds_gst_router)
app.include_router(inventory_router)
app.include_router(inventory_alerts_router)
app.include_router(stock_audit_router)
app.include_router(purchase_orders_router)
app.include_router(asset_router)
app.include_router(asset_management_router)
app.include_router(asset_reports_router)

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

