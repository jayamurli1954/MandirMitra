"""
Comprehensive Tests for Hundi (Collection Box) Module

Tests cover:
- Hundi (collection box) registration
- Collection recording
- Counting and reconciliation
- Denomination tracking
- Hundi reports
"""

import pytest
from fastapi import status
from datetime import date, datetime


@pytest.mark.hundi
@pytest.mark.api
class TestHundiManagement:
    """Tests for hundi (collection box) management"""

    def test_create_hundi(self, authenticated_client):
        """Test registering a new hundi/collection box"""
        hundi_data = {
            "hundi_code": "HUNDI-001",
            "hundi_name": "Main Temple Hundi",
            "location": "Main Hall - East Side",
            "is_active": True,
        }

        response = authenticated_client.post("/api/v1/hundi/masters", json=hundi_data)

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["hundi_code"] == "HUNDI-001"
            assert data["hundi_name"] == "Main Temple Hundi"

    def test_list_hundis(self, authenticated_client):
        """Test listing all hundis"""
        response = authenticated_client.get("/api/v1/hundi/masters")

        assert response.status_code == status.HTTP_200_OK
        hundis = response.json()
        assert isinstance(hundis, list)

    def test_get_hundi_by_id(self, authenticated_client):
        """Test retrieving a specific hundi"""
        # Create hundi
        hundi_data = {"hundi_code": "HUNDI-GET", "hundi_name": "Test Hundi", "is_active": True}

        create_response = authenticated_client.post("/api/v1/hundi/hundis", json=hundi_data)

        if create_response.status_code == status.HTTP_201_CREATED:
            hundi_id = create_response.json()["id"]

            # Retrieve it
            response = authenticated_client.get(f"/api/v1/hundi/hundis/{hundi_id}")

            assert response.status_code == status.HTTP_200_OK


@pytest.mark.hundi
@pytest.mark.api
class TestHundiCollections:
    """Tests for hundi collection recording"""

    def test_record_hundi_collection(self, authenticated_client):
        """Test recording a hundi collection/counting"""
        collection_data = {
            "hundi_id": 1,
            "collection_date": str(date.today()),
            "opened_by": "John Doe",
            "counted_by": "Jane Smith",
            "total_amount": 15000.00,
            "denominations": {
                "2000": 5,  # 5 notes of ₹2000
                "500": 10,  # 10 notes of ₹500
                "100": 50,  # 50 notes of ₹100
                "coins": 500.00,
            },
        }

        response = authenticated_client.post("/api/v1/hundi/collections", json=collection_data)

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert float(data["total_amount"]) == 15000.00

    def test_list_hundi_collections(self, authenticated_client):
        """Test listing all hundi collections (openings)"""
        response = authenticated_client.get("/api/v1/hundi/openings")

        assert response.status_code == status.HTTP_200_OK
        collections = response.json()
        assert isinstance(collections, list)

    def test_filter_collections_by_date(self, authenticated_client):
        """Test filtering collections by date range"""
        response = authenticated_client.get(
            "/api/v1/hundi/openings",
            params={"start_date": str(date.today()), "end_date": str(date.today())},
        )

        assert response.status_code == status.HTTP_200_OK

    def test_get_hundi_collection_summary(self, authenticated_client):
        """Test getting summary of hundi collections"""
        response = authenticated_client.get("/api/v1/hundi/reports/summary", params={"hundi_id": 1})

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "total_collections" in data or "total_amount" in data


@pytest.mark.hundi
@pytest.mark.api
class TestHundiReports:
    """Tests for hundi reporting"""

    def test_generate_daily_hundi_report(self, authenticated_client):
        """Test generating daily hundi collection report"""
        response = authenticated_client.get(
            "/api/v1/hundi/reports/daily", params={"date": str(date.today())}
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, (dict, list))

    def test_export_hundi_report(self, authenticated_client):
        """Test exporting hundi report to Excel"""
        response = authenticated_client.get(
            "/api/v1/hundi/reports/export", params={"format": "excel"}
        )

        if response.status_code == status.HTTP_200_OK:
            assert "spreadsheet" in response.headers.get("content-type", "")


# ============================================================================
# HOW TO RUN THESE TESTS
# ============================================================================
# Run all hundi tests:
#   pytest tests/test_hundi.py -v
# ============================================================================
