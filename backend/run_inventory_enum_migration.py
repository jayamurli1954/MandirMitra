"""
Add Inventory Transaction Types to Database Enum
Adds inventory_purchase, inventory_issue, and inventory_adjustment to transactiontype enum
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
    # Format: postgresql://user:password@host:port/database
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
    print("Add Inventory Transaction Types to Enum")
    print("=" * 60)
    
    try:
        # Get database connection details
        db_url = settings.DATABASE_URL
        print(f"🔌 Connecting to database...")
        print(f"   Database: {db_url.split('/')[-1] if '/' in db_url else 'N/A'}")
        
        conn_params = parse_database_url(db_url)
        
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True  # Required for ALTER TYPE
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        print("\n📝 Adding enum values...")
        
        # Read and execute SQL
        sql_file = Path(__file__).parent / 'migrations' / 'add_inventory_transaction_types.sql'
        with open(sql_file, 'r') as f:
            sql = f.read()
        
        cursor.execute(sql)
        
        print("✅ Enum values added successfully!")
        print("\nAdded transaction types:")
        print("  - inventory_purchase")
        print("  - inventory_issue")
        print("  - inventory_adjustment")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()




