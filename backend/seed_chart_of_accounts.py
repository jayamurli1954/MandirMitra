"""
Seed Script: Default Chart of Accounts
Creates a comprehensive chart of accounts for a new temple
Run this after temple registration to set up accounting structure
"""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.temple import Temple
from app.models.accounting import Account, AccountType, AccountSubType

# Import all models to ensure tables are created
from app.models.user import User
from app.models.devotee import Devotee
from app.models.donation import Donation, DonationCategory
from app.models.seva import Seva, SevaBooking
from app.models.vendor import Vendor
from app.models.inkind_sponsorship import InKindDonation, InKindConsumption, Sponsorship, SponsorshipPayment
from app.models.upi_banking import UpiPayment, BankAccount, BankTransaction, BankReconciliation
from app.models.accounting import JournalEntry, JournalLine
from app.models.panchang_display_settings import PanchangDisplaySettings


def create_default_chart_of_accounts(db: Session, temple_id: int):
    """
    Create default chart of accounts for a temple
    """

    accounts = [
        # ===== ASSETS =====

        # Main Asset Account
        {
            "account_code": "1000",
            "account_name": "Assets",
            "account_name_kannada": "ಆಸ್ತಿಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": None,
            "parent_account_id": None,
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "All assets owned by the temple"
        },

        # Current Assets
        {
            "account_code": "1100",
            "account_name": "Current Assets",
            "account_name_kannada": "ಚಾಲ್ತಿ ಆಸ್ತಿಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.CURRENT_ASSET,
            "parent_code": "1000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Assets that can be converted to cash within one year"
        },
        {
            "account_code": "1101",
            "account_name": "Cash in Hand - Counter",
            "account_name_kannada": "ಕೈಯಲ್ಲಿರುವ ನಗದು - ಕೌಂಟರ್",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.CASH_BANK,
            "parent_code": "1100",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Cash at donation counter"
        },
        {
            "account_code": "1102",
            "account_name": "Cash in Hand - Hundi",
            "account_name_kannada": "ಕೈಯಲ್ಲಿರುವ ನಗದು - ಹುಂಡಿ",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.CASH_BANK,
            "parent_code": "1100",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Cash from hundi collection"
        },
        {
            "account_code": "1110",
            "account_name": "Bank - SBI Current Account",
            "account_name_kannada": "ಬ್ಯಾಂಕ್ - ಎಸ್‌ಬಿಐ ಚಾಲ್ತಿ ಖಾತೆ",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.CASH_BANK,
            "parent_code": "1100",
            "is_system_account": False,
            "allow_manual_entry": True,
            "description": "SBI Current Account"
        },
        {
            "account_code": "1111",
            "account_name": "Bank - HDFC Savings Account",
            "account_name_kannada": "ಬ್ಯಾಂಕ್ - ಎಚ್‌ಡಿಎಫ್‌ಸಿ ಉಳಿತಾಯ ಖಾತೆ",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.CASH_BANK,
            "parent_code": "1100",
            "is_system_account": False,
            "allow_manual_entry": True,
            "description": "HDFC Savings Account"
        },
        {
            "account_code": "1120",
            "account_name": "Sponsorship Receivable",
            "account_name_kannada": "ಪ್ರಾಯೋಜಕತ್ವ ಸ್ವೀಕರಿಸಬೇಕಾದವು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.RECEIVABLE,
            "parent_code": "1100",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Amount receivable from committed sponsorships"
        },
        {
            "account_code": "1130",
            "account_name": "Inventory - Annadana Stores",
            "account_name_kannada": "ದಾಸ್ತಾನು - ಅನ್ನದಾನ ಸಾಮಗ್ರಿಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.INVENTORY,
            "parent_code": "1100",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Rice, Dal, Oil and other consumables for Annadana"
        },
        {
            "account_code": "1131",
            "account_name": "Inventory - Pooja Materials",
            "account_name_kannada": "ದಾಸ್ತಾನು - ಪೂಜಾ ಸಾಮಗ್ರಿಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.INVENTORY,
            "parent_code": "1100",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Flowers, oil, camphor, incense for pooja"
        },

        # Fixed Assets
        {
            "account_code": "1200",
            "account_name": "Fixed Assets",
            "account_name_kannada": "ಸ್ಥಿರ ಆಸ್ತಿಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.FIXED_ASSET,
            "parent_code": "1000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Long-term assets"
        },
        {
            "account_code": "1201",
            "account_name": "Temple Building",
            "account_name_kannada": "ದೇವಾಲಯ ಕಟ್ಟಡ",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.FIXED_ASSET,
            "parent_code": "1200",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Temple building and structures"
        },
        {
            "account_code": "1202",
            "account_name": "Land",
            "account_name_kannada": "ಭೂಮಿ",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.FIXED_ASSET,
            "parent_code": "1200",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Land owned by temple"
        },
        {
            "account_code": "1210",
            "account_name": "Furniture & Fixtures",
            "account_name_kannada": "ಪೀಠೋಪಕರಣಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.FIXED_ASSET,
            "parent_code": "1200",
            "is_system_account": False,
            "allow_manual_entry": True,
            "description": "Chairs, tables, almirahs"
        },
        {
            "account_code": "1211",
            "account_name": "Vehicles",
            "account_name_kannada": "ವಾಹನಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.FIXED_ASSET,
            "parent_code": "1200",
            "is_system_account": False,
            "allow_manual_entry": True,
            "description": "Temple vehicles"
        },
        {
            "account_code": "1212",
            "account_name": "Computer & Equipment",
            "account_name_kannada": "ಕಂಪ್ಯೂಟರ್ ಮತ್ತು ಉಪಕರಣಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.FIXED_ASSET,
            "parent_code": "1200",
            "is_system_account": False,
            "allow_manual_entry": True,
            "description": "Computers, printers, sound systems"
        },

        # Precious Assets
        {
            "account_code": "1300",
            "account_name": "Precious Assets",
            "account_name_kannada": "ಬೆಲೆಬಾಳುವ ಆಸ್ತಿಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.PRECIOUS_ASSET,
            "parent_code": "1000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Gold, silver, precious items"
        },
        {
            "account_code": "1301",
            "account_name": "Gold Ornaments",
            "account_name_kannada": "ಚಿನ್ನದ ಆಭರಣಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.PRECIOUS_ASSET,
            "parent_code": "1300",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Gold ornaments donated to temple"
        },
        {
            "account_code": "1302",
            "account_name": "Silver Articles",
            "account_name_kannada": "ಬೆಳ್ಳಿ ವಸ್ತುಗಳು",
            "account_type": AccountType.ASSET,
            "account_subtype": AccountSubType.PRECIOUS_ASSET,
            "parent_code": "1300",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Silver articles donated to temple"
        },

        # ===== LIABILITIES =====

        # Main Liability Account
        {
            "account_code": "2000",
            "account_name": "Liabilities",
            "account_name_kannada": "ಹೊಣೆಗಾರಿಕೆಗಳು",
            "account_type": AccountType.LIABILITY,
            "account_subtype": None,
            "parent_account_id": None,
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "All liabilities and obligations"
        },

        # Current Liabilities
        {
            "account_code": "2100",
            "account_name": "Current Liabilities",
            "account_name_kannada": "ಚಾಲ್ತಿ ಹೊಣೆಗಾರಿಕೆಗಳು",
            "account_type": AccountType.LIABILITY,
            "account_subtype": AccountSubType.CURRENT_LIABILITY,
            "parent_code": "2000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Short-term obligations"
        },
        {
            "account_code": "2101",
            "account_name": "Vendor Payables",
            "account_name_kannada": "ಮಾರಾಟಗಾರರಿಗೆ ಪಾವತಿಸಬೇಕಾದವು",
            "account_type": AccountType.LIABILITY,
            "account_subtype": AccountSubType.CURRENT_LIABILITY,
            "parent_code": "2100",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Amount payable to vendors"
        },
        {
            "account_code": "2102",
            "account_name": "Advance from Devotees",
            "account_name_kannada": "ಭಕ್ತರಿಂದ ಮುಂಗಡ",
            "account_type": AccountType.LIABILITY,
            "account_subtype": AccountSubType.CURRENT_LIABILITY,
            "parent_code": "2100",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Advance received for future sevas/events"
        },

        # Long-term Liabilities
        {
            "account_code": "2200",
            "account_name": "Long-term Liabilities",
            "account_name_kannada": "ದೀರ್ಘಾವಧಿ ಹೊಣೆಗಾರಿಕೆಗಳು",
            "account_type": AccountType.LIABILITY,
            "account_subtype": AccountSubType.LONG_TERM_LIABILITY,
            "parent_code": "2000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Long-term obligations"
        },

        # ===== EQUITY/FUNDS =====

        # Main Equity Account
        {
            "account_code": "3000",
            "account_name": "Corpus & Funds",
            "account_name_kannada": "ನಿಧಿಗಳು",
            "account_type": AccountType.EQUITY,
            "account_subtype": AccountSubType.CORPUS_FUND,
            "parent_account_id": None,
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Corpus and reserve funds"
        },
        {
            "account_code": "3001",
            "account_name": "Corpus Fund",
            "account_name_kannada": "ಮೂಲ ನಿಧಿ",
            "account_type": AccountType.EQUITY,
            "account_subtype": AccountSubType.CORPUS_FUND,
            "parent_code": "3000",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Permanent endowment fund (cannot be spent)"
        },
        {
            "account_code": "3002",
            "account_name": "Building Fund",
            "account_name_kannada": "ಕಟ್ಟಡ ನಿಧಿ",
            "account_type": AccountType.EQUITY,
            "account_subtype": AccountSubType.GENERAL_FUND,
            "parent_code": "3000",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Fund reserved for building construction/renovation"
        },

        # ===== INCOME =====

        # Main Income Account
        {
            "account_code": "4000",
            "account_name": "Income",
            "account_name_kannada": "ಆದಾಯ",
            "account_type": AccountType.INCOME,
            "account_subtype": None,
            "parent_account_id": None,
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "All income received"
        },

        # ===== DONATION INCOME BLOCK (4100-4199) =====
        # Parent Account
        {
            "account_code": "4100",
            "account_name": "Donation Income",
            "account_name_kannada": "ದಾನ ಆದಾಯ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "All donation income (4100-4199 block)"
        },
        # General/Method-based Donations (4101-4109)
        {
            "account_code": "4101",
            "account_name": "General Donation",
            "account_name_kannada": "ಸಾಮಾನ್ಯ ದಾನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4100",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "General donations without specific category"
        },
        {
            "account_code": "4102",
            "account_name": "Cash Donation",
            "account_name_kannada": "ನಗದು ದಾನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4100",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Cash donations received at counter"
        },
        {
            "account_code": "4103",
            "account_name": "Online/UPI Donation",
            "account_name_kannada": "ಆನ್‌ಲೈನ್/ಯುಪಿಐ ದಾನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4100",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Online and UPI donations"
        },
        {
            "account_code": "4104",
            "account_name": "Hundi Collection",
            "account_name_kannada": "ಹುಂಡಿ ಸಂಗ್ರಹ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4100",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Collections from hundi"
        },
        # Purpose-based Donations (4110-4149)
        {
            "account_code": "4110",
            "account_name": "Annadana Fund Donation",
            "account_name_kannada": "ಅನ್ನದಾನ ನಿಧಿ ದಾನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4100",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Donations for free food distribution"
        },
        {
            "account_code": "4111",
            "account_name": "Building/Construction Fund",
            "account_name_kannada": "ಕಟ್ಟಡ ನಿಧಿ ದಾನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4100",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Donations for temple construction/renovation"
        },
        {
            "account_code": "4112",
            "account_name": "Festival Fund Donation",
            "account_name_kannada": "ಉತ್ಸವ ನಿಧಿ ದಾನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4100",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Donations for festival celebrations"
        },
        {
            "account_code": "4113",
            "account_name": "Education Fund Donation",
            "account_name_kannada": "ಶಿಕ್ಷಣ ನಿಧಿ ದಾನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4100",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Donations for educational activities"
        },
        {
            "account_code": "4114",
            "account_name": "Corpus Fund Donation",
            "account_name_kannada": "ಮೂಲ ನಿಧಿ ದಾನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4100",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Donations to permanent endowment fund"
        },
        {
            "account_code": "4115",
            "account_name": "Medical Aid Fund Donation",
            "account_name_kannada": "ವೈದ್ಯಕೀಯ ಸಹಾಯ ನಿಧಿ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4100",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Donations for medical assistance programs"
        },
        # Codes 4116-4199 reserved for future donation categories

        # ===== SEVA INCOME BLOCK (4200-4299) =====
        # Parent Account
        {
            "account_code": "4200",
            "account_name": "Seva Income",
            "account_name_kannada": "ಸೇವಾ ಆದಾಯ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "All seva and pooja income (4200-4299 block)"
        },
        # Individual Seva Types (4201-4249)
        {
            "account_code": "4201",
            "account_name": "Abhisheka Seva",
            "account_name_kannada": "ಅಭಿಷೇಕ ಸೇವೆ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Abhisheka seva bookings"
        },
        {
            "account_code": "4202",
            "account_name": "Archana",
            "account_name_kannada": "ಅರ್ಚನೆ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Archana bookings"
        },
        {
            "account_code": "4203",
            "account_name": "Kumkumarchana",
            "account_name_kannada": "ಕುಂಕುಮಾರ್ಚನೆ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Kumkumarchana seva"
        },
        {
            "account_code": "4204",
            "account_name": "Alankara Seva",
            "account_name_kannada": "ಅಲಂಕಾರ ಸೇವೆ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Alankara (decoration) seva"
        },
        {
            "account_code": "4205",
            "account_name": "Vahana Seva",
            "account_name_kannada": "ವಾಹನ ಸೇವೆ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Vahana seva bookings"
        },
        {
            "account_code": "4206",
            "account_name": "Satyanarayana Pooja",
            "account_name_kannada": "ಸತ್ಯನಾರಾಯಣ ಪೂಜೆ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Satyanarayana Pooja"
        },
        {
            "account_code": "4207",
            "account_name": "Navagraha Pooja",
            "account_name_kannada": "ನವಗ್ರಹ ಪೂಜೆ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Navagraha Pooja"
        },
        {
            "account_code": "4208",
            "account_name": "Special Pooja",
            "account_name_kannada": "ವಿಶೇಷ ಪೂಜೆ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from special poojas"
        },
        {
            "account_code": "4209",
            "account_name": "Kalyanam/Marriage Ceremony",
            "account_name_kannada": "ಕಲ್ಯಾಣ / ವಿವಾಹ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from temple marriage ceremonies"
        },
        {
            "account_code": "4210",
            "account_name": "Upanayana/Thread Ceremony",
            "account_name_kannada": "ಉಪನಯನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Upanayana ceremonies"
        },
        {
            "account_code": "4211",
            "account_name": "Annaprasana/First Rice Ceremony",
            "account_name_kannada": "ಅನ್ನಪ್ರಾಶನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Annaprasana ceremonies"
        },
        {
            "account_code": "4212",
            "account_name": "Namakarana/Naming Ceremony",
            "account_name_kannada": "ನಾಮಕರಣ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Namakarana ceremonies"
        },
        {
            "account_code": "4213",
            "account_name": "Ayushya Homam",
            "account_name_kannada": "ಆಯುಷ್ಯ ಹೋಮ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Ayushya Homam"
        },
        {
            "account_code": "4214",
            "account_name": "Mrityunjaya Homam",
            "account_name_kannada": "ಮೃತ್ಯುಂಜಯ ಹೋಮ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Mrityunjaya Homam"
        },
        {
            "account_code": "4215",
            "account_name": "Ganapathi Homam",
            "account_name_kannada": "ಗಣಪತಿ ಹೋಮ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SEVA_INCOME,
            "parent_code": "4200",
            "is_system_account": False,
            "allow_manual_entry": False,
            "description": "Income from Ganapathi Homam"
        },
        # Codes 4216-4299 reserved for future seva types

        # Sponsorship Income
        {
            "account_code": "4300",
            "account_name": "Sponsorship Income",
            "account_name_kannada": "ಪ್ರಾಯೋಜಕತ್ವ ಆದಾಯ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SPONSORSHIP_INCOME,
            "parent_code": "4000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Income from sponsorships"
        },
        {
            "account_code": "4301",
            "account_name": "Festival Sponsorship",
            "account_name_kannada": "ಉತ್ಸವ ಪ್ರಾಯೋಜಕತ್ವ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SPONSORSHIP_INCOME,
            "parent_code": "4300",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Festival sponsorship income"
        },
        {
            "account_code": "4302",
            "account_name": "Annadana Sponsorship",
            "account_name_kannada": "ಅನ್ನದಾನ ಪ್ರಾಯೋಜಕತ್ವ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.SPONSORSHIP_INCOME,
            "parent_code": "4300",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Annadana sponsorship income"
        },

        # In-Kind Donation Income
        {
            "account_code": "4400",
            "account_name": "In-Kind Donation Income",
            "account_name_kannada": "ವಸ್ತು ದಾನ ಆದಾಯ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Income from non-monetary donations"
        },
        {
            "account_code": "4401",
            "account_name": "Consumables Donation",
            "account_name_kannada": "ಉಪಭೋಗ ವಸ್ತುಗಳ ದಾನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4400",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Rice, dal, oil donations"
        },
        {
            "account_code": "4402",
            "account_name": "Asset Donation",
            "account_name_kannada": "ಆಸ್ತಿ ದಾನ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.DONATION_INCOME,
            "parent_code": "4400",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Gold, silver, furniture donations"
        },

        # Other Income
        {
            "account_code": "4500",
            "account_name": "Other Income",
            "account_name_kannada": "ಇತರ ಆದಾಯ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.OTHER_INCOME,
            "parent_code": "4000",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Miscellaneous income"
        },
        {
            "account_code": "4501",
            "account_name": "Interest Income",
            "account_name_kannada": "ಬಡ್ಡಿ ಆದಾಯ",
            "account_type": AccountType.INCOME,
            "account_subtype": AccountSubType.OTHER_INCOME,
            "parent_code": "4500",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Interest from bank deposits"
        },

        # ===== EXPENSES =====

        # Main Expense Account
        {
            "account_code": "5000",
            "account_name": "Expenses",
            "account_name_kannada": "ವೆಚ್ಚಗಳು",
            "account_type": AccountType.EXPENSE,
            "account_subtype": None,
            "parent_account_id": None,
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "All expenses"
        },

        # Operational Expenses
        {
            "account_code": "5100",
            "account_name": "Operational Expenses",
            "account_name_kannada": "ಕಾರ್ಯಾಚರಣಾ ವೆಚ್ಚಗಳು",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.OPERATIONAL_EXPENSE,
            "parent_code": "5000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Regular operational expenses"
        },
        {
            "account_code": "5101",
            "account_name": "Priest Salaries",
            "account_name_kannada": "ಪೂಜಾರಿ ವೇತನ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.OPERATIONAL_EXPENSE,
            "parent_code": "5100",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Salaries paid to priests"
        },
        {
            "account_code": "5102",
            "account_name": "Staff Salaries",
            "account_name_kannada": "ಸಿಬ್ಬಂದಿ ವೇತನ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.OPERATIONAL_EXPENSE,
            "parent_code": "5100",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Salaries paid to staff"
        },
        {
            "account_code": "5110",
            "account_name": "Electricity Charges",
            "account_name_kannada": "ವಿದ್ಯುತ್ ಶುಲ್ಕ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.OPERATIONAL_EXPENSE,
            "parent_code": "5100",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Electricity bills"
        },
        {
            "account_code": "5111",
            "account_name": "Water Charges",
            "account_name_kannada": "ನೀರಿನ ಶುಲ್ಕ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.OPERATIONAL_EXPENSE,
            "parent_code": "5100",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Water bills"
        },
        {
            "account_code": "5120",
            "account_name": "Maintenance & Repairs",
            "account_name_kannada": "ನಿರ್ವಹಣೆ ಮತ್ತು ದುರಸ್ತಿ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.OPERATIONAL_EXPENSE,
            "parent_code": "5100",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Building and equipment maintenance"
        },

        # Pooja & Ritual Expenses
        {
            "account_code": "5200",
            "account_name": "Pooja & Ritual Expenses",
            "account_name_kannada": "ಪೂಜಾ ಮತ್ತು ಆಚರಣೆ ವೆಚ್ಚಗಳು",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.RITUAL_EXPENSE,
            "parent_code": "5000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Pooja and ritual related expenses"
        },
        {
            "account_code": "5201",
            "account_name": "Flower Decoration Expense",
            "account_name_kannada": "ಹೂವಿನ ಅಲಂಕಾರ ವೆಚ್ಚ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.RITUAL_EXPENSE,
            "parent_code": "5200",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Flowers for daily pooja and decoration"
        },
        {
            "account_code": "5202",
            "account_name": "Pooja Materials",
            "account_name_kannada": "ಪೂಜಾ ಸಾಮಗ್ರಿಗಳು",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.RITUAL_EXPENSE,
            "parent_code": "5200",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Oil, camphor, incense, etc."
        },
        {
            "account_code": "5203",
            "account_name": "Prasadam Expenses",
            "account_name_kannada": "ಪ್ರಸಾದ ವೆಚ್ಚ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.RITUAL_EXPENSE,
            "parent_code": "5200",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Materials for preparing prasadam"
        },

        # Annadana Expenses
        {
            "account_code": "5300",
            "account_name": "Annadana Expenses",
            "account_name_kannada": "ಅನ್ನದಾನ ವೆಚ್ಚಗಳು",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.OPERATIONAL_EXPENSE,
            "parent_code": "5000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Free food distribution expenses"
        },
        {
            "account_code": "5301",
            "account_name": "Vegetables & Groceries",
            "account_name_kannada": "ತರಕಾರಿಗಳು ಮತ್ತು ದಿನಸಿ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.OPERATIONAL_EXPENSE,
            "parent_code": "5300",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Vegetables and groceries for annadana"
        },
        {
            "account_code": "5302",
            "account_name": "Cooking Gas",
            "account_name_kannada": "ಅಡುಗೆ ಅನಿಲ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.OPERATIONAL_EXPENSE,
            "parent_code": "5300",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "LPG for cooking"
        },

        # Festival Expenses
        {
            "account_code": "5400",
            "account_name": "Festival Expenses",
            "account_name_kannada": "ಉತ್ಸವ ವೆಚ್ಚಗಳು",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.FESTIVAL_EXPENSE,
            "parent_code": "5000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Festival and special event expenses"
        },
        {
            "account_code": "5401",
            "account_name": "Tent Hiring",
            "account_name_kannada": "ಟೆಂಟ್ ಬಾಡಿಗೆ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.FESTIVAL_EXPENSE,
            "parent_code": "5400",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Tent rental for festivals"
        },
        {
            "account_code": "5402",
            "account_name": "Sound System",
            "account_name_kannada": "ಧ್ವನಿ ವ್ಯವಸ್ಥೆ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.FESTIVAL_EXPENSE,
            "parent_code": "5400",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Sound system rental"
        },
        {
            "account_code": "5403",
            "account_name": "Lighting Expense",
            "account_name_kannada": "ಬೆಳಕು ವೆಚ್ಚ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.FESTIVAL_EXPENSE,
            "parent_code": "5400",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Special lighting for festivals"
        },

        # Administrative Expenses
        {
            "account_code": "5500",
            "account_name": "Administrative Expenses",
            "account_name_kannada": "ಆಡಳಿತಾತ್ಮಕ ವೆಚ್ಚಗಳು",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.ADMINISTRATIVE_EXPENSE,
            "parent_code": "5000",
            "is_system_account": True,
            "allow_manual_entry": False,
            "description": "Administrative expenses"
        },
        {
            "account_code": "5501",
            "account_name": "Audit Fees",
            "account_name_kannada": "ಲೆಕ್ಕಪರಿಶೋಧನಾ ಶುಲ್ಕ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.ADMINISTRATIVE_EXPENSE,
            "parent_code": "5500",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Audit and accounting fees"
        },
        {
            "account_code": "5502",
            "account_name": "Bank Charges",
            "account_name_kannada": "ಬ್ಯಾಂಕ್ ಶುಲ್ಕಗಳು",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.ADMINISTRATIVE_EXPENSE,
            "parent_code": "5500",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Bank service charges"
        },
        {
            "account_code": "5503",
            "account_name": "Printing & Stationery",
            "account_name_kannada": "ಮುದ್ರಣ ಮತ್ತು ಲೇಖನ ಸಾಮಗ್ರಿ",
            "account_type": AccountType.EXPENSE,
            "account_subtype": AccountSubType.ADMINISTRATIVE_EXPENSE,
            "parent_code": "5500",
            "is_system_account": True,
            "allow_manual_entry": True,
            "description": "Printing and stationery items"
        },
    ]

    # Create accounts with parent-child relationships
    account_map = {}  # Map account_code to account.id

    # First pass: Create all accounts without parent_account_id
    for acc_data in accounts:
        parent_code = acc_data.pop('parent_code', None)

        account = Account(
            temple_id=temple_id,
            **acc_data
        )
        db.add(account)
        db.flush()  # Get account.id

        account_map[account.account_code] = account.id

    # Second pass: Update parent_account_id
    for account in db.query(Account).filter(Account.temple_id == temple_id).all():
        # Find parent code from original data
        for acc_data in accounts:
            if acc_data['account_code'] == account.account_code:
                parent_code = acc_data.get('parent_code')
                if parent_code and parent_code in account_map:
                    account.parent_account_id = account_map[parent_code]
                break

    db.commit()
    print(f"✅ Created {len(accounts)} accounts for temple_id {temple_id}")


