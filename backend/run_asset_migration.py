"""
Asset Management Tables Migration
Creates tables for asset management following standard accounting practices
"""

import psycopg2
from app.core.config import settings
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def parse_database_url(url):
    """Parse DATABASE_URL into connection parameters"""
    url = url.replace('postgresql://', '')
    if '@' in url:
        auth, rest = url.split('@', 1)
        user, password = auth.split(':', 1)
    else:
        user = 'postgres'
        password = ''
        rest = url
    
    if '/' in rest:
        host_port, database = rest.split('/', 1)
    else:
        host_port = rest
        database = 'temple_db'
    
    if ':' in host_port:
        host, port = host_port.split(':')
    else:
        host = host_port
        port = '5432'
    
    return {
        'host': host,
        'port': port,
        'database': database,
        'user': user,
        'password': password
    }

def main():
    print("=" * 60)
    print("Asset Management Tables Migration")
    print("=" * 60)
    
    try:
        # Get database connection details
        db_url = settings.DATABASE_URL
        print(f"🔌 Connecting to database...")
        print(f"   Database: {db_url.split('/')[-1] if '/' in db_url else 'N/A'}")
        
        conn_params = parse_database_url(db_url)
        
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        print("\n📝 Creating asset management tables...")
        
        # Read and execute SQL
        sql_file = Path(__file__).parent / 'migrations' / 'add_asset_tables.sql'
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Execute SQL statements
        cursor.execute(sql)
        
        print("✅ Asset management tables created successfully!")
        print("\nTables created:")
        print("  - asset_categories")
        print("  - assets")
        print("  - capital_work_in_progress")
        print("  - asset_expenses")
        print("  - depreciation_schedules")
        print("  - asset_revaluations")
        print("  - asset_disposals")
        print("  - asset_maintenance")
        print("  - tenders (optional - for future use)")
        print("  - tender_bids (optional - for future use)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("\nNote: Tender process tables are created but optional.")
        print("      They can be used when a temple requests tender functionality.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
