"""Planner flows for Learning Path Lab, against a locally generated starter
dataset (fixed seed). The lab is synthetic and loopback-only by design."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from .pages.learning_path_lab import LearningPathLabPage
from .visual import assert_matches_snapshot

pytestmark = pytest.mark.e2e


def test_planner_loads_with_seeded_employees(page, lpl_url):
    lab = LearningPathLabPage(page, lpl_url)
    lab.load()
    expect(lab.employee.locator("option")).not_to_have_count(0)
    expect(page.locator("#stats")).not_to_be_empty()
    # Visual regression guard for the planner header and form.
    assert_matches_snapshot("lpl-planner.png", page.screenshot())


def test_search_filters_employee_options(page, lpl_url):
    lab = LearningPathLabPage(page, lpl_url)
    lab.load()
    lab.search_for("EMP-000001")
    expect(lab.employee.locator("option").first).to_contain_text("EMP-000001")


def test_build_plan_renders_gap_table_and_cost(page, lpl_url):
    lab = LearningPathLabPage(page, lpl_url)
    lab.load()
    lab.build_plan()
    lab.expect_plan_rendered()
    expect(lab.result).to_contain_text("Department budget available")


def test_invalid_hours_show_error_banner(page, lpl_url):
    lab = LearningPathLabPage(page, lpl_url)
    lab.load()
    lab.hours.fill("0")
    lab.build_plan()
    expect(lab.error).not_to_be_empty(timeout=15_000)
