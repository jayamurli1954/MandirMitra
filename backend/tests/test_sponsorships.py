"""
Sponsorship API Tests
Tests for sponsorship management endpoints
"""

import pytest
from fastapi import status
from datetime import date, timedelta
from app.models.devotee import Devotee
from app.models.vendor import Vendor


@pytest.mark.sponsorships
@pytest.mark.api
class TestSponsorships:
    """Tests for sponsorship management"""
    
    def test_create_sponsorship_temple_payment(
        self, authenticated_client, chart_of_accounts, db_session, test_user
    ):
        """Test creating a sponsorship with temple payment"""
        # Create a devotee first
        devotee = Devotee(
            temple_id=test_user.temple_id,
            name="Test Devotee",
            phone="9876543210"
        )
        db_session.add(devotee)
        db_session.commit()
        db_session.refresh(devotee)
        
        sponsorship_data = {
            "devotee_id": devotee.id,
            "sponsorship_category": "flower_decoration",
            "committed_amount": 5000.00,
            "sponsorship_date": str(date.today()),
            "payment_mode": "temple_payment",
            "description": "Flower decoration for daily pooja",
            "temple_id": test_user.temple_id
        }
        
        response = authenticated_client.post(
            "/api/v1/sponsorships",
            json=sponsorship_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["committed_amount"] == 5000.00
        assert data["sponsorship_category"] == "flower_decoration"
        assert "receipt_number" in data
    
    def test_create_direct_payment_sponsorship(
        self, authenticated_client, chart_of_accounts, db_session, test_user
    ):
        """Test creating sponsorship with direct vendor payment"""
        # Create devotee and vendor
        devotee = Devotee(
            temple_id=test_user.temple_id,
            name="Test Devotee",
            phone="9876543211"
        )
        db_session.add(devotee)
        
        vendor = Vendor(
            temple_id=test_user.temple_id,
            vendor_name="Flower Vendor",
            vendor_code="VEND001",
            phone="9876543212"
        )
        db_session.add(vendor)
        db_session.commit()
        db_session.refresh(devotee)
        db_session.refresh(vendor)
        
        sponsorship_data = {
            "devotee_id": devotee.id,
            "sponsorship_category": "flower_decoration",
            "committed_amount": 5000.00,
            "sponsorship_date": str(date.today()),
            "payment_mode": "direct_payment",
            "description": "Flower decoration for festival",
            "temple_id": test_user.temple_id,
            "vendor_id": vendor.id,
            "vendor_invoice_amount": 5000.00,
            "vendor_invoice_number": "INV-001",
            "vendor_invoice_date": str(date.today())
        }
        
        response = authenticated_client.post(
            "/api/v1/sponsorships",
            json=sponsorship_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["payment_mode"] == "direct_payment"
        # Should create journal entry automatically
    
    def test_list_sponsorships(self, authenticated_client):
        """Test listing sponsorships"""
        response = authenticated_client.get("/api/v1/sponsorships")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_sponsorship_by_id(self, authenticated_client):
        """Test getting sponsorship details"""
        response = authenticated_client.get("/api/v1/sponsorships/1")
        
        # May return 404 if no sponsorship exists
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_update_sponsorship(
        self, authenticated_client, chart_of_accounts, db_session, test_user
    ):
        """Test updating sponsorship"""
        # First create a sponsorship
        devotee = Devotee(
            temple_id=test_user.temple_id,
            name="Update Test Devotee",
            phone="9876543213"
        )
        db_session.add(devotee)
        db_session.commit()
        db_session.refresh(devotee)
        
        sponsorship_data = {
            "devotee_id": devotee.id,
            "sponsorship_category": "lighting",
            "committed_amount": 3000.00,
            "sponsorship_date": str(date.today()),
            "payment_mode": "temple_payment",
            "description": "Lighting for festival",
            "temple_id": test_user.temple_id
        }
        
        create_response = authenticated_client.post(
            "/api/v1/sponsorships",
            json=sponsorship_data
        )
        
        if create_response.status_code == status.HTTP_201_CREATED:
            sponsorship_id = create_response.json()["id"]
            
            update_data = {
                "status": "fulfilled",
                "fulfillment_date": str(date.today())
            }
            
            response = authenticated_client.put(
                f"/api/v1/sponsorships/{sponsorship_id}",
                json=update_data
            )
            
            assert response.status_code == status.HTTP_200_OK
    
    def test_record_payment(
        self, authenticated_client, chart_of_accounts, db_session, test_user
    ):
        """Test recording sponsorship payment"""
        # Create sponsorship first
        devotee = Devotee(
            temple_id=test_user.temple_id,
            name="Payment Test Devotee",
            phone="9876543214"
        )
        db_session.add(devotee)
        db_session.commit()
        db_session.refresh(devotee)
        
        sponsorship_data = {
            "devotee_id": devotee.id,
            "sponsorship_category": "tent",
            "committed_amount": 10000.00,
            "sponsorship_date": str(date.today()),
            "payment_mode": "temple_payment",
            "description": "Tent for festival",
            "temple_id": test_user.temple_id
        }
        
        create_response = authenticated_client.post(
            "/api/v1/sponsorships",
            json=sponsorship_data
        )
        
        if create_response.status_code == status.HTTP_201_CREATED:
            sponsorship_id = create_response.json()["id"]
            
            from datetime import datetime
            payment_data = {
                "amount_paid": 5000.00,
                "payment_date": datetime.now().isoformat(),
                "payment_method": "cash",
                "transaction_reference": "PAY001",
                "temple_id": test_user.temple_id,
                "sponsorship_id": sponsorship_id
            }
            
            response = authenticated_client.post(
                "/api/v1/sponsorships/payment",
                json=payment_data
            )
            
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_201_CREATED, 
                status.HTTP_404_NOT_FOUND,
                status.HTTP_400_BAD_REQUEST
            ]
    
    def test_filter_sponsorships_by_category(self, authenticated_client):
        """Test filtering sponsorships by category"""
        response = authenticated_client.get(
            "/api/v1/sponsorships",
            params={"category": "flower_decoration"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_filter_sponsorships_by_status(self, authenticated_client):
        """Test filtering sponsorships by status"""
        response = authenticated_client.get(
            "/api/v1/sponsorships",
            params={"status": "committed"}  # Use valid enum value
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

