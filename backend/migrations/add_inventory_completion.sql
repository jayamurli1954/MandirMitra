-- Migration: Complete Inventory Module (100%)
-- Adds Purchase Orders, GRN, GIN, Expiry Tracking, Low Stock Alerts

-- ===== ADD EXPIRY FIELDS TO ITEMS =====
ALTER TABLE items
ADD COLUMN IF NOT EXISTS has_expiry BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS shelf_life_days INTEGER;

COMMENT ON COLUMN items.has_expiry IS 'Whether item has expiry date';
COMMENT ON COLUMN items.shelf_life_days IS 'Shelf life in days (if applicable)';

-- ===== PURCHASE ORDERS =====
CREATE TABLE IF NOT EXISTS purchase_orders (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    po_number VARCHAR(50) NOT NULL UNIQUE,
    po_date DATE NOT NULL,
    vendor_id INTEGER REFERENCES vendors(id) ON DELETE CASCADE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    requested_by INTEGER REFERENCES users(id) ON DELETE SET NULL NOT NULL,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    total_amount NUMERIC(15, 2) DEFAULT 0.00,
    tax_amount NUMERIC(15, 2) DEFAULT 0.00,
    grand_total NUMERIC(15, 2) DEFAULT 0.00,
    expected_delivery_date DATE,
    delivery_address TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_po_temple ON purchase_orders(temple_id);
CREATE INDEX IF NOT EXISTS idx_po_number ON purchase_orders(po_number);
CREATE INDEX IF NOT EXISTS idx_po_vendor ON purchase_orders(vendor_id);
CREATE INDEX IF NOT EXISTS idx_po_status ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_po_date ON purchase_orders(po_date);

CREATE TABLE IF NOT EXISTS purchase_order_items (
    id SERIAL PRIMARY KEY,
    po_id INTEGER REFERENCES purchase_orders(id) ON DELETE CASCADE NOT NULL,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE NOT NULL,
    ordered_quantity NUMERIC(15, 3) NOT NULL,
    received_quantity NUMERIC(15, 3) DEFAULT 0.00,
    pending_quantity NUMERIC(15, 3) DEFAULT 0.00,
    unit_price NUMERIC(15, 2) NOT NULL,
    total_amount NUMERIC(15, 2) NOT NULL,
    store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_po_items_po ON purchase_order_items(po_id);
CREATE INDEX IF NOT EXISTS idx_po_items_item ON purchase_order_items(item_id);

-- ===== GRN (GOODS RECEIPT NOTE) =====
CREATE TABLE IF NOT EXISTS grns (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    grn_number VARCHAR(50) NOT NULL UNIQUE,
    grn_date DATE NOT NULL,
    po_id INTEGER REFERENCES purchase_orders(id) ON DELETE SET NULL,
    vendor_id INTEGER REFERENCES vendors(id) ON DELETE CASCADE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    bill_number VARCHAR(100),
    bill_date DATE,
    received_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    received_at TIMESTAMPTZ,
    total_amount NUMERIC(15, 2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_grn_temple ON grns(temple_id);
CREATE INDEX IF NOT EXISTS idx_grn_number ON grns(grn_number);
CREATE INDEX IF NOT EXISTS idx_grn_po ON grns(po_id);
CREATE INDEX IF NOT EXISTS idx_grn_vendor ON grns(vendor_id);
CREATE INDEX IF NOT EXISTS idx_grn_status ON grns(status);
CREATE INDEX IF NOT EXISTS idx_grn_date ON grns(grn_date);

CREATE TABLE IF NOT EXISTS grn_items (
    id SERIAL PRIMARY KEY,
    grn_id INTEGER REFERENCES grns(id) ON DELETE CASCADE NOT NULL,
    po_item_id INTEGER REFERENCES purchase_order_items(id) ON DELETE SET NULL,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE NOT NULL,
    ordered_quantity NUMERIC(15, 3) NOT NULL,
    received_quantity NUMERIC(15, 3) NOT NULL,
    accepted_quantity NUMERIC(15, 3) NOT NULL,
    rejected_quantity NUMERIC(15, 3) DEFAULT 0.00,
    unit_price NUMERIC(15, 2) NOT NULL,
    total_amount NUMERIC(15, 2) NOT NULL,
    store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE NOT NULL,
    expiry_date DATE,
    batch_number VARCHAR(100),
    quality_checked BOOLEAN DEFAULT FALSE,
    quality_checked_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    quality_notes TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_grn_items_grn ON grn_items(grn_id);
CREATE INDEX IF NOT EXISTS idx_grn_items_item ON grn_items(item_id);
CREATE INDEX IF NOT EXISTS idx_grn_items_expiry ON grn_items(expiry_date);

-- ===== GIN (GOODS ISSUE NOTE) =====
CREATE TABLE IF NOT EXISTS gins (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    gin_number VARCHAR(50) NOT NULL UNIQUE,
    gin_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    issued_from_store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE NOT NULL,
    issued_to VARCHAR(200) NOT NULL,
    purpose VARCHAR(200) NOT NULL,
    requested_by INTEGER REFERENCES users(id) ON DELETE SET NULL NOT NULL,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    issued_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    issued_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gin_temple ON gins(temple_id);
CREATE INDEX IF NOT EXISTS idx_gin_number ON gins(gin_number);
CREATE INDEX IF NOT EXISTS idx_gin_status ON gins(status);
CREATE INDEX IF NOT EXISTS idx_gin_date ON gins(gin_date);
CREATE INDEX IF NOT EXISTS idx_gin_store ON gins(issued_from_store_id);

CREATE TABLE IF NOT EXISTS gin_items (
    id SERIAL PRIMARY KEY,
    gin_id INTEGER REFERENCES gins(id) ON DELETE CASCADE NOT NULL,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE NOT NULL,
    requested_quantity NUMERIC(15, 3) NOT NULL,
    issued_quantity NUMERIC(15, 3) NOT NULL,
    unit_cost NUMERIC(15, 2) DEFAULT 0.00,
    total_cost NUMERIC(15, 2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gin_items_gin ON gin_items(gin_id);
CREATE INDEX IF NOT EXISTS idx_gin_items_item ON gin_items(item_id);

-- ===== ADD GRN/GIN LINKS TO STOCK MOVEMENTS =====
ALTER TABLE stock_movements
ADD COLUMN IF NOT EXISTS grn_id INTEGER REFERENCES grns(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS gin_id INTEGER REFERENCES gins(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS expiry_date DATE,
ADD COLUMN IF NOT EXISTS batch_number VARCHAR(100);

CREATE INDEX IF NOT EXISTS idx_stock_movements_grn ON stock_movements(grn_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_gin ON stock_movements(gin_id);

-- ===== LOW STOCK ALERTS TABLE =====
CREATE TABLE IF NOT EXISTS low_stock_alerts (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE NOT NULL,
    store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE NOT NULL,
    current_quantity NUMERIC(15, 3) NOT NULL,
    reorder_level NUMERIC(15, 3) NOT NULL,
    alert_date DATE NOT NULL,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    acknowledged_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_low_stock_temple ON low_stock_alerts(temple_id);
CREATE INDEX IF NOT EXISTS idx_low_stock_item ON low_stock_alerts(item_id);
CREATE INDEX IF NOT EXISTS idx_low_stock_store ON low_stock_alerts(store_id);
CREATE INDEX IF NOT EXISTS idx_low_stock_acknowledged ON low_stock_alerts(is_acknowledged);
CREATE INDEX IF NOT EXISTS idx_low_stock_date ON low_stock_alerts(alert_date);

-- ===== STOCK AUDIT TABLE =====
CREATE TABLE IF NOT EXISTS stock_audits (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    audit_number VARCHAR(50) NOT NULL UNIQUE,
    audit_date DATE NOT NULL,
    store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE NOT NULL,
    conducted_by INTEGER REFERENCES users(id) ON DELETE SET NULL NOT NULL,
    verified_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'draft', -- draft, in_progress, completed
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stock_audit_temple ON stock_audits(temple_id);
CREATE INDEX IF NOT EXISTS idx_stock_audit_number ON stock_audits(audit_number);
CREATE INDEX IF NOT EXISTS idx_stock_audit_store ON stock_audits(store_id);
CREATE INDEX IF NOT EXISTS idx_stock_audit_status ON stock_audits(status);

CREATE TABLE IF NOT EXISTS stock_audit_items (
    id SERIAL PRIMARY KEY,
    audit_id INTEGER REFERENCES stock_audits(id) ON DELETE CASCADE NOT NULL,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE NOT NULL,
    book_quantity NUMERIC(15, 3) NOT NULL, -- System quantity
    physical_quantity NUMERIC(15, 3) NOT NULL, -- Counted quantity
    variance_quantity NUMERIC(15, 3) NOT NULL, -- physical - book
    book_value NUMERIC(15, 2) NOT NULL,
    physical_value NUMERIC(15, 2) NOT NULL,
    variance_value NUMERIC(15, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stock_audit_items_audit ON stock_audit_items(audit_id);
CREATE INDEX IF NOT EXISTS idx_stock_audit_items_item ON stock_audit_items(item_id);

-- Comments
COMMENT ON TABLE purchase_orders IS 'Purchase Orders for inventory items';
COMMENT ON TABLE grns IS 'Goods Receipt Notes - formal receipt of purchased items';
COMMENT ON TABLE gins IS 'Goods Issue Notes - formal issue of items from store';
COMMENT ON TABLE low_stock_alerts IS 'Low stock alerts when items fall below reorder level';
COMMENT ON TABLE stock_audits IS 'Stock audit records for physical verification';

