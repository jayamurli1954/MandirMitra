-- Migration: Add GST and FCRA optional fields to temples table
-- Date: January 2025
-- Description: Adds optional GST and FCRA fields to support compliance features

-- Add GST (Goods and Services Tax) fields - Optional
ALTER TABLE temples 
ADD COLUMN IF NOT EXISTS gst_applicable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS gstin VARCHAR(15),
ADD COLUMN IF NOT EXISTS gst_registration_date VARCHAR(50),
ADD COLUMN IF NOT EXISTS gst_tax_rates TEXT;

-- Add FCRA (Foreign Contribution Regulation Act) fields - Optional
ALTER TABLE temples 
ADD COLUMN IF NOT EXISTS fcra_applicable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS fcra_bank_account_id INTEGER;

-- Add comments for documentation
COMMENT ON COLUMN temples.gst_applicable IS 'Whether GST is applicable for this temple (optional)';
COMMENT ON COLUMN temples.gstin IS '15-character GSTIN if GST is applicable';
COMMENT ON COLUMN temples.fcra_applicable IS 'Whether FCRA is applicable (receiving foreign donations)';
COMMENT ON COLUMN temples.fcra_bank_account_id IS 'Link to bank account used for FCRA transactions';






