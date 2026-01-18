-- Migration: Add name_prefix, first_name, and last_name columns to devotees table
-- Date: 2025-11-28
-- Description: Split devotee name into first_name and last_name, add name_prefix for proper identification

-- Add name_prefix column (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'devotees' AND column_name = 'name_prefix'
    ) THEN
        ALTER TABLE devotees ADD COLUMN name_prefix VARCHAR(10);
        COMMENT ON COLUMN devotees.name_prefix IS 'Mr., Mrs., Ms., M/s, Dr., etc.';
    END IF;
END $$;

-- Add first_name column (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'devotees' AND column_name = 'first_name'
    ) THEN
        ALTER TABLE devotees ADD COLUMN first_name VARCHAR(100);
        COMMENT ON COLUMN devotees.first_name IS 'First name of devotee';
    END IF;
END $$;

-- Add last_name column (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'devotees' AND column_name = 'last_name'
    ) THEN
        ALTER TABLE devotees ADD COLUMN last_name VARCHAR(100);
        COMMENT ON COLUMN devotees.last_name IS 'Last name of devotee (optional)';
    END IF;
END $$;

-- Migrate existing data: Split name into first_name and last_name
-- For existing records, populate first_name and last_name from name field
UPDATE devotees 
SET 
    first_name = CASE 
        WHEN name IS NOT NULL AND name != '' THEN
            SPLIT_PART(TRIM(name), ' ', 1)
        ELSE NULL
    END,
    last_name = CASE 
        WHEN name IS NOT NULL AND name != '' AND LENGTH(TRIM(name)) > LENGTH(SPLIT_PART(TRIM(name), ' ', 1)) THEN
            SUBSTRING(TRIM(name) FROM LENGTH(SPLIT_PART(TRIM(name), ' ', 1)) + 2)
        ELSE NULL
    END
WHERE first_name IS NULL OR first_name = '';

-- Make first_name NOT NULL after migration (but allow existing NULLs temporarily)
-- We'll update the constraint after ensuring all records have first_name
DO $$ 
BEGIN
    -- Update any remaining NULL first_name to use name or 'Unknown'
    UPDATE devotees 
    SET first_name = COALESCE(name, 'Unknown')
    WHERE first_name IS NULL OR first_name = '';
    
    -- Now make first_name NOT NULL
    ALTER TABLE devotees ALTER COLUMN first_name SET NOT NULL;
EXCEPTION
    WHEN OTHERS THEN
        -- If constraint already exists or other error, continue
        RAISE NOTICE 'Could not set first_name NOT NULL: %', SQLERRM;
END $$;


