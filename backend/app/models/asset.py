"""
Asset Management Models
Tracks temple assets, procurement, depreciation, revaluation, and disposal
Following standard accounting practices and audit compliance
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    Date,
    ForeignKey,
    Enum as SQLEnum,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


# Enums


class AssetType(str, enum.Enum):
    """Asset types"""

    FIXED = "fixed"  # Land, buildings, vehicles
    MOVABLE = "movable"  # Furniture, equipment
    PRECIOUS = "precious"  # Gold, silver, precious metals
    INTANGIBLE = "intangible"  # Software, licenses
    CWIP = "cwip"  # Capital work in progress


class AssetStatus(str, enum.Enum):
    """Asset status"""

    ACTIVE = "active"
    UNDER_CONSTRUCTION = "under_construction"
    DISPOSED = "disposed"
    SOLD = "sold"
    SCRAPPED = "scrapped"
    DONATED = "donated"


class DisposalType(str, enum.Enum):
    """Asset disposal types"""

    SALE = "sale"
    SCRAP = "scrap"
    DONATION = "donation"
    LOSS = "loss"
    THEFT = "theft"


class MaintenanceType(str, enum.Enum):
    """Maintenance types"""

    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    ROUTINE = "routine"
    EMERGENCY = "emergency"


# Import depreciation methods enum (will be created)
try:
    from app.models.depreciation_methods import DepreciationMethod
except ImportError:
    # Fallback if not yet created
    class DepreciationMethod(str, enum.Enum):
        STRAIGHT_LINE = "straight_line"
        WDV = "wdv"
        DOUBLE_DECLINING = "double_declining"
        DECLINING_BALANCE = "declining_balance"
        UNITS_OF_PRODUCTION = "units_of_production"
        ANNUITY = "annuity"
        DEPLETION = "depletion"
        SINKING_FUND = "sinking_fund"
        NONE = "none"


# Models


class AssetCategory(Base):
    """Asset category master - Classification of assets"""

    __tablename__ = "asset_categories"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Category Details
    code = Column(String(20), nullable=False, index=True)  # FIXED, MOVABLE, PRECIOUS
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_category_id = Column(Integer, ForeignKey("asset_categories.id"), nullable=True)

    # Depreciation Defaults
    default_depreciation_method = Column(
        SQLEnum(DepreciationMethod), default=DepreciationMethod.STRAIGHT_LINE
    )
    default_useful_life_years = Column(Float, default=0.0)
    default_depreciation_rate_percent = Column(Float, default=0.0)  # For WDV/Double Declining
    is_depreciable = Column(Boolean, default=True)

    # Accounting Links
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)  # Asset account
    accumulated_depreciation_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    revaluation_reserve_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    parent_category = relationship("AssetCategory", remote_side=[id])
    assets = relationship("Asset", back_populates="category")

    def __repr__(self):
        return f"<AssetCategory(code='{self.code}', name='{self.name}')>"


class Asset(Base):
    """Asset Master - Main asset register"""

    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Asset Identification
    asset_number = Column(String(50), nullable=False, unique=True, index=True)  # AST001, AST002
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("asset_categories.id"), nullable=False)
    asset_type = Column(SQLEnum(AssetType), nullable=False)

    # Physical Identification
    location = Column(String(200))  # Physical location
    tag_number = Column(String(50))  # Physical tag number
    serial_number = Column(String(100))  # Manufacturer serial number
    identification_mark = Column(Text)  # Unique identification marks

    # Financial - Purchase
    purchase_date = Column(Date, nullable=False)
    original_cost = Column(Float, nullable=False, default=0.0)
    current_book_value = Column(Float, default=0.0)
    accumulated_depreciation = Column(Float, default=0.0)
    revalued_amount = Column(Float, default=0.0)  # If revalued
    revaluation_reserve = Column(Float, default=0.0)  # Revaluation reserve amount

    # Depreciation Configuration
    depreciation_method = Column(
        SQLEnum(DepreciationMethod), default=DepreciationMethod.STRAIGHT_LINE
    )
    useful_life_years = Column(Float, default=0.0)
    depreciation_rate_percent = Column(Float, default=0.0)  # For WDV, Declining Balance
    salvage_value = Column(Float, default=0.0)  # Residual value
    is_depreciable = Column(Boolean, default=True)
    depreciation_start_date = Column(Date, nullable=True)

    # For Units of Production Method
    total_estimated_units = Column(Float, nullable=True)  # Total production capacity/usage
    units_used_to_date = Column(Float, default=0.0)  # Cumulative units used

    # For Annuity Method
    interest_rate_percent = Column(Float, nullable=True)  # Discount rate

    # For Sinking Fund Method
    sinking_fund_interest_rate = Column(Float, nullable=True)
    sinking_fund_payments_per_year = Column(Integer, default=1)

    # Status
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.ACTIVE)
    cwip_id = Column(
        Integer, ForeignKey("capital_work_in_progress.id"), nullable=True
    )  # If under construction

    # Purchase Details
    purchase_invoice_number = Column(String(100))
    purchase_invoice_date = Column(Date)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    warranty_expiry_date = Column(Date, nullable=True)

    # Tender Process (Optional - for future implementation)
    tender_id = Column(
        Integer, ForeignKey("tenders.id"), nullable=True
    )  # If procured through tender

    # Accounting
    asset_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    temple = relationship("Temple")
    category = relationship("AssetCategory", back_populates="assets")
    vendor = relationship("Vendor")
    # Link to CWIP record (when this asset originated from a CWIP project)
    # This is a one-to-one relationship: Asset.cwip_id -> CapitalWorkInProgress.id
    # Since both sides have foreign keys, we don't use back_populates here
    # Instead, we'll define it unidirectionally from Asset to CWIP
    cwip = relationship("CapitalWorkInProgress", foreign_keys=[cwip_id], uselist=False)
    asset_account = relationship("Account", foreign_keys=[asset_account_id])
    depreciation_schedules = relationship("DepreciationSchedule", back_populates="asset")
    revaluations = relationship("AssetRevaluation", back_populates="asset")
    disposals = relationship("AssetDisposal", back_populates="asset")
    maintenance_records = relationship("AssetMaintenance", back_populates="asset")
    transfer_history = relationship(
        "AssetTransfer", back_populates="asset", cascade="all, delete-orphan"
    )
    valuation_history = relationship(
        "AssetValuationHistory", back_populates="asset", cascade="all, delete-orphan"
    )
    physical_verifications = relationship(
        "AssetPhysicalVerification", back_populates="asset", cascade="all, delete-orphan"
    )
    insurance_records = relationship(
        "AssetInsurance", back_populates="asset", cascade="all, delete-orphan"
    )
    documents = relationship("AssetDocument", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Asset(asset_number='{self.asset_number}', name='{self.name}')>"


class CapitalWorkInProgress(Base):
    """Capital Work in Progress - For construction/installation projects"""

    __tablename__ = "capital_work_in_progress"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Project Identification
    cwip_number = Column(String(50), nullable=False, unique=True, index=True)  # CWIP001
    project_name = Column(String(200), nullable=False)
    description = Column(Text)
    asset_category_id = Column(Integer, ForeignKey("asset_categories.id"), nullable=False)

    # Project Timeline
    start_date = Column(Date, nullable=False)
    expected_completion_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)

    # Financial
    total_budget = Column(Float, default=0.0)
    total_expenditure = Column(Float, default=0.0)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)  # CWIP account

    # Status
    status = Column(
        String(20), default="in_progress"
    )  # in_progress, completed, suspended, cancelled
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)  # When capitalized

    # Tender Process (Optional)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    temple = relationship("Temple")
    category = relationship("AssetCategory")
    # Link back to the capitalized asset, if any
    # This is a one-to-one relationship: CapitalWorkInProgress.asset_id -> Asset.id
    # Since both sides have foreign keys, we define it unidirectionally from CWIP to Asset
    asset = relationship("Asset", foreign_keys=[asset_id], uselist=False)
    cwip_account = relationship("Account", foreign_keys=[account_id])
    expenses = relationship("AssetExpense", back_populates="cwip")

    def __repr__(self):
        return f"<CapitalWorkInProgress(cwip_number='{self.cwip_number}', project_name='{self.project_name}')>"


class AssetExpense(Base):
    """Expenses for CWIP - Material, labor, overhead"""

    __tablename__ = "asset_expenses"

    id = Column(Integer, primary_key=True, index=True)
    cwip_id = Column(Integer, ForeignKey("capital_work_in_progress.id"), nullable=False)

    # Expense Details
    expense_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    expense_category = Column(String(50))  # MATERIAL, LABOR, OVERHEAD, OTHER
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    reference_number = Column(String(100))  # Bill/Invoice number

    # Accounting
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    cwip = relationship("CapitalWorkInProgress", back_populates="expenses")
    vendor = relationship("Vendor")
    journal_entry = relationship("JournalEntry")

    def __repr__(self):
        return f"<AssetExpense(amount={self.amount}, description='{self.description}')>"


class DepreciationSchedule(Base):
    """Depreciation schedule - Records depreciation for each period"""

    __tablename__ = "depreciation_schedules"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    # Period Details
    financial_year = Column(String(10), nullable=False, index=True)  # 2024-25
    period = Column(String(20), default="yearly")  # MONTHLY, YEARLY
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    # Depreciation Calculation
    depreciation_method_used = Column(SQLEnum(DepreciationMethod), nullable=False)
    opening_book_value = Column(Float, nullable=False)
    depreciation_amount = Column(Float, nullable=False)
    closing_book_value = Column(Float, nullable=False)
    depreciation_rate = Column(Float, nullable=True)  # If applicable

    # For Units of Production
    units_produced_this_period = Column(Float, nullable=True)
    total_units_produced_to_date = Column(Float, nullable=True)

    # For Annuity Method
    interest_component = Column(Float, nullable=True)
    principal_component = Column(Float, nullable=True)

    # Accounting
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    posted_date = Column(Date, nullable=True)
    status = Column(String(20), default="calculated")  # calculated, posted, cancelled

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    asset = relationship("Asset", back_populates="depreciation_schedules")
    journal_entry = relationship("JournalEntry")

    def __repr__(self):
        return f"<DepreciationSchedule(asset_id={self.asset_id}, period='{self.period}', amount={self.depreciation_amount})>"


class AssetRevaluation(Base):
    """Asset revaluation records"""

    __tablename__ = "asset_revaluations"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    # Revaluation Details
    revaluation_date = Column(Date, nullable=False)
    revaluation_type = Column(String(20), nullable=False)  # INCREASE, DECREASE

    # Valuation
    previous_book_value = Column(Float, nullable=False)
    revalued_amount = Column(Float, nullable=False)
    revaluation_amount = Column(Float, nullable=False)  # Difference

    # Valuation Method
    valuation_method = Column(String(50))  # MARKET_VALUE, PROFESSIONAL_VALUER, INDEX_BASED
    valuer_name = Column(String(200))
    valuation_report_number = Column(String(100))
    valuation_report_date = Column(Date, nullable=True)

    # Accounting
    revaluation_reserve_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    asset = relationship("Asset", back_populates="revaluations")
    revaluation_reserve_account = relationship(
        "Account", foreign_keys=[revaluation_reserve_account_id]
    )
    journal_entry = relationship("JournalEntry")

    def __repr__(self):
        return f"<AssetRevaluation(asset_id={self.asset_id}, revaluation_amount={self.revaluation_amount})>"


class AssetDisposal(Base):
    """Asset disposal records"""

    __tablename__ = "asset_disposals"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    # Disposal Details
    disposal_date = Column(Date, nullable=False)
    disposal_type = Column(SQLEnum(DisposalType), nullable=False)
    disposal_reason = Column(Text)

    # Financial
    book_value_at_disposal = Column(Float, nullable=False)
    accumulated_depreciation_at_disposal = Column(Float, nullable=False)
    disposal_proceeds = Column(Float, default=0.0)  # If sold
    gain_loss_amount = Column(Float, default=0.0)  # Gain (positive) or Loss (negative)

    # Details
    buyer_name = Column(String(200))  # If sold
    disposal_document_number = Column(String(100))

    # Approval Workflow
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Accounting
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    asset = relationship("Asset", back_populates="disposals")
    journal_entry = relationship("JournalEntry")
    approved_by_user = relationship("User", foreign_keys=[approved_by])

    def __repr__(self):
        return f"<AssetDisposal(asset_id={self.asset_id}, disposal_type='{self.disposal_type}')>"


class AssetMaintenance(Base):
    """Asset maintenance records"""

    __tablename__ = "asset_maintenance"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    # Maintenance Details
    maintenance_date = Column(Date, nullable=False)
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False)
    description = Column(Text, nullable=False)
    cost = Column(Float, default=0.0)

    # Vendor/Service Provider
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    service_provider_name = Column(String(200))

    # Next Maintenance
    next_maintenance_date = Column(Date, nullable=True)
    next_maintenance_notes = Column(Text)

    # Accounting (if capitalized)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    is_capitalized = Column(Boolean, default=False)  # If added to asset cost

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    asset = relationship("Asset", back_populates="maintenance_records")
    vendor = relationship("Vendor")
    journal_entry = relationship("JournalEntry")

    def __repr__(self):
        return f"<AssetMaintenance(asset_id={self.asset_id}, maintenance_type='{self.maintenance_type}')>"


# Tender Process Models (Optional - for future implementation)
# These are designed but not required for basic asset procurement
# Can be enabled when needed


class Tender(Base):
    """
    Tender Process - Optional feature for transparent procurement
    Can be enabled/disabled based on temple requirements
    Many small temples don't need this, larger temples do
    """

    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # Tender Identification
    tender_number = Column(String(50), nullable=False, unique=True, index=True)  # TND001
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Tender Details
    tender_type = Column(String(50))  # ASSET_PROCUREMENT, INVENTORY_PURCHASE, CONSTRUCTION, SERVICE
    estimated_value = Column(Float, default=0.0)

    # Timeline
    tender_issue_date = Column(Date, nullable=False)
    last_date_submission = Column(Date, nullable=False)
    opening_date = Column(Date, nullable=True)
    award_date = Column(Date, nullable=True)

    # Status
    status = Column(String(50), default="draft")  # draft, published, closed, awarded, cancelled

    # Documents
    tender_document_path = Column(String(500))  # Path to tender document
    terms_conditions = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    temple = relationship("Temple")
    bids = relationship("TenderBid", back_populates="tender")

    def __repr__(self):
        return f"<Tender(tender_number='{self.tender_number}', title='{self.title}')>"


class TenderBid(Base):
    """Tender bids from vendors"""

    __tablename__ = "tender_bids"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    # Bid Details
    bid_amount = Column(Float, nullable=False)
    bid_date = Column(Date, nullable=False)
    validity_period_days = Column(Integer, default=90)

    # Status
    status = Column(String(50), default="submitted")  # submitted, shortlisted, rejected, awarded

    # Documents
    bid_document_path = Column(String(500))
    technical_specifications = Column(Text)

    # Evaluation
    technical_score = Column(Float, nullable=True)
    financial_score = Column(Float, nullable=True)
    total_score = Column(Float, nullable=True)
    evaluation_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime, nullable=True)
    evaluated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    tender = relationship("Tender", back_populates="bids")
    vendor = relationship("Vendor")

    def __repr__(self):
        return f"<TenderBid(tender_id={self.tender_id}, vendor_id={self.vendor_id}, bid_amount={self.bid_amount})>"
