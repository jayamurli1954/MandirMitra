# Step 1: Create Audit Logs Table - EASIEST METHOD

## ✅ Recommended: Use Database Client (pgAdmin/DBeaver)

Since `psql` is not available, use a database client:

### Steps:

1. **Open your database client:**
   - pgAdmin (if you have PostgreSQL installed)
   - DBeaver (free, works with any database)
   - DataGrip (JetBrains)
   - Or any SQL client you have

2. **Connect to your database:**
   - Database: `temple_db`
   - Host: `localhost` (or your database host)
   - Port: `5432` (default PostgreSQL port)
   - User: `postgres` (or your database user)
   - Password: (your database password)

3. **Open the SQL file:**
   - File location: `D:\MandirSync\backend\scripts\create_audit_logs_table.sql`
   - Or copy the SQL content below

4. **Copy and paste this SQL:**

```sql
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    user_name VARCHAR(200) NOT NULL,
    user_email VARCHAR(100) NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changes JSONB,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_role ON audit_logs(user_role);
```

5. **Execute the SQL** (usually F5 or "Run" button)

6. **Verify it worked:**
   ```sql
   SELECT COUNT(*) FROM audit_logs;
   -- Should return 0 (table exists but empty)
   ```

---

## ✅ Alternative: Install PostgreSQL Tools

If you want to use `psql` in the future:

1. **Download PostgreSQL:**
   - https://www.postgresql.org/download/windows/
   - Install PostgreSQL (includes psql)

2. **Add to PATH:**
   - Usually: `C:\Program Files\PostgreSQL\15\bin`
   - Add to Windows PATH environment variable

3. **Then you can use:**
   ```bash
   psql -d temple_db -f backend/scripts/create_audit_logs_table.sql
   ```

---

## ✅ Alternative: Use Python (if environment is activated)

If you have your project's virtual environment activated:

```bash
cd D:\MandirSync\backend
# Make sure your environment is activated
python -m scripts.create_audit_logs_table
```

But since you're getting "ModuleNotFoundError", you need to activate the correct environment first.

---

**RECOMMENDED: Use Option 1 (Database Client) - It's the easiest!**



