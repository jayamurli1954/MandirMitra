-- Add INVENTORY_PURCHASE, INVENTORY_ISSUE, and INVENTORY_ADJUSTMENT to transactiontype enum

-- First, check if the enum values already exist
DO $$
BEGIN
    -- Add INVENTORY_PURCHASE if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'inventory_purchase' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'transactiontype')
    ) THEN
        ALTER TYPE transactiontype ADD VALUE 'inventory_purchase';
    END IF;

    -- Add INVENTORY_ISSUE if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'inventory_issue' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'transactiontype')
    ) THEN
        ALTER TYPE transactiontype ADD VALUE 'inventory_issue';
    END IF;

    -- Add INVENTORY_ADJUSTMENT if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'inventory_adjustment' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'transactiontype')
    ) THEN
        ALTER TYPE transactiontype ADD VALUE 'inventory_adjustment';
    END IF;
END $$;




