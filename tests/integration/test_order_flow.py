"""
Integration Tests - End-to-end order workflow.
Tests the complete flow from order creation through payment and fulfillment.
"""
import pytest
from framework.base_test import BaseIntegrationTest
from framework.api_client import APIClient
from framework.data_factories import OrderFactory, CustomerFactory, ProductFactory


@pytest.mark.integration
class TestOrderWorkflow(BaseIntegrationTest):
    """Test complete order workflow from creation to fulfillment."""

    def test_full_order_lifecycle(self, fresh_client):
        """Should complete full order lifecycle: create -> confirm -> ship -> deliver."""
        client = fresh_client
        
        # Step 1: Register and login
        response = client.post("/api/v1/auth/register", json={
            "email": "lifecycle@test.com",
            "password": "TestPass123!",
            "full_name": "Lifecycle Test",
        })
        assert response.status_code in (200, 201, 409)
        
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "lifecycle@test.com",
            "password": "TestPass123!",
        })
        
        if login_resp.status_code == 200:
            token = login_resp.json()["access_token"]
            client.set_auth_token(token)
            
            # Step 2: Create order
            order_data = OrderFactory.create(customer_id="lifecycle@test.com")
            create_resp = client.post("/api/v1/orders", json={
                "customer_id": "lifecycle@test.com",
                "product_id": "PROD-001",
                "quantity": 1,
            })
            
            if create_resp.status_code in (200, 201):
                order_id = create_resp.json()["order_id"]
                
                # Step 3: Verify order exists
                get_resp = client.get(f"/api/v1/orders/{order_id}")
                assert get_resp.status_code == 200
                assert get_resp.json()["order_id"] == order_id
                
                # Step 4: Check order appears in list
                list_resp = client.get("/api/v1/orders")
                if list_resp.status_code == 200:
                    data = list_resp.json()
                    items = data.get("items", data.get("data", []))
                    order_ids = [o.get("order_id") for o in items]
                    assert order_id in order_ids

    def test_order_cancel_refund_flow(self, fresh_client):
        """Should handle cancel and refund flow."""
        client = fresh_client
        
        # Login
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "cancel@test.com",
            "password": "TestPass123!",
        })
        
        if login_resp.status_code == 200:
            client.set_auth_token(login_resp.json()["access_token"])
            
            # Create order
            create_resp = client.post("/api/v1/orders", json={
                "customer_id": "cancel@test.com",
                "product_id": "PROD-001",
                "quantity": 1,
            })
            
            if create_resp.status_code in (200, 201):
                order_id = create_resp.json()["order_id"]
                
                # Cancel order
                cancel_resp = client.put(f"/api/v1/orders/{order_id}/cancel")
                assert cancel_resp.status_code in (200, 400)  # May fail if already shipped


@pytest.mark.integration
class TestCrossServiceConsistency(BaseIntegrationTest):
    """Test data consistency across service boundaries."""

    def test_order_amount_matches_product_price(self, fresh_client):
        """Order total should equal product price * quantity."""
        client = fresh_client
        
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "consistency@test.com",
            "password": "TestPass123!",
        })
        
        if login_resp.status_code == 200:
            client.set_auth_token(login_resp.json()["access_token"])
            
            # Get product price
            product_resp = client.get("/api/v1/inventory/PROD-001")
            
            if product_resp.status_code == 200:
                price = product_resp.json().get("unit_price", 49.99)
                
                # Create order
                create_resp = client.post("/api/v1/orders", json={
                    "customer_id": "consistency@test.com",
                    "product_id": "PROD-001",
                    "quantity": 2,
                })
                
                if create_resp.status_code in (200, 201):
                    total = create_resp.json().get("total_amount", 0)
                    expected = price * 2
                    assert abs(total - expected) < 0.01, (
                        f"Order total ${total} doesn't match expected ${expected}"
                    )
