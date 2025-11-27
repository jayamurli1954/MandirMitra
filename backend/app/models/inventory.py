"""
Inventory Management Models
Tracks temple inventory items, stores, stock movements, and balances
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Date, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


# Enums

class StockMovementType(str, enum.Enum):
    """Types of stock movements"""
    PURCHASE = "purchase"  # Stock in - Purchase from vendor
    ISSUE = "issue"  # Stock out - Issue to temple use (pooja, kitchen, maintenance)
    ADJUSTMENT = "adjustment"  # Stock adjustment (shortage, excess, write-off)
    TRANSFER = "transfer"  # Transfer between stores
    RETURN = "return"  # Return from issue (if item not used)
    SALES = "sales"  # Sales to devotees (if applicable)


class ItemCategory(str, enum.Enum):
    """Inventory item categories"""
    POOJA_MATERIAL = "pooja_material"  # Camphor, kumkum, flowers, etc.
    GROCERY = "grocery"  # Rice, dal, oil, spices for annadanam
    CLEANING = "cleaning"  # Soap, detergent, cleaning supplies
    MAINTENANCE = "maintenance"  # Electrical items, plumbing, etc.
    GENERAL = "general"  # Other items


class Unit(str, enum.Enum):
    """Units of measurement"""
    KG = "kg"
    GRAM = "gram"
    LITRE = "litre"
    ML = "ml"
    PIECE = "piece"
    PACKET = "packet"
    BOX = "box"
    BOTTLE = "bottle"
    BAG = "bag"


# Models

class Store(Base):
    """Store/Location master - Different storage locations in temple"""
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # Store Details
    code = Column(String(20), nullable=False, index=True)  # ST001, ST002, etc.
    name = Column(String(100), nullable=False)  # Main Store, Kitchen Store, Hundi Room
    location = Column(String(200))  # Physical location description
    is_active = Column(Boolean, default=True)
    
    # Accounting Link - Inventory account for this store
    inventory_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    temple = relationship("Temple")
    inventory_account = relationship("Account")
    stock_balances = relationship("StockBalance", back_populates="store")
    
    def __repr__(self):
        return f"<Store(code='{self.code}', name='{self.name}')>"


class Item(Base):
    """Inventory Item Master"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # Item Identification
    code = Column(String(50), nullable=False, index=True)  # ITM001, ITM002, etc.
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Item Details
    category = Column(SQLEnum(ItemCategory), nullable=False, default=ItemCategory.GENERAL)
    unit = Column(SQLEnum(Unit), nullable=False, default=Unit.PIECE)
    
    # Stock Management
    reorder_level = Column(Float, default=0.0)  # Minimum stock level
    reorder_quantity = Column(Float, default=0.0)  # Quantity to order when below reorder level
    has_expiry = Column(Boolean, default=False)  # Whether item has expiry date
    shelf_life_days = Column(Integer, nullable=True)  # Shelf life in days (if applicable)
    
    # Pricing (optional - for valuation)
    standard_cost = Column(Float, default=0.0)  # Standard cost per unit
    
    # GST Information (if applicable)
    hsn_code = Column(String(20))
    gst_rate = Column(Float, default=0.0)  # GST percentage
    
    # Accounting Links
    inventory_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)  # Inventory asset account
    expense_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)  # Expense account when consumed
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    temple = relationship("Temple")
    inventory_account = relationship("Account", foreign_keys=[inventory_account_id])
    expense_account = relationship("Account", foreign_keys=[expense_account_id])
    stock_balances = relationship("StockBalance", back_populates="item")
    movements = relationship("StockMovement", back_populates="item")
    
    def __repr__(self):
        return f"<Item(code='{self.code}', name='{self.name}')>"


class StockBalance(Base):
    """Current stock balance for each item in each store"""
    __tablename__ = "stock_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # References
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    
    # Balance
    quantity = Column(Float, nullable=False, default=0.0)
    value = Column(Float, nullable=False, default=0.0)  # Total value = quantity * standard_cost
    
    # Expiry tracking (for items with expiry dates)
    earliest_expiry_date = Column(Date, nullable=True, index=True)  # Earliest expiry in stock
    batch_numbers = Column(Text, nullable=True)  # JSON array of batch numbers
    
    # Last movement
    last_movement_date = Column(Date)
    last_movement_id = Column(Integer, ForeignKey("stock_movements.id"), nullable=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    temple = relationship("Temple")
    item = relationship("Item", back_populates="stock_balances")
    store = relationship("Store", back_populates="stock_balances")
    last_movement = relationship("StockMovement", foreign_keys=[last_movement_id])
    
    def __repr__(self):
        return f"<StockBalance(item_id={self.item_id}, store_id={self.store_id}, qty={self.quantity})>"


class StockMovement(Base):
    """Stock movement transactions (Purchase, Issue, Adjustment, Transfer, etc.)"""
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    
    # Movement Details
    movement_type = Column(SQLEnum(StockMovementType), nullable=False, index=True)
    movement_number = Column(String(50), unique=True, nullable=False, index=True)  # PUR/2025/001, ISS/2025/001, etc.
    movement_date = Column(Date, nullable=False, index=True)
    
    # References
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)  # Source or destination store
    
    # For transfers - destination store
    to_store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    
    # Link to GRN/GIN
    grn_id = Column(Integer, ForeignKey("grns.id"), nullable=True, index=True)
    gin_id = Column(Integer, ForeignKey("gins.id"), nullable=True, index=True)
    
    # Quantity and Value
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, default=0.0)  # Price per unit (for purchase) or cost (for issue)
    total_value = Column(Float, nullable=False)  # quantity * unit_price
    
    # Additional Details
    reference_number = Column(String(100))  # Bill number, issue slip number, etc.
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)  # For purchases
    issued_to = Column(String(200))  # Person/department who received (for issues)
    purpose = Column(String(200))  # Purpose of issue (Pooja, Annadanam, Maintenance, etc.)
    notes = Column(Text)
    
    # Expiry Date (for items with expiry)
    expiry_date = Column(Date, nullable=True, index=True)
    batch_number = Column(String(100), nullable=True)
    
    # Accounting
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)  # Linked journal entry
    
    # User who created
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    temple = relationship("Temple")
    item = relationship("Item", back_populates="movements")
    store = relationship("Store", foreign_keys=[store_id])
    to_store = relationship("Store", foreign_keys=[to_store_id])
    vendor = relationship("Vendor")
    journal_entry = relationship("JournalEntry")
    creator = relationship("User")
    grn = relationship("GRN", back_populates="stock_movement")
    gin = relationship("GIN", back_populates="stock_movement")
    
    def __repr__(self):
        return f"<StockMovement(number='{self.movement_number}', type='{self.movement_type}', qty={self.quantity})>"


