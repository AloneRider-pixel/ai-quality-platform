"""
Custom assertion helpers for API and LLM testing.
"""
import re
from typing import Any, Dict, List, Optional


def assert_status_code(response, expected: int, message: str = None):
    """Assert HTTP status code with descriptive error."""
    msg = message or f"Expected status {expected}, got {response.status_code}"
    assert response.status_code == expected, f"{msg}\nBody: {response.text[:500]}"


def assert_response_time(response_time_ms: float, max_ms: float):
    """Assert response time is within acceptable bounds."""
    assert response_time_ms <= max_ms, (
        f"Response time {response_time_ms:.0f}ms exceeds limit of {max_ms:.0f}ms"
    )


def assert_json_schema(response, schema: Dict):
    """Assert response matches expected JSON schema (basic validation)."""
    data = response.json()
    
    for key, expected_type in schema.items():
        assert key in data, f"Missing key: '{key}' in response"
        if expected_type == "string":
            assert isinstance(data[key], str), f"Key '{key}' should be string"
        elif expected_type == "integer":
            assert isinstance(data[key], int), f"Key '{key}' should be integer"
        elif expected_type == "number":
            assert isinstance(data[key], (int, float)), f"Key '{key}' should be number"
        elif expected_type == "boolean":
            assert isinstance(data[key], bool), f"Key '{key}' should be boolean"
        elif expected_type == "array":
            assert isinstance(data[key], list), f"Key '{key}' should be array"
        elif expected_type == "object":
            assert isinstance(data[key], dict), f"Key '{key}' should be object"


def assert_pagination(response, page: int, page_size: int, total: int):
    """Assert pagination response structure."""
    data = response.json()
    assert "items" in data or "data" in data, "Missing items/data in paginated response"
    
    items = data.get("items", data.get("data", []))
    assert len(items) <= page_size, f"Got {len(items)} items, expected <= {page_size}"
    
    if "total" in data:
        assert data["total"] == total, f"Expected total={total}, got {data['total']}"
    
    if "page" in data:
        assert data["page"] == page, f"Expected page={page}, got {data['page']}"


def assert_no_sql_injection(response):
    """Assert response doesn't leak SQL error details."""
    text = response.text.lower()
    sql_patterns = [
        "sql syntax", "mysql", "postgres", "sqlite", "oracle",
        "syntax error", "undefined table", "column does not exist",
        "unclosed quotation", "sqlstate", "pg_query",
    ]
    for pattern in sql_patterns:
        assert pattern not in text, f"Possible SQL injection leak: '{pattern}' found in response"


def assert_no_stack_trace(response):
    """Assert response doesn't contain stack traces."""
    text = response.text
    stack_patterns = [
        r"Traceback \(most recent call last\)",
        r"File \".*\", line \d+",
        r"at .* \(.*:\d+:\d+\)",
        r"Stack Trace:",
    ]
    for pattern in stack_patterns:
        assert not re.search(pattern, text), f"Stack trace leaked in response: {pattern}"


def assert_contains_all(response_text: str, expected_strings: List[str]):
    """Assert response contains all expected strings."""
    for s in expected_strings:
        assert s in response_text, f"Expected string '{s}' not found in response"


def assert_unique_values(items: List[Dict], key: str):
    """Assert all values for a key are unique."""
    values = [item[key] for item in items]
    assert len(values) == len(set(values)), f"Duplicate values found for key '{key}'"


def assert_sorted(items: List[Dict], key: str, ascending: bool = True):
    """Assert items are sorted by key."""
    values = [item[key] for item in items]
    if ascending:
        assert values == sorted(values), f"Items not sorted ascending by '{key}'"
    else:
        assert values == sorted(values, reverse=True), f"Items not sorted descending by '{key}'"
