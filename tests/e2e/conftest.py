"""Fixtures for the browser E2E suite.

Every test runs against locally started instances of the owner's own apps
with deterministic seed data. No test in this directory talks to a live or
shared system; the optional read-only live smoke is under tests/e2e/live/
and only runs when E2E_LIVE=1 is set (CI: the opt-in scheduled workflow).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from . import targets
from .quarantine import load_quarantine, quarantine_reason_for

ARTIFACTS_DIR = Path(os.environ.get("E2E_ARTIFACTS_DIR", "reports/e2e-artifacts"))
WORK_DIR = Path(os.environ.get("E2E_WORK_DIR", ".e2e-work"))


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: browser end-to-end tests against locally started apps")
    config.addinivalue_line("markers", "live: read-only smoke against the public demos (opt-in only)")


def pytest_collection_modifyitems(items):
    entries = load_quarantine()
    for item in items:
        reason = quarantine_reason_for(item.nodeid, entries)
        if reason is not None:
            item.add_marker(pytest.mark.xfail(reason=f"quarantined: {reason}", strict=False))
        if "live" in item.keywords and os.environ.get("E2E_LIVE") != "1":
            item.add_marker(pytest.mark.skip(reason="live smoke is opt-in (E2E_LIVE=1); read-only checks only"))


@pytest.fixture(scope="session")
def e2e_work_dir(tmp_path_factory):
    path = Path(os.environ.get("E2E_WORK_DIR", tmp_path_factory.mktemp("e2e-work")))
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture(scope="session")
def e2e_artifacts_dir():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    return ARTIFACTS_DIR


@pytest.fixture(scope="session")
def fraud_url(e2e_work_dir, e2e_artifacts_dir):
    server, url = targets.start_fraud(targets.load_specs()["fraud"], e2e_work_dir, e2e_artifacts_dir)
    yield url
    server.stop()


@pytest.fixture(scope="session")
def lpl_url(e2e_work_dir, e2e_artifacts_dir):
    server, url = targets.start_lpl(targets.load_specs()["lpl"], e2e_work_dir, e2e_artifacts_dir)
    yield url
    server.stop()


@pytest.fixture(scope="session")
def stocksense_url(e2e_work_dir, e2e_artifacts_dir):
    servers, url = targets.start_stocksense(targets.load_specs()["stocksense"], e2e_work_dir, e2e_artifacts_dir)
    yield url
    for server in servers:
        server.stop()
