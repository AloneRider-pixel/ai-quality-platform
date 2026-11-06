#!/usr/bin/env bash
# Clone the pinned E2E target apps into .e2e-targets/ for local runs.
# CI checks the same SHAs out with actions/checkout instead.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import json, pathlib, subprocess, sys
lock = json.loads(pathlib.Path("tests/e2e/targets.lock.json").read_text())
root = pathlib.Path(".e2e-targets")
root.mkdir(exist_ok=True)
for name, spec in lock.items():
    path = root / name
    if not (path / ".git").exists():
        subprocess.run(["git", "clone", "--quiet", f"https://github.com/{spec['repo']}.git", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "fetch", "--quiet", "origin", spec["sha"]], check=True)
    subprocess.run(["git", "-C", str(path), "checkout", "--quiet", spec["sha"]], check=True)
    print(f"{name}: {spec['repo']}@{spec['sha'][:12]}")
PY
