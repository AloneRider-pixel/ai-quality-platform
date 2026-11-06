"""Core flows for the fraud-detection-engine demo, against a locally started
instance with a deterministic synthetic model. Read-only UI interaction:
scoring posts to the local instance's own audit log, never a shared system."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from .pages.fraud_demo import FraudDemoPage
from .visual import assert_matches_snapshot

pytestmark = pytest.mark.e2e


def test_demo_page_loads(page, fraud_url):
    demo = FraudDemoPage(page, fraud_url)
    demo.load()
    expect(demo.form).to_be_visible()
    expect(demo.out).to_contain_text("No result yet.")
    # Visual regression guard for the demo page structure.
    assert_matches_snapshot("fraud-demo-page.png", page.screenshot(full_page=True))


def test_sample_drain_transaction_scores(page, fraud_url):
    demo = FraudDemoPage(page, fraud_url)
    demo.load()
    demo.fill_sample("drain")
    demo.submit()
    expect(demo.out).to_contain_text("fraud_prob:", timeout=15_000)
    expect(demo.out).to_contain_text(re.compile(r"action: (ALLOW|BLOCK)"))
    expect(demo.out).to_contain_text("server latency:")
    # The result card is flagged with the decision class.
    expect(demo.out).to_have_class(re.compile(r"\b(ALLOW|BLOCK)\b"))


def test_small_payment_sample_scores(page, fraud_url):
    demo = FraudDemoPage(page, fraud_url)
    demo.load()
    demo.fill_sample("small")
    demo.submit()
    expect(demo.out).to_contain_text("fraud_prob:", timeout=15_000)
    expect(demo.out).to_have_class(re.compile(r"\b(ALLOW|BLOCK)\b"))


def test_form_fields_use_numeric_validation(page, fraud_url):
    demo = FraudDemoPage(page, fraud_url)
    demo.load()
    for field in ("step", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"):
        assert demo.form.locator(f'input[name="{field}"]').get_attribute("type") == "number", field


def test_error_banner_on_rejected_score(page, fraud_url):
    """The UI must surface a rejected scoring request instead of hanging."""
    demo = FraudDemoPage(page, fraud_url)
    demo.load()
    page.route("**/score", lambda route: route.fulfill(
        status=422,
        content_type="application/json",
        body='{"detail": [{"loc": ["body", "amount"], "msg": "Input should be a valid number"}]}',
    ))
    demo.fill_sample("drain")
    demo.submit()
    expect(demo.out).to_contain_text("Error:", timeout=15_000)
