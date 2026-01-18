"""
Script to create In-Kind Donation and Sponsorship accounts if they don't exist
Run this to ensure all in-kind accounts are available for proper accounting
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.temple import Temple
from app.models.accounting import Account, AccountType, AccountSubType

def create_inkind_accounts(db: Session, temple_id: int):
    """
    Create in-kind donation and sponsorship accounts if they don't exist
    """
    accounts_to_create = [
        # In-Kind Donation Income (if not exists)
        {
            "account_code": "4400",
            "account_name": "In-Kind Donation Income",
            "account_name_kannada": "ವಸ್ತು ದಾನ ಆದಾಯ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_account_id": None,  # Will be set to 4000 if exists
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Income from non-monetary donations and in-kind sponsorships"
        },
        {
            "account_code": "4403",
            "account_name": "In-Kind Sponsorship Income",
            "account_name_kannada": "ವಸ್ತು ಪ್ರಾಯೋಜಕತ್ವ ಆದಾಯ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SPONSORSHIP_INCOME,
            "parent_account_id": None,  # Will be set to 4400 if exists
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Income from in-kind sponsorships (direct vendor payment)"
        },
        # In-Kind Expense Accounts (for direct payment sponsorships)
        {
            "account_code": "5404",
            "account_name": "Flower Decoration Expense (In-Kind)",
            "account_name_kannada": "ಹೂವಿನ ಅಲಂಕಾರ ವೆಚ್ಚ (ವಸ್ತು)",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.FESTIVAL_EXPENSE,
            "parent_account_id": None,  # Will be set to 5400 if exists
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Flower decoration expense for in-kind sponsorships (no cash movement)"
        },
        {
            "account_code": "5405",
            "account_name": "Lighting Expense (In-Kind)",
            "account_name_kannada": "ಬೆಳಕು ವೆಚ್ಚ (ವಸ್ತು)",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.FESTIVAL_EXPENSE,
            "parent_account_id": None,  # Will be set to 5400 if exists
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Lighting expense for in-kind sponsorships (no cash movement)"
        },
        {
            "account_code": "5406",
            "account_name": "Tent Expense (In-Kind)",
            "account_name_kannada": "ಟೆಂಟ್ ವೆಚ್ಚ (ವಸ್ತು)",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.FESTIVAL_EXPENSE,
            "parent_account_id": None,  # Will be set to 5400 if exists
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Tent expense for in-kind sponsorships (no cash movement)"
        },
        {
            "account_code": "5407",
            "account_name": "Sound System Expense (In-Kind)",
            "account_name_kannada": "ಧ್ವನಿ ವ್ಯವಸ್ಥೆ ವೆಚ್ಚ (ವಸ್ತು)",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.FESTIVAL_EXPENSE,
            "parent_account_id": None,  # Will be set to 5400 if exists
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Sound system expense for in-kind sponsorships (no cash movement)"
        },
    ]
    
    # Get parent accounts
    parent_4000 = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == D000"
    ).first()
    
    parent_5400 = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == "5400"
    ).first()
    
    parent_4400 = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == "4400"
    ).first()
    
    created_count = 0
    for acc_data in accounts_to_create:
        # Check if account already exists
        existing = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == acc_data["account_code"]
        ).first()
        
        if existing:
            print(f"ℹ️  Account {acc_data['account_code']} already exists: {existing.account_name}")
            continue
        
        # Set parent account
        if acc_data["account_code"] in ["4400", "4403"]:
            acc_data["parent_account_id"] = parent_4000.id if parent_4000 else None
        elif acc_data["account_code"] in ["5404", "5405", "5406", "5407"]:
            acc_data["parent_account_id"] = parent_5400.id if parent_5400 else None
        
        # For 4403, set parent to 4400 if it exists
        if acc_data["account_code"] == "4403" and parent_4400:
            acc_data["parent_account_id"] = parent_4400.id
        
        account = Account(
            temple_id=temple_id,
            **acc_data
        )
        db.add(account)
        created_count += 1
        print(f"✅ Created account {acc_data['account_code']}: {acc_data['account_name']}")
    
    db.commit()
    print(f"\n✅ Created {created_count} in-kind accounts for temple_id {temple_id}")
    return created_count


def main():
    db = SessionLocal()
    try:
        # Get all temples
        temples = db.query(Temple).all()
        
        if not temples:
            print("❌ No temples found. Please create a temple first.")
            return
        
        for temple in temples:
            print(f"\n📋 Processing temple: {temple.name} (ID: {temple.id})")
            create_inkind_accounts(db, temple.id)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()


