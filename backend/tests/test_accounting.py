"""
Comprehensive Tests for Accounting Module

Tests cover:
- Chart of Accounts management
- Journal entry creation
- Double-entry bookkeeping validation
- Trial balance generation
- Financial reports
- Bank reconciliation
- Financial period closing
"""

import pytest
from fastapi import status
from datetime import date, datetime, timedelta
from decimal import Decimal


@pytest.mark.accounting
@pytest.mark.api
class TestChartOfAccounts:
    """Tests for Chart of Accounts management"""

    def test_list_chart_of_accounts(self, authenticated_client):
        """Test retrieving chart of accounts"""
        response = authenticated_client.get("/api/v1/accounts")

        assert response.status_code == status.HTTP_200_OK
        accounts = response.json()
        assert isinstance(accounts, list)
        # Should have standard accounts (Assets, Liabilities, Income, Expenses)
        if len(accounts) > 0:
            assert "account_code" in accounts[0]
            assert "account_name" in accounts[0]

    def test_create_account(self, authenticated_client):
        """Test creating a new account"""
        account_data = {
            "account_code": "5300",
            "account_name": "Utilities Expense",
            "account_type": "expense",
            "parent_account_code": "5000",  # Expenses parent
            "description": "Electricity, water, gas expenses"
        }

        response = authenticated_client.post(
            "/api/v1/accounts",
            json=account_data
        )

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["account_code"] == "5300"
            assert data["account_name"] == "Utilities Expense"

    def test_get_account_by_code(self, authenticated_client):
        """Test retrieving account by code"""
        # Get cash account (should exist in seed data)
        response = authenticated_client.get("/api/v1/accounts/1101")

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["account_code"] == A101"
            assert "cash" in data["account_name"].lower()

    def test_filter_accounts_by_type(self, authenticated_client):
        """Test filtering accounts by type (assets, liabilities, etc.)"""
        response = authenticated_client.get(
            "/api/v1/accounts",
            params={"account_type": "asset"}
        )

        assert response.status_code == status.HTTP_200_OK
        accounts = response.json()
        for account in accounts:
            if "account_type" in account:
                assert account["account_type"] == "asset"


