"""
Link Categories to Accounts Script

Automatically links donation categories and seva types to their corresponding
accounts in the chart of accounts based on name matching and code block structure.
"""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.donation import DonationCategory
from app.models.devotee import Devotee  # Needed for SQLAlchemy relationship resolution
from app.models.seva import Seva
from app.models.accounting import Account
from app.models.temple import Temple
from app.models.user import User  # Needed for SQLAlchemy relationship resolution
from app.models.panchang_display_settings import PanchangDisplaySettings  # Needed for SQLAlchemy relationship resolution

# Mapping for donation categories to account codes
DONATION_CATEGORY_MAPPING = {
    "General": "4101",
    "General Donation": "4101",
    "Cash": "4102",
    "Cash Donation": "4102",
    "Online": "4103",
    "UPI": "4103",
    "Online/UPI": "4103",
    "Hundi": "4104",
    "Hundi Collection": "4104",
    "Annadana": "4110",
    "Annadana Fund": "4110",
    "Building": "4111",
    "Construction": "4111",
    "Building Fund": "4111",
    "Building/Construction": "4111",
    "Festival": "4112",
    "Festival Fund": "4112",
    "Education": "4113",
    "Education Fund": "4113",
    "Corpus": "4114",
    "Corpus Fund": "4114",
    "Medical": "4115",
    "Medical Aid": "4115",
}

# Mapping for seva types to account codes
SEVA_CATEGORY_MAPPING = {
    "Abhisheka": "4201",
    "Archana": "4202",
    "Kumkumarchana": "4203",
    "Alankara": "4204",
    "Vahana": "4205",
    "Vahana Seva": "4205",
    "Satyanarayana": "4206",
    "Satyanarayana Pooja": "4206",
    "Navagraha": "4207",
    "Navagraha Pooja": "4207",
    "Special Pooja": "4208",
    "Kalyanam": "4209",
    "Marriage": "4209",
    "Upanayana": "4210",
    "Thread Ceremony": "4210",
    "Annaprasana": "4211",
    "Namakarana": "4212",
    "Ayushya Homam": "4213",
    "Mrityunjaya Homam": "4214",
    "Ganapathi Homam": "4215",
}

def find_best_match(name: str, mapping: dict) -> str:
    """Find best matching account code for a category name"""
    name_lower = name.lower()

    # Try exact match first
    for key, code in mapping.items():
        if key.lower() == name_lower:
            return code

    # Try partial match
    for key, code in mapping.items():
        if key.lower() in name_lower or name_lower in key.lower():
            return code

    return None

def link_donation_categories(db: Session, temple_id: int):
    """Link donation categories to accounts"""
    print("\n📦 Linking Donation Categories to Accounts")
    print("=" * 60)

    categories = db.query(DonationCategory).filter(
        DonationCategory.temple_id == temple_id
    ).all()

    linked_count = 0
    skipped_count = 0
    unmatched = []

    for category in categories:
        # Check if already linked
        if category.account_id:
            print(f"   ⏭️  {category.name}: Already linked")
            skipped_count += 1
            continue

        # Find matching account code
        account_code = find_best_match(category.name, DONATION_CATEGORY_MAPPING)

        if not account_code:
            # Default to General Donation
            account_code = "4101"
            unmatched.append(category.name)

        # Get account
        account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == account_code
        ).first()

        if account:
            category.account_id = account.id
            db.flush()
            print(f"   ✅ {category.name:30} → {account.account_code} - {account.account_name}")
            linked_count += 1
        else:
            print(f"   ⚠️  {category.name}: Account {account_code} not found")
            unmatched.append(category.name)

    db.commit()

    print(f"\n📊 Summary:")
    print(f"   Linked: {linked_count}")
    print(f"   Already linked: {skipped_count}")
    print(f"   Unmatched/Defaults: {len(unmatched)}")

    if unmatched:
        print(f"\n   Unmapped categories (using default 4101):")
        for cat in unmatched:
            print(f"     - {cat}")

def link_sevas(db: Session):
    """Link seva types to accounts"""
    print("\n🕉️  Linking Seva Types to Accounts")
    print("=" * 60)

    sevas = db.query(Seva).all()

    linked_count = 0
    skipped_count = 0
    unmatched = []

    for seva in sevas:
        # Check if already linked
        if seva.account_id:
            print(f"   ⏭️  {seva.name_english}: Already linked")
            skipped_count += 1
            continue

        # Try to match by English name
        account_code = find_best_match(seva.name_english, SEVA_CATEGORY_MAPPING)

        if not account_code:
            # Default to Special Pooja
            account_code = "4208"
            unmatched.append(seva.name_english)

        # Get account (sevas don't have temple_id, so get first match)
        account = db.query(Account).filter(
            Account.account_code == account_code
        ).first()

        if account:
            seva.account_id = account.id
            db.flush()
            print(f"   ✅ {seva.name_english:30} → {account.account_code} - {account.account_name}")
            linked_count += 1
        else:
            print(f"   ⚠️  {seva.name_english}: Account {account_code} not found")
            unmatched.append(seva.name_english)

    db.commit()

    print(f"\n📊 Summary:")
    print(f"   Linked: {linked_count}")
    print(f"   Already linked: {skipped_count}")
    print(f"   Unmatched/Defaults: {len(unmatched)}")

    if unmatched:
        print(f"\n   Unmapped sevas (using default 4208):")
        for seva_name in unmatched:
            print(f"     - {seva_name}")

def main():
    """Main function"""
    db = SessionLocal()

    try:
        # Get temple
        temple = db.query(Temple).first()

        if not temple:
            print("⚠️  No temple found. Please create a temple first.")
            return

        print(f"\n🕉️  Temple: {temple.name}")
        print(f"   ID: {temple.id}")

        # Check if chart of accounts exists
        account_count = db.query(Account).filter(Account.temple_id == temple.id).count()

        if account_count == 0:
            print("\n⚠️  No chart of accounts found!")
            print("   Please run: python seed_chart_of_accounts.py")
            return

        print(f"   Accounts in chart: {account_count}")

        # Link donation categories
        link_donation_categories(db, temple.id)

        # Link sevas
        link_sevas(db)

        print("\n" + "=" * 60)
        print("✅ Category-Account linking completed successfully!")
        print("\n💡 Next steps:")
        print("   1. New donations will use category-linked accounts")
        print("   2. New seva bookings will use seva-linked accounts")
        print("   3. Run sync_donations_to_accounting.py to update existing donations")
        print("   4. Run sync_sevas_to_accounting.py to post existing seva bookings")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
