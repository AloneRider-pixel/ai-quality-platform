from portfolio_hardening.eval_gate import MetricResult, evaluate_gate


def test_metrics_can_pass_with_weighted_score() -> None:
    result = evaluate_gate(
        [
            MetricResult("groundedness", 0.96, 0.90, weight=2),
            MetricResult("toxicity", 0.99, 0.95, weight=1),
        ]
    )
    assert result.passed is True
    assert result.failures == ()
    assert result.score >= 0.8


def test_hard_failure_blocks_gate() -> None:
    result = evaluate_gate(
        [MetricResult("groundedness", 0.96, 0.90), MetricResult("safety", 0.4, 0.9, hard_fail=True)]
    )
    assert result.passed is False
    assert result.failures == ("safety",)


def test_empty_suite_fails_closed() -> None:
    result = evaluate_gate([])
    assert result.passed is False
    assert result.failures == ("no_metrics",)


def test_failure_order_is_deterministic() -> None:
    metrics = [
        MetricResult("zeta", 0.4, 0.9),
        MetricResult("alpha", 0.4, 0.9),
    ]
    assert evaluate_gate(metrics).failures == ("alpha", "zeta")
