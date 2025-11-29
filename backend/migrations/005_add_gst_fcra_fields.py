"""
Migration: Add GST and FCRA optional fields to temples table
Date: January 2025
"""

# This is a SQL migration script
# Run using: psql -d temple_db -f backend/migrations/005_add_gst_fcra_fields.sql

SQL_MIGRATION = """
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

-- Add comment for documentation
COMMENT ON COLUMN temples.gst_applicable IS 'Whether GST is applicable for this temple (optional)';
COMMENT ON COLUMN temples.gstin IS '15-character GSTIN if GST is applicable';
COMMENT ON COLUMN temples.fcra_applicable IS 'Whether FCRA is applicable (receiving foreign donations)';
COMMENT ON COLUMN temples.fcra_bank_account_id IS 'Link to bank account used for FCRA transactions';
"""

if __name__ == "__main__":
    print("This is a SQL migration script.")
    print("Please run the SQL directly in your database:")
    print("\n" + SQL_MIGRATION)








