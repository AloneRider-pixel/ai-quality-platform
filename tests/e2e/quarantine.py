"""Flaky-test quarantine for the browser suite.

Quarantined tests still run and still appear in the report, but a failure
becomes a non-blocking xfail so one flaky browser test cannot block the whole
gate. A test earns its way back by being removed from quarantine.txt after a
fix and a green run history - see tests/e2e/README.md.
"""

from __future__ import annotations

from pathlib import Path

QUARANTINE_PATH = Path(__file__).with_name("quarantine.txt")


def load_quarantine(path: Path = QUARANTINE_PATH) -> dict[str, str]:
    """Parse quarantine.txt into {nodeid_or_marker: reason}. Blank lines and
    '#' comments are ignored. Each entry is 'exact.py::node_id - reason' or
    a bare substring matched against the test node id."""
    entries: dict[str, str] = {}
    if not path.exists():
        return entries
    for lineno, raw in enumerate(path.read_text().splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if " - " in line:
            key, reason = line.split(" - ", 1)
        else:
            key, reason = line, "quarantined"
        key = key.strip()
        if not key:
            raise ValueError(f"{path}:{lineno}: empty quarantine key")
        entries[key] = reason.strip() or "quarantined"
    return entries


def quarantine_reason_for(nodeid: str, entries: dict[str, str]) -> str | None:
    for key, reason in entries.items():
        if key in nodeid:
            return reason
    return None
