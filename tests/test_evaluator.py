from unittest.mock import patch
from terminal_dreamgym.evaluator import compute_stats, detect_regressions, evaluate, summarize_successes


def test_success_rate_calculations():
    assert summarize_successes(3, 4) == {"successes": 3, "total": 4, "rate": 0.75}


def test_regression_detection():
    baseline = [
        {"task_id": "a", "split": "adversarial", "success": True},
        {"task_id": "b", "split": "adversarial", "success": False},
        {"task_id": "c", "split": "heldout", "success": True},
    ]
    candidate = [
        {"task_id": "a", "split": "adversarial", "success": False},
        {"task_id": "b", "split": "adversarial", "success": True},
        {"task_id": "c", "split": "heldout", "success": False},
    ]
    assert detect_regressions(baseline, candidate) == ["a", "c"]
    assert detect_regressions(baseline, candidate, split="adversarial") == ["a"]


def test_compute_stats_ci():
    stats = compute_stats([0.1, 0.2, 0.15])
    assert stats["mean"] == 0.15
    assert stats["stdev"] > 0
    assert stats["ci95"] > 0


@patch("terminal_dreamgym.evaluator.run_strategy")
@patch("terminal_dreamgym.evaluator.score_practice_for_skill")
def test_evaluate_sweep_logic(mock_practice, mock_run_strategy):
    mock_run_strategy.side_effect = lambda strategy, mode, active_skills=None, seed=None: {
        "strategy": strategy,
        "mode": mode,
        "seed": seed,
        "summary": {
            "train": {"rate": 0.2},
            "heldout": {"rate": 0.3},
            "adversarial": {"rate": 0.1},
        },
        "traces": []
    }
    mock_practice.return_value = 0.8

    payload = evaluate(mode="qwen", models=["qwen"], seeds=[42, 43])

    assert payload["mode"] == "qwen"
    assert payload["models"] == ["qwen"]
    assert payload["seeds"] == [42, 43]

    aggregated = payload["aggregated"]
    assert "qwen" in aggregated
    qwen_stats = aggregated["qwen"]

    assert qwen_stats["baseline_scores"]["train"]["mean"] == 0.2
    assert qwen_stats["baseline_scores"]["train"]["ci95"] == 0

    for eval_stat in qwen_stats["evaluations"]:
        assert "naive_false_promotion_rate" in eval_stat
        assert "gated_false_promotion_rate" in eval_stat
        assert "wrongly_rejected_rate" in eval_stat

