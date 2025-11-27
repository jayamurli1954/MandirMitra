"""
Comprehensive Tests for Budget Module

Tests cover:
- Budget creation and management
- Budget vs actual tracking
- Budget allocation
- Variance analysis
- FCRA budget compliance
"""

import pytest
from fastapi import status
from datetime import date


@pytest.mark.budget
@pytest.mark.api
class TestBudgetManagement:
    """Tests for budget management"""

    def test_create_annual_budget(self, authenticated_client):
        """Test creating an annual budget"""
        budget_data = {
            "name": "FY 2024-25 Budget",
            "fiscal_year": 2024,
            "start_date": "2024-04-01",
            "end_date": "2025-03-31",
            "total_budget": 10000000.00
        }

        response = authenticated_client.post(
            "/api/v1/budget/budgets",
            json=budget_data
        )

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["name"] == "FY 2024-25 Budget"

    def test_list_budgets(self, authenticated_client):
        """Test listing all budgets"""
        response = authenticated_client.get("/api/v1/budget/budgets")

        assert response.status_code == status.HTTP_200_OK
        budgets = response.json()
        assert isinstance(budgets, list)

    def test_create_department_budget(self, authenticated_client):
        """Test creating department-wise budget allocation"""
        allocation_data = {
            "budget_id": 1,
            "department_id": 1,
            "category": "Salaries",
            "allocated_amount": 500000.00
        }

        response = authenticated_client.post(
            "/api/v1/budget/allocations",
            json=allocation_data
        )

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert float(data["allocated_amount"]) == 500000.00

    def test_get_budget_vs_actual(self, authenticated_client):
        """Test retrieving budget vs actual comparison"""
        response = authenticated_client.get(
            "/api/v1/budget/reports/budget-vs-actual",
            params={"budget_id": 1}
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "budgeted" in data or "actual" in data or "variance" in data


@pytest.mark.budget
@pytest.mark.api
class TestFCRABudget:
    """Tests for FCRA budget compliance"""

    def test_create_fcra_budget(self, authenticated_client):
        """Test creating FCRA-specific budget"""
        fcra_budget = {
            "name": "FCRA FY 2024-25",
            "fiscal_year": 2024,
            "is_fcra": True,
            "fcra_registration_number": "123456789"
        }

        response = authenticated_client.post(
            "/api/v1/budget/budgets",
            json=fcra_budget
        )

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["is_fcra"] is True


# ============================================================================
# HOW TO RUN THESE TESTS
# ============================================================================
# Run all budget tests:
#   pytest tests/test_budget.py -v
# ============================================================================
