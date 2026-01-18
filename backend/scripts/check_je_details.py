"""
Check journal entry details for booking 7
"""

import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.seva import SevaBooking
from app.models.accounting import JournalEntry, JournalLine, Account, TransactionType, JournalEntryStatus

# Import all models
from app.models.temple import Temple
from app.models.user import User
from app.models.devotee import Devotee
from app.models.donation import Donation, DonationCategory
from app.models.seva import Seva
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
from app.models.sacred_events_cache import SacredEventsCache

def check_je():
    db = SessionLocal()
    try:
        # Find all journal entries for booking 7 (should have cancelled and new one)
        entries = db.query(JournalEntry).filter(
            JournalEntry.reference_type == TransactionType.SEVA,
            JournalEntry.reference_id == 7
        ).order_by(JournalEntry.id).all()
        
        print(f"\nFound {len(entries)} journal entry(ies) for booking 7:\n")
        
        for je in entries:
        
            print(f"Journal Entry: {je.entry_number}")
            print(f"  ID: {je.id}")
            print(f"  Date: {je.entry_date}")
            print(f"  Status: {je.status}")
            if je.status == JournalEntryStatus.CANCELLED:
                print(f"  Cancelled By: {je.cancelled_by}")
                print(f"  Cancellation Reason: {je.cancellation_reason}")
            print(f"  Narration: {je.narration}")
            print(f"\n  Journal Lines:")
            
            for line in je.journal_lines:
                account = line.account
                print(f"    Account: {account.account_code} - {account.account_name}")
                print(f"      Debit: ₹{line.debit_amount:,.2f}")
                print(f"      Credit: ₹{line.credit_amount:,.2f}")
            print()
        
        # Check all journal entries for account 3003 (old code)
        old_account = db.query(Account).filter(Account.account_code == '3003').first()
        if old_account:
            print(f"\nOld account 3003 still exists: {old_account.account_name}")
            lines = db.query(JournalLine).join(JournalEntry).filter(
                JournalLine.account_id == old_account.id,
                JournalEntry.status == 'posted'
            ).all()
            print(f"  Has {len(lines)} journal lines")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_je()

