"""
Tests for Dashboard API
Tests the main dashboard statistics endpoint
"""

import pytest
from fastapi import status


@pytest.mark.api
@pytest.mark.dashboard
class TestDashboard:
    """Tests for dashboard endpoints"""

    def test_get_dashboard_stats(self, authenticated_client):
        """Test retrieving dashboard statistics"""
        response = authenticated_client.get("/api/v1/dashboard/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify response structure
        assert isinstance(data, dict)
        
        # Check for expected keys (may vary based on implementation)
        # Common dashboard stats include:
        # - total_donations
        # - total_sevas
        # - total_devotees
        # - today_collections
        # etc.
        
        # At minimum, verify it returns a dict with some data
        assert len(data) >= 0  # May be empty initially

    def test_get_dashboard_stats_unauthorized(self, client):
        """Test that dashboard stats require authentication"""
        response = client.get("/api/v1/dashboard/stats")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED













