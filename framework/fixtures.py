"""
Shared PyTest fixtures for all tests.
"""
import os
import time
import pytest
import httpx
from framework.api_client import APIClient
from framework.data_factories import OrderFactory, CustomerFactory, ProductFactory, UserAuthFactory


BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def api_client():
    """Session-scoped API client."""
    client = APIClient(base_url=BASE_URL)
    yield client
    client.close()


@pytest.fixture
def fresh_client():
    """Function-scoped API client for isolated tests."""
    client = APIClient(base_url=BASE_URL)
    yield client
    client.close()


@pytest.fixture
def auth_token(api_client):
    """Get a valid auth token for authenticated requests."""
    # Register a test user
    creds = UserAuthFactory.create_credentials()
    api_client.post("/api/v1/auth/register", json={
        "email": creds["email"],
        "password": creds["password"],
        "full_name": "Test User",
    })
    
    # Login
    response = api_client.post("/api/v1/auth/login", json={
        "email": creds["email"],
        "password": creds["password"],
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
def authenticated_client(api_client, auth_token):
    """API client with authentication."""
    if auth_token:
        api_client.set_auth_token(auth_token)
    return api_client


@pytest.fixture
def sample_order():
    """Generate a sample order."""
    return OrderFactory.create()


@pytest.fixture
def sample_orders():
    """Generate a batch of sample orders."""
    return OrderFactory.create_batch(10)


@pytest.fixture
def sample_customer():
    """Generate a sample customer."""
    return CustomerFactory.create()


@pytest.fixture
def sample_product():
    """Generate a sample product."""
    return ProductFactory.create()


@pytest.fixture
def sample_products():
    """Generate a batch of sample products."""
    return ProductFactory.create_batch(5)


@pytest.fixture
def timestamp():
    """Current timestamp for unique naming."""
    return int(time.time() * 1000)


@pytest.fixture
def wait_for_service():
    """Wait for a service to become available."""
    def _wait(url: str, timeout: int = 30):
        start = time.time()
        while time.time() - start < timeout:
            try:
                response = httpx.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(1)
        return False
    return _wait
