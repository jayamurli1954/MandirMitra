# Database Migration Instructions

## Add Devotee Name Fields Migration

**Date:** 28th November 2025  
**Purpose:** Add `name_prefix`, `first_name`, and `last_name` columns to `devotees` table

### Quick Migration (Recommended)

Run the Python migration script:

```powershell
cd backend
python migrations/add_devotee_name_fields.py
```

### Manual Migration (Alternative)

If the Python script doesn't work, you can run the SQL directly:

```powershell
# Connect to PostgreSQL
psql -U postgres -d temple_db

# Then run:
\i migrations/add_devotee_name_fields.sql
```

Or copy and paste the SQL from `backend/migrations/add_devotee_name_fields.sql` into your PostgreSQL client.

### What the Migration Does

1. **Adds three new columns:**
   - `name_prefix` (VARCHAR(10)) - For Mr., Mrs., Ms., M/s, etc.
   - `first_name` (VARCHAR(100)) - First name of devotee
   - `last_name` (VARCHAR(100)) - Last name (optional)

2. **Migrates existing data:**
   - Splits existing `name` field into `first_name` and `last_name`
   - First word becomes `first_name`, rest becomes `last_name`

3. **Makes first_name NOT NULL:**
   - After migration, ensures all records have a first_name

### Verification

After running the migration, verify it worked:

```sql
-- Check if columns exist
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'devotees' 
AND column_name IN ('name_prefix', 'first_name', 'last_name');

-- Check if data was migrated
SELECT id, name, first_name, last_name, name_prefix 
FROM devotees 
LIMIT 5;
```

### Troubleshooting

**Error: "column already exists"**
- The migration is idempotent (safe to run multiple times)
- This means the columns already exist, which is fine

**Error: "relation devotees does not exist"**
- Make sure you're connected to the correct database
- Check your DATABASE_URL in `.env` file

**Error: "permission denied"**
- Make sure your database user has ALTER TABLE permissions
- You may need to run as the postgres superuser

### After Migration

Once the migration is complete:
1. Restart the backend server
2. The donation recording should work correctly
3. New devotees will have first_name and last_name fields

