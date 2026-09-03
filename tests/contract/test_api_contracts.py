"""
Contract Tests - API schema validation and backward compatibility.
Ensures API responses match expected schemas and don't break clients.
"""
import pytest
from framework.base_test import BaseAPITest
from framework.assertions import assert_status_code


# Expected API response schemas
ORDER_SCHEMA = {
    "order_id": "string",
    "customer_id": "string",
    "product_id": "string",
    "quantity": "integer",
    "total_amount": "number",
    "status": "string",
}

PRODUCT_SCHEMA = {
    "product_id": "string",
    "product_name": "string",
    "quantity_available": "integer",
    "unit_price": "number",
}

PAGINATED_RESPONSE_SCHEMA = {
    "items": "array",
    "total": "integer",
    "page": "integer",
    "page_size": "integer",
}

HEALTH_SCHEMA = {
    "status": "string",
    "service": "string",
    "version": "string",
}


@pytest.mark.contract
class TestHealthContract(BaseAPITest):
    """Test health endpoint contract."""

    def test_health_response_schema(self, fresh_client):
        """Health endpoint must return expected schema."""
        response = fresh_client.get("/health")
        assert_status_code(response, 200)
        
        data = response.json()
        assert "status" in data, "Missing 'status' in health response"
        assert "service" in data, "Missing 'service' in health response"
        assert isinstance(data["status"], str), "'status' must be string"
        assert data["status"] == "healthy", "Service should report healthy"


@pytest.mark.contract
class TestOrderContract(BaseAPITest):
    """Test order endpoints contract."""

    def test_create_order_response_fields(self, authenticated_client):
        """Order creation must return all required fields."""
        response = authenticated_client.post("/api/v1/orders", json={
            "customer_id": "CUST-001",
            "product_id": "PROD-001",
            "quantity": 1,
        })
        
        if response.status_code in (200, 201):
            data = response.json()
            for field, expected_type in ORDER_SCHEMA.items():
                assert field in data, f"Missing field '{field}' in order response"
                
                if expected_type == "string":
                    assert isinstance(data[field], str), f"'{field}' must be string"
                elif expected_type == "integer":
                    assert isinstance(data[field], int), f"'{field}' must be integer"
                elif expected_type == "number":
                    assert isinstance(data[field], (int, float)), f"'{field}' must be number"

    def test_order_status_values(self, authenticated_client):
        """Order status must be from allowed values."""
        valid_statuses = {"pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "failed"}
        
        response = authenticated_client.post("/api/v1/orders", json={
            "customer_id": "CUST-001",
            "product_id": "PROD-001",
            "quantity": 1,
        })
        
        if response.status_code in (200, 201):
            status = response.json().get("status", "")
            assert status in valid_statuses, (
                f"Invalid order status: '{status}'. Must be one of: {valid_statuses}"
            )

    def test_list_orders_pagination_contract(self, authenticated_client):
        """Paginated order list must return expected structure."""
        response = authenticated_client.get("/api/v1/orders", params={"page": 1, "page_size": 10})
        
        if response.status_code == 200:
            data = response.json()
            assert "items" in data or "data" in data, "Missing items/data in paginated response"
            assert "total" in data, "Missing 'total' in paginated response"
            assert isinstance(data["total"], int), "'total' must be integer"


@pytest.mark.contract
class TestInventoryContract(BaseAPITest):
    """Test inventory endpoint contract."""

    def test_inventory_response_fields(self, fresh_client):
        """Inventory endpoint must return all required fields."""
        response = fresh_client.get("/api/v1/inventory/PROD-001")
        
        if response.status_code == 200:
            data = response.json()
            for field in ["product_id", "product_name", "quantity_available"]:
                assert field in data, f"Missing field '{field}' in inventory response"

    def test_inventory_quantity_non_negative(self, fresh_client):
        """Inventory quantity must never be negative."""
        response = fresh_client.get("/api/v1/inventory")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            for item in items:
                qty = item.get("quantity_available", item.get("stock", 0))
                assert qty >= 0, f"Negative quantity for {item.get('product_id')}: {qty}"


@pytest.mark.contract
class TestBackwardCompatibility(BaseAPITest):
    """Test that API changes don't break existing clients."""

    def test_no_field_removal_in_order(self, authenticated_client):
        """Previously returned fields must not be removed."""
        # These fields must always be present in order responses
        required_fields = ["order_id", "customer_id", "status"]
        
        response = authenticated_client.post("/api/v1/orders", json={
            "customer_id": "CUST-001",
            "product_id": "PROD-001",
            "quantity": 1,
        })
        
        if response.status_code in (200, 201):
            data = response.json()
            for field in required_fields:
                assert field in data, f"Regression: field '{field}' removed from order response"

    def test_error_response_format(self, fresh_client):
        """Error responses must follow consistent format."""
        response = fresh_client.get("/api/v1/orders/NONEXISTENT")
        
        if response.status_code >= 400:
            data = response.json()
            # Must have either 'detail' or 'error' key
            assert "detail" in data or "error" in data, (
                "Error response must include 'detail' or 'error' key"
            )
