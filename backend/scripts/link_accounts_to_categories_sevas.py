"""
Script to link accounts to donation categories and sevas based on account codes

This script will:
1. Find accounts by account code
2. Link them to matching donation categories/sevas
3. Show which links were created
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.donation import DonationCategory
from app.models.seva import Seva
from app.models.accounting import Account

# Mapping of category names to account codes
CATEGORY_ACCOUNT_MAPPING = {
    "General Donation": "4101",
    "Building Fund": "4111",
    "Annadana Fund": "4112",
    "Festival Sponsorship": "4113",
    "Corpus Fund Donation": "4114",
    "Education Fund": "4115",
    # Add more mappings as needed
    "Annadanam": "4112",  # Alternative name
    "Construction Fund": "4111",  # Alternative name
    "Corpus Fund": "4114",  # Alternative name
}

# Mapping of seva names/categories to account codes
SEVA_ACCOUNT_MAPPING = {
    # By category
    "abhisheka": "4201",
    "archana": "4202",
    "pooja": "4203",  # Special Pooja
    "alankara": "4204",
    "vahana_seva": "4205",
    "special": "4203",  # Special Pooja
    
    # By specific seva names (if needed)
    "Satyanarayana Pooja": "4206",
    "Navagraha Pooja": "4207",
    # Add more specific seva names as needed
}

def link_donation_categories(db: Session, temple_id: int = None):
    """Link donation categories to accounts"""
    print("\n" + "="*60)
    print("LINKING DONATION CATEGORIES TO ACCOUNTS")
    print("="*60)
    
    # Get all categories
    query = db.query(DonationCategory)
    if temple_id:
        query = query.filter(DonationCategory.temple_id == temple_id)
    categories = query.all()
    
    if not categories:
        print("No donation categories found!")
        return
    
    print(f"\nFound {len(categories)} donation categories")
    
    linked_count = 0
    not_found = []
    
    for category in categories:
        # Check if already linked
        if category.account_id:
            account = db.query(Account).filter(Account.id == category.account_id).first()
            if account:
                print(f"  ✓ {category.name} already linked to {account.account_code} - {account.account_name}")
                continue
        
        # Find matching account code
        account_code = None
        category_name_lower = category.name.lower()
        
        # Try exact match first
        if category.name in CATEGORY_ACCOUNT_MAPPING:
            account_code = CATEGORY_ACCOUNT_MAPPING[category.name]
        else:
            # Try case-insensitive match
            for key, code in CATEGORY_ACCOUNT_MAPPING.items():
                if key.lower() == category_name_lower:
                    account_code = code
                    break
        
        if not account_code:
            not_found.append(category.name)
            print(f"  ✗ {category.name} - No mapping found")
            continue
        
        # Find account by code
        account_query = db.query(Account).filter(Account.account_code == account_code)
        if temple_id:
            account_query = account_query.filter(Account.temple_id == temple_id)
        account = account_query.first()
        
        if not account:
            print(f"  ✗ {category.name} - Account {account_code} not found in database")
            not_found.append(f"{category.name} (Account {account_code} not found)")
            continue
        
        # Link the account
        category.account_id = account.id
        linked_count += 1
        print(f"  ✓ Linked {category.name} → {account.account_code} - {account.account_name}")
    
    db.commit()
    
    print(f"\n✓ Successfully linked {linked_count} categories")
    if not_found:
        print(f"\n⚠ {len(not_found)} categories could not be linked:")
        for name in not_found:
            print(f"  - {name}")
        print("\nTo fix:")
        print("  1. Add mapping to CATEGORY_ACCOUNT_MAPPING in this script")
        print("  2. Or manually link via API: PUT /api/v1/donations/categories/{id} with account_id")


def link_sevas(db: Session, temple_id: int = None):
    """Link sevas to accounts"""
    print("\n" + "="*60)
    print("LINKING SEVAS TO ACCOUNTS")
    print("="*60)
    
    # Get all sevas
    query = db.query(Seva).filter(Seva.is_active == True)
    if temple_id:
        # Note: Seva model might not have temple_id, adjust if needed
        pass
    sevas = query.all()
    
    if not sevas:
        print("No active sevas found!")
        return
    
    print(f"\nFound {len(sevas)} active sevas")
    
    linked_count = 0
    not_found = []
    
    for seva in sevas:
        # Check if already linked
        if seva.account_id:
            account = db.query(Account).filter(Account.id == seva.account_id).first()
            if account:
                print(f"  ✓ {seva.name_english} already linked to {account.account_code} - {account.account_name}")
                continue
        
        # Find matching account code by category
        account_code = None
        
        # Try category-based mapping
        if seva.category and seva.category.value in SEVA_ACCOUNT_MAPPING:
            account_code = SEVA_ACCOUNT_MAPPING[seva.category.value]
        
        # Try name-based mapping
        if not account_code:
            seva_name_lower = seva.name_english.lower()
            for key, code in SEVA_ACCOUNT_MAPPING.items():
                if key.lower() in seva_name_lower or seva_name_lower in key.lower():
                    account_code = code
                    break
        
        if not account_code:
            not_found.append(seva.name_english)
            print(f"  ✗ {seva.name_english} ({seva.category.value if seva.category else 'no category'}) - No mapping found")
            continue
        
        # Find account by code
        account_query = db.query(Account).filter(Account.account_code == account_code)
        if temple_id:
            account_query = account_query.filter(Account.temple_id == temple_id)
        account = account_query.first()
        
        if not account:
            print(f"  ✗ {seva.name_english} - Account {account_code} not found in database")
            not_found.append(f"{seva.name_english} (Account {account_code} not found)")
            continue
        
        # Link the account
        seva.account_id = account.id
        linked_count += 1
        print(f"  ✓ Linked {seva.name_english} ({seva.category.value}) → {account.account_code} - {account.account_name}")
    
    db.commit()
    
    print(f"\n✓ Successfully linked {linked_count} sevas")
    if not_found:
        print(f"\n⚠ {len(not_found)} sevas could not be linked:")
        for name in not_found:
            print(f"  - {name}")
        print("\nTo fix:")
        print("  1. Add mapping to SEVA_ACCOUNT_MAPPING in this script")
        print("  2. Or manually link via API: PUT /api/v1/sevas/{id} with account_id")


def show_unlinked_items(db: Session, temple_id: int = None):
    """Show categories and sevas that are not linked to accounts"""
    print("\n" + "="*60)
    print("UNLINKED ITEMS")
    print("="*60)
    
    # Unlinked categories
    query = db.query(DonationCategory).filter(DonationCategory.account_id == None)
    if temple_id:
        query = query.filter(DonationCategory.temple_id == temple_id)
    unlinked_categories = query.all()
    
    if unlinked_categories:
        print(f"\nUnlinked Donation Categories ({len(unlinked_categories)}):")
        for cat in unlinked_categories:
            print(f"  - {cat.name} (ID: {cat.id})")
    else:
        print("\n✓ All donation categories are linked!")
    
    # Unlinked sevas
    query = db.query(Seva).filter(
        Seva.is_active == True,
        Seva.account_id == None
    )
    unlinked_sevas = query.all()
    
    if unlinked_sevas:
        print(f"\nUnlinked Sevas ({len(unlinked_sevas)}):")
        for seva in unlinked_sevas:
            print(f"  - {seva.name_english} ({seva.category.value if seva.category else 'no category'}) (ID: {seva.id})")
    else:
        print("\n✓ All sevas are linked!")


def main():
    """Main entry point"""
    db = SessionLocal()
    
    try:
        # Auto-detect temple_id (for standalone mode)
        temple = db.query(Account).first()
        temple_id = temple.temple_id if temple else None
        
        if temple_id:
            print(f"Detected temple_id: {temple_id}")
        else:
            print("No temple_id detected - will link for all temples")
        
        # Link categories
        link_donation_categories(db, temple_id)
        
        # Link sevas
        link_sevas(db, temple_id)
        
        # Show unlinked items
        show_unlinked_items(db, temple_id)
        
        print("\n" + "="*60)
        print("LINKING COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Verify the links in your database")
        print("2. Test by creating a new donation/seva booking")
        print("3. Check that journal entries use the correct accounts")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()