def main():
    """
    Main function to seed chart of accounts
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = SessionLocal()

    try:
        # Get first temple (or create demo temple if none exists)
        temple = db.query(Temple).first()

        if not temple:
            print("⚠️  No temple found. Creating demo temple...")
            temple = Temple(
                name="Demo Temple",
                slug="demo-temple",
                primary_deity="Lord Ganesha",
                is_active=True
            )
            db.add(temple)
            db.commit()
            db.refresh(temple)
            print(f"✅ Created demo temple: {temple.name}")

        # Check if accounts already exist
        existing_count = db.query(Account).filter(Account.temple_id == temple.id).count()

        if existing_count > 0:
            print(f"⚠️  Temple '{temple.name}' already has {existing_count} accounts.")
            response = input("Do you want to add default accounts anyway? (y/n): ")
            if response.lower() != 'y':
                print("❌ Aborted.")
                return

        # Create chart of accounts
        print(f"\n🔧 Creating default chart of accounts for temple: {temple.name}")
        create_default_chart_of_accounts(db, temple.id)

        print("\n✅ Chart of Accounts created successfully!")
        print("\n📊 Account Summary:")

        # Print summary by type
        for account_type in AccountType:
            count = db.query(Account).filter(
                Account.temple_id == temple.id,
                Account.account_type == account_type
            ).count()
            print(f"   {account_type.value.title()}: {count} accounts")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
