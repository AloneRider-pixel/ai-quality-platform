"""Page object for the fraud-detection-engine demo page served at /."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from .base import BasePage


class FraudDemoPage(BasePage):
    HEADING = "Fraud Detection Engine"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.form = page.locator("#f")
        self.out = page.locator("#out")

    def load(self) -> None:
        self.goto("/")
        expect(self.page).to_have_title(re.compile("Fraud Detection Engine"))
        expect(self.page.get_by_role("heading", name=self.HEADING)).to_be_visible()

    def fill_sample(self, kind: str) -> None:
        label = {"drain": "Sample: account drain transfer", "small": "Sample: small payment"}[kind]
        self.page.get_by_role("button", name=label).click()

    def submit(self) -> None:
        self.form.get_by_role("button", name="Score transaction").click()

    def result_text(self) -> str:
        return self.out.inner_text()

    def result_action_class(self) -> str:
        return self.out.get_attribute("class") or ""
