"""
Asset History Models
Handles asset transfer history, valuation history, physical verification, and insurance tracking
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Date, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class VerificationStatus(str, enum.Enum):
    """Physical verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    DISCREPANCY = "discrepancy"
    NOT_FOUND = "not_found"


class AssetTransfer(Base):
    """Asset Transfer History"""
    __tablename__ = "asset_transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transfer Details
    transfer_date = Column(Date, nullable=False, index=True)
    from_location = Column(String(200))  # Previous location
    to_location = Column(String(200), nullable=False)  # New location
    transfer_reason = Column(Text)
    
    # Transfer Authorization
    transferred_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    temple = relationship("Temple")
    asset = relationship("Asset", back_populates="transfer_history")
    transferred_by_user = relationship("User", foreign_keys=[transferred_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])


class AssetValuationHistory(Base):
    """Asset Valuation History Timeline"""
    __tablename__ = "asset_valuation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Valuation Details
    valuation_date = Column(Date, nullable=False, index=True)
    valuation_type = Column(String(50), nullable=False)  # PURCHASE, REVALUATION, MARKET_VALUE, INSURANCE, DISPOSAL
    valuation_amount = Column(Float, nullable=False)
    
    # Valuation Method
    valuation_method = Column(String(50))  # MARKET_VALUE, PROFESSIONAL_VALUER, INDEX_BASED, COST_BASED
    valuer_name = Column(String(200))
    valuation_report_number = Column(String(100))
    valuation_report_date = Column(Date, nullable=True)
    
    # Reference
    reference_id = Column(Integer, nullable=True)  # ID of revaluation or disposal record
    reference_type = Column(String(50))  # revaluation, disposal, purchase
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    asset = relationship("Asset", back_populates="valuation_history")
    created_by_user = relationship("User")


class AssetPhysicalVerification(Base):
    """Asset Physical Verification Records"""
    __tablename__ = "asset_physical_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Verification Details
    verification_date = Column(Date, nullable=False, index=True)
    verification_number = Column(String(50), unique=True, nullable=False, index=True)  # VER/2025/001
    status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, index=True)
    
    # Physical Check
    verified_location = Column(String(200))  # Where asset was found
    condition = Column(String(50))  # GOOD, FAIR, POOR, DAMAGED
    condition_notes = Column(Text)
    
    # Verification Team
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    verified_by_second = Column(Integer, ForeignKey("users.id"), nullable=True)  # Second verifier
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Dates
    verified_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Discrepancy
    has_discrepancy = Column(Boolean, default=False)
    discrepancy_details = Column(Text)
    
    # Photos/Documents
    photo_urls = Column(Text)  # JSON array of photo URLs
    document_urls = Column(Text)  # JSON array of document URLs
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    temple = relationship("Temple")
    asset = relationship("Asset", back_populates="physical_verifications")
    verified_by_user = relationship("User", foreign_keys=[verified_by])
    verified_by_second_user = relationship("User", foreign_keys=[verified_by_second])
    approved_by_user = relationship("User", foreign_keys=[approved_by])


class AssetInsurance(Base):
    """Asset Insurance Tracking"""
    __tablename__ = "asset_insurance"
    
    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Insurance Details
    policy_number = Column(String(100), nullable=False)
    insurance_company = Column(String(200), nullable=False)
    policy_start_date = Column(Date, nullable=False)
    policy_end_date = Column(Date, nullable=False, index=True)
    premium_amount = Column(Float, default=0.0)
    insured_value = Column(Float, nullable=False)
    
    # Coverage
    coverage_type = Column(String(50))  # FIRE, THEFT, DAMAGE, COMPREHENSIVE
    coverage_details = Column(Text)
    
    # Renewal
    auto_renewal = Column(Boolean, default=False)
    renewal_reminder_days = Column(Integer, default=30)  # Days before expiry to remind
    
    # Contact
    agent_name = Column(String(200))
    agent_contact = Column(String(100))
    
    # Documents
    policy_document_url = Column(String(500))
    claim_history = Column(Text)  # JSON array of claims
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    temple = relationship("Temple")
    asset = relationship("Asset", back_populates="insurance_records")
    created_by_user = relationship("User")


class AssetDocument(Base):
    """Asset Documents and Images"""
    __tablename__ = "asset_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document Details
    document_type = Column(String(50), nullable=False)  # IMAGE, INVOICE, WARRANTY, MANUAL, CERTIFICATE, OTHER
    document_name = Column(String(200), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))  # image/jpeg, application/pdf, etc.
    
    # Description
    description = Column(Text)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    asset = relationship("Asset", back_populates="documents")
    uploaded_by_user = relationship("User")



