"""
HTTP API Client wrapper for testing.
Provides standardized request methods, response validation, and metrics collection.
"""
import time
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ResponseMetrics:
    """Captures metrics for each API response."""
    status_code: int = 0
    latency_ms: float = 0
    content_length: int = 0
    request_method: str = ""
    request_url: str = ""
    response_body: Any = None
    error: Optional[str] = None


@dataclass
class TestSession:
    """Tracks all requests made during a test session."""
    requests: list = field(default_factory=list)
    
    @property
    def total_requests(self) -> int:
        return len(self.requests)
    
    @property
    def avg_latency_ms(self) -> float:
        if not self.requests:
            return 0
        return sum(r.latency_ms for r in self.requests) / len(self.requests)
    
    @property
    def p95_latency_ms(self) -> float:
        if not self.requests:
            return 0
        latencies = sorted(r.latency_ms for r in self.requests)
        idx = int(len(latencies) * 0.95)
        return latencies[min(idx, len(latencies) - 1)]
    
    @property
    def error_rate(self) -> float:
        if not self.requests:
            return 0
        errors = sum(1 for r in self.requests if r.status_code >= 400)
        return errors / len(self.requests)


class APIClient:
    """
    HTTP client for API testing with:
    - Base URL configuration
    - Auth header injection
    - Request/response logging
    - Latency tracking
    - Response metrics collection
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._headers = headers or {}
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._headers,
            timeout=timeout,
        )
        self._session = TestSession()

    def set_auth_token(self, token: str):
        """Set Bearer token for authenticated requests."""
        self._client.headers["Authorization"] = f"Bearer {token}"

    def set_header(self, key: str, value: str):
        """Set a custom header."""
        self._client.headers[key] = value

    def _track(self, method: str, url: str, start: float, response=None, error=None):
        """Track request metrics."""
        metrics = ResponseMetrics(
            request_method=method,
            request_url=url,
            latency_ms=(time.time() - start) * 1000,
            status_code=response.status_code if response else 0,
            content_length=len(response.content) if response else 0,
            response_body=response.json() if response and response.headers.get("content-type", "").startswith("application/json") else None,
            error=str(error) if error else None,
        )
        self._session.requests.append(metrics)
        return metrics

    def get(self, path: str, params: Optional[Dict] = None, **kwargs) -> httpx.Response:
        """Make GET request."""
        start = time.time()
        try:
            response = self._client.get(path, params=params, **kwargs)
            self._track("GET", path, start, response=response)
            return response
        except Exception as e:
            self._track("GET", path, start, error=e)
            raise

    def post(self, path: str, json: Optional[Dict] = None, **kwargs) -> httpx.Response:
        """Make POST request."""
        start = time.time()
        try:
            response = self._client.post(path, json=json, **kwargs)
            self._track("POST", path, start, response=response)
            return response
        except Exception as e:
            self._track("POST", path, start, error=e)
            raise

    def put(self, path: str, json: Optional[Dict] = None, **kwargs) -> httpx.Response:
        """Make PUT request."""
        start = time.time()
        try:
            response = self._client.put(path, json=json, **kwargs)
            self._track("PUT", path, start, response=response)
            return response
        except Exception as e:
            self._track("PUT", path, start, error=e)
            raise

    def delete(self, path: str, **kwargs) -> httpx.Response:
        """Make DELETE request."""
        start = time.time()
        try:
            response = self._client.delete(path, **kwargs)
            self._track("DELETE", path, start, response=response)
            return response
        except Exception as e:
            self._track("DELETE", path, start, error=e)
            raise

    def patch(self, path: str, json: Optional[Dict] = None, **kwargs) -> httpx.Response:
        """Make PATCH request."""
        start = time.time()
        try:
            response = self._client.patch(path, json=json, **kwargs)
            self._track("PATCH", path, start, response=response)
            return response
        except Exception as e:
            self._track("PATCH", path, start, error=e)
            raise

    @property
    def session(self) -> TestSession:
        """Get session metrics."""
        return self._session

    def reset_session(self):
        """Reset session metrics."""
        self._session = TestSession()

    def close(self):
        """Close the HTTP client."""
        self._client.close()
