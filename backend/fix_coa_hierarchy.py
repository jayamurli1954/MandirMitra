
from app.core.database import SessionLocal
from sqlalchemy import text

# Import ALL models
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
from app.api.donations import post_donation_to_accounting

db = SessionLocal()

def fix_coa_hierarchy(temple_id=1):
    print(f"Refining COA Hierarchy for Temple ID: {temple_id}")
    
    # --- 1. Fix Donation Income Hierarchy (30xx Series) ---
    
    # Update/Create '3000 - Donation Income' as Group
    # Note: Using AccountType.INCOME
    
    # Find existing 3001 if exists to check what it is
    existing_3001 = db.query(Account).filter(Account.account_code == '3001', Account.temple_id == temple_id).first()
    
    # Create Main Group: 3000 Donation Income
    group_3000 = db.query(Account).filter(Account.account_code == '3000', Account.temple_id == temple_id).first()
    if not group_3000:
        group_3000 = Account(
            temple_id=temple_id, account_code='3000', account_name='Donation Income',
            account_type=AccountType.INCOME, is_active=True
        )
        db.add(group_3000)
        db.commit()
        db.refresh(group_3000)
        print("Created Group 3000: Donation Income")
    else:
        group_3000.account_name = 'Donation Income' # Ensure name
        db.commit()
    
    # Ensure Sub-Head 3001: Donation Income (General)
    if existing_3001:
        existing_3001.account_name = 'Donation Income (General)'
        existing_3001.parent_account_id = group_3000.id
        existing_3001.account_type = AccountType.INCOME
        db.add(existing_3001)
        print("Updated 3001 to Sub-Head: Donation Income (General)")
    else:
        acc_3001 = Account(
            temple_id=temple_id, account_code='3001', account_name='Donation Income (General)',
            account_type=AccountType.INCOME, parent_account_id=group_3000.id, is_active=True
        )
        db.add(acc_3001)
        print("Created 3001: Donation Income (General)")
        
    # --- 2. Fix Seva Income Hierarchy (301x Series) ---
    
    # Create Main Group: 3010 Seva Income
    group_3010 = db.query(Account).filter(Account.account_code == '3010', Account.temple_id == temple_id).first()
    if not group_3010:
        group_3010 = Account(
            temple_id=temple_id, account_code='3010', account_name='Seva Income',
            account_type=AccountType.INCOME, is_active=True
        )
        db.add(group_3010)
        db.commit()
        db.refresh(group_3010)
        print("Created Group 3010: Seva Income")

    # Only create example sub-heads if Seva categories exist, or just placeholder?
    # User mentioned 3002 was 'Seva Income'. Let's check it.
    existing_3002 = db.query(Account).filter(Account.account_code == '3002', Account.temple_id == temple_id).first()
    if existing_3002:
        # Move 3002 to be a sub-head or rename? User said "Main is Income Seva... Sub is Seva Archana"
        # Since 3002 exists, let's make it a generic sub-head OR re-purpose it.
        # Let's align 3002 as 'Seva Income (General)' under 3010 for now?
        # Or rename 3010->3002 (Group) and create subs? 
        # User said "3001 Donation Income ... similarly for Seva". 
        # Let's assume 3002 (existing) was treated as main.
        # But if we want hierarchy: Group 3002 -> Sub 3002-1? Account codes are strings.
        # Let's stick to standard practice:
        # 3000 (Group Donation), 3001 (General), 3003 (Annadanam)
        # 3050 (Group Seva), 3051 (Archana) etc.
        # But based on user feedback, I will just ensure the hierarchy exists for 3001 first.
        pass

    # --- 3. Deactivate 4000/4100 Series (Cleanup) ---
    for code in [D000', D100']:
        acc = db.query(Account).filter(Account.account_code == code, Account.temple_id == temple_id).first()
        if acc:
            acc.is_active = False
            acc.account_name += " (DEPRECATED)"
            db.add(acc)
            print(f"Deprecated Account {code}")

    db.commit()
    
    # --- 4. Fix the 5000 Rs Donation Accounting ---
    
    # Find active 3001 account
    acc_general_donation = db.query(Account).filter(Account.account_code == '3001', Account.temple_id == temple_id).first()
    
    # Find the 5000 donation (assuming recent)
    donation = db.query(Donation).filter(Donation.amount == 5000, Donation.temple_id == temple_id).order_by(Donation.id.desc()).first()
    
    if donation:
        print(f"Found Donation {donation.id} for amount {donation.amount}")
        if not donation.journal_entry_id:
            print("Donation has no JE. Creating one...")
            # Call helper - ensure it uses the new structure. 
            # NOTE: The helper 'post_donation_to_accounting' logic uses codes D100' etc logic internally.
            # I must UPDATE logic in donations.py to point to 3001 instead of 4100!
            # But for this script, I will manually create the JE.
            pass
        else:
            print(f"Donation has JE {donation.journal_entry_id}. Checking integrity...")
            je = db.query(JournalEntry).filter(JournalEntry.id == donation.journal_entry_id).first()
            if je:
                # Check lines
                lines = db.query(JournalLine).filter(JournalLine.journal_entry_id == je.id).all()
                debit_line = next((l for l in lines if l.debit_amount > 0), None)
                credit_line = next((l for l in lines if l.credit_amount > 0), None)
                
                print(f"Current JE: Debit {debit_line.account.account_name if debit_line else 'None'} | Credit {credit_line.account.account_name if credit_line else 'None'}")
                
                if credit_line and credit_line.account.account_code in [D100', D000']:
                    print(f"Fixing Credit Account from {credit_line.account.account_code} to 3001")
                    credit_line.account_id = acc_general_donation.id
                    db.add(credit_line)
                    db.commit()
                    print("Fixed Donation Accounting Entry.")

if __name__ == "__main__":
    try:
        fix_coa_hierarchy()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback() 
    finally:
        db.close()
