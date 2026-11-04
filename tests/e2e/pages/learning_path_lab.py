"""Page object for the Learning Path Lab planner UI served at /."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from .base import BasePage


class LearningPathLabPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.search = page.locator("#search")
        self.employee = page.locator("#employee")
        self.hours = page.locator("#hours")
        self.plan_button = page.locator("#plan")
        self.result = page.locator("#result")
        self.error = page.locator("#error")

    def load(self) -> None:
        self.goto("/")
        expect(self.page.get_by_role("heading", name="Make the next skill attainable.")).to_be_visible()
        # Wait for the initial dataset load: the employee select gets options.
        expect(self.employee.locator("option").first).to_be_attached(timeout=15_000)

    def search_for(self, term: str) -> None:
        self.search.fill(term)
        # The page reloads employees on input; wait for a matching option.
        expect(self.employee.locator("option", has_text=term).first).to_be_attached(timeout=15_000)

    def build_plan(self) -> None:
        self.plan_button.click()

    def expect_plan_rendered(self) -> None:
        expect(self.result.get_by_role("heading", level=3, name="Assessed skill gaps")).to_be_visible(timeout=15_000)
        expect(self.result).to_contain_text("INR")
