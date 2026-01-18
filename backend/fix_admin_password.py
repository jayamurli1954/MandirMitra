
import os
import sys

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# --- MONKEY PATCH FOR BCRYPT/PASSLIB ---
import bcrypt
if not hasattr(bcrypt, '__about__'):
    class MockAbout:
        __version__ = bcrypt.__version__
    bcrypt.__about__ = MockAbout()
# ---------------------------------------

from app.core.database import SessionLocal
from app.models.user import User
# Comprehensive models import to avoid Mapper errors
from app.models.temple import Temple
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import Seva, SevaBooking
from app.models.accounting import Account, JournalEntry
from app.models.inventory import Store, Item
from app.models.asset import Asset
from app.models.hundi import HundiOpening
from app.models.hr import Employee
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.upi_banking import BankAccount
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.asset_history import AssetTransfer
from app.models.budget import Budget
from app.models.bank_reconciliation import BankReconciliation
from app.models.financial_period import FinancialPeriod
from app.models.inkind_sponsorship import InKindDonation
from app.core.security import get_password_hash

def fix_admin_password():
    session = SessionLocal()
    try:
        print("Fixing Admin Password...")
        admin = session.query(User).filter(User.email == "admin@temple.com").first()
        if not admin:
            print("❌ Admin user not found!")
            return

        # Use direct bcrypt hashing to avoid passlib errors
        print(f"Hashing password 'admin123'...")
        password_bytes = "admin123".encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        new_hash = hashed_bytes.decode('utf-8')
        
        # Ensure the hash format is compatible ($2b$...)
        print(f"Generated hash: {new_hash}")
        
        admin.password_hash = new_hash
        session.commit()
        print("✅ Admin password reset to 'admin123' successfully.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    fix_admin_password()
