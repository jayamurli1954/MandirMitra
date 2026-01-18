-- Asset Management Tables Migration
-- Creates tables for asset management following standard accounting practices

-- Asset Categories
CREATE TABLE IF NOT EXISTS asset_categories (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id INTEGER REFERENCES asset_categories(id),
    default_depreciation_method VARCHAR(50) DEFAULT 'straight_line',
    default_useful_life_years FLOAT DEFAULT 0.0,
    default_depreciation_rate_percent FLOAT DEFAULT 0.0,
    is_depreciable BOOLEAN DEFAULT TRUE,
    account_id INTEGER REFERENCES accounts(id),
    accumulated_depreciation_account_id INTEGER REFERENCES accounts(id),
    revaluation_reserve_account_id INTEGER REFERENCES accounts(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(temple_id, code)
);

-- Assets
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id),
    asset_number VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL REFERENCES asset_categories(id),
    asset_type VARCHAR(50) NOT NULL,
    location VARCHAR(200),
    tag_number VARCHAR(50),
    serial_number VARCHAR(100),
    identification_mark TEXT,
    purchase_date DATE NOT NULL,
    original_cost FLOAT NOT NULL DEFAULT 0.0,
    current_book_value FLOAT DEFAULT 0.0,
    accumulated_depreciation FLOAT DEFAULT 0.0,
    revalued_amount FLOAT DEFAULT 0.0,
    revaluation_reserve FLOAT DEFAULT 0.0,
    depreciation_method VARCHAR(50) DEFAULT 'straight_line',
    useful_life_years FLOAT DEFAULT 0.0,
    depreciation_rate_percent FLOAT DEFAULT 0.0,
    salvage_value FLOAT DEFAULT 0.0,
    is_depreciable BOOLEAN DEFAULT TRUE,
    depreciation_start_date DATE,
    total_estimated_units FLOAT,
    units_used_to_date FLOAT DEFAULT 0.0,
    interest_rate_percent FLOAT,
    sinking_fund_interest_rate FLOAT,
    sinking_fund_payments_per_year INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'active',
    cwip_id INTEGER REFERENCES capital_work_in_progress(id),
    purchase_invoice_number VARCHAR(100),
    purchase_invoice_date DATE,
    vendor_id INTEGER REFERENCES vendors(id),
    warranty_expiry_date DATE,
    tender_id INTEGER,  -- Optional: for future tender process
    asset_account_id INTEGER REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Capital Work in Progress
