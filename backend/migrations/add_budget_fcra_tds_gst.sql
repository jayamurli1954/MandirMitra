-- Migration: Add Budget, FCRA, TDS/GST support
-- Complete Accounting Core module

-- ===== BUDGET TABLES =====
CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    financial_year_id INTEGER REFERENCES financial_years(id) ON DELETE CASCADE,
    budget_name VARCHAR(200) NOT NULL,
    budget_type VARCHAR(20) NOT NULL DEFAULT 'annual',
    budget_period_start DATE NOT NULL,
    budget_period_end DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    submitted_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    submitted_at TIMESTAMPTZ,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    total_budgeted_amount NUMERIC(15, 2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_budgets_temple ON budgets(temple_id);
CREATE INDEX IF NOT EXISTS idx_budgets_financial_year ON budgets(financial_year_id);
CREATE INDEX IF NOT EXISTS idx_budgets_status ON budgets(status);

CREATE TABLE IF NOT EXISTS budget_items (
    id SERIAL PRIMARY KEY,
    budget_id INTEGER REFERENCES budgets(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    budgeted_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_budget_items_budget ON budget_items(budget_id);
CREATE INDEX IF NOT EXISTS idx_budget_items_account ON budget_items(account_id);

CREATE TABLE IF NOT EXISTS budget_revisions (
    id SERIAL PRIMARY KEY,
    budget_id INTEGER REFERENCES budgets(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    revision_date DATE NOT NULL,
    revision_reason TEXT,
    previous_total NUMERIC(15, 2) DEFAULT 0.00,
    new_total NUMERIC(15, 2) DEFAULT 0.00,
    revised_by INTEGER REFERENCES users(id) ON DELETE SET NULL NOT NULL,
    revised_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_budget_revisions_budget ON budget_revisions(budget_id);

-- ===== ADD FCRA/TDS/GST FIELDS TO DONATIONS =====
ALTER TABLE donations
ADD COLUMN IF NOT EXISTS is_fcra_donation BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS fcra_receipt_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS foreign_currency VARCHAR(10),
ADD COLUMN IF NOT EXISTS foreign_amount NUMERIC(15, 2),
ADD COLUMN IF NOT EXISTS exchange_rate NUMERIC(10, 4),
ADD COLUMN IF NOT EXISTS tds_applicable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS tds_amount NUMERIC(15, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS tds_section VARCHAR(50),
ADD COLUMN IF NOT EXISTS gst_applicable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS gst_amount NUMERIC(15, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS gst_rate NUMERIC(5, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS hsn_code VARCHAR(20);

CREATE INDEX IF NOT EXISTS idx_donations_fcra ON donations(is_fcra_donation);
CREATE INDEX IF NOT EXISTS idx_donations_tds ON donations(tds_applicable);
CREATE INDEX IF NOT EXISTS idx_donations_gst ON donations(gst_applicable);

-- Comments
COMMENT ON COLUMN donations.is_fcra_donation IS 'True if this is a foreign contribution (FCRA)';
COMMENT ON COLUMN donations.fcra_receipt_number IS 'FCRA receipt number if applicable';
COMMENT ON COLUMN donations.foreign_currency IS 'Currency code for foreign donations (USD, GBP, etc.)';
COMMENT ON COLUMN donations.foreign_amount IS 'Amount in foreign currency';
COMMENT ON COLUMN donations.exchange_rate IS 'Exchange rate at time of donation';
COMMENT ON COLUMN donations.tds_applicable IS 'True if TDS is applicable on this donation';
COMMENT ON COLUMN donations.tds_amount IS 'TDS amount deducted';
COMMENT ON COLUMN donations.tds_section IS 'TDS section (e.g., 194A, 80G)';
COMMENT ON COLUMN donations.gst_applicable IS 'True if GST is applicable';
COMMENT ON COLUMN donations.gst_amount IS 'GST amount';
COMMENT ON COLUMN donations.gst_rate IS 'GST rate percentage';
COMMENT ON COLUMN donations.hsn_code IS 'HSN code for GST';




