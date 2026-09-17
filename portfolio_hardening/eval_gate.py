from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricResult:
    name: str
    value: float
    threshold: float
    weight: float = 1.0
    hard_fail: bool = False

    @property
    def passed(self) -> bool:
        return self.value >= self.threshold


@dataclass(frozen=True)
class QualityGate:
    passed: bool
    score: float
    failures: tuple[str, ...]


def evaluate_gate(metrics: list[MetricResult], minimum_score: float = 0.8) -> QualityGate:
    if not metrics:
        return QualityGate(False, 0.0, ("no_metrics",))
    total_weight = sum(max(item.weight, 0.0) for item in metrics)
    if total_weight == 0:
        return QualityGate(False, 0.0, ("invalid_weights",))

    normalized = []
    failures: list[str] = []
    for item in metrics:
        ratio = 1.0 if item.passed else max(0.0, item.value / item.threshold)
        normalized.append(ratio * item.weight)
        if item.hard_fail and not item.passed:
            failures.append(item.name)
        elif not item.passed:
            failures.append(item.name)
    score = sum(normalized) / total_weight
    return QualityGate(
        passed=score >= minimum_score and not any(
            item.hard_fail and not item.passed for item in metrics
        ),
        score=round(score, 4),
        failures=tuple(sorted(failures)),
    )
