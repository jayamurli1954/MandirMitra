"""
Tests for Accounts API (Chart of Accounts)
Tests account management endpoints
"""

import pytest
from fastapi import status
from datetime import date


@pytest.mark.api
@pytest.mark.accounting
class TestChartOfAccounts:
    """Tests for chart of accounts management"""

    def test_list_accounts(self, authenticated_client):
        """Test retrieving list of accounts"""
        response = authenticated_client.get("/api/v1/accounts/")

        assert response.status_code == status.HTTP_200_OK
        accounts = response.json()
        assert isinstance(accounts, list)

    def test_get_account_hierarchy(self, authenticated_client):
        """Test retrieving account hierarchy"""
        response = authenticated_client.get("/api/v1/accounts/hierarchy")

        assert response.status_code == status.HTTP_200_OK
        hierarchy = response.json()
        assert isinstance(hierarchy, list)

    def test_create_account(self, authenticated_client, test_user):
        """Test creating a new account"""
        account_data = {
            "account_code": "9999",
            "account_name": "Test Account",
            "account_type": "expense",
            "temple_id": test_user.temple_id,
            "parent_account_id": None,
            "is_active": True
        }

        response = authenticated_client.post(
            "/api/v1/accounts/",
            json=account_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["account_code"] == "9999"
        assert data["account_name"] == "Test Account"
        assert "id" in data

    def test_get_account_by_id(self, authenticated_client, test_user):
        """Test retrieving a specific account"""
        # First create an account
        account_data = {
            "account_code": "8888",
            "account_name": "Test Get Account",
            "account_type": "asset",
            "temple_id": test_user.temple_id,
            "is_active": True
        }
        create_response = authenticated_client.post(
            "/api/v1/accounts/",
            json=account_data
        )
        account_id = create_response.json()["id"]

        # Now get it
        response = authenticated_client.get(f"/api/v1/accounts/{account_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == account_id
        assert data["account_code"] == "8888"

    def test_get_account_not_found(self, authenticated_client):
        """Test getting non-existent account"""
        response = authenticated_client.get("/api/v1/accounts/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_account(self, authenticated_client, test_user):
        """Test updating an account"""
        # Create account first
        account_data = {
            "account_code": "7777",
            "account_name": "Original Name",
            "account_type": "liability",
            "temple_id": test_user.temple_id,
            "is_active": True
        }
        create_response = authenticated_client.post(
            "/api/v1/accounts/",
            json=account_data
        )
        account_id = create_response.json()["id"]

        # Update it
        update_data = {
            "account_name": "Updated Name"
        }
        response = authenticated_client.put(
            f"/api/v1/accounts/{account_id}",
            json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["account_name"] == "Updated Name"

    def test_get_account_balance(self, authenticated_client, test_user):
        """Test getting account balance"""
        # Create account first
        account_data = {
            "account_code": "6666",
            "account_name": "Balance Test Account",
            "account_type": "asset",
            "temple_id": test_user.temple_id,
            "is_active": True
        }
        create_response = authenticated_client.post(
            "/api/v1/accounts/",
            json=account_data
        )
        account_id = create_response.json()["id"]

        # Get balance
        response = authenticated_client.get(f"/api/v1/accounts/{account_id}/balance")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "account_id" in data
        assert "balance" in data or "debit_balance" in data or "credit_balance" in data

    def test_check_account_transactions(self, authenticated_client, test_user):
        """Test checking if account has transactions"""
        # Create account first
        account_data = {
            "account_code": "5555",
            "account_name": "Transaction Check Account",
            "account_type": "expense",
            "temple_id": test_user.temple_id,
            "is_active": True
        }
        create_response = authenticated_client.post(
            "/api/v1/accounts/",
            json=account_data
        )
        account_id = create_response.json()["id"]

        # Check transactions
        response = authenticated_client.get(f"/api/v1/accounts/{account_id}/has-transactions")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "has_transactions" in data
        assert isinstance(data["has_transactions"], bool)

    def test_delete_account(self, authenticated_client, test_user):
        """Test deleting an account"""
        # Create account first
        account_data = {
            "account_code": "4444",
            "account_name": "Delete Test Account",
            "account_type": "expense",
            "temple_id": test_user.temple_id,
            "is_active": True
        }
        create_response = authenticated_client.post(
            "/api/v1/accounts/",
            json=account_data
        )
        account_id = create_response.json()["id"]

        # Delete it
        response = authenticated_client.delete(f"/api/v1/accounts/{account_id}")

        # Should return 200 or 204
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

        # Verify it's deleted
        get_response = authenticated_client.get(f"/api/v1/accounts/{account_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_account_duplicate_code(self, authenticated_client, test_user):
        """Test that duplicate account codes are rejected"""
        account_data = {
            "account_code": "3333",
            "account_name": "First Account",
            "account_type": "asset",
            "temple_id": test_user.temple_id,
            "is_active": True
        }
        authenticated_client.post("/api/v1/accounts/", json=account_data)

        # Try to create another with same code
        duplicate_data = {
            "account_code": "3333",
            "account_name": "Duplicate Account",
            "account_type": "liability",
            "temple_id": test_user.temple_id,
            "is_active": True
        }
        response = authenticated_client.post(
            "/api/v1/accounts/",
            json=duplicate_data
        )

        # Should fail with 400 or 409
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_409_CONFLICT
        ]

    def test_create_account_invalid_type(self, authenticated_client, test_user):
        """Test that invalid account types are rejected"""
        account_data = {
            "account_code": "2222",
            "account_name": "Invalid Type Account",
            "account_type": "invalid_type",
            "temple_id": test_user.temple_id,
            "is_active": True
        }

        response = authenticated_client.post(
            "/api/v1/accounts/",
            json=account_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

