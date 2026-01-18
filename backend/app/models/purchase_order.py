"""
Purchase Order Models
Handles purchase orders, GRN (Goods Receipt Note), and GIN (Goods Issue Note)
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


class POStatus(str, enum.Enum):
    """Purchase Order Status"""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class GRNStatus(str, enum.Enum):
    """GRN Status"""

    PENDING = "pending"
    RECEIVED = "received"
    PARTIALLY_RECEIVED = "partially_received"
    REJECTED = "rejected"


class GINStatus(str, enum.Enum):
    """GIN Status"""

    DRAFT = "draft"
    APPROVED = "approved"
    ISSUED = "issued"
    CANCELLED = "cancelled"


class PurchaseOrder(Base):
    """Purchase Order Master"""

    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # PO Details
    po_number = Column(String(50), unique=True, nullable=False, index=True)  # PO/2025/001
    po_date = Column(Date, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    # Status
    status = Column(SQLEnum(POStatus), default=POStatus.DRAFT, index=True)

    # Approval
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Totals
    total_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)

    # Delivery
    expected_delivery_date = Column(Date, nullable=True)
    delivery_address = Column(Text, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    vendor = relationship("Vendor")
    requested_by_user = relationship("User", foreign_keys=[requested_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    po_items = relationship(
        "PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan"
    )
    grns = relationship("GRN", back_populates="purchase_order")


class PurchaseOrderItem(Base):
    """Purchase Order Items"""

    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(
        Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)

    # Quantity
    ordered_quantity = Column(Float, nullable=False)
    received_quantity = Column(Float, default=0.0)  # Track received quantity
    pending_quantity = Column(Float, default=0.0)  # ordered - received

    # Pricing
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)

    # Store
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="po_items")
    item = relationship("Item")
    store = relationship("Store")


class GRN(Base):
    """Goods Receipt Note"""

    __tablename__ = "grns"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # GRN Details
    grn_number = Column(String(50), unique=True, nullable=False, index=True)  # GRN/2025/001
    grn_date = Column(Date, nullable=False, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    # Status
    status = Column(SQLEnum(GRNStatus), default=GRNStatus.PENDING, index=True)

    # Receipt Details
    bill_number = Column(String(100), nullable=True)
    bill_date = Column(Date, nullable=True)
    received_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    received_at = Column(DateTime, nullable=True)

    # Totals
    total_amount = Column(Float, default=0.0)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    purchase_order = relationship("PurchaseOrder", back_populates="grns")
    vendor = relationship("Vendor")
    received_by_user = relationship("User", foreign_keys=[received_by])
    grn_items = relationship("GRNItem", back_populates="grn", cascade="all, delete-orphan")
    stock_movement = relationship("StockMovement", back_populates="grn", uselist=False)


class GRNItem(Base):
    """GRN Items"""

    __tablename__ = "grn_items"

    id = Column(Integer, primary_key=True, index=True)
    grn_id = Column(Integer, ForeignKey("grns.id", ondelete="CASCADE"), nullable=False, index=True)
    po_item_id = Column(Integer, ForeignKey("purchase_order_items.id"), nullable=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)

    # Quantity
    ordered_quantity = Column(Float, nullable=False)  # From PO
    received_quantity = Column(Float, nullable=False)
    accepted_quantity = Column(Float, nullable=False)  # After quality check
    rejected_quantity = Column(Float, default=0.0)

    # Pricing
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)

    # Store
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)

    # Expiry Date (if applicable)
    expiry_date = Column(Date, nullable=True)
    batch_number = Column(String(100), nullable=True)

    # Quality Check
    quality_checked = Column(Boolean, default=False)
    quality_checked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    quality_notes = Column(Text, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    grn = relationship("GRN", back_populates="grn_items")
    po_item = relationship("PurchaseOrderItem")
    item = relationship("Item")
    store = relationship("Store")
    quality_checker = relationship("User", foreign_keys=[quality_checked_by])


class GIN(Base):
    """Goods Issue Note"""

    __tablename__ = "gins"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)

    # GIN Details
    gin_number = Column(String(50), unique=True, nullable=False, index=True)  # GIN/2025/001
    gin_date = Column(Date, nullable=False, index=True)

    # Status
    status = Column(SQLEnum(GINStatus), default=GINStatus.DRAFT, index=True)

    # Issue Details
    issued_from_store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    issued_to = Column(String(200), nullable=False)  # Person/department
    purpose = Column(String(200), nullable=False)  # Pooja, Annadanam, Maintenance, etc.

    # Approval
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    issued_at = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    temple = relationship("Temple")
    issued_from_store = relationship("Store", foreign_keys=[issued_from_store_id])
    requested_by_user = relationship("User", foreign_keys=[requested_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    issued_by_user = relationship("User", foreign_keys=[issued_by])
    gin_items = relationship("GINItem", back_populates="gin", cascade="all, delete-orphan")
    stock_movement = relationship("StockMovement", back_populates="gin", uselist=False)


class GINItem(Base):
    """GIN Items"""

    __tablename__ = "gin_items"

    id = Column(Integer, primary_key=True, index=True)
    gin_id = Column(Integer, ForeignKey("gins.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)

    # Quantity
    requested_quantity = Column(Float, nullable=False)
    issued_quantity = Column(Float, nullable=False)

    # Pricing (for valuation)
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    gin = relationship("GIN", back_populates="gin_items")
    item = relationship("Item")
