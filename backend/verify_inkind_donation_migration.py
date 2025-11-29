"""
Verification Script: Verify In-Kind Donation Migration
This script verifies that the migration was successful and checks the database state
"""

import psycopg2
from urllib.parse import urlparse
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

DB_CONFIG = parse_database_url(settings.DATABASE_URL)

def verify_migration():
    """Verify that the migration was successful"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("Verifying In-Kind Donation Migration")
        print("=" * 60)
        
        # Check if donation_type column exists
        print("\n1. Checking donation_type column...")
        cursor.execute("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'donations' AND column_name = 'donation_type'
        """)
        result = cursor.fetchone()
        if result:
            print(f"   ✅ donation_type column exists")
            print(f"      Type: {result[1]}")
            print(f"      Default: {result[2]}")
            print(f"      Nullable: {result[3]}")
        else:
            print("   ❌ donation_type column NOT found")
            return False
        
        # Check enum types
        print("\n2. Checking enum types...")
        cursor.execute("""
            SELECT typname FROM pg_type 
            WHERE typname IN ('donationtype', 'inkinddonationsubtype')
        """)
        enums = cursor.fetchall()
        enum_names = [e[0] for e in enums]
        if 'donationtype' in enum_names:
            print("   ✅ donationtype enum exists")
        else:
            print("   ❌ donationtype enum NOT found")
        
        if 'inkinddonationsubtype' in enum_names:
            print("   ✅ inkinddonationsubtype enum exists")
        else:
            print("   ❌ inkinddonationsubtype enum NOT found")
        
        # Check new columns
        print("\n3. Checking new in-kind donation columns...")
        new_columns = [
            'inkind_subtype', 'item_name', 'item_description', 'quantity', 'unit',
            'value_assessed', 'appraised_by', 'appraisal_date', 'purity',
            'weight_gross', 'weight_net', 'event_name', 'event_date',
            'sponsorship_category', 'inventory_item_id', 'asset_id', 'store_id',
            'current_balance', 'photo_url', 'document_url', 'journal_entry_id'
        ]
        
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'donations'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        missing_columns = []
        for col in new_columns:
            if col in existing_columns:
                print(f"   ✅ {col}")
            else:
                print(f"   ❌ {col} - MISSING")
                missing_columns.append(col)
        
        if missing_columns:
            print(f"\n   ⚠️  Missing columns: {', '.join(missing_columns)}")
            return False
        
        # Check indexes
        print("\n4. Checking indexes...")
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'donations' 
            AND indexname LIKE 'idx_donations_%'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        
        expected_indexes = [
            'idx_donations_donation_type',
            'idx_donations_inkind_subtype',
            'idx_donations_item_name',
            'idx_donations_inventory_item_id',
            'idx_donations_asset_id',
            'idx_donations_store_id',
            'idx_donations_journal_entry_id'
        ]
        
        for idx in expected_indexes:
            if idx in indexes:
                print(f"   ✅ {idx}")
            else:
                print(f"   ⚠️  {idx} - not found (may not be critical)")
        
        # Check existing donations
        print("\n5. Checking existing donations...")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN donation_type = 'cash' THEN 1 END) as cash_count,
                COUNT(CASE WHEN donation_type = 'in_kind' THEN 1 END) as inkind_count,
                COUNT(CASE WHEN donation_type IS NULL THEN 1 END) as null_count
            FROM donations
        """)
        result = cursor.fetchone()
        if result:
            total, cash_count, inkind_count, null_count = result
            print(f"   Total donations: {total}")
            print(f"   Cash donations: {cash_count}")
            print(f"   In-kind donations: {inkind_count}")
            if null_count > 0:
                print(f"   ⚠️  NULL donation_type: {null_count} (should be 0)")
            else:
                print(f"   ✅ All donations have donation_type set")
        
        # Check payment_mode nullable
        print("\n6. Checking payment_mode nullable...")
        cursor.execute("""
            SELECT is_nullable
            FROM information_schema.columns
            WHERE table_name = 'donations' AND column_name = 'payment_mode'
        """)
        result = cursor.fetchone()
        if result and result[0] == 'YES':
            print("   ✅ payment_mode is nullable (correct for in-kind donations)")
        else:
            print("   ⚠️  payment_mode is NOT nullable (may cause issues for in-kind donations)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Migration verification complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test creating an in-kind donation via API")
        print("2. Verify accounting entries are created correctly")
        print("3. Test inventory integration for inventory-type donations")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    verify_migration()



