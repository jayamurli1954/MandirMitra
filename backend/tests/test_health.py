"""
Sample Health Check Tests for MandirMitra

This is a starter test file demonstrating how to write tests.
You can use this as a template for testing other modules.
"""

import pytest
from fastapi import status


class TestHealthCheck:
    """
    Basic health check tests to verify the API is running.
    """

    def test_root_endpoint(self, client):
        """
        Test that the root endpoint returns a welcome message.
        """
        response = client.get("/")

        # Check status code
        assert response.status_code == status.HTTP_200_OK

        # Check response contains expected data
        data = response.json()
        assert "message" in data or "name" in data

    def test_docs_endpoint(self, client):
        """
        Test that API documentation is accessible.
        """
        response = client.get("/docs")

        # Should return HTML page
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")

    def test_openapi_schema(self, client):
        """
        Test that OpenAPI schema is accessible.
        """
        response = client.get("/openapi.json")

        assert response.status_code == status.HTTP_200_OK

        # Verify it's valid JSON with OpenAPI structure
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


# ============================================================================
# EXAMPLE TESTS FOR OTHER MODULES (UNCOMMENT WHEN ENDPOINTS ARE READY)
# ============================================================================

# @pytest.mark.donations
# class TestDonations:
#     """
#     Example tests for donation endpoints.
#     """
#
#     def test_create_donation(self, authenticated_client, test_donation_data):
#         """Test creating a new donation."""
#         response = authenticated_client.post(
#             "/api/donations/",
#             json=test_donation_data
#         )
#
#         assert response.status_code == status.HTTP_201_CREATED
#         data = response.json()
#         assert data["donor_name"] == test_donation_data["donor_name"]
#         assert data["amount"] == test_donation_data["amount"]
#
#
#     def test_get_donation(self, authenticated_client, test_donation_data):
#         """Test retrieving a donation by ID."""
#         # First create a donation
#         create_response = authenticated_client.post(
#             "/api/donations/",
#             json=test_donation_data
#         )
#         donation_id = create_response.json()["id"]
#
#         # Then retrieve it
#         response = authenticated_client.get(f"/api/donations/{donation_id}")
#
#         assert response.status_code == status.HTTP_200_OK
#         data = response.json()
#         assert data["id"] == donation_id
#
#
#     def test_list_donations(self, authenticated_client):
#         """Test listing all donations."""
#         response = authenticated_client.get("/api/donations/")
#
#         assert response.status_code == status.HTTP_200_OK
#         data = response.json()
#         assert isinstance(data, list)


# @pytest.mark.sevas
# class TestSevaBookings:
#     """
#     Example tests for seva booking endpoints.
#     """
#
#     def test_create_seva_booking(self, authenticated_client, test_seva_data):
#         """Test creating a new seva booking."""
#         response = authenticated_client.post(
#             "/api/sevas/bookings",
#             json=test_seva_data
#         )
#
#         assert response.status_code == status.HTTP_201_CREATED
#         data = response.json()
#         assert data["devotee_name"] == test_seva_data["devotee_name"]


# @pytest.mark.hr
# class TestHRModule:
#     """
#     Example tests for HR endpoints.
#     """
#
#     def test_create_employee(self, authenticated_client):
#         """Test creating a new employee."""
#         employee_data = {
#             "employee_code": "EMP-0001",
#             "full_name": "Rajesh Kumar",
#             "department": "Accounts",
#             "designation": "Accountant",
#             "salary": 25000.00,
#             "joining_date": "2025-01-01"
#         }
#
#         response = authenticated_client.post(
#             "/api/hr/employees",
#             json=employee_data
#         )
#
#         assert response.status_code == status.HTTP_201_CREATED
#         data = response.json()
#         assert data["employee_code"] == employee_data["employee_code"]


# ============================================================================
# HOW TO RUN THESE TESTS
# ============================================================================
# 1. All tests:              pytest
# 2. Specific file:          pytest tests/test_health.py
# 3. Specific test:          pytest tests/test_health.py::TestHealthCheck::test_root_endpoint
# 4. With coverage:          pytest --cov=app
# 5. Only donations tests:   pytest -m donations
# 6. Verbose output:         pytest -v
# ============================================================================
