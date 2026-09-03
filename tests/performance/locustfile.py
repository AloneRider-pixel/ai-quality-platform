"""
Load Tests - Locust-based performance testing.
Tests API performance under concurrent load.
"""
import random
from locust import HttpUser, task, between, events


class ECommerceLoadTest(HttpUser):
    """Simulates concurrent users hitting the e-commerce API."""
    
    wait_time = between(0.5, 2)
    host = "http://localhost:8000"
    
    def on_start(self):
        """Register and authenticate before starting."""
        import string
        email = f"load_{''.join(random.choices(string.ascii_lowercase, k=8))}@test.com"
        self.email = email
        self.password = "LoadTest123!"
        
        # Register
        self.client.post("/api/v1/auth/register", json={
            "email": email,
            "password": self.password,
            "full_name": "Load Test User",
        })
        
        # Login
        resp = self.client.post("/api/v1/auth/login", json={
            "email": email,
            "password": self.password,
        })
        
        if resp.status_code == 200:
            self.token = resp.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(5)
    def create_order(self):
        """Create an order."""
        if not self.token:
            return
        self.client.post("/api/v1/orders", json={
            "customer_id": self.email,
            "product_id": f"PROD-{random.randint(1, 5):03d}",
            "quantity": random.randint(1, 3),
        }, headers=self.headers, name="/api/v1/orders [POST]")
    
    @task(10)
    def list_orders(self):
        """List orders."""
        if not self.token:
            return
        self.client.get("/api/v1/orders", headers=self.headers, name="/api/v1/orders [GET]")
    
    @task(8)
    def get_order(self):
        """Get a specific order."""
        if not self.token:
            return
        order_id = f"ORD-{random.randint(1, 100):06d}"
        self.client.get(f"/api/v1/orders/{order_id}", headers=self.headers, name="/api/v1/orders/{id} [GET]")
    
    @task(3)
    def check_health(self):
        """Check service health."""
        self.client.get("/health", name="/health")
    
    @task(4)
    def check_inventory(self):
        """Check product inventory."""
        product_id = f"PROD-{random.randint(1, 5):03d}"
        self.client.get(f"/api/v1/inventory/{product_id}", name="/api/v1/inventory/{id} [GET]")


# Run with:
# locust -f tests/performance/locustfile.py --host http://localhost:8000
#
# Headless:
# locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 60s --host http://localhost:8000
