"""StockSense dashboard and symbol flows, against a locally started stack:
backend on SQLite with the CSV market-data provider (checked-in sample data,
seeded demo user) and the frontend built against that backend. The demo
sign-in uses the app's own seeded reviewer account on the local instance;
no live service, real account, or shared system is touched."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from .pages.stocksense import StockSensePage

pytestmark = pytest.mark.e2e


def test_landing_page_loads(page, stocksense_url):
    app = StockSensePage(page, stocksense_url)
    app.load_landing()
    expect(page.get_by_role("button", name="Sign in").first).to_be_visible()


def test_demo_sign_in_opens_dashboard(page, stocksense_url):
    app = StockSensePage(page, stocksense_url)
    app.load_landing()
    app.open_demo_dashboard()
    expect(page.get_by_role("navigation")).to_contain_text("Overview")


def test_dashboard_lists_seeded_symbols(page, stocksense_url):
    app = StockSensePage(page, stocksense_url)
    app.load_landing()
    app.open_demo_dashboard()
    # The deterministic CSV seed data leads with GOLD.
    expect(page.get_by_role("button", name="GOLD", exact=True).first).to_be_visible(timeout=30_000)
    expect(page.locator("main.dashboard")).to_contain_text("Good", timeout=30_000)


def test_symbol_overview_renders(page, stocksense_url):
    app = StockSensePage(page, stocksense_url)
    app.load_landing()
    app.open_demo_dashboard()
    app.select_symbol("GOLD")
    app.expect_symbol_overview("GOLD")
