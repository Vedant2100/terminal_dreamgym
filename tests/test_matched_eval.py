from __future__ import annotations

import shutil

import terminal_dreamgym.gemini_agent as agent_mod
from terminal_dreamgym.matched_eval import analyze, base_task, load_records, paired_difference, render_markdown, run_matched


class NoEditClient:
    name = "stub"
    model = "stub-model"
    available = True
    last_usage = {"prompt_tokens": 100, "completion_tokens": 5, "finish_reason": "stop"}

    def generate_text(self, prompt, seed=None):
        return "I refuse to output file blocks"


def test_base_task():
    assert base_task("python_email_whitespace_v3") == "python_email_whitespace"
    assert base_task("no_variant") == "no_variant"


def test_run_matched_writes_one_record_per_job_and_resumes(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_mod, "make_client", lambda provider: NoEditClient())
    out = tmp_path / "res.jsonl"
    tasks = ["python_email_whitespace_v1", "python_price_currency_spacing_v1"]
    n = run_matched(out, conditions=["no_skill", "placebo"], seeds=[1], concurrency=2, task_ids=tasks)
    records = load_records(out)
    assert n == 4 and len(records) == 4
    for r in records:
        shutil.rmtree(r["run_dir"], ignore_errors=True)
    by_task = {(r["condition"], r["task_id"]): r for r in records}
    free = by_task[("no_skill", "python_price_currency_spacing_v1")]
    assert free["solved_before_any_edit"] and free["success"] and free["model_calls"] == 0
    hard = by_task[("placebo", "python_email_whitespace_v1")]
    assert not hard["success"] and hard["model_calls"] == 3 and hard["parsed_edits"] == 0
    # Second call finds everything done.
    assert run_matched(out, conditions=["no_skill", "placebo"], seeds=[1], concurrency=2, task_ids=tasks) == 0


def _rec(condition, task_id, success, seed=1, free=False, split="train"):
    return {
        "condition": condition, "seed": seed, "task_id": task_id, "base_task": base_task(task_id),
        "split": split, "family": "f", "success": success, "score_passed": success, "regressions": [],
        "first_attempt_success": success, "first_attempt_score_passed": success, "solved_before_any_edit": free,
        "model_calls": 1, "parsed_edits": 1, "prompt_tokens": 10, "completion_tokens": 1, "max_prompt_tokens": 10,
        "length_truncated": False, "infra_error": False, "notes": [], "model": "m", "temperature": 0.7,
        "max_steps": 3, "duration_seconds": 1.0, "diff": "", "run_dir": "",
    }


def test_paired_difference_uses_base_tasks_as_units():
    records = []
    for v in range(1, 6):  # five variants of one base task where A always wins
        records += [_rec("a", f"t1_v{v}", True), _rec("b", f"t1_v{v}", False)]
    records += [_rec("a", "t2_v1", False), _rec("b", "t2_v1", False)]
    d = paired_difference(records, "a", "b", reps=200)
    assert d["n_base_tasks"] == 2  # not 6 runs
    assert d["diff"] == 0.5
    assert d["base_tasks_better"] == 1 and d["base_tasks_tied"] == 1


def test_analyze_excludes_tasks_solved_before_any_edit():
    records = [
        _rec("no_skill", "easy_v1", True, free=True), _rec("handwritten_skills", "easy_v1", True, free=True),
        _rec("no_skill", "hard_v1", False), _rec("handwritten_skills", "hard_v1", True),
    ]
    result = analyze(records)
    assert result["excluded_base_tasks_solved_before_edit"] == ["easy"]
    primary = result["comparisons"][0]
    assert primary["primary"] and primary["overall"]["n_base_tasks"] == 1
    assert result["per_condition"]["no_skill"]["success"] == 0.0
    assert "Matched-condition evaluation" in render_markdown(result)


def test_load_records_skips_partial_last_line(tmp_path):
    path = tmp_path / "r.jsonl"
    path.write_text('{"a": 1}\n{"a": 2', encoding="utf-8")
    assert load_records(path) == [{"a": 1}]


def test_harness_exception_becomes_infra_record(tmp_path, monkeypatch):
    def boom(provider):
        raise RuntimeError("server gone")

    monkeypatch.setattr(agent_mod, "make_client", boom)
    out = tmp_path / "res.jsonl"
    run_matched(out, conditions=["no_skill"], seeds=[1], concurrency=1, task_ids=["python_email_whitespace_v1"])
    (record,) = load_records(out)
    assert record["infra_error"] and "server gone" in record["notes"][0]
    assert analyze([record])["infra_error_records"] == 1
