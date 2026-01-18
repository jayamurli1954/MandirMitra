
from app.core.database import SessionLocal
from sqlalchemy import text

# Import ALL models to ensure mappers are initialized correctly
from app.models.user import User
from app.models.temple import Temple
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry, JournalLine, AccountType
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.inventory import Store, Item, StockBalance, StockMovement
from app.models.asset import Asset
from app.models.asset_history import AssetTransfer, AssetValuationHistory, AssetPhysicalVerification, AssetInsurance, AssetDocument
from app.models.hundi import HundiOpening, HundiMaster, HundiDenominationCount
from app.models.hr import Employee, Department, Designation, SalaryComponent, SalaryStructure, Payroll, LeaveType, LeaveApplication
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.upi_banking import BankAccount, UpiPayment, BankTransaction
from app.models.token_seva import TokenInventory, TokenSale, TokenReconciliation
from app.models.budget import Budget
from app.models.bank_reconciliation import BankReconciliation, BankStatement, BankStatementEntry
from app.models.financial_period import FinancialPeriod
from app.models.inkind_sponsorship import InKindDonation, Sponsorship
from app.api.donations import post_donation_to_accounting

db = SessionLocal()

def fix_accounts(temple_id=1):
    print(f"Fixing accounts for Temple ID: {temple_id}")
    
    # 1. Create Root Accounts if missing
    assets_root = db.query(Account).filter(Account.temple_id == temple_id, Account.account_code == A000').first()
    if not assets_root:
        assets_root = Account(
            temple_id=temple_id, account_code=A000', account_name='Assets', 
            account_type=AccountType.ASSET
        )
        db.add(assets_root)
        db.commit()
    
    income_root = db.query(Account).filter(Account.temple_id == temple_id, Account.account_code == D000').first()
    if not income_root:
        income_root = Account(
            temple_id=temple_id, account_code=D000', account_name='Income', 
            account_type=AccountType.INCOME
        )
        db.add(income_root)
        db.commit()

    # 2. Create Leaf Accounts
    accounts_to_create = [
        {'code': A101', 'name': 'Cash in Hand - Counter', 'type': AccountType.ASSET, 'parent': assets_root.id},
        {'code': A102', 'name': 'Cash in Hand - Hundi', 'type': AccountType.ASSET, 'parent': assets_root.id},
        {'code': A110', 'name': 'Main Bank Account', 'type': AccountType.ASSET, 'parent': assets_root.id},
        {'code': '1300', 'name': 'Inventory Assets', 'type': AccountType.ASSET, 'parent': assets_root.id},
        {'code': D100', 'name': 'Donation Income (General)', 'type': AccountType.INCOME, 'parent': income_root.id}
    ]

    for acc_data in accounts_to_create:
        acc = db.query(Account).filter(Account.temple_id == temple_id, Account.account_code == acc_data['code']).first()
        if not acc:
            print(f"Creating account {acc_data['code']} - {acc_data['name']}")
            new_acc = Account(
                temple_id=temple_id,
                account_code=acc_data['code'],
                account_name=acc_data['name'],
                account_type=acc_data['type'],
                parent_account_id=acc_data['parent'],
                is_active=True
            )
            db.add(new_acc)
        else:
            print(f"Account {acc_data['code']} already exists.")

    db.commit()
    print("Accounts fixed successfully.")

if __name__ == "__main__":
    try:
        fix_accounts()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
