"""Unit tests for framework-level assertions."""
from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

import pytest

from framework.base_test import BaseAPITest


def test_assert_response_time_accepts_response_within_budget() -> None:
    test = BaseAPITest()
    response = SimpleNamespace(elapsed=timedelta(milliseconds=120))
    test.assert_response_time(response, max_ms=150)


def test_assert_response_time_rejects_slow_response() -> None:
    test = BaseAPITest()
    response = SimpleNamespace(elapsed=timedelta(milliseconds=220))
    with pytest.raises(AssertionError, match="220"):
        test.assert_response_time(response, max_ms=150)
