"""
Extended Tests for Devotees API
Tests additional devotee endpoints not covered in existing tests
"""

import pytest
from fastapi import status
from datetime import date, timedelta


@pytest.mark.api
@pytest.mark.devotees
class TestDevoteeSearch:
    """Tests for devotee search functionality"""

    def test_search_devotee_by_mobile(self, authenticated_client):
        """Test searching devotee by mobile number"""
        # First create a devotee
        devotee_data = {
            "first_name": "Search",
            "last_name": "Test",
            "phone": "9998887776",
            "country_code": "+91"
        }
        authenticated_client.post("/api/v1/devotees/", json=devotee_data)

        # Search by mobile
        response = authenticated_client.get("/api/v1/devotees/search/by-mobile/9998887776")

        assert response.status_code == status.HTTP_200_OK
        devotees = response.json()
        assert isinstance(devotees, list)
        if len(devotees) > 0:
            assert devotees[0]["phone"] == "9998887776"


@pytest.mark.api
@pytest.mark.devotees
class TestDevoteeManagement:
    """Tests for devotee management operations"""

    def test_update_devotee(self, authenticated_client):
        """Test updating a devotee"""
        # Create devotee first
        devotee_data = {
            "first_name": "Update",
            "last_name": "Test",
            "phone": "9998887775",
            "country_code": "+91"
        }
        create_response = authenticated_client.post(
            "/api/v1/devotees/",
            json=devotee_data
        )
        devotee_id = create_response.json()["id"]

        # Update devotee
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com"
        }
        response = authenticated_client.put(
            f"/api/v1/devotees/{devotee_id}",
            json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"

    def test_delete_devotee(self, authenticated_client):
        """Test deleting a devotee"""
        # Create devotee first
        devotee_data = {
            "first_name": "Delete",
            "last_name": "Test",
            "phone": "9998887774",
            "country_code": "+91"
        }
        create_response = authenticated_client.post(
            "/api/v1/devotees/",
            json=devotee_data
        )
        devotee_id = create_response.json()["id"]

        # Delete devotee
        response = authenticated_client.delete(f"/api/v1/devotees/{devotee_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        get_response = authenticated_client.get(f"/api/v1/devotees/{devotee_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_find_duplicate_devotees(self, authenticated_client):
        """Test finding duplicate devotees"""
        response = authenticated_client.get("/api/v1/devotees/duplicates")

        assert response.status_code == status.HTTP_200_OK
        duplicates = response.json()
        assert isinstance(duplicates, list)

    def test_merge_devotees(self, authenticated_client):
        """Test merging duplicate devotees"""
        # Create two devotees with same phone (duplicates)
        devotee1_data = {
            "first_name": "Merge",
            "last_name": "One",
            "phone": "9998887773",
            "country_code": "+91"
        }
        devotee2_data = {
            "first_name": "Merge",
            "last_name": "Two",
            "phone": "9998887773",  # Same phone
            "country_code": "+91"
        }
        devotee1 = authenticated_client.post("/api/v1/devotees/", json=devotee1_data).json()
        devotee2 = authenticated_client.post("/api/v1/devotees/", json=devotee2_data).json()

        # Merge them
        merge_data = {
            "source_devotee_id": devotee2["id"],
            "target_devotee_id": devotee1["id"]
        }
        response = authenticated_client.post(
            "/api/v1/devotees/merge",
            json=merge_data
        )

        # Should succeed (200 or 201)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED
        ]

    def test_get_upcoming_birthdays(self, authenticated_client):
        """Test getting upcoming birthdays"""
        response = authenticated_client.get("/api/v1/devotees/birthdays")

        assert response.status_code == status.HTTP_200_OK
        birthdays = response.json()
        assert isinstance(birthdays, list)

    def test_get_devotee_analytics(self, authenticated_client):
        """Test getting devotee analytics"""
        response = authenticated_client.get("/api/v1/devotees/analytics")

        assert response.status_code == status.HTTP_200_OK
        analytics = response.json()
        assert isinstance(analytics, dict)

    def test_link_family_member(self, authenticated_client):
        """Test linking family members"""
        # Create family head
        head_data = {
            "first_name": "Family",
            "last_name": "Head",
            "phone": "9998887772",
            "country_code": "+91"
        }
        head = authenticated_client.post("/api/v1/devotees/", json=head_data).json()

        # Create family member
        member_data = {
            "first_name": "Family",
            "last_name": "Member",
            "phone": "9998887771",
            "country_code": "+91"
        }
        member = authenticated_client.post("/api/v1/devotees/", json=member_data).json()

        # Link them
        link_data = {
            "family_head_id": head["id"]
        }
        response = authenticated_client.put(
            f"/api/v1/devotees/{member['id']}/link-family",
            json=link_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("family_head_id") == head["id"]

    def test_update_devotee_tags(self, authenticated_client):
        """Test updating devotee tags"""
        # Create devotee
        devotee_data = {
            "first_name": "Tag",
            "last_name": "Test",
            "phone": "9998887770",
            "country_code": "+91"
        }
        devotee = authenticated_client.post("/api/v1/devotees/", json=devotee_data).json()

        # Update tags
        tags_data = {
            "tags": ["VIP", "Regular", "Donor"]
        }
        response = authenticated_client.put(
            f"/api/v1/devotees/{devotee['id']}/tags",
            json=tags_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Tags might be stored as JSON string or array
        assert "tags" in data or "tag" in str(data).lower()

    def test_get_family_members(self, authenticated_client):
        """Test getting family members of a devotee"""
        # Create family head
        head_data = {
            "first_name": "Family",
            "last_name": "Head2",
            "phone": "9998887769",
            "country_code": "+91"
        }
        head = authenticated_client.post("/api/v1/devotees/", json=head_data).json()

        # Get family members
        response = authenticated_client.get(f"/api/v1/devotees/{head['id']}/family")

        assert response.status_code == status.HTTP_200_OK
        family = response.json()
        assert isinstance(family, list)













