-- Migration: Add Asset History, Transfer, Verification, Insurance, and Documents tables
-- Complete Asset module to 100%

-- ===== ASSET TRANSFER TABLE =====
CREATE TABLE IF NOT EXISTS asset_transfers (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE NOT NULL,
    transfer_date DATE NOT NULL,
    from_location VARCHAR(200),
    to_location VARCHAR(200) NOT NULL,
    transfer_reason TEXT,
    transferred_by INTEGER REFERENCES users(id) ON DELETE SET NULL NOT NULL,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_asset_transfers_temple ON asset_transfers(temple_id);
CREATE INDEX IF NOT EXISTS idx_asset_transfers_asset ON asset_transfers(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_transfers_date ON asset_transfers(transfer_date);

-- ===== ASSET VALUATION HISTORY TABLE =====
CREATE TABLE IF NOT EXISTS asset_valuation_history (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE NOT NULL,
    valuation_date DATE NOT NULL,
    valuation_type VARCHAR(50) NOT NULL,
    valuation_amount NUMERIC(15, 2) NOT NULL,
    valuation_method VARCHAR(50),
    valuer_name VARCHAR(200),
    valuation_report_number VARCHAR(100),
    valuation_report_date DATE,
    reference_id INTEGER,
    reference_type VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_asset_valuation_history_asset ON asset_valuation_history(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_valuation_history_date ON asset_valuation_history(valuation_date);
CREATE INDEX IF NOT EXISTS idx_asset_valuation_history_type ON asset_valuation_history(valuation_type);

-- ===== ASSET PHYSICAL VERIFICATION TABLE =====
CREATE TABLE IF NOT EXISTS asset_physical_verifications (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE NOT NULL,
    verification_date DATE NOT NULL,
    verification_number VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(20) DEFAULT 'pending',
    verified_location VARCHAR(200) NOT NULL,
    condition VARCHAR(50),
    condition_notes TEXT,
    verified_by INTEGER REFERENCES users(id) ON DELETE SET NULL NOT NULL,
    verified_by_second INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    has_discrepancy BOOLEAN DEFAULT FALSE,
    discrepancy_details TEXT,
    photo_urls TEXT,
    document_urls TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_asset_physical_verifications_temple ON asset_physical_verifications(temple_id);
CREATE INDEX IF NOT EXISTS idx_asset_physical_verifications_asset ON asset_physical_verifications(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_physical_verifications_date ON asset_physical_verifications(verification_date);
CREATE INDEX IF NOT EXISTS idx_asset_physical_verifications_status ON asset_physical_verifications(status);
CREATE INDEX IF NOT EXISTS idx_asset_physical_verifications_number ON asset_physical_verifications(verification_number);

-- ===== ASSET INSURANCE TABLE =====
CREATE TABLE IF NOT EXISTS asset_insurance (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE NOT NULL,
    policy_number VARCHAR(100) NOT NULL,
    insurance_company VARCHAR(200) NOT NULL,
    policy_start_date DATE NOT NULL,
    policy_end_date DATE NOT NULL,
    premium_amount NUMERIC(15, 2) DEFAULT 0.00,
    insured_value NUMERIC(15, 2) NOT NULL,
    coverage_type VARCHAR(50),
    coverage_details TEXT,
    auto_renewal BOOLEAN DEFAULT FALSE,
    renewal_reminder_days INTEGER DEFAULT 30,
    agent_name VARCHAR(200),
    agent_contact VARCHAR(100),
    policy_document_url VARCHAR(500),
    claim_history TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_asset_insurance_temple ON asset_insurance(temple_id);
CREATE INDEX IF NOT EXISTS idx_asset_insurance_asset ON asset_insurance(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_insurance_end_date ON asset_insurance(policy_end_date);
CREATE INDEX IF NOT EXISTS idx_asset_insurance_active ON asset_insurance(is_active);

-- ===== ASSET DOCUMENTS TABLE =====
CREATE TABLE IF NOT EXISTS asset_documents (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_name VARCHAR(200) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    description TEXT,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_asset_documents_asset ON asset_documents(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_documents_type ON asset_documents(document_type);

-- ===== ENHANCE ASSET DISPOSAL TABLE =====
ALTER TABLE asset_disposals
ADD COLUMN IF NOT EXISTS approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

CREATE INDEX IF NOT EXISTS idx_asset_disposals_approved_by ON asset_disposals(approved_by);

-- Comments
COMMENT ON TABLE asset_transfers IS 'Asset transfer history - tracks location changes';
COMMENT ON TABLE asset_valuation_history IS 'Complete valuation timeline for assets';
COMMENT ON TABLE asset_physical_verifications IS 'Physical verification records for audit compliance';
COMMENT ON TABLE asset_insurance IS 'Insurance policy tracking with expiry alerts';
COMMENT ON TABLE asset_documents IS 'Asset documents and images storage';

COMMENT ON COLUMN asset_physical_verifications.status IS 'Verification status: pending, verified, discrepancy, not_found';
COMMENT ON COLUMN asset_valuation_history.valuation_type IS 'PURCHASE, REVALUATION, MARKET_VALUE, INSURANCE, DISPOSAL';

