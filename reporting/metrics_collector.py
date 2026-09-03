"""
Metrics Collector - Collects test metrics and exposes them for Grafana.
Tracks test pass rates, latency, coverage, and quality scores.
"""
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class TestMetrics:
    """Tracks metrics for a test run."""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration_seconds: float = 0
    avg_latency_ms: float = 0
    p95_latency_ms: float = 0
    api_tests_passed: int = 0
    llm_tests_passed: int = 0
    integration_tests_passed: int = 0
    contract_tests_passed: int = 0
    hallucination_rate: float = 0
    faithfulness_score: float = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @property
    def pass_rate(self) -> float:
        if self.total_tests == 0:
            return 0
        return self.passed / self.total_tests
    
    @property
    def quality_score(self) -> float:
        """Composite quality score (0-100)."""
        return (
            self.pass_rate * 60 +
            (1 - self.hallucination_rate) * 20 +
            self.faithfulness_score * 20
        )


class MetricsCollector:
    """Collects and stores test metrics across runs."""

    def __init__(self, storage_path: str = "reports/metrics_history.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._history = self._load_history()
        self._current = TestMetrics()

    def record_test_result(self, outcome: str, category: str = "", latency_ms: float = 0):
        """Record a single test result."""
        self._current.total_tests += 1
        
        if outcome == "passed":
            self._current.passed += 1
        elif outcome == "failed":
            self._current.failed += 1
        elif outcome == "skipped":
            self._current.skipped += 1
        elif outcome == "error":
            self._current.errors += 1
        
        # Category tracking
        if outcome == "passed":
            if category == "api":
                self._current.api_tests_passed += 1
            elif category == "llm":
                self._current.llm_tests_passed += 1
            elif category == "integration":
                self._current.integration_tests_passed += 1
            elif category == "contract":
                self._current.contract_tests_passed += 1

    def set_llm_metrics(self, hallucination_rate: float, faithfulness_score: float):
        """Set LLM-specific quality metrics."""
        self._current.hallucination_rate = hallucination_rate
        self._current.faithfulness_score = faithfulness_score

    def finalize(self, duration_seconds: float = 0):
        """Finalize the current test run metrics."""
        self._current.duration_seconds = duration_seconds
        self._history.append(asdict(self._current))
        self._save_history()
        return self._current

    def get_trend(self, metric: str, last_n: int = 10) -> List[float]:
        """Get trend for a specific metric over recent runs."""
        values = [run.get(metric, 0) for run in self._history[-last_n:]]
        return values

    def get_latest(self) -> Dict:
        """Get latest metrics snapshot."""
        return asdict(self._current)

    def get_summary(self) -> Dict:
        """Get summary of all historical metrics."""
        if not self._history:
            return {"runs": 0}
        
        return {
            "total_runs": len(self._history),
            "avg_pass_rate": sum(r["pass_rate"] if "pass_rate" in r else (r.get("passed", 0) / max(r.get("total_tests", 1), 1)) for r in self._history) / len(self._history),
            "latest": self._history[-1] if self._history else {},
            "avg_duration": sum(r.get("duration_seconds", 0) for r in self._history) / len(self._history),
        }

    def _load_history(self) -> List[Dict]:
        if self.storage_path.exists():
            try:
                return json.loads(self.storage_path.read_text())
            except Exception:
                return []
        return []

    def _save_history(self):
        self.storage_path.write_text(json.dumps(self._history, indent=2))


# Singleton
metrics_collector = MetricsCollector()
