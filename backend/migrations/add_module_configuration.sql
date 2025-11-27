-- Migration: Add Module Configuration to Temples Table
-- This allows temples to enable/disable modules selectively

-- Add module configuration columns
ALTER TABLE temples 
ADD COLUMN IF NOT EXISTS module_donations_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS module_sevas_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS module_inventory_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS module_assets_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS module_accounting_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS module_tender_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS module_hr_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS module_hundi_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS module_panchang_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS module_reports_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS module_token_seva_enabled BOOLEAN DEFAULT TRUE;

-- Update existing temples to have all modules enabled (except tender)
UPDATE temples 
SET 
    module_donations_enabled = TRUE,
    module_sevas_enabled = TRUE,
    module_inventory_enabled = TRUE,
    module_assets_enabled = TRUE,
    module_accounting_enabled = TRUE,
    module_tender_enabled = FALSE,  -- Optional module, disabled by default
    module_hr_enabled = TRUE,  -- HR & Salary Management
    module_hundi_enabled = TRUE,  -- Hundi Management
    module_panchang_enabled = TRUE,
    module_reports_enabled = TRUE,
    module_token_seva_enabled = TRUE
WHERE module_donations_enabled IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN temples.module_donations_enabled IS 'Enable/disable donations module';
COMMENT ON COLUMN temples.module_sevas_enabled IS 'Enable/disable sevas module';
COMMENT ON COLUMN temples.module_inventory_enabled IS 'Enable/disable inventory management module';
COMMENT ON COLUMN temples.module_assets_enabled IS 'Enable/disable asset management module';
COMMENT ON COLUMN temples.module_accounting_enabled IS 'Enable/disable accounting module';
COMMENT ON COLUMN temples.module_tender_enabled IS 'Enable/disable tender management module (optional)';
COMMENT ON COLUMN temples.module_hr_enabled IS 'Enable/disable HR & Salary Management module';
COMMENT ON COLUMN temples.module_hundi_enabled IS 'Enable/disable Hundi Management module';
COMMENT ON COLUMN temples.module_panchang_enabled IS 'Enable/disable panchang module';
COMMENT ON COLUMN temples.module_reports_enabled IS 'Enable/disable reports module';
COMMENT ON COLUMN temples.module_token_seva_enabled IS 'Enable/disable token seva module';

