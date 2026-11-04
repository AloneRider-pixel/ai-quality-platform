"""Unit tests for the e2e quarantine mechanism itself."""

from __future__ import annotations

from tests.e2e.quarantine import load_quarantine, quarantine_reason_for


def test_load_quarantine_parses_entries_and_comments(tmp_path):
    f = tmp_path / "quarantine.txt"
    f.write_text(
        "# comment\n"
        "\n"
        "tests/e2e/test_a.py::test_flaky - flaky under parallel load\n"
        "test_b.py::test_other\n"
    )
    entries = load_quarantine(f)
    assert entries == {
        "tests/e2e/test_a.py::test_flaky": "flaky under parallel load",
        "test_b.py::test_other": "quarantined",
    }


def test_load_quarantine_missing_file_is_empty(tmp_path):
    assert load_quarantine(tmp_path / "nope.txt") == {}


def test_reason_matches_by_substring():
    entries = {"test_a.py::test_flaky": "known flake"}
    assert quarantine_reason_for("tests/e2e/test_a.py::test_flaky", entries) == "known flake"
    assert quarantine_reason_for("tests/e2e/test_c.py::test_stable", entries) is None


def test_committed_quarantine_file_is_valid():
    # The real file must always parse, so a typo can never silently
    # disable the mechanism.
    load_quarantine()
