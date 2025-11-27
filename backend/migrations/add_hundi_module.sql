-- Migration: Add Hundi Management Module Tables
-- Complete hundi management system with opening, counting, verification, and bank deposit

-- ===== HUNDI MASTERS =====
CREATE TABLE IF NOT EXISTS hundi_masters (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    hundi_code VARCHAR(50) NOT NULL UNIQUE,
    hundi_name VARCHAR(200) NOT NULL,
    hundi_location VARCHAR(200),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    requires_verification BOOLEAN DEFAULT TRUE,
    min_verifiers INTEGER DEFAULT 2,
    default_bank_account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hundi_masters_temple ON hundi_masters(temple_id);
CREATE INDEX IF NOT EXISTS idx_hundi_masters_code ON hundi_masters(hundi_code);
CREATE INDEX IF NOT EXISTS idx_hundi_masters_active ON hundi_masters(is_active);

-- ===== HUNDI OPENINGS =====
-- Create enum if it doesn't exist
DO $$ BEGIN
    CREATE TYPE hundistatus AS ENUM ('scheduled', 'opened', 'counting', 'verified', 'deposited', 'reconciled', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS hundi_openings (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    
    -- Hundi Identification
    hundi_code VARCHAR(50) NOT NULL,
    hundi_name VARCHAR(200) NOT NULL,
    hundi_location VARCHAR(200),
    
    -- Opening Schedule
    scheduled_date DATE NOT NULL,
    scheduled_time VARCHAR(10),
    actual_opened_date DATE,
    actual_opened_time VARCHAR(10),
    
    -- Sealed Number Tracking
    sealed_number VARCHAR(100),
    seal_photo_url VARCHAR(500),
    seal_video_url VARCHAR(500),
    
    -- Status
    status hundistatus NOT NULL DEFAULT 'scheduled',
    
    -- Counting Information
    counting_started_at TIMESTAMPTZ,
    counting_completed_at TIMESTAMPTZ,
    total_amount FLOAT DEFAULT 0.0,
    
    -- Verification (Multi-person)
    verified_by_user_1_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    verified_by_user_2_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    verified_by_user_3_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    
    -- Discrepancy Tracking
    has_discrepancy BOOLEAN DEFAULT FALSE,
    discrepancy_amount FLOAT DEFAULT 0.0,
    discrepancy_reason TEXT,
    discrepancy_resolved BOOLEAN DEFAULT FALSE,
    discrepancy_resolved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    discrepancy_resolved_at TIMESTAMPTZ,
    
    -- Bank Deposit
    bank_account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL,
    bank_deposit_date DATE,
    bank_deposit_reference VARCHAR(100),
    bank_deposit_amount FLOAT,
    journal_entry_id INTEGER REFERENCES journal_entries(id) ON DELETE SET NULL,
    
    -- Reconciliation
    reconciled BOOLEAN DEFAULT FALSE,
    reconciled_at TIMESTAMPTZ,
    reconciled_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- Notes and Documentation
    notes TEXT,
    counting_sheet_url VARCHAR(500),
    photo_urls JSONB,
    video_urls JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_hundi_openings_temple ON hundi_openings(temple_id);
CREATE INDEX IF NOT EXISTS idx_hundi_openings_code ON hundi_openings(hundi_code);
CREATE INDEX IF NOT EXISTS idx_hundi_openings_date ON hundi_openings(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_hundi_openings_status ON hundi_openings(status);
CREATE INDEX IF NOT EXISTS idx_hundi_openings_verified ON hundi_openings(verified_by_user_1_id, verified_by_user_2_id);

-- ===== HUNDI DENOMINATION COUNTS =====
CREATE TABLE IF NOT EXISTS hundi_denomination_counts (
    id SERIAL PRIMARY KEY,
    hundi_opening_id INTEGER NOT NULL REFERENCES hundi_openings(id) ON DELETE CASCADE,
    
    -- Denomination Details
    denomination_value FLOAT NOT NULL,
    denomination_type VARCHAR(20) NOT NULL,  -- 'note' or 'coin'
    currency VARCHAR(10) DEFAULT 'INR',
    
    -- Count
    quantity INTEGER NOT NULL DEFAULT 0,
    total_amount FLOAT NOT NULL DEFAULT 0.0,
    
    -- Counting Details
    counted_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    counted_at TIMESTAMPTZ DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE,
    verified_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_denomination_counts_opening ON hundi_denomination_counts(hundi_opening_id);
CREATE INDEX IF NOT EXISTS idx_denomination_counts_denomination ON hundi_denomination_counts(denomination_value);

-- Add comments for documentation
COMMENT ON TABLE hundi_masters IS 'Master data for hundis (different hundis in temple)';
COMMENT ON TABLE hundi_openings IS 'Hundi opening schedule and tracking with multi-person verification';
COMMENT ON TABLE hundi_denomination_counts IS 'Denomination-wise counting for each hundi opening';

COMMENT ON COLUMN hundi_openings.status IS 'Hundi opening status: scheduled, opened, counting, verified, deposited, reconciled, cancelled';
COMMENT ON COLUMN hundi_openings.min_verifiers IS 'Minimum number of verifiers required (2-3 people)';
COMMENT ON COLUMN hundi_openings.total_amount IS 'Total amount counted from all denominations';
COMMENT ON COLUMN hundi_denomination_counts.denomination_value IS 'Value of note/coin (e.g., 2000, 500, 100, 50, 20, 10, 5, 2, 1, 0.5, 0.25)';
