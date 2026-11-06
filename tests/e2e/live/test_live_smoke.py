"""Optional READ-ONLY smoke checks against the public demo deployments.

Off by default: these only run when E2E_LIVE=1 is set, which in CI happens
only in the separate opt-in scheduled workflow after the owner approves
watching the live demos. They perform GETs and page loads only - no logins,
no forms, no writes - and tolerate free-tier cold starts with long timeouts
that are reported, not hidden.
"""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e, pytest.mark.live]

FRAUD_DEMO = "https://fraud-detection-engine-6n53.onrender.com"
STOCKSENSE_DEMO = "https://stocksense-ai-demo.onrender.com"

COLD_START_BUDGET_S = 120.0


def _load_with_cold_start(page, url: str) -> float:
    start = time.monotonic()
    page.goto(url, wait_until="domcontentloaded", timeout=int(COLD_START_BUDGET_S * 1000))
    return time.monotonic() - start


def test_fraud_demo_public_page_loads(page):
    elapsed = _load_with_cold_start(page, FRAUD_DEMO)
    expect(page.get_by_role("heading", name="Fraud Detection Engine")).to_be_visible(timeout=60_000)
    print(f"fraud demo loaded in {elapsed:.1f}s (cold start included)")


def test_stocksense_demo_public_page_loads(page):
    elapsed = _load_with_cold_start(page, STOCKSENSE_DEMO)
    expect(page).to_have_title("StockSense AI — NSE predictions, scored against real closes", timeout=60_000)
    print(f"stocksense demo loaded in {elapsed:.1f}s (cold start included)")
