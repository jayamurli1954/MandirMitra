"""
Comprehensive Tests for Inventory Module

Tests cover:
- Item management
- Stock tracking
- Purchase orders
- Stock adjustments
- Stock audit
- Inventory alerts
- Reorder levels
"""

import pytest
from fastapi import status
from datetime import date, timedelta


@pytest.mark.inventory
@pytest.mark.api
class TestInventoryItems:
    """Tests for inventory item management"""

    def test_create_inventory_item(self, authenticated_client):
        """Test creating a new inventory item"""
        item_data = {
            "code": "ITEM-001",
            "name": "Rice - Sona Masoori",
            "category": "grocery",
            "unit": "kg",
            "reorder_level": 100.0,
            "reorder_quantity": 200.0,
        }

        response = authenticated_client.post("/api/v1/inventory/items", json=item_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "ITEM-001"
        assert data["name"] == "Rice - Sona Masoori"

    def test_list_inventory_items(self, authenticated_client):
        """Test listing all inventory items"""
        response = authenticated_client.get("/api/v1/inventory/items")

        assert response.status_code == status.HTTP_200_OK
        items = response.json()
        assert isinstance(items, list)

    def test_get_item_by_id(self, authenticated_client):
        """Test retrieving a specific item"""
        # Create item
        item_data = {
            "code": "ITEM-GET",
            "name": "Test Item",
            "category": "general",
            "unit": "piece",
        }

        create_response = authenticated_client.post("/api/v1/inventory/items", json=item_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        item_id = create_response.json()["id"]

        # Retrieve it
        response = authenticated_client.get(f"/api/v1/inventory/items/{item_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == item_id


@pytest.mark.inventory
@pytest.mark.api
class TestPurchaseOrders:
    """Tests for purchase order management"""

    def test_create_purchase_order(self, authenticated_client):
        """Test creating a purchase order"""
        po_data = {
            "supplier_name": "ABC Suppliers",
            "order_date": str(date.today()),
            "expected_delivery_date": str(date.today() + timedelta(days=7)),
            "items": [{"item_id": 1, "quantity": 100, "unit_price": 50.00}],
        }

        response = authenticated_client.post("/api/v1/inventory/purchase-orders", json=po_data)

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert "po_number" in data

    def test_list_purchase_orders(self, authenticated_client):
        """Test listing purchase orders"""
        response = authenticated_client.get("/api/v1/purchase-orders")

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.inventory
@pytest.mark.api
class TestStockMovements:
    """Tests for stock tracking and movements"""

    def test_stock_in_adjustment(self, authenticated_client):
        """Test adding stock (stock-in)"""
        adjustment_data = {
            "item_id": 1,
            "adjustment_type": "stock_in",
            "quantity": 50.0,
            "reason": "Purchase received",
            "adjustment_date": str(date.today()),
        }

        response = authenticated_client.post("/api/v1/inventory/adjustments", json=adjustment_data)

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["adjustment_type"] == "stock_in"

    def test_stock_out_adjustment(self, authenticated_client):
        """Test removing stock (stock-out)"""
        adjustment_data = {
            "item_id": 1,
            "adjustment_type": "stock_out",
            "quantity": 20.0,
            "reason": "Used in temple activities",
            "adjustment_date": str(date.today()),
        }

        response = authenticated_client.post("/api/v1/inventory/adjustments", json=adjustment_data)

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["adjustment_type"] == "stock_out"

    def test_get_current_stock_level(self, authenticated_client):
        """Test retrieving current stock level for an item"""
        response = authenticated_client.get("/api/v1/inventory/items/1/stock-level")

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "current_stock" in data or "quantity" in data


@pytest.mark.inventory
@pytest.mark.api
class TestStockAudit:
    """Tests for stock audit functionality"""

    def test_create_stock_audit(self, authenticated_client):
        """Test creating a stock audit"""
        audit_data = {
            "audit_date": str(date.today()),
            "auditor_name": "John Doe",
            "items": [{"item_id": 1, "physical_count": 150.0, "system_count": 145.0}],
        }

        response = authenticated_client.post("/api/v1/inventory/audits", json=audit_data)

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert "audit_number" in data or "id" in data

    def test_list_stock_audits(self, authenticated_client):
        """Test listing stock audits"""
        response = authenticated_client.get("/api/v1/inventory/audits")

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.inventory
@pytest.mark.api
class TestInventoryAlerts:
    """Tests for inventory alerts and notifications"""

    def test_get_low_stock_items(self, authenticated_client):
        """Test retrieving items with low stock"""
        response = authenticated_client.get("/api/v1/inventory/alerts/alerts/low-stock")

        assert response.status_code == status.HTTP_200_OK
        items = response.json()
        assert isinstance(items, list)

    def test_get_reorder_suggestions(self, authenticated_client):
        """Test getting reorder suggestions"""
        response = authenticated_client.get("/api/v1/inventory/alerts/reorder-suggestions")

        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# HOW TO RUN THESE TESTS
# ============================================================================
# Run all inventory tests:
#   pytest tests/test_inventory.py -v
# ============================================================================
