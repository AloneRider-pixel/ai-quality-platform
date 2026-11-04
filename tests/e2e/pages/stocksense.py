"""Page object for the StockSense frontend (local backend, seeded demo mode)."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base import BasePage


class StockSensePage(BasePage):
    def load_landing(self) -> None:
        self.goto("/")
        expect(self.page).to_have_title("StockSense AI — NSE predictions, scored against real closes")

    def open_demo_dashboard(self) -> None:
        self.page.get_by_role("button", name="Live dashboard").first.click()
        # Signed in: the app shell renders with navigation and the symbol search.
        expect(self.page.get_by_role("button", name="Sign out")).to_be_visible(timeout=30_000)
        expect(self.page.get_by_placeholder("Search symbol")).to_be_visible(timeout=30_000)

    def select_symbol(self, symbol: str) -> None:
        self.page.get_by_role("button", name=symbol, exact=True).first.click()

    def expect_symbol_overview(self, symbol: str) -> None:
        expect(self.page.get_by_placeholder("Search symbol")).to_be_visible()
        expect(self.page.locator("main.dashboard")).to_contain_text(symbol, timeout=30_000)
