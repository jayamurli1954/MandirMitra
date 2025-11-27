"""
Migration Script: Add HR & Salary Management Module Tables
Run this script to create all HR-related tables
"""

import psycopg2
from psycopg2 import sql
import os
from pathlib import Path
from urllib.parse import urlparse

# Import settings to use same database configuration
from app.core.config import settings

def parse_database_url(url: str):
    """Parse PostgreSQL connection URL into connection parameters"""
    parsed = urlparse(url)
    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/') or 'mandirsync',
        'user': parsed.username or 'postgres',
        'password': parsed.password or ''
    }

# Get database config from settings (same as application uses)
DB_CONFIG = parse_database_url(settings.DATABASE_URL)

def run_migration():
    """Execute the HR module migration SQL"""
    migration_file = Path(__file__).parent / 'migrations' / 'add_hr_module.sql'
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    try:
        # Read SQL file
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Connect to database
        print("🔌 Connecting to database...")
        print(f"   Host: {DB_CONFIG['host']}")
        print(f"   Port: {DB_CONFIG['port']}")
        print(f"   Database: {DB_CONFIG['database']}")
        print(f"   User: {DB_CONFIG['user']}")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Execute SQL
        print("📝 Executing migration SQL...")
        cursor.execute(sql_content)
        
        # Commit
        conn.commit()
        print("✅ Migration completed successfully!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("HR & Salary Management Module Migration")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        print("\n✅ HR module tables created successfully!")
        print("\nTables created:")
        print("  - departments")
        print("  - designations")
        print("  - employees")
        print("  - salary_components")
        print("  - salary_structures")
        print("  - salary_structure_components")
        print("  - payrolls")
        print("  - payroll_components")
        print("  - leave_types")
        print("  - leave_applications")
        print("\nNext steps:")
        print("1. Create default salary components (Basic, HRA, PF, etc.)")
        print("2. Create departments and designations")
        print("3. Add employees")
        print("4. Create salary structures for employees")
        print("5. Process payrolls")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        exit(1)