CREATE TABLE IF NOT EXISTS capital_work_in_progress (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id),
    cwip_number VARCHAR(50) NOT NULL UNIQUE,
    project_name VARCHAR(200) NOT NULL,
    description TEXT,
    asset_category_id INTEGER NOT NULL REFERENCES asset_categories(id),
    start_date DATE NOT NULL,
    expected_completion_date DATE,
    actual_completion_date DATE,
    total_budget FLOAT DEFAULT 0.0,
    total_expenditure FLOAT DEFAULT 0.0,
    account_id INTEGER REFERENCES accounts(id),
    status VARCHAR(20) DEFAULT 'in_progress',
    asset_id INTEGER REFERENCES assets(id),
    tender_id INTEGER,  -- Optional: for future tender process
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Asset Expenses (for CWIP)
CREATE TABLE IF NOT EXISTS asset_expenses (
    id SERIAL PRIMARY KEY,
    cwip_id INTEGER NOT NULL REFERENCES capital_work_in_progress(id),
    expense_date DATE NOT NULL,
    description TEXT NOT NULL,
    amount FLOAT NOT NULL,
    expense_category VARCHAR(50),
    vendor_id INTEGER REFERENCES vendors(id),
    reference_number VARCHAR(100),
    journal_entry_id INTEGER REFERENCES journal_entries(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Depreciation Schedule
CREATE TABLE IF NOT EXISTS depreciation_schedules (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    financial_year VARCHAR(10) NOT NULL,
    period VARCHAR(20) DEFAULT 'yearly',
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    depreciation_method_used VARCHAR(50) NOT NULL,
    opening_book_value FLOAT NOT NULL,
    depreciation_amount FLOAT NOT NULL,
    closing_book_value FLOAT NOT NULL,
    depreciation_rate FLOAT,
    units_produced_this_period FLOAT,
    total_units_produced_to_date FLOAT,
    interest_component FLOAT,
    principal_component FLOAT,
    journal_entry_id INTEGER REFERENCES journal_entries(id),
    posted_date DATE,
    status VARCHAR(20) DEFAULT 'calculated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Asset Revaluation
CREATE TABLE IF NOT EXISTS asset_revaluations (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    revaluation_date DATE NOT NULL,
    revaluation_type VARCHAR(20) NOT NULL,
    previous_book_value FLOAT NOT NULL,
    revalued_amount FLOAT NOT NULL,
    revaluation_amount FLOAT NOT NULL,
    valuation_method VARCHAR(50),
    valuer_name VARCHAR(200),
    valuation_report_number VARCHAR(100),
    valuation_report_date DATE,
    revaluation_reserve_account_id INTEGER REFERENCES accounts(id),
    journal_entry_id INTEGER REFERENCES journal_entries(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Asset Disposal
CREATE TABLE IF NOT EXISTS asset_disposals (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    disposal_date DATE NOT NULL,
    disposal_type VARCHAR(50) NOT NULL,
    disposal_reason TEXT,
    book_value_at_disposal FLOAT NOT NULL,
    accumulated_depreciation_at_disposal FLOAT NOT NULL,
    disposal_proceeds FLOAT DEFAULT 0.0,
    gain_loss_amount FLOAT DEFAULT 0.0,
    buyer_name VARCHAR(200),
    disposal_document_number VARCHAR(100),
    journal_entry_id INTEGER REFERENCES journal_entries(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Asset Maintenance
CREATE TABLE IF NOT EXISTS asset_maintenance (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    maintenance_date DATE NOT NULL,
    maintenance_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    cost FLOAT DEFAULT 0.0,
    vendor_id INTEGER REFERENCES vendors(id),
    service_provider_name VARCHAR(200),
    next_maintenance_date DATE,
    next_maintenance_notes TEXT,
    journal_entry_id INTEGER REFERENCES journal_entries(id),
    is_capitalized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Tender Process Tables (Optional - for future implementation)
-- These tables are created but not required for basic procurement

-- Tenders
CREATE TABLE IF NOT EXISTS tenders (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id),
    tender_number VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    tender_type VARCHAR(50),
    estimated_value FLOAT DEFAULT 0.0,
    tender_issue_date DATE NOT NULL,
    last_date_submission DATE NOT NULL,
    opening_date DATE,
    award_date DATE,
    status VARCHAR(50) DEFAULT 'draft',
    tender_document_path VARCHAR(500),
    terms_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- Tender Bids
CREATE TABLE IF NOT EXISTS tender_bids (
    id SERIAL PRIMARY KEY,
    tender_id INTEGER NOT NULL REFERENCES tenders(id),
    vendor_id INTEGER NOT NULL REFERENCES vendors(id),
    bid_amount FLOAT NOT NULL,
    bid_date DATE NOT NULL,
    validity_period_days INTEGER DEFAULT 90,
    status VARCHAR(50) DEFAULT 'submitted',
    bid_document_path VARCHAR(500),
    technical_specifications TEXT,
    technical_score FLOAT,
    financial_score FLOAT,
    total_score FLOAT,
    evaluation_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evaluated_at TIMESTAMP,
    evaluated_by INTEGER REFERENCES users(id)
);

-- Add foreign key constraints for tender_id in assets and cwip
-- (These are optional fields, so they're nullable)
-- Note: Foreign key constraint will be added when tender tables are confirmed to be used

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_assets_temple_id ON assets(temple_id);
CREATE INDEX IF NOT EXISTS idx_assets_category_id ON assets(category_id);
CREATE INDEX IF NOT EXISTS idx_assets_asset_number ON assets(asset_number);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
CREATE INDEX IF NOT EXISTS idx_cwip_temple_id ON capital_work_in_progress(temple_id);
CREATE INDEX IF NOT EXISTS idx_cwip_status ON capital_work_in_progress(status);
CREATE INDEX IF NOT EXISTS idx_depreciation_asset_id ON depreciation_schedules(asset_id);
CREATE INDEX IF NOT EXISTS idx_depreciation_financial_year ON depreciation_schedules(financial_year);
CREATE INDEX IF NOT EXISTS idx_asset_expenses_cwip_id ON asset_expenses(cwip_id);
CREATE INDEX IF NOT EXISTS idx_asset_revaluations_asset_id ON asset_revaluations(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_disposals_asset_id ON asset_disposals(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_maintenance_asset_id ON asset_maintenance(asset_id);
