"""
Default Chart of Accounts (COA) - Comprehensive 5-Digit Structure
Following industry standard: 1xxxx = Assets, 2xxxx = Liabilities, 3xxxx = Equity, 4xxxx = Income, 5xxxx = Expenses
"""

from typing import List, Dict
from app.models.accounting import AccountType, AccountSubType


class DefaultCOA:
    """Default Chart of Accounts with comprehensive account heads"""
    
    @staticmethod
    def get_default_accounts() -> List[Dict]:
        """
        Returns list of default accounts with 5-digit codes
        Structure: ABCDE where A = Account Class, BC = Major Category, DE = Account
        """
        return [
            # ==========================================
            # 1xxxx - ASSETS
            # ==========================================
            
            # 11000-11999: Current Assets
            {
                "account_code": "11001",
                "account_name": "Cash in Hand - Counter",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CASH_BANK,
                "description": "Cash kept at temple counter for daily transactions",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "11002",
                "account_name": "Cash in Hand - Hundi",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CASH_BANK,
                "description": "Cash collected from hundi boxes",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "11003",
                "account_name": "Petty Cash",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CASH_BANK,
                "description": "Small cash expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "11010",
                "account_name": "Advance to Staff",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.RECEIVABLE,
                "description": "Advances given to staff members",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "11020",
                "account_name": "Prepaid Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CURRENT_ASSET,
                "description": "Expenses paid in advance",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "11030",
                "account_name": "Other Current Assets",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CURRENT_ASSET,
                "description": "Other current assets",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 12000-12999: Bank & Cash
            {
                "account_code": "12001",
                "account_name": "Bank - Current Account",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CASH_BANK,
                "description": "Primary bank current account",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "12002",
                "account_name": "Bank - Savings Account",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CASH_BANK,
                "description": "Bank savings account",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "12003",
                "account_name": "Bank - OD/CC Account",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CASH_BANK,
                "description": "Bank overdraft or cash credit account",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "12010",
                "account_name": "Fixed Deposits",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CURRENT_ASSET,
                "description": "Bank fixed deposits",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "12020",
                "account_name": "Margin Money",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CURRENT_ASSET,
                "description": "Margin money deposited with banks",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 13000-13999: Trade Receivables
            {
                "account_code": "13000",
                "account_name": "Trade Receivables",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.RECEIVABLE,
                "description": "Control account for all receivables",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "13001",
                "account_name": "Sundry Debtors",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.RECEIVABLE,
                "description": "Amounts receivable from customers",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "13002",
                "account_name": "GST Refund Receivable",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.RECEIVABLE,
                "description": "GST refunds due from government",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "13003",
                "account_name": "Other Receivables",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.RECEIVABLE,
                "description": "Other amounts receivable",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 14000-14999: Inventory
            {
                "account_code": "14001",
                "account_name": "Stock-in-Trade",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.INVENTORY,
                "description": "General stock inventory",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "14002",
                "account_name": "Raw Materials",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.INVENTORY,
                "description": "Raw materials for pooja items",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "14003",
                "account_name": "Pooja Materials Inventory",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.INVENTORY,
                "description": "Inventory of pooja materials",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "14004",
                "account_name": "Prasadam Inventory",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.INVENTORY,
                "description": "Inventory of prasadam items",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "14005",
                "account_name": "Finished Goods",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.INVENTORY,
                "description": "Finished goods inventory",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 15000-15999: Fixed Assets
            {
                "account_code": "15001",
                "account_name": "Land",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.FIXED_ASSET,
                "description": "Temple land and property",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "15002",
                "account_name": "Building",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.FIXED_ASSET,
                "description": "Temple buildings and structures",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "15003",
                "account_name": "Plant & Machinery",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.FIXED_ASSET,
                "description": "Plant and machinery",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "15004",
                "account_name": "Furniture & Fixtures",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.FIXED_ASSET,
                "description": "Furniture and fixtures",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "15005",
                "account_name": "Computers & IT Equipment",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.FIXED_ASSET,
                "description": "Computers and IT equipment",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "15006",
                "account_name": "Vehicles",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.FIXED_ASSET,
                "description": "Temple vehicles",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "15010",
                "account_name": "Temple Gold & Silver",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.PRECIOUS_ASSET,
                "description": "Gold and silver assets (idols, jewellery)",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "15011",
                "account_name": "Precious Metals & Stones",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.PRECIOUS_ASSET,
                "description": "Other precious metals and stones",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "15020",
                "account_name": "Capital Work in Progress",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.FIXED_ASSET,
                "description": "Construction work in progress",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "15999",
                "account_name": "Accumulated Depreciation",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.FIXED_ASSET,
                "description": "Contra asset - accumulated depreciation",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 16000-16999: Intangible Assets
            {
                "account_code": "16001",
                "account_name": "Software & Licenses",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CURRENT_ASSET,
                "description": "Software licenses and intangible assets",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "16002",
                "account_name": "Goodwill",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CURRENT_ASSET,
                "description": "Goodwill (if applicable)",
                "is_active": True,
                "parent_account_id": None
            },
            
            # ==========================================
            # 2xxxx - LIABILITIES
            # ==========================================
            
            # 21000-21999: Current Liabilities
            {
                "account_code": "21001",
                "account_name": "Sundry Creditors",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Amounts payable to suppliers",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "21002",
                "account_name": "Outstanding Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Expenses incurred but not paid",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "21003",
                "account_name": "Advance Seva Booking",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Advance bookings for future sevas (liability until seva performed)",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "21004",
                "account_name": "Advance from Customers",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Advance payments received from customers",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "21010",
                "account_name": "Sponsorship Receivable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Sponsorship amounts received in advance",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 22000-22999: Payables
            {
                "account_code": "22001",
                "account_name": "Accounts Payable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Trade payables",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "22002",
                "account_name": "Salary Payable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Outstanding salary payable",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "22003",
                "account_name": "Priest Fees Payable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Priest fees payable",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 23000-23999: Statutory Liabilities
            {
                "account_code": "23001",
                "account_name": "GST Output Payable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "GST collected (output tax)",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "23002",
                "account_name": "GST Input Credit",
                "account_name_kannada": None,
                "account_type": AccountType.ASSET,
                "account_subtype": AccountSubType.CURRENT_ASSET,
                "description": "GST paid on purchases (input credit)",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "23003",
                "account_name": "TDS Payable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Tax deducted at source payable",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "23004",
                "account_name": "TCS Payable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Tax collected at source payable",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "23005",
                "account_name": "PF Payable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Provident Fund payable",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "23006",
                "account_name": "ESI Payable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Employee State Insurance payable",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "23007",
                "account_name": "Professional Tax Payable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Professional tax payable",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "23008",
                "account_name": "Income Tax Payable",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Income tax payable",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 24000-24999: Loans
            {
                "account_code": "24001",
                "account_name": "Secured Loans",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.LONG_TERM_LIABILITY,
                "description": "Secured loans from banks",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "24002",
                "account_name": "Unsecured Loans",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.LONG_TERM_LIABILITY,
                "description": "Unsecured loans",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "24003",
                "account_name": "Term Loan",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.LONG_TERM_LIABILITY,
                "description": "Term loans from banks",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "24004",
                "account_name": "Vehicle Loan",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.LONG_TERM_LIABILITY,
                "description": "Vehicle loan",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "24005",
                "account_name": "Temple Construction Loan",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.LONG_TERM_LIABILITY,
                "description": "Loan for temple construction",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 25000-25999: Provisions
            {
                "account_code": "25001",
                "account_name": "Provision for Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Provisions made for expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "25002",
                "account_name": "Provision for Taxation",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Provision for income tax",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "25003",
                "account_name": "Gratuity Provision",
                "account_name_kannada": None,
                "account_type": AccountType.LIABILITY,
                "account_subtype": AccountSubType.CURRENT_LIABILITY,
                "description": "Provision for gratuity",
                "is_active": True,
                "parent_account_id": None
            },
            
            # ==========================================
            # 3xxxx - EQUITY
            # ==========================================
            
            # 31000-31999: Capital
            {
                "account_code": "31001",
                "account_name": "Owner's Capital",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "Owner's capital contribution",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "31002",
                "account_name": "Partner Capital",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "Partner capital (for partnerships)",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "31003",
                "account_name": "Share Capital",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "Share capital (for companies)",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "31004",
                "account_name": "Corpus Fund",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "Temple/Trust corpus fund",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 32000-32999: Reserves
            {
                "account_code": "32001",
                "account_name": "General Reserve",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "General reserve fund",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "32002",
                "account_name": "Capital Reserve",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "Capital reserve",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "32003",
                "account_name": "Revaluation Reserve",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "Revaluation reserve",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "32004",
                "account_name": "Donation Reserve",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "Reserve from donations",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 33000-33999: Retained Earnings
            {
                "account_code": "33001",
                "account_name": "Opening Balance",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "Opening balance brought forward",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "33002",
                "account_name": "Current Year Surplus",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "Current year profit/surplus",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "31010",
                "account_name": "General Fund",
                "account_name_kannada": None,
                "account_type": AccountType.EQUITY,
                "account_subtype": None,
                "description": "General fund for temple operations",
                "is_active": True,
                "parent_account_id": None
            },
            
            # ==========================================
            # 4xxxx - INCOME
            # ==========================================
            
            # 41000-41999: Operating Income
            {
                "account_code": "41001",
                "account_name": "Sales - Local",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.OTHER_INCOME,
                "description": "Sales within state (local)",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "41002",
                "account_name": "Sales - Interstate",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.OTHER_INCOME,
                "description": "Interstate sales",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "41003",
                "account_name": "Sales - Export",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.OTHER_INCOME,
                "description": "Export sales",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "41004",
                "account_name": "Sales - Exempt",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.OTHER_INCOME,
                "description": "Exempt sales",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 42000-42999: Service / Professional Income
            {
                "account_code": "42001",
                "account_name": "Professional Fees",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.SEVA_INCOME,
                "description": "Professional service fees",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "42002",
                "account_name": "Seva Income - General",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.SEVA_INCOME,
                "description": "General seva income",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "42003",
                "account_name": "Consultancy Income",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.SEVA_INCOME,
                "description": "Consultancy income",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 43000-43999: Other Income
            {
                "account_code": "43001",
                "account_name": "Interest Income",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.OTHER_INCOME,
                "description": "Interest earned on deposits",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "43002",
                "account_name": "Rent Income",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.OTHER_INCOME,
                "description": "Rental income",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "43003",
                "account_name": "Commission Income",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.OTHER_INCOME,
                "description": "Commission income",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "44001",
                "account_name": "General Donations",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.DONATION_INCOME,
                "description": "General donations from devotees",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "44002",
                "account_name": "Hundi Collections",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.DONATION_INCOME,
                "description": "Collections from hundi boxes",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "44003",
                "account_name": "Specific Purpose Donations",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.DONATION_INCOME,
                "description": "Donations for specific purposes",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "44004",
                "account_name": "In-Kind Donation Income",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.DONATION_INCOME,
                "description": "In-kind donations (goods, services)",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "44005",
                "account_name": "Government Grant",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.DONATION_INCOME,
                "description": "Government grants received",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "45001",
                "account_name": "Sponsorship Income",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.SPONSORSHIP_INCOME,
                "description": "Event sponsorship income",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "45002",
                "account_name": "In-Kind Sponsorship Income",
                "account_name_kannada": None,
                "account_type": AccountType.INCOME,
                "account_subtype": AccountSubType.SPONSORSHIP_INCOME,
                "description": "In-kind sponsorship income",
                "is_active": True,
                "parent_account_id": None
            },
            
            # ==========================================
            # 5xxxx - EXPENSES
            # ==========================================
            
            # 51000-51999: Direct Expenses
            {
                "account_code": "51001",
                "account_name": "Purchases",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Direct purchases",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "51002",
                "account_name": "Freight Inward",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Freight charges on purchases",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "51003",
                "account_name": "Direct Labour",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Direct labor costs",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "51004",
                "account_name": "Pooja Materials Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Expenses for pooja materials",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 52000-52999: Employee Costs
            {
                "account_code": "52001",
                "account_name": "Salaries",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Employee salaries",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "52002",
                "account_name": "Wages",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Daily wages",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "52003",
                "account_name": "Priest Fees",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Priest fees and honorarium",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "52004",
                "account_name": "Employer PF",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Employer's PF contribution",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "52005",
                "account_name": "Employer ESI",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Employer's ESI contribution",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "52006",
                "account_name": "Bonus",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Employee bonuses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "52007",
                "account_name": "Staff Welfare Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Staff welfare and benefits",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 53000-53999: Administrative Expenses
            {
                "account_code": "53001",
                "account_name": "Rent",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Rent expense",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "53002",
                "account_name": "Electricity",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Electricity charges",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "53003",
                "account_name": "Office Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "General office expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "53004",
                "account_name": "Repairs & Maintenance",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Repairs and maintenance expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "53005",
                "account_name": "Temple Maintenance",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Temple maintenance and upkeep",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "53006",
                "account_name": "Printing & Stationery",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Printing and stationery expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "53007",
                "account_name": "Water Charges",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Water charges",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "53008",
                "account_name": "Security Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Security and guard expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "53009",
                "account_name": "Cleaning & Sanitation",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Cleaning and sanitation expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "53010",
                "account_name": "Telephone & Internet",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Telephone and internet charges",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "53011",
                "account_name": "Insurance Premium",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Insurance premium payments",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 54000-54999: Finance & Other Expenses
            {
                "account_code": "54001",
                "account_name": "Bank Charges",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Bank service charges",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54002",
                "account_name": "Interest on Loan",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Interest paid on loans",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54003",
                "account_name": "Legal & Professional Fees",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Legal and professional consultation fees",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54004",
                "account_name": "Festival Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Festival celebration expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54005",
                "account_name": "Event Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Special event expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54006",
                "account_name": "Decoration Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Temple decoration expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54007",
                "account_name": "Prasadam Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Prasadam preparation expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54008",
                "account_name": "Advertising & Promotion",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Advertising and promotion expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54009",
                "account_name": "Travel & Conveyance",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Travel and conveyance expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54010",
                "account_name": "Audit Fees",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Audit and accounting fees",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54011",
                "account_name": "Depreciation/Revaluation Expense",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Depreciation and revaluation expenses",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "54012",
                "account_name": "Miscellaneous Expenses",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Other miscellaneous expenses",
                "is_active": True,
                "parent_account_id": None
            },
            
            # 55000-55999: Depreciation
            {
                "account_code": "55001",
                "account_name": "Depreciation - Building",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Depreciation on buildings",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "55002",
                "account_name": "Depreciation - Plant",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Depreciation on plant and machinery",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "55003",
                "account_name": "Depreciation - Computers",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Depreciation on computers and IT equipment",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "55004",
                "account_name": "Depreciation - Furniture",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Depreciation on furniture and fixtures",
                "is_active": True,
                "parent_account_id": None
            },
            {
                "account_code": "55005",
                "account_name": "Depreciation - Vehicles",
                "account_name_kannada": None,
                "account_type": AccountType.EXPENSE,
                "account_subtype": None,
                "description": "Depreciation on vehicles",
                "is_active": True,
                "parent_account_id": None
            },
        ]
    
    @staticmethod
    def get_code_mapping() -> Dict[str, str]:
        """
        Returns mapping of old account codes to new 5-digit codes
        Used for migration
        """
        return {
            # Assets
            "A101": "11001",  # Cash in Hand - Counter
            "A102": "11002",  # Cash in Hand - Hundi
            "A110": "12001",  # Bank Account
            "1300": "14003",  # Inventory Asset -> Pooja Materials Inventory
            "1400": "15002",  # Fixed Assets
            "1402": "21010",  # Sponsorship Receivable (Liability)
            "1500": "15010",  # Precious Assets -> Temple Gold & Silver
            "1620": "15020",  # CWIP
            "1601": "15020",  # CWIP - Building
            "1701": "15999",  # Accumulated Depreciation - Building
            "1702": "15999",  # Accumulated Depreciation - Vehicle
            "1703": "15999",  # Accumulated Depreciation - Computers
            "1710": "15999",  # Accumulated Depreciation - Furniture
            "1720": "15999",  # Accumulated Depreciation - Other
            "1801": "32003",  # Revaluation Reserve - Building
            "1802": "32003",  # Revaluation Reserve - Building
            "1803": "32003",  # Revaluation Reserve - Gold
            "1804": "32003",  # Revaluation Reserve - Silver
            "1805": "32003",  # Revaluation Reserve - Other

            # Liabilities
            "3003": "21003",  # Advance Seva Booking

            # Income (old 3xxx codes were wrong)
            "3001": "44001",  # Donation Income -> General Donations
            "3002": "42002",  # Seva Income -> Seva Income - General
            "D100": "44001",  # Donation Income - Main -> General Donations
            "4101": "44001",  # Donation Income
            "4200": "42002",  # Seva Income - Main -> Seva Income - General
            "4300": "45001",  # Sponsorship Income
            "4301": "45001",  # Sponsorship Income
            "4400": "44004",  # In-Kind Donation Income
            "4403": "45002",  # In-Kind Sponsorship Income
            "4500": "43001",  # Other Income -> Interest Income
            "4599": "43003",  # Other Income -> Commission Income

            # Expenses
            "5001": "54012",  # Default operational expense -> Miscellaneous
            "5100": "11020",  # Prepaid Expenses (Asset, not expense)
            "5200": "52001",  # Salaries
            "5300": "54012",  # Other Expenses -> Miscellaneous
            "5400": "54004",  # Festival Expenses
            "5404": "54004",  # Festival Expenses
            "5405": "54005",  # Event Expenses
            "5406": "54006",  # Decoration Expenses
            "5407": "54007",  # Prasadam Expenses
            "6001": "54011",  # Depreciation/Revaluation Expense

            # Equity
            "3101": "31010",  # General Fund
        }
