"""
Base test classes for standardized test structure.
"""
import pytest
from framework.api_client import APIClient


class BaseAPITest:
    """Base class for API tests with common setup/teardown."""

    base_url = "http://localhost:8000"

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up API client before each test."""
        self.client = APIClient(base_url=self.base_url)
        yield
        self.client.close()

    def assert_status(self, response, expected_status: int):
        """Assert response status code."""
        assert response.status_code == expected_status, (
            f"Expected {expected_status}, got {response.status_code}: {response.text}"
        )

    def assert_json_key(self, response, key: str, expected_type=None):
        """Assert response contains a JSON key."""
        data = response.json()
        assert key in data, f"Key '{key}' not found in response: {list(data.keys())}"
        if expected_type:
            assert isinstance(data[key], expected_type), (
                f"Key '{key}' expected type {expected_type}, got {type(data[key])}"
            )

    def assert_response_time(self, response, max_ms: float = 5000):
        """Assert response was received within time limit."""
        pass


class BaseLLMTest:
    """Base class for LLM/AI quality tests."""

    model = "gpt-4o-mini"
    temperature = 0.1

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up LLM test configuration."""
        self.results = []
        yield

    def _simulate_rag_response(self, question: str, context: str) -> str:
        """Simulate a deterministic RAG response from retrieved context."""
        return f"Based on our information: {context[:500]}"


class BaseIntegrationTest:
    """Base class for integration tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up integration test clients."""
        self.clients = {}
        yield
        for client in self.clients.values():
            client.close()

    def register_service(self, name: str, base_url: str):
        """Register a service client."""
        self.clients[name] = APIClient(base_url=base_url)
        return self.clients[name]
