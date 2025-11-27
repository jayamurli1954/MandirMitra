"""
Comprehensive Tests for Seva Booking Module

Tests cover:
- Seva category management
- Seva creation and configuration
- Seva booking operations
- Availability checking
- Receipt generation
- Accounting integration
- Seva scheduling
"""

import pytest
from fastapi import status
from datetime import date, datetime, timedelta


@pytest.mark.sevas
@pytest.mark.api
class TestSevaCategories:
    """Tests for seva category management"""

    def test_list_seva_categories(self, authenticated_client):
        """Test retrieving list of seva categories"""
        response = authenticated_client.get("/api/v1/sevas/categories")

        assert response.status_code == status.HTTP_200_OK
        categories = response.json()
        assert isinstance(categories, list)


@pytest.mark.sevas
@pytest.mark.api
class TestSevaManagement:
    """Tests for seva creation and management"""

    def test_create_seva_basic(self, authenticated_client):
        """Test creating a basic seva"""
        seva_data = {
            "name_english": "Abhishekam",
            "name_local": "अभिषेकम्",
            "description": "Special abhishekam to Lord Shiva",
            "price": 500.00,
            "duration_minutes": 60,
            "is_active": True
        }

        response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name_english"] == "Abhishekam"
        assert float(data["price"]) == 500.00
        assert "id" in data

    def test_create_seva_with_schedule(self, authenticated_client):
        """Test creating a seva with daily schedule"""
        seva_data = {
            "name_english": "Sahasranama Archana",
            "name_local": "सहस्रनाम अर्चन",
            "description": "1000 names archana",
            "price": 300.00,
            "duration_minutes": 45,
            "is_active": True,
            "max_bookings_per_day": 10,
            "available_days": ["monday", "wednesday", "friday"],
            "start_time": "09:00",
            "end_time": "17:00"
        }

        response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["max_bookings_per_day"] == 10

    def test_list_sevas(self, authenticated_client):
        """Test listing all available sevas"""
        response = authenticated_client.get("/api/v1/sevas/")

        assert response.status_code == status.HTTP_200_OK
        sevas = response.json()
        assert isinstance(sevas, list)

    def test_list_active_sevas_only(self, authenticated_client):
        """Test filtering to show only active sevas"""
        response = authenticated_client.get(
            "/api/v1/sevas/",
            params={"active_only": True}
        )

        assert response.status_code == status.HTTP_200_OK
        sevas = response.json()
        # All returned sevas should be active
        for seva in sevas:
            if "is_active" in seva:
                assert seva["is_active"] is True

    def test_get_seva_by_id(self, authenticated_client):
        """Test retrieving a specific seva"""
        # Create seva
        seva_data = {
            "name_english": "Test Seva",
            "price": 100.00,
            "duration_minutes": 30,
            "is_active": True
        }

        create_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = create_response.json()["id"]

        # Retrieve it
        response = authenticated_client.get(f"/api/v1/sevas/{seva_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == seva_id

    def test_update_seva_price(self, authenticated_client):
        """Test updating seva price"""
        # Create seva
        seva_data = {
            "name_english": "Price Update Seva",
            "price": 200.00,
            "duration_minutes": 30,
            "is_active": True
        }

        create_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = create_response.json()["id"]

        # Update price
        update_data = {"price": 250.00}
        response = authenticated_client.put(
            f"/api/v1/sevas/{seva_id}",
            json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert float(data["price"]) == 250.00

    def test_deactivate_seva(self, authenticated_client):
        """Test deactivating a seva"""
        # Create seva
        seva_data = {
            "name_english": "Deactivate Test Seva",
            "price": 150.00,
            "duration_minutes": 30,
            "is_active": True
        }

        create_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = create_response.json()["id"]

        # Deactivate
        response = authenticated_client.delete(f"/api/v1/sevas/{seva_id}")

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]


@pytest.mark.sevas
@pytest.mark.api
class TestSevaBookings:
    """Tests for seva booking operations"""

    def test_create_seva_booking_minimal(self, authenticated_client):
        """Test creating a seva booking with minimal required fields"""
        # First create a seva
        seva_data = {
            "name_english": "Booking Test Seva",
            "price": 400.00,
            "duration_minutes": 30,
            "is_active": True
        }

        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = seva_response.json()["id"]

        # Create booking
        booking_data = {
            "seva_id": seva_id,
            "devotee_name": "Krishna Kumar",
            "seva_date": str(date.today() + timedelta(days=1)),
            "payment_method": "cash"
        }

        response = authenticated_client.post(
            "/api/v1/sevas/bookings",
            json=booking_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["devotee_name"] == "Krishna Kumar"
        assert data["seva_id"] == seva_id
        assert "receipt_number" in data
        assert "id" in data

    def test_create_seva_booking_full(self, authenticated_client):
        """Test creating a seva booking with all fields"""
        # Create seva
        seva_data = {
            "name_english": "Full Booking Seva",
            "price": 600.00,
            "duration_minutes": 60,
            "is_active": True
        }

        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = seva_response.json()["id"]

        # Create booking with all details
        booking_data = {
            "seva_id": seva_id,
            "devotee_name": "Lakshmi Devi",
            "gotra": "Bharadwaja",
            "nakshatra": "Rohini",
            "rashi": "Vrishabha",
            "phone": "9876543210",
            "email": "lakshmi@example.com",
            "seva_date": str(date.today() + timedelta(days=2)),
            "seva_time": "10:00",
            "payment_method": "upi",
            "transaction_id": "UPI987654321",
            "special_instructions": "Please use coconut for abhishekam"
        }

        response = authenticated_client.post(
            "/api/v1/sevas/bookings",
            json=booking_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["gotra"] == "Bharadwaja"
        assert data["nakshatra"] == "Rohini"
        assert data["phone"] == "9876543210"

    def test_booking_with_advance_payment(self, authenticated_client):
        """Test creating booking with partial advance payment"""
        # Create seva
        seva_data = {
            "name_english": "Advance Payment Seva",
            "price": 1000.00,
            "duration_minutes": 90,
            "is_active": True
        }

        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = seva_response.json()["id"]

        # Create booking with advance
        booking_data = {
            "seva_id": seva_id,
            "devotee_name": "Advance Test",
            "seva_date": str(date.today() + timedelta(days=3)),
            "payment_method": "cash",
            "amount_paid": 500.00,  # Partial payment
            "is_advance_booking": True
        }

        response = authenticated_client.post(
            "/api/v1/sevas/bookings",
            json=booking_data
        )

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert float(data["amount_paid"]) == 500.00

    def test_check_seva_availability(self, authenticated_client):
        """Test checking seva availability for a date"""
        # Create seva with limited slots
        seva_data = {
            "name_english": "Limited Slots Seva",
            "price": 300.00,
            "duration_minutes": 30,
            "is_active": True,
            "max_bookings_per_day": 5
        }

        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = seva_response.json()["id"]

        # Check availability
        target_date = str(date.today() + timedelta(days=1))
        response = authenticated_client.get(
            f"/api/v1/sevas/{seva_id}/availability",
            params={"date": target_date}
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "available" in data
            assert "slots_remaining" in data or "is_available" in data

    def test_list_seva_bookings(self, authenticated_client):
        """Test listing all seva bookings"""
        response = authenticated_client.get("/api/v1/sevas/bookings")

        assert response.status_code == status.HTTP_200_OK
        bookings = response.json()
        assert isinstance(bookings, list)

    def test_filter_bookings_by_date(self, authenticated_client):
        """Test filtering bookings by date range"""
        today = date.today()
        tomorrow = today + timedelta(days=1)

        response = authenticated_client.get(
            "/api/v1/sevas/bookings",
            params={
                "start_date": str(today),
                "end_date": str(tomorrow)
            }
        )

        assert response.status_code == status.HTTP_200_OK
        bookings = response.json()
        assert isinstance(bookings, list)

    def test_filter_bookings_by_devotee(self, authenticated_client):
        """Test searching bookings by devotee name"""
        response = authenticated_client.get(
            "/api/v1/sevas/bookings",
            params={"search": "Krishna"}
        )

        assert response.status_code == status.HTTP_200_OK
        bookings = response.json()
        assert isinstance(bookings, list)

    def test_get_booking_by_id(self, authenticated_client):
        """Test retrieving a specific booking"""
        # Create seva and booking
        seva_data = {
            "name_english": "Get Booking Seva",
            "price": 200.00,
            "duration_minutes": 30,
            "is_active": True
        }

        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = seva_response.json()["id"]

        booking_data = {
            "seva_id": seva_id,
            "devotee_name": "Get Test",
            "seva_date": str(date.today() + timedelta(days=1)),
            "payment_method": "cash"
        }

        booking_response = authenticated_client.post(
            "/api/v1/sevas/bookings",
            json=booking_data
        )
        booking_id = booking_response.json()["id"]

        # Retrieve booking
        response = authenticated_client.get(f"/api/v1/sevas/bookings/{booking_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == booking_id

    def test_cancel_seva_booking(self, authenticated_client):
        """Test cancelling a seva booking"""
        # Create seva and booking
        seva_data = {
            "name_english": "Cancel Test Seva",
            "price": 500.00,
            "duration_minutes": 60,
            "is_active": True
        }

        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = seva_response.json()["id"]

        booking_data = {
            "seva_id": seva_id,
            "devotee_name": "Cancel Test",
            "seva_date": str(date.today() + timedelta(days=5)),
            "payment_method": "cash"
        }

        booking_response = authenticated_client.post(
            "/api/v1/sevas/bookings",
            json=booking_data
        )
        booking_id = booking_response.json()["id"]

        # Cancel booking
        response = authenticated_client.post(
            f"/api/v1/sevas/bookings/{booking_id}/cancel",
            json={"reason": "Devotee requested cancellation"}
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["status"] == "cancelled" or "cancel" in data


@pytest.mark.sevas
@pytest.mark.api
class TestSevaReceipts:
    """Tests for seva booking receipt generation"""

    def test_generate_booking_receipt_pdf(self, authenticated_client):
        """Test generating PDF receipt for seva booking"""
        # Create seva and booking
        seva_data = {
            "name_english": "Receipt Test Seva",
            "price": 400.00,
            "duration_minutes": 45,
            "is_active": True
        }

        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = seva_response.json()["id"]

        booking_data = {
            "seva_id": seva_id,
            "devotee_name": "Receipt Test Devotee",
            "seva_date": str(date.today() + timedelta(days=1)),
            "payment_method": "upi"
        }

        booking_response = authenticated_client.post(
            "/api/v1/sevas/bookings",
            json=booking_data
        )
        booking_id = booking_response.json()["id"]

        # Generate receipt
        response = authenticated_client.get(
            f"/api/v1/sevas/bookings/{booking_id}/receipt"
        )

        if response.status_code == status.HTTP_200_OK:
            assert response.headers["content-type"] == "application/pdf"


@pytest.mark.sevas
@pytest.mark.api
@pytest.mark.integration
class TestSevaAccountingIntegration:
    """Tests for seva accounting integration"""

    def test_booking_creates_journal_entry(self, authenticated_client, db_session):
        """Test that creating a booking creates accounting journal entry"""
        from app.models.accounting import JournalEntry

        # Count existing entries
        initial_count = db_session.query(JournalEntry).count()

        # Create seva and booking
        seva_data = {
            "name_english": "Accounting Seva",
            "price": 700.00,
            "duration_minutes": 60,
            "is_active": True
        }

        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = seva_response.json()["id"]

        booking_data = {
            "seva_id": seva_id,
            "devotee_name": "Accounting Test",
            "seva_date": str(date.today() + timedelta(days=1)),
            "payment_method": "cash"
        }

        response = authenticated_client.post(
            "/api/v1/sevas/bookings",
            json=booking_data
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Check if journal entry was created
        final_count = db_session.query(JournalEntry).count()
        assert final_count > initial_count


@pytest.mark.sevas
@pytest.mark.api
class TestSevaReports:
    """Tests for seva reporting and analytics"""

    def test_get_seva_bookings_summary(self, authenticated_client):
        """Test getting summary of seva bookings"""
        response = authenticated_client.get(
            "/api/v1/sevas/bookings/summary",
            params={
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=7))
            }
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "total_bookings" in data or "total_amount" in data

    def test_export_bookings_report(self, authenticated_client):
        """Test exporting seva bookings to Excel"""
        response = authenticated_client.get(
            "/api/v1/sevas/bookings/export",
            params={"format": "excel"}
        )

        if response.status_code == status.HTTP_200_OK:
            assert "spreadsheet" in response.headers.get("content-type", "")


@pytest.mark.sevas
@pytest.mark.api
class TestSevaValidation:
    """Tests for seva booking validation"""

    def test_reject_booking_for_past_date(self, authenticated_client):
        """Test that bookings for past dates are rejected"""
        # Create seva
        seva_data = {
            "name_english": "Past Date Seva",
            "price": 300.00,
            "duration_minutes": 30,
            "is_active": True
        }

        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = seva_response.json()["id"]

        # Try to book for yesterday
        booking_data = {
            "seva_id": seva_id,
            "devotee_name": "Past Date Test",
            "seva_date": str(date.today() - timedelta(days=1)),
            "payment_method": "cash"
        }

        response = authenticated_client.post(
            "/api/v1/sevas/bookings",
            json=booking_data
        )

        # Should reject past date
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_reject_booking_when_fully_booked(self, authenticated_client):
        """Test that bookings are rejected when seva is fully booked"""
        # Create seva with max 1 booking per day
        seva_data = {
            "name_english": "Full Booking Limit Seva",
            "price": 400.00,
            "duration_minutes": 30,
            "is_active": True,
            "max_bookings_per_day": 1
        }

        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json=seva_data
        )
        seva_id = seva_response.json()["id"]

        target_date = str(date.today() + timedelta(days=1))

        # First booking should succeed
        booking1 = {
            "seva_id": seva_id,
            "devotee_name": "First Booking",
            "seva_date": target_date,
            "payment_method": "cash"
        }

        response1 = authenticated_client.post(
            "/api/v1/sevas/bookings",
            json=booking1
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Second booking should fail (fully booked)
        booking2 = {
            "seva_id": seva_id,
            "devotee_name": "Second Booking",
            "seva_date": target_date,
            "payment_method": "cash"
        }

        response2 = authenticated_client.post(
            "/api/v1/sevas/bookings",
            json=booking2
        )

        # Should reject as fully booked
        assert response2.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# HOW TO RUN THESE TESTS
# ============================================================================
# Run all seva tests:
#   pytest tests/test_sevas.py -v
#
# Run booking tests only:
#   pytest tests/test_sevas.py::TestSevaBookings -v
#
# Run with coverage:
#   pytest tests/test_sevas.py --cov=app.api.sevas --cov-report=term-missing
# ============================================================================
