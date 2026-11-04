"""Lifecycle management for the locally started E2E target apps.

The browser suite tests the owner's own applications (StockSense, the fraud
demo, Learning Path Lab) against *locally started* instances with deterministic
seed data. It never signs up, logs into, or writes to any live or shared
system; the optional read-only live smoke lives under tests/e2e/live/ and is
off unless explicitly enabled.

Target checkouts are pinned by SHA in targets.lock.json. CI checks them out
with actions/checkout; locally, run scripts/e2e_targets_setup.sh once.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCK_PATH = Path(__file__).with_name("targets.lock.json")


@dataclass(frozen=True)
class TargetSpec:
    name: str
    repo: str
    sha: str


def load_specs() -> dict[str, TargetSpec]:
    raw = json.loads(LOCK_PATH.read_text())
    return {name: TargetSpec(name=name, repo=v["repo"], sha=v["sha"]) for name, v in raw.items()}


def targets_root() -> Path:
    return Path(os.environ.get("E2E_TARGETS_DIR", REPO_ROOT / ".e2e-targets"))


def ensure_checkout(spec: TargetSpec) -> Path:
    """Return the pinned checkout for a target, cloning it if necessary."""
    path = targets_root() / spec.name
    if not (path / ".git").exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--quiet", f"https://github.com/{spec.repo}.git", str(path)],
            check=True,
        )
    head = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    if head != spec.sha:
        subprocess.run(["git", "-C", str(path), "fetch", "--quiet", "origin", spec.sha], check=True)
        subprocess.run(["git", "-C", str(path), "checkout", "--quiet", spec.sha], check=True)
    return path


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_http_ready(url: str, proc: "ManagedServer", timeout: float = 90.0) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if proc.process.poll() is not None:
            raise RuntimeError(
                f"{proc.name} exited with code {proc.process.returncode} while waiting for {url}. "
                f"See log: {proc.log_path}"
            )
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                if resp.status < 500:
                    return
        except urllib.error.HTTPError as exc:
            if exc.code < 500:  # server is answering, route may differ
                return
            last_error = exc
        except Exception as exc:  # connection refused while the server boots
            last_error = exc
        time.sleep(0.5)
    raise RuntimeError(f"{proc.name} did not become ready at {url} within {timeout}s ({last_error}). Log: {proc.log_path}")


class ManagedServer:
    """A target-app subprocess with its log captured for CI artifacts."""

    def __init__(self, name: str, args: list[str], *, cwd: Path, env: dict[str, str], log_dir: Path):
        self.name = name
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = log_dir / f"{name}.log"
        self._log = open(self.log_path, "wb")
        self.process = subprocess.Popen(
            args,
            cwd=str(cwd),
            env=env,
            stdout=self._log,
            stderr=subprocess.STDOUT,
        )

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=10)
        self._log.close()


def python_env(extra: dict[str, str]) -> dict[str, str]:
    env = os.environ.copy()
    env.update(extra)
    env["PYTHONUNBUFFERED"] = "1"
    return env


def start_fraud(spec: TargetSpec, work_dir: Path, log_dir: Path) -> tuple[ManagedServer, str]:
    """Train the deterministic synthetic model (if needed) and serve the demo."""
    checkout = ensure_checkout(spec)
    artifacts = work_dir / "fraud-artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    if not (artifacts / "model.onnx").exists():
        subprocess.run(
            [sys.executable, "-m", "fraud_engine.train", "--out", str(artifacts)],
            cwd=str(checkout),
            env=python_env({}),
            check=True,
            capture_output=True,
        )
    port = free_port()
    server = ManagedServer(
        "fraud-demo",
        [sys.executable, "-m", "uvicorn", "fraud_engine.serve:app_factory", "--factory",
         "--host", "127.0.0.1", "--port", str(port)],
        cwd=checkout,
        env=python_env({"ARTIFACT_DIR": str(artifacts), "AUDIT_DB": str(work_dir / "fraud-audit.db")}),
        log_dir=log_dir,
    )
    url = f"http://127.0.0.1:{port}"
    wait_http_ready(f"{url}/health", server)
    return server, url


def start_lpl(spec: TargetSpec, work_dir: Path, log_dir: Path) -> tuple[ManagedServer, str]:
    """Generate the deterministic starter dataset and serve the planner UI."""
    checkout = ensure_checkout(spec)
    db = work_dir / "lpl-lab.sqlite"
    if not db.exists():
        subprocess.run(
            [sys.executable, "-m", "learninglab", "--db", str(db), "generate", "--scale", "starter"],
            cwd=str(checkout),
            check=True,
            capture_output=True,
        )
    port = free_port()
    server = ManagedServer(
        "learning-path-lab",
        [sys.executable, "-m", "learninglab", "--db", str(db), "serve", "--port", str(port)],
        cwd=checkout,
        env=python_env({}),
        log_dir=log_dir,
    )
    url = f"http://127.0.0.1:{port}"
    wait_http_ready(f"{url}/api/summary", server)
    return server, url


def start_stocksense(spec: TargetSpec, work_dir: Path, log_dir: Path) -> tuple[list[ManagedServer], str]:
    """Start the StockSense backend (SQLite + CSV provider, seeded demo mode)
    and the built frontend via `vite preview`. Returns the frontend URL."""
    checkout = ensure_checkout(spec)
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm is required for the StockSense frontend build")

    backend_port = free_port()
    frontend_port = free_port()
    db = work_dir / "stocksense.db"
    backend_env = python_env({
        "ENVIRONMENT": "development",
        "DEMO_MODE": "true",
        "MARKET_DATA_PROVIDER": "csv",
        "DATABASE_URL": f"sqlite:///{db}",
        "JWT_SECRET": "e2e-local-only-secret",
        "CORS_ORIGINS": f"http://127.0.0.1:{frontend_port}",
        "ALLOWED_HOSTS": "*",
        "LOG_FORMAT": "text",
    })
    backend = ManagedServer(
        "stocksense-backend",
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(backend_port)],
        cwd=checkout,
        env=backend_env,
        log_dir=log_dir,
    )
    wait_http_ready(f"http://127.0.0.1:{backend_port}/api/v1/health", backend, timeout=180.0)

    frontend = checkout / "frontend"
    if not (frontend / "node_modules").exists():
        subprocess.run([npm, "ci", "--no-audit", "--no-fund"], cwd=str(frontend), check=True)
    build_env = os.environ.copy()
    build_env["VITE_DEMO"] = "true"
    build_env["VITE_API_BASE_URL"] = f"http://127.0.0.1:{backend_port}/api/v1"
    subprocess.run([npm, "run", "build"], cwd=str(frontend), env=build_env, check=True)
    preview = ManagedServer(
        "stocksense-frontend",
        [npm, "run", "preview", "--", "--host", "127.0.0.1", "--port", str(frontend_port), "--strictPort"],
        cwd=frontend,
        env=python_env({}),
        log_dir=log_dir,
    )
    url = f"http://127.0.0.1:{frontend_port}"
    wait_http_ready(url, preview)
    return [backend, preview], url
