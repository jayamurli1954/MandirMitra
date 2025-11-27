-- Migration: Add In-Kind Donation Support to Donations Table
-- This migration adds fields to support in-kind donations (non-monetary donations)
-- alongside existing cash donations

-- Step 1: Create enum types for donation_type and inkind_subtype
DO $$ 
BEGIN
    -- Create donation_type enum if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'donationtype') THEN
        CREATE TYPE donationtype AS ENUM ('cash', 'in_kind');
    END IF;
    
    -- Create inkinddonationsubtype enum if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'inkinddonationsubtype') THEN
        CREATE TYPE inkinddonationsubtype AS ENUM ('inventory', 'event_sponsorship', 'asset');
    END IF;
END $$;

-- Step 2: Add donation_type column (default to 'cash' for existing records)
ALTER TABLE donations 
ADD COLUMN IF NOT EXISTS donation_type donationtype NOT NULL DEFAULT 'cash';

-- Step 3: Make payment_mode nullable (since in-kind donations don't have payment mode)
ALTER TABLE donations 
ALTER COLUMN payment_mode DROP NOT NULL;

-- Step 4: Add in-kind donation fields
ALTER TABLE donations 
ADD COLUMN IF NOT EXISTS inkind_subtype inkinddonationsubtype,
ADD COLUMN IF NOT EXISTS item_name VARCHAR(200),
ADD COLUMN IF NOT EXISTS item_description TEXT,
ADD COLUMN IF NOT EXISTS quantity FLOAT,
ADD COLUMN IF NOT EXISTS unit VARCHAR(50),
ADD COLUMN IF NOT EXISTS value_assessed FLOAT,
ADD COLUMN IF NOT EXISTS appraised_by VARCHAR(200),
ADD COLUMN IF NOT EXISTS appraisal_date DATE,
ADD COLUMN IF NOT EXISTS purity VARCHAR(50),
ADD COLUMN IF NOT EXISTS weight_gross FLOAT,
ADD COLUMN IF NOT EXISTS weight_net FLOAT,
ADD COLUMN IF NOT EXISTS event_name VARCHAR(200),
ADD COLUMN IF NOT EXISTS event_date DATE,
ADD COLUMN IF NOT EXISTS sponsorship_category VARCHAR(100),
ADD COLUMN IF NOT EXISTS inventory_item_id INTEGER REFERENCES items(id),
ADD COLUMN IF NOT EXISTS asset_id INTEGER REFERENCES assets(id),
ADD COLUMN IF NOT EXISTS store_id INTEGER REFERENCES stores(id),
ADD COLUMN IF NOT EXISTS current_balance FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS document_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS journal_entry_id INTEGER REFERENCES journal_entries(id);

-- Step 5: Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_donations_donation_type ON donations(donation_type);
CREATE INDEX IF NOT EXISTS idx_donations_inkind_subtype ON donations(inkind_subtype);
CREATE INDEX IF NOT EXISTS idx_donations_item_name ON donations(item_name);
CREATE INDEX IF NOT EXISTS idx_donations_inventory_item_id ON donations(inventory_item_id);
CREATE INDEX IF NOT EXISTS idx_donations_asset_id ON donations(asset_id);
CREATE INDEX IF NOT EXISTS idx_donations_store_id ON donations(store_id);
CREATE INDEX IF NOT EXISTS idx_donations_journal_entry_id ON donations(journal_entry_id);

-- Step 6: Add comments for documentation
COMMENT ON COLUMN donations.donation_type IS 'Type of donation: cash (monetary) or in_kind (goods/services/assets)';
COMMENT ON COLUMN donations.inkind_subtype IS 'Sub-type of in-kind donation: inventory (consumables), event_sponsorship, or asset';
COMMENT ON COLUMN donations.item_name IS 'Name of donated item (for in-kind donations)';
COMMENT ON COLUMN donations.quantity IS 'Quantity of donated item';
COMMENT ON COLUMN donations.unit IS 'Unit of measurement (kg, grams, pieces, etc.)';
COMMENT ON COLUMN donations.value_assessed IS 'Assessed/estimated value of in-kind donation';
COMMENT ON COLUMN donations.inventory_item_id IS 'Link to inventory item if donation is inventory type';
COMMENT ON COLUMN donations.asset_id IS 'Link to asset register if donation is asset type';
COMMENT ON COLUMN donations.store_id IS 'Store location where inventory donation is received';
COMMENT ON COLUMN donations.current_balance IS 'Remaining quantity for inventory donations';

-- Step 7: Update existing records to ensure consistency
-- All existing donations are cash donations, so ensure payment_mode is set
UPDATE donations 
SET payment_mode = COALESCE(payment_mode, 'Cash')
WHERE donation_type = 'cash' AND payment_mode IS NULL;

-- Migration complete
-- Note: This migration is backward compatible - all existing donations remain as cash donations

