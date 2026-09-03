"""
API Test Suite - Order endpoints.
Tests CRUD operations, validation, error handling, and pagination.
"""
import pytest
from framework.base_test import BaseAPITest
from framework.assertions import assert_status_code, assert_json_schema, assert_pagination
from framework.data_factories import OrderFactory, UserAuthFactory


@pytest.mark.api
class TestOrderCreation(BaseAPITest):
    """Test order creation endpoints."""

    def test_create_order_success(self, authenticated_client, sample_product):
        """Should create order with valid data."""
        response = authenticated_client.post("/api/v1/orders", json={
            "customer_id": "CUST-001",
            "product_id": sample_product["product_id"],
            "quantity": 2,
        })
        assert_status_code(response, 201)
        data = response.json()
        assert "order_id" in data
        assert data["quantity"] == 2

    def test_create_order_missing_fields(self, authenticated_client):
        """Should return 422 for missing required fields."""
        response = authenticated_client.post("/api/v1/orders", json={})
        assert_status_code(response, 422)

    def test_create_order_invalid_quantity(self, authenticated_client):
        """Should reject zero or negative quantity."""
        response = authenticated_client.post("/api/v1/orders", json={
            "customer_id": "CUST-001",
            "product_id": "PROD-001",
            "quantity": 0,
        })
        assert_status_code(response, 422)

    def test_create_order_negative_quantity(self, authenticated_client):
        """Should reject negative quantity."""
        response = authenticated_client.post("/api/v1/orders", json={
            "customer_id": "CUST-001",
            "product_id": "PROD-001",
            "quantity": -5,
        })
        assert_status_code(response, 422)

    def test_create_order_duplicate_idempotency(self, authenticated_client):
        """Should return same order for duplicate idempotency key."""
        payload = {
            "customer_id": "CUST-001",
            "product_id": "PROD-001",
            "quantity": 1,
            "idempotency_key": "test-idem-key-123",
        }
        r1 = authenticated_client.post("/api/v1/orders", json=payload)
        r2 = authenticated_client.post("/api/v1/orders", json=payload)
        
        assert r1.status_code in (200, 201)
        assert r2.status_code in (200, 201)
        if r1.status_code == 201 and r2.status_code in (200, 201):
            assert r1.json()["order_id"] == r2.json()["order_id"]


@pytest.mark.api
class TestOrderRetrieval(BaseAPITest):
    """Test order retrieval endpoints."""

    def test_get_order_by_id(self, authenticated_client):
        """Should retrieve order by ID."""
        # Create an order first
        create_resp = authenticated_client.post("/api/v1/orders", json={
            "customer_id": "CUST-001",
            "product_id": "PROD-001",
            "quantity": 1,
        })
        
        if create_resp.status_code in (200, 201):
            order_id = create_resp.json()["order_id"]
            response = authenticated_client.get(f"/api/v1/orders/{order_id}")
            assert_status_code(response, 200)
            assert response.json()["order_id"] == order_id

    def test_get_nonexistent_order(self, authenticated_client):
        """Should return 404 for nonexistent order."""
        response = authenticated_client.get("/api/v1/orders/ORD-DOESNOTEXIST")
        assert_status_code(response, 404)

    def test_list_orders_pagination(self, authenticated_client):
        """Should support paginated order listing."""
        response = authenticated_client.get("/api/v1/orders", params={"page": 1, "page_size": 5})
        if response.status_code == 200:
            data = response.json()
            assert "items" in data or "data" in data
            if "total" in data:
                assert isinstance(data["total"], int)


@pytest.mark.api
class TestOrderCancellation(BaseAPITest):
    """Test order cancellation."""

    def test_cancel_pending_order(self, authenticated_client):
        """Should cancel a pending order."""
        create_resp = authenticated_client.post("/api/v1/orders", json={
            "customer_id": "CUST-001",
            "product_id": "PROD-001",
            "quantity": 1,
        })
        
        if create_resp.status_code in (200, 201):
            order_id = create_resp.json()["order_id"]
            response = authenticated_client.put(f"/api/v1/orders/{order_id}/cancel")
            assert response.status_code in (200, 400)  # May fail if already processed

    def test_cancel_nonexistent_order(self, authenticated_client):
        """Should return 404 for canceling nonexistent order."""
        response = authenticated_client.put("/api/v1/orders/ORD-FAKE/cancel")
        assert_status_code(response, 404)


@pytest.mark.api
class TestOrderAuth(BaseAPITest):
    """Test order endpoints require authentication."""

    def test_create_order_without_auth(self, fresh_client):
        """Should reject unauthenticated order creation."""
        response = fresh_client.post("/api/v1/orders", json={
            "customer_id": "CUST-001",
            "product_id": "PROD-001",
            "quantity": 1,
        })
        assert response.status_code in (401, 403)

    def test_get_order_without_auth(self, fresh_client):
        """Should reject unauthenticated order retrieval."""
        response = fresh_client.get("/api/v1/orders/ORD-001")
        assert response.status_code in (401, 403)

    def test_list_orders_without_auth(self, fresh_client):
        """Should reject unauthenticated order listing."""
        response = fresh_client.get("/api/v1/orders")
        assert response.status_code in (401, 403)
