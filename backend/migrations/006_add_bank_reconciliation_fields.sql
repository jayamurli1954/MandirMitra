-- Migration: Add Bank Reconciliation fields to journal_lines
-- Date: 2026-02-25

ALTER TABLE journal_lines ADD COLUMN is_cleared BOOLEAN DEFAULT TRUE;
ALTER TABLE journal_lines ADD COLUMN cleared_at TIMESTAMP NULL;

-- Create index for performance
CREATE INDEX ix_journal_lines_is_cleared ON journal_lines (is_cleared);

-- Update existing bank transactions to be cleared by default (to avoid breaking current data)
-- Assuming accounts with subtype 'cash_bank' are bank accounts.
-- However, we can just leave them as TRUE for now as per the DEFAULT.
