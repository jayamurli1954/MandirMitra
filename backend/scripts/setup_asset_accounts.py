"""
Setup Asset Accounts in Chart of Accounts
Creates asset accounts (1500-1999 series) following standard accounting practices
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.accounting import Account, AccountType, AccountSubType

# Import all models to ensure relationships are properly configured
from app.models.temple import Temple
from app.models.user import User
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.seva import Seva, SevaBooking
from app.models.accounting import JournalEntry, JournalLine
from app.models.bank_reconciliation import BankStatement, BankStatementEntry, BankReconciliation, ReconciliationOutstandingItem
from app.models.financial_period import FinancialYear, FinancialPeriod, PeriodClosing
from app.models.vendor import Vendor
from app.models.token_seva import TokenInventory, TokenSale, TokenReconciliation
from app.models.inkind_sponsorship import (
    InKindDonation, InKindConsumption,
    Sponsorship, SponsorshipPayment
)
from app.models.upi_banking import (
    UpiPayment, BankAccount, BankTransaction
)
from app.models.inventory import Store, Item, StockBalance, StockMovement

# Asset Account Structure (1500-1999)
ASSET_ACCOUNT_STRUCTURE = {
    # Fixed Assets (1500-1599)
    "1500": {
        "account_name": "Fixed Assets",
        "account_name_kannada": "ಸ್ಥಿರ ಆಸ್ತಿಗಳು",
        "description": "All fixed assets (1500-1599 block)",
        "is_parent": True
    },
    "1501": {
        "account_name": "Land",
        "account_name_kannada": "ಭೂಮಿ",
        "description": "Land owned by temple",
        "parent_code": "1500",
        "is_depreciable": False
    },
    "1502": {
        "account_name": "Buildings",
        "account_name_kannada": "ಕಟ್ಟಡಗಳು",
        "description": "Temple buildings and structures",
        "parent_code": "1500",
        "is_depreciable": True
    },
    "1503": {
        "account_name": "Building Improvements",
        "account_name_kannada": "ಕಟ್ಟಡ ಸುಧಾರಣೆಗಳು",
        "description": "Improvements to buildings",
        "parent_code": "1500",
        "is_depreciable": True
    },
    "1510": {
        "account_name": "Vehicles",
        "account_name_kannada": "ವಾಹನಗಳು",
        "description": "Temple vehicles",
        "parent_code": "1500",
        "is_depreciable": True
    },
    "1520": {
        "account_name": "Furniture & Fixtures",
        "account_name_kannada": "ಪೀಠೋಪಕರಣಗಳು",
        "description": "Furniture and fixtures",
        "parent_code": "1500",
        "is_depreciable": True
    },
    "1530": {
        "account_name": "Computer & Equipment",
        "account_name_kannada": "ಕಂಪ್ಯೂಟರ್ ಮತ್ತು ಉಪಕರಣಗಳು",
        "description": "Computers and equipment",
        "parent_code": "1500",
        "is_depreciable": True
    },
    "1540": {
        "account_name": "Electrical Installations",
        "account_name_kannada": "ವಿದ್ಯುತ್ ಸ್ಥಾಪನೆಗಳು",
        "description": "Electrical installations",
        "parent_code": "1500",
        "is_depreciable": True
    },
    "1550": {
        "account_name": "Plumbing & Sanitation",
        "account_name_kannada": "ನೀರು ಮತ್ತು ಸ್ವಚ್ಛತೆ",
        "description": "Plumbing and sanitation systems",
        "parent_code": "1500",
        "is_depreciable": True
    },
    "1560": {
        "account_name": "Temple Idols & Statues",
        "account_name_kannada": "ದೇವಾಲಯ ಮೂರ್ತಿಗಳು",
        "description": "Temple idols and statues",
        "parent_code": "1500",
        "is_depreciable": False  # Usually not depreciated
    },
    "1570": {
        "account_name": "Sound & Lighting Systems",
        "account_name_kannada": "ಶಬ್ದ ಮತ್ತು ಬೆಳಕಿನ ವ್ಯವಸ್ಥೆಗಳು",
        "description": "Sound and lighting systems",
        "parent_code": "1500",
        "is_depreciable": True
    },
    "1580": {
        "account_name": "Other Fixed Assets",
        "account_name_kannada": "ಇತರ ಸ್ಥಿರ ಆಸ್ತಿಗಳು",
        "description": "Other fixed assets",
        "parent_code": "1500",
        "is_depreciable": True
    },
    
    # Capital Work in Progress (1600-1699)
    "1600": {
        "account_name": "Capital Work in Progress",
        "account_name_kannada": "ಬಂಡವಾಳ ಕೆಲಸ ಪ್ರಗತಿಯಲ್ಲಿದೆ",
        "description": "All CWIP projects (1600-1699 block)",
        "is_parent": True
    },
    "1601": {
        "account_name": "Building Construction",
        "account_name_kannada": "ಕಟ್ಟಡ ನಿರ್ಮಾಣ",
        "description": "Building construction in progress",
        "parent_code": "1600"
    },
    "1602": {
        "account_name": "Building Renovation",
        "account_name_kannada": "ಕಟ್ಟಡ ನವೀಕರಣ",
        "description": "Building renovation in progress",
        "parent_code": "1600"
    },
    "1603": {
        "account_name": "Infrastructure Development",
        "account_name_kannada": "ಮೂಲಸೌಕರ್ಯ ಅಭಿವೃದ್ಧಿ",
        "description": "Infrastructure development in progress",
        "parent_code": "1600"
    },
    "1610": {
        "account_name": "Installation in Progress",
        "account_name_kannada": "ಸ್ಥಾಪನೆ ಪ್ರಗತಿಯಲ್ಲಿದೆ",
        "description": "Installation projects in progress",
        "parent_code": "1600"
    },
    "1620": {
        "account_name": "Other CWIP",
        "account_name_kannada": "ಇತರ CWIP",
        "description": "Other capital work in progress",
        "parent_code": "1600"
    },
    
    # Accumulated Depreciation (1700-1799)
    "1700": {
        "account_name": "Accumulated Depreciation",
        "account_name_kannada": "ಸಂಚಿತ ಸವಕಳಿ",
        "description": "All accumulated depreciation (1700-1799 block)",
        "is_parent": True
    },
    "1701": {
        "account_name": "Accumulated Depreciation - Buildings",
        "account_name_kannada": "ಸಂಚಿತ ಸವಕಳಿ - ಕಟ್ಟಡಗಳು",
        "description": "Accumulated depreciation on buildings",
        "parent_code": "1700"
    },
    "1702": {
        "account_name": "Accumulated Depreciation - Vehicles",
        "account_name_kannada": "ಸಂಚಿತ ಸವಕಳಿ - ವಾಹನಗಳು",
        "description": "Accumulated depreciation on vehicles",
        "parent_code": "1700"
    },
    "1703": {
        "account_name": "Accumulated Depreciation - Equipment",
        "account_name_kannada": "ಸಂಚಿತ ಸವಕಳಿ - ಉಪಕರಣಗಳು",
        "description": "Accumulated depreciation on equipment",
        "parent_code": "1700"
    },
    "1710": {
        "account_name": "Accumulated Depreciation - Furniture",
        "account_name_kannada": "ಸಂಚಿತ ಸವಕಳಿ - ಪೀಠೋಪಕರಣಗಳು",
        "description": "Accumulated depreciation on furniture",
        "parent_code": "1700"
    },
    "1720": {
        "account_name": "Accumulated Depreciation - Other",
        "account_name_kannada": "ಸಂಚಿತ ಸವಕಳಿ - ಇತರ",
        "description": "Accumulated depreciation on other assets",
        "parent_code": "1700"
    },
    
    # Revaluation Reserve (1800-1899)
    "1800": {
        "account_name": "Revaluation Reserve",
        "account_name_kannada": "ಮರುಮೌಲ್ಯನ ಮೀಸಲು",
        "description": "All revaluation reserves (1800-1899 block)",
        "is_parent": True
    },
    "1801": {
        "account_name": "Revaluation Reserve - Land",
        "account_name_kannada": "ಮರುಮೌಲ್ಯನ ಮೀಸಲು - ಭೂಮಿ",
        "description": "Revaluation reserve for land",
        "parent_code": "1800"
    },
    "1802": {
        "account_name": "Revaluation Reserve - Buildings",
        "account_name_kannada": "ಮರುಮೌಲ್ಯನ ಮೀಸಲು - ಕಟ್ಟಡಗಳು",
        "description": "Revaluation reserve for buildings",
        "parent_code": "1800"
    },
    "1803": {
        "account_name": "Revaluation Reserve - Gold",
        "account_name_kannada": "ಮರುಮೌಲ್ಯನ ಮೀಸಲು - ಚಿನ್ನ",
        "description": "Revaluation reserve for gold",
        "parent_code": "1800"
    },
    "1804": {
        "account_name": "Revaluation Reserve - Silver",
        "account_name_kannada": "ಮರುಮೌಲ್ಯನ ಮೀಸಲು - ಬೆಳ್ಳಿ",
        "description": "Revaluation reserve for silver",
        "parent_code": "1800"
    },
    "1805": {
        "account_name": "Revaluation Reserve - Other",
        "account_name_kannada": "ಮರುಮೌಲ್ಯನ ಮೀಸಲು - ಇತರ",
        "description": "Revaluation reserve for other assets",
        "parent_code": "1800"
    },
    
    # Precious Assets (1900-1999)
    "1900": {
        "account_name": "Precious Assets",
        "account_name_kannada": "ಬೆಲೆಬಾಳುವ ಆಸ್ತಿಗಳು",
        "description": "All precious assets (1900-1999 block)",
        "is_parent": True
    },
    "1901": {
        "account_name": "Gold Ornaments",
        "account_name_kannada": "ಚಿನ್ನದ ಆಭರಣಗಳು",
        "description": "Gold ornaments and items",
        "parent_code": "1900",
        "is_depreciable": False
    },
    "1902": {
        "account_name": "Silver Articles",
        "account_name_kannada": "ಬೆಳ್ಳಿ ವಸ್ತುಗಳು",
        "description": "Silver articles and items",
        "parent_code": "1900",
        "is_depreciable": False
    },
    "1903": {
        "account_name": "Precious Stones",
        "account_name_kannada": "ಬೆಲೆಬಾಳುವ ಕಲ್ಲುಗಳು",
        "description": "Precious stones and gems",
        "parent_code": "1900",
        "is_depreciable": False
    },
    "1904": {
        "account_name": "Other Precious Items",
        "account_name_kannada": "ಇತರ ಬೆಲೆಬಾಳುವ ವಸ್ತುಗಳು",
        "description": "Other precious items",
        "parent_code": "1900",
        "is_depreciable": False
    }
}

# Depreciation Expense Accounts (6000-6099)
DEPRECIATION_EXPENSE_ACCOUNTS = {
    "6001": {
        "account_name": "Depreciation Expense",
        "account_name_kannada": "ಸವಕಳಿ ವೆಚ್ಚ",
        "description": "Depreciation expense for all assets",
        "parent_code": "6000"  # Assuming 6000 is Expenses parent
    }
}


def get_or_create_parent_account(db: Session, temple_id: int, account_code: str):
    """Get or create parent account (1000 - Assets)"""
    parent_account = db.query(Account).filter(
        Account.temple_id == temple_id,
        Account.account_code == "1000"
    ).first()
    
    if not parent_account:
        print(f"⚠️  Parent account 1000 (Assets) not found. Please run seed_chart_of_accounts.py first.")
        return None
    
    return parent_account


def create_asset_accounts(db: Session, temple_id: int):
    """Create asset accounts (1500-1999 series)"""
    parent_account = get_or_create_parent_account(db, temple_id, "1000")
    if not parent_account:
        return False
    
    created_count = 0
    updated_count = 0
    
    # Create parent accounts first
    parent_accounts = {}
    for code, data in ASSET_ACCOUNT_STRUCTURE.items():
        if data.get("is_parent"):
            account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == code
            ).first()
            
            if not account:
                account = Account(
                    temple_id=temple_id,
                    account_code=code,
                    account_name=data["account_name"],
                    account_name_kannada=data.get("account_name_kannada", ""),
                    account_type=AccountType.ASSET,
                    account_subtype=AccountSubType.FIXED_ASSET if "1500" <= code < "1600" else AccountSubType.INVENTORY if "1900" <= code < "2000" else None,
                    parent_account_id=parent_account.id,
                    is_system_account=True,
                    allow_manual_entry=False,
                    description=data["description"]
                )
                db.add(account)
                db.flush()
                created_count += 1
                print(f"✅ Created parent account: {code} - {account.account_name}")
            else:
                updated_count += 1
                print(f"ℹ️  Parent account {code} already exists")
            
            parent_accounts[code] = account
    
    # Create child accounts
    for code, data in ASSET_ACCOUNT_STRUCTURE.items():
        if data.get("is_parent"):
            continue
        
        parent_code = data.get("parent_code")
        if not parent_code or parent_code not in parent_accounts:
            continue
        
        account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == code
        ).first()
        
        if not account:
            # Determine account subtype
            if "1500" <= code < "1600":
                subtype = AccountSubType.FIXED_ASSET
            elif "1600" <= code < "1700":
                subtype = AccountSubType.FIXED_ASSET  # CWIP is also fixed asset
            elif "1700" <= code < "1800":
                subtype = AccountSubType.FIXED_ASSET  # Accumulated depreciation
            elif "1800" <= code < "1900":
                subtype = None  # Revaluation reserve (equity)
            elif "1900" <= code < "2000":
                subtype = AccountSubType.PRECIOUS_ASSET
            else:
                subtype = AccountSubType.FIXED_ASSET
            
            account = Account(
                temple_id=temple_id,
                account_code=code,
                account_name=data["account_name"],
                account_name_kannada=data.get("account_name_kannada", ""),
                account_type=AccountType.ASSET,
                account_subtype=subtype,
                parent_account_id=parent_accounts[parent_code].id,
                is_system_account=True,
                allow_manual_entry=False,
                description=data["description"]
            )
            db.add(account)
            db.flush()
            created_count += 1
            print(f"✅ Created account: {code} - {account.account_name}")
        else:
            updated_count += 1
            print(f"ℹ️  Account {code} already exists")
    
    db.commit()
    print(f"\n📊 Summary: Created {created_count} accounts, {updated_count} already existed")
    return True


def main():
    """Main function to setup asset accounts"""
    print("=" * 60)
    print("Asset Accounts Setup")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get temple_id from accounts
        sample_account = db.query(Account).filter(Account.account_code == "1000").first()
        temple_id = sample_account.temple_id if sample_account else None
        
        if temple_id:
            print(f"🏛️  Processing temple ID: {temple_id}")
        else:
            print("🏛️  Processing in standalone mode (temple_id=None)")
        
        print("-" * 60)
        
        # Create asset accounts
        print("\n📝 Creating asset accounts (1500-1999)...")
        if create_asset_accounts(db, temple_id):
            print("✅ Asset accounts created successfully")
        else:
            print("❌ Failed to create asset accounts")
            return
        
        print("\n" + "=" * 60)
        print("✅ Asset accounts setup completed!")
        print("\nAccount Code Series:")
        print("  1500-1599 - Fixed Assets")
        print("  1600-1699 - Capital Work in Progress")
        print("  1700-1799 - Accumulated Depreciation")
        print("  1800-1899 - Revaluation Reserve")
        print("  1900-1999 - Precious Assets")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    main()