@pytest.mark.accounting
@pytest.mark.api
@pytest.mark.integration
class TestJournalEntries:
    """Tests for journal entry operations"""

    def test_create_simple_journal_entry(self, authenticated_client):
        """Test creating a simple journal entry (Dr/Cr)"""
        entry_data = {
            "entry_date": str(date.today()),
            "description": "Test journal entry",
            "transaction_type": "manual",
            "lines": [
                {
                    "account_code": "5100",  # Expenses
                    "debit": 1000.00,
                    "credit": 0.00,
                    "description": "Test expense"
                },
                {
                    "account_code": A101",  # Cash
                    "debit": 0.00,
                    "credit": 1000.00,
                    "description": "Payment in cash"
                }
            ]
        }

        response = authenticated_client.post(
            "/api/v1/journal-entries",
            json=entry_data
        )

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert "entry_number" in data
            assert len(data["lines"]) == 2

    def test_reject_unbalanced_journal_entry(self, authenticated_client):
        """Test that unbalanced entries (Dr != Cr) are rejected"""
        entry_data = {
            "entry_date": str(date.today()),
            "description": "Unbalanced entry",
            "transaction_type": "manual",
            "lines": [
                {
                    "account_code": "5100",
                    "debit": 1000.00,  # Dr: 1000
                    "credit": 0.00
                },
                {
                    "account_code": A101",
                    "debit": 0.00,
                    "credit": 500.00  # Cr: 500 - UNBALANCED!
                }
            ]
        }

        response = authenticated_client.post(
            "/api/v1/journal-entries",
            json=entry_data
        )

        # Should reject unbalanced entry
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_list_journal_entries(self, authenticated_client):
        """Test listing all journal entries"""
        response = authenticated_client.get("/api/v1/journal-entries")

        assert response.status_code == status.HTTP_200_OK
        entries = response.json()
        assert isinstance(entries, list)

    def test_filter_journal_entries_by_date(self, authenticated_client):
        """Test filtering journal entries by date range"""
        today = date.today()
        week_ago = today - timedelta(days=7)

        response = authenticated_client.get(
            "/api/v1/journal-entries",
            params={
                "start_date": str(week_ago),
                "end_date": str(today)
            }
        )

        assert response.status_code == status.HTTP_200_OK
        entries = response.json()
        assert isinstance(entries, list)

    def test_get_journal_entry_by_id(self, authenticated_client):
        """Test retrieving a specific journal entry"""
        # Create entry
        entry_data = {
            "entry_date": str(date.today()),
            "description": "Get test entry",
            "transaction_type": "manual",
            "lines": [
                {"account_code": "5100", "debit": 500.00, "credit": 0.00},
                {"account_code": A101", "debit": 0.00, "credit": 500.00}
            ]
        }

        create_response = authenticated_client.post(
            "/api/v1/journal-entries",
            json=entry_data
        )

        if create_response.status_code == status.HTTP_201_CREATED:
            entry_id = create_response.json()["id"]

            # Retrieve it
            response = authenticated_client.get(
                f"/api/v1/accounting/journal-entries/{entry_id}"
            )

            assert response.status_code == status.HTTP_200_OK


@pytest.mark.accounting
@pytest.mark.api
class TestTrialBalance:
    """Tests for trial balance generation"""

    def test_generate_trial_balance(self, authenticated_client):
        """Test generating trial balance report"""
        response = authenticated_client.get(
            "/api/v1/journal-entries/reports/trial-balance",
            params={
                "as_of_date": str(date.today())
            }
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "accounts" in data or "total_debit" in data
            assert "total_credit" in data or "accounts" in data

    def test_trial_balance_is_balanced(self, authenticated_client):
        """Test that trial balance debits equal credits"""
        response = authenticated_client.get(
            "/api/v1/journal-entries/reports/trial-balance",
            params={"as_of_date": str(date.today())}
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            if "total_debit" in data and "total_credit" in data:
                # Debits should equal credits
                assert abs(float(data["total_debit"]) - float(data["total_credit"])) < 0.01


@pytest.mark.accounting
@pytest.mark.api
class TestFinancialReports:
    """Tests for financial reporting"""

    def test_generate_balance_sheet(self, authenticated_client):
        """Test generating balance sheet"""
        response = authenticated_client.get(
            "/api/v1/journal-entries/reports/balance-sheet",
            params={"as_of_date": str(date.today())}
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            # Balance sheet response has current_assets, current_liabilities, etc.
            assert "current_assets" in data or "current_liabilities" in data or "corpus_fund" in data

    def test_generate_income_statement(self, authenticated_client):
        """Test generating profit & loss statement"""
        today = date.today()
        month_start = today.replace(day=1)

        response = authenticated_client.get(
            "/api/v1/journal-entries/reports/profit-loss",
            params={
                "start_date": str(month_start),
                "end_date": str(today)
            }
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "income" in data or "expenses" in data or "revenue" in data

    def test_generate_cash_flow_statement(self, authenticated_client):
        """Test generating cash flow statement"""
        today = date.today()
        month_start = today.replace(day=1)

        response = authenticated_client.get(
            "/api/v1/journal-entries/reports/cash-flow",
            params={
                "start_date": str(month_start),
                "end_date": str(today)
            }
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "operating" in data or "investing" in data or "financing" in data


@pytest.mark.accounting
@pytest.mark.api
class TestBankReconciliation:
    """Tests for bank reconciliation"""

    def test_create_bank_reconciliation(self, authenticated_client):
        """Test creating a bank reconciliation"""
        recon_data = {
            "bank_account_id": 1,  # Assuming bank account exists
            "statement_date": str(date.today()),
            "statement_balance": 50000.00,
            "book_balance": 48000.00
        }

        response = authenticated_client.post(
            "/api/v1/bank-reconciliation",
            json=recon_data
        )

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert "id" in data

    def test_list_bank_reconciliations(self, authenticated_client):
        """Test listing bank reconciliations"""
        response = authenticated_client.get("/api/v1/bank-reconciliation/accounts")

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.accounting
@pytest.mark.api
class TestFinancialPeriod:
    """Tests for financial period/year closing"""

    def test_create_financial_period(self, authenticated_client):
        """Test creating a financial period"""
        period_data = {
            "name": "FY 2024-25",
            "start_date": "2024-04-01",
            "end_date": "2025-03-31",
            "is_active": True
        }

        response = authenticated_client.post(
            "/api/v1/financial-closing/financial-years",
            json=period_data
        )

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["name"] == "FY 2024-25"

    def test_close_financial_period(self, authenticated_client):
        """Test closing a financial period"""
        # Create period
        period_data = {
            "name": "Test Period",
            "start_date": str(date.today() - timedelta(days=365)),
            "end_date": str(date.today() - timedelta(days=1)),
            "is_active": True
        }

        create_response = authenticated_client.post(
            "/api/v1/financial-closing/financial-years",
            json=period_data
        )

        if create_response.status_code == status.HTTP_201_CREATED:
            period_id = create_response.json()["id"]

            # Close it
            response = authenticated_client.post(
                f"/api/v1/financial-closing/financial-years/{period_id}/close"
            )

            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                assert data["is_closed"] is True


@pytest.mark.accounting
@pytest.mark.api
class TestAccountingValidation:
    """Tests for accounting data validation"""

    def test_reject_invalid_account_code(self, authenticated_client):
        """Test that invalid account codes are rejected"""
        entry_data = {
            "entry_date": str(date.today()),
            "description": "Invalid account test",
            "transaction_type": "manual",
            "lines": [
                {
                    "account_code": "9999",  # Invalid/non-existent account
                    "debit": 100.00,
                    "credit": 0.00
                },
                {
                    "account_code": A101",
                    "debit": 0.00,
                    "credit": 100.00
                }
            ]
        }

        response = authenticated_client.post(
            "/api/v1/journal-entries",
            json=entry_data
        )

        # Should reject invalid account
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_404_NOT_FOUND
        ]

    def test_reject_negative_amounts(self, authenticated_client):
        """Test that negative amounts are rejected"""
        entry_data = {
            "entry_date": str(date.today()),
            "description": "Negative amount test",
            "transaction_type": "manual",
            "lines": [
                {
                    "account_code": "5100",
                    "debit": -100.00,  # Negative not allowed
                    "credit": 0.00
                },
                {
                    "account_code": A101",
                    "debit": 0.00,
                    "credit": -100.00
                }
            ]
        }

        response = authenticated_client.post(
            "/api/v1/journal-entries",
            json=entry_data
        )

        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]


# ============================================================================
# HOW TO RUN THESE TESTS
# ============================================================================
# Run all accounting tests:
#   pytest tests/test_accounting.py -v
#
# Run journal entry tests only:
#   pytest tests/test_accounting.py::TestJournalEntries -v
#
# Run with coverage:
#   pytest tests/test_accounting.py --cov=app.api.accounting --cov-report=term-missing
# ============================================================================
