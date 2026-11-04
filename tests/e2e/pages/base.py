"""Shared page-object base: carries the Playwright page and the base URL."""

from __future__ import annotations

from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def goto(self, path: str = "/") -> None:
        self.page.goto(self.base_url + path, wait_until="domcontentloaded")
