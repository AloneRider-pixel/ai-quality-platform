"""Visual snapshot comparison for the browser suite.

Baselines live under tests/e2e/snapshots/. A missing baseline fails the test
and writes the actual screenshot next to it, unless E2E_UPDATE_SNAPSHOTS=1 is
set, which writes the baseline and passes (use it to (re)generate baselines
deliberately, then review and commit the PNGs).

Comparison: fraction of pixels where any RGB channel differs by more than a
fixed per-channel threshold must stay within max_diff_ratio. Rendering varies
slightly across machines and browser builds, so keep regions stable and the
ratio honest rather than exact.
"""

from __future__ import annotations

import io
import os
from pathlib import Path

from PIL import Image

SNAPSHOTS_DIR = Path(__file__).with_name("snapshots")
CHANNEL_THRESHOLD = 24


class SnapshotMismatch(AssertionError):
    pass


def _diff_ratio(baseline: Image.Image, actual: Image.Image) -> float:
    if baseline.size != actual.size:
        return 1.0
    b = baseline.convert("RGB")
    a = actual.convert("RGB")
    bp, ap = b.tobytes(), a.tobytes()
    total = b.size[0] * b.size[1]
    diff = 0
    for i in range(0, len(bp), 3):
        if (abs(bp[i] - ap[i]) > CHANNEL_THRESHOLD
                or abs(bp[i + 1] - ap[i + 1]) > CHANNEL_THRESHOLD
                or abs(bp[i + 2] - ap[i + 2]) > CHANNEL_THRESHOLD):
            diff += 1
    return diff / total


def assert_matches_snapshot(name: str, png_bytes: bytes, *, max_diff_ratio: float = 0.05) -> None:
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    baseline_path = SNAPSHOTS_DIR / name
    actual = Image.open(io.BytesIO(png_bytes))
    if not baseline_path.exists():
        if os.environ.get("E2E_UPDATE_SNAPSHOTS") == "1":
            baseline_path.write_bytes(png_bytes)
            return
        missing_path = baseline_path.with_suffix(".actual.png")
        missing_path.write_bytes(png_bytes)
        raise SnapshotMismatch(
            f"No baseline snapshot {baseline_path}. Actual written to {missing_path}. "
            "Regenerate deliberately with E2E_UPDATE_SNAPSHOTS=1, review the PNG, and commit it."
        )
    baseline = Image.open(baseline_path)
    ratio = _diff_ratio(baseline, actual)
    if ratio > max_diff_ratio:
        actual_path = baseline_path.with_suffix(".actual.png")
        actual_path.write_bytes(png_bytes)
        raise SnapshotMismatch(
            f"Snapshot {name} differs from baseline: {ratio:.3%} of pixels "
            f"(allowed {max_diff_ratio:.3%}). Actual written to {actual_path}."
        )
