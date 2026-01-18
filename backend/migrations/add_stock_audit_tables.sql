-- Migration: Add Stock Audit and Wastage tables
-- Complete Inventory module to 100%

-- ===== STOCK AUDIT TABLES =====
CREATE TABLE IF NOT EXISTS stock_audits (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    audit_number VARCHAR(50) NOT NULL UNIQUE,
    audit_date DATE NOT NULL,
    store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    conducted_by INTEGER REFERENCES users(id) ON DELETE SET NULL NOT NULL,
    verified_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    total_items_audited INTEGER DEFAULT 0,
    items_with_discrepancy INTEGER DEFAULT 0,
    total_discrepancy_value NUMERIC(15, 2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stock_audits_temple ON stock_audits(temple_id);
CREATE INDEX IF NOT EXISTS idx_stock_audits_store ON stock_audits(store_id);
CREATE INDEX IF NOT EXISTS idx_stock_audits_date ON stock_audits(audit_date);
CREATE INDEX IF NOT EXISTS idx_stock_audits_status ON stock_audits(status);
CREATE INDEX IF NOT EXISTS idx_stock_audits_number ON stock_audits(audit_number);

CREATE TABLE IF NOT EXISTS stock_audit_items (
    id SERIAL PRIMARY KEY,
    audit_id INTEGER REFERENCES stock_audits(id) ON DELETE CASCADE NOT NULL,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE NOT NULL,
    book_quantity NUMERIC(15, 3) NOT NULL,
    book_value NUMERIC(15, 2) NOT NULL,
    physical_quantity NUMERIC(15, 3) NOT NULL,
    physical_value NUMERIC(15, 2) NOT NULL,
    quantity_discrepancy NUMERIC(15, 3) DEFAULT 0.00,
    value_discrepancy NUMERIC(15, 2) DEFAULT 0.00,
    discrepancy_reason TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stock_audit_items_audit ON stock_audit_items(audit_id);
CREATE INDEX IF NOT EXISTS idx_stock_audit_items_item ON stock_audit_items(item_id);

-- ===== STOCK WASTAGE TABLE =====
CREATE TABLE IF NOT EXISTS stock_wastages (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    wastage_number VARCHAR(50) NOT NULL UNIQUE,
    wastage_date DATE NOT NULL,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE NOT NULL,
    store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE NOT NULL,
    quantity NUMERIC(15, 3) NOT NULL,
    unit_cost NUMERIC(15, 2) NOT NULL,
    total_value NUMERIC(15, 2) NOT NULL,
    reason VARCHAR(20) NOT NULL,
    reason_details TEXT,
    recorded_by INTEGER REFERENCES users(id) ON DELETE SET NULL NOT NULL,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    journal_entry_id INTEGER REFERENCES journal_entries(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stock_wastages_temple ON stock_wastages(temple_id);
CREATE INDEX IF NOT EXISTS idx_stock_wastages_item ON stock_wastages(item_id);
CREATE INDEX IF NOT EXISTS idx_stock_wastages_store ON stock_wastages(store_id);
CREATE INDEX IF NOT EXISTS idx_stock_wastages_date ON stock_wastages(wastage_date);
CREATE INDEX IF NOT EXISTS idx_stock_wastages_reason ON stock_wastages(reason);
CREATE INDEX IF NOT EXISTS idx_stock_wastages_number ON stock_wastages(wastage_number);

-- Comments
COMMENT ON TABLE stock_audits IS 'Stock audit records for physical verification';
COMMENT ON TABLE stock_audit_items IS 'Individual items in stock audit';
COMMENT ON TABLE stock_wastages IS 'Stock wastage/damage records';

COMMENT ON COLUMN stock_audits.status IS 'Audit status: draft, in_progress, completed, approved, discrepancy';
COMMENT ON COLUMN stock_wastages.reason IS 'Wastage reason: expired, damaged, spoiled, theft, loss, other';




