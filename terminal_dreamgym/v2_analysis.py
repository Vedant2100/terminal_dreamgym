"""Calibration selection and analysis for benchmark v2 (docs/benchmark_v2_protocol.md)."""
from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from terminal_dreamgym.matched_eval import _per_base_task

CONDITION_ORDER = ["no_skill", "handwritten_skills", "strong_skill", "placebo", "model_skill", "symptom_patch"]


# -- stage 1 --------------------------------------------------------------------


def calibration_keep(records: list[dict[str, Any]], low: int = 1, high: int = 4, n_seeds: int = 5):
    """Tasks strictly solved in low..high of their n_seeds no_skill calibration runs.

    Returns (kept ids, {task_id: successes}). A task without exactly n_seeds
    non-infrastructure records is an error, not a silent drop.
    """
    runs = defaultdict(list)
    for r in records:
        if r["condition"] == "no_skill" and not r.get("infra_error"):
            runs[r["task_id"]].append(bool(r["success"]))
    incomplete = {t: len(v) for t, v in runs.items() if len(v) != n_seeds}
    if incomplete:
        raise ValueError(f"tasks without {n_seeds} calibration runs: {incomplete}")
    counts = {t: sum(v) for t, v in runs.items()}
    return sorted(t for t, c in counts.items() if low <= c <= high), counts


# -- stage 2 --------------------------------------------------------------------


def _quantiles(values: list[float], level: float) -> list[float]:
    values = sorted(values)
    tail = (1 - level) / 2
    return [round(values[int(tail * len(values))], 4), round(values[int((1 - tail) * len(values)) - 1], 4)]


def difference(records, a, b, metric="success", include=lambda r: True, level=0.95, reps=10000, seed=0):
    """Mean over tasks of (a - b) with a repo-cluster bootstrap CI and a task-level one."""
    pa = _per_base_task(records, a, metric, include)
    pb = _per_base_task(records, b, metric, include)
    keys = sorted(set(pa) & set(pb))
    if not keys:
        return None
    repo_of = {r["base_task"]: r["family"] for r in records}
    diffs = {k: pa[k] - pb[k] for k in keys}
    by_repo = defaultdict(list)
    for k in keys:
        by_repo[repo_of[k]].append(diffs[k])
    repos = sorted(by_repo)
    rng = random.Random(seed)
    cluster = []
    for _ in range(reps):
        sample = [d for repo in (rng.choice(repos) for _ in repos) for d in by_repo[repo]]
        cluster.append(mean(sample))
    rng = random.Random(seed)
    flat = list(diffs.values())
    task = [mean(rng.choice(flat) for _ in flat) for _ in range(reps)]
    return {
        "a": a, "b": b, "metric": metric, "level": level,
        "n_tasks": len(keys), "n_repos": len(repos),
        "mean_a": round(mean(pa[k] for k in keys), 4), "mean_b": round(mean(pb[k] for k in keys), 4),
        "diff": round(mean(flat), 4),
        "ci_repo_cluster": _quantiles(cluster, level),
        "ci_task": _quantiles(task, level),
        "tasks_better": sum(d > 0 for d in flat), "tasks_worse": sum(d < 0 for d in flat),
        "tasks_tied": sum(d == 0 for d in flat),
    }


def analyze_v2(records, tasks_file: Path, co_primary, secondary, primary_level=0.975) -> dict[str, Any]:
    meta = {t["id"]: t for t in json.loads(Path(tasks_file).read_text(encoding="utf-8"))}
    infra = [r for r in records if r.get("infra_error")]
    records = [r for r in records if not r.get("infra_error")]
    conditions = [c for c in CONDITION_ORDER if any(r["condition"] == c for r in records)]
    per_condition = {}
    for c in conditions:
        rs = [r for r in records if r["condition"] == c]
        per_condition[c] = {
            "runs": len(rs),
            "success": round(mean(r["success"] for r in rs), 4),
            "score_passed": round(mean(r["score_passed"] for r in rs), 4),
            "first_attempt_success": round(mean(r["first_attempt_success"] for r in rs), 4),
            "score_passed_but_regressed": sum(1 for r in rs if r["score_passed"] and r["regressions"]),
            "unparseable_reply_rate": round(
                1 - sum(r["parsed_edits"] for r in rs) / max(1, sum(r["model_calls"] for r in rs)), 4
            ),
            "solved_before_any_edit": sum(1 for r in rs if r["solved_before_any_edit"]),
            "by_seed": {str(s): round(mean(r["success"] for r in rs if r["seed"] == s), 4)
                        for s in sorted({r["seed"] for r in rs})},
        }
    comparisons = []
    for a, b in co_primary:
        if a in conditions and b in conditions:
            comparisons.append({"role": "co-primary", "overall": difference(records, a, b, level=primary_level)})
    for a, b in secondary:
        if a in conditions and b in conditions:
            comparisons.append({"role": "secondary", "overall": difference(records, a, b)})
    for cmp in comparisons:
        a, b = cmp["overall"]["a"], cmp["overall"]["b"]
        cmp["first_attempt"] = difference(records, a, b, "first_attempt_success", reps=2000)
        for field in ("expected_failure_mode", "difficulty"):
            groups = sorted({meta[r["task_id"]].get(field, "") for r in records})
            cmp[f"by_{field}"] = {
                g: difference(records, a, b, include=lambda r, g=g, f=field: meta[r["task_id"]].get(f, "") == g, reps=2000)
                for g in groups
            }
    per_task = {}
    for c in conditions:
        for k, v in _per_base_task(records, c, "success", lambda r: True).items():
            per_task.setdefault(k, {})[c] = round(v, 3)
    return {
        "infra_error_records": len(infra),
        "n_tasks": len({r["task_id"] for r in records}),
        "n_repos": len({r["family"] for r in records}),
        "category_counts": dict(Counter(meta[t]["expected_failure_mode"] for t in {r["task_id"] for r in records})),
        "per_condition": per_condition,
        "comparisons": comparisons,
        "per_task": per_task,
        "settings": {
            "models": sorted({r["model"] for r in records}),
            "temperatures": sorted({r["temperature"] for r in records}),
            "max_steps": sorted({r["max_steps"] for r in records}),
            "seeds": sorted({r["seed"] for r in records}),
        },
    }


def _ci(d, key="ci_repo_cluster") -> str:
    if not d:
        return "n/a"
    lo, hi = d[key]
    return f"{d['diff']:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def render_v2_markdown(result: dict[str, Any]) -> str:
    st = result["settings"]
    lines = [
        "# Benchmark v2 evaluation", "",
        f"Model {', '.join(st['models'])}; temperature {st['temperatures']}; up to {st['max_steps']} attempts; "
        f"seeds {st['seeds']}. {result['n_tasks']} tasks in {result['n_repos']} repos "
        f"({', '.join(f'{k} {v}' for k, v in sorted(result['category_counts'].items()))}).", "",
        "Success is strict: the target test passes and no test that passed before the edit fails afterwards.", "",
        "## Success rates", "",
        "| Condition | Runs | Strict success | Target test only | First attempt | Passed but broke another test | Unparseable replies |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for c, v in result["per_condition"].items():
        lines.append(f"| {c} | {v['runs']} | {v['success']:.3f} | {v['score_passed']:.3f} | {v['first_attempt_success']:.3f} | "
                     f"{v['score_passed_but_regressed']} | {v['unparseable_reply_rate']:.1%} |")
    lines += [
        "", "## Paired differences", "",
        "Mean over tasks of (A − B). Primary interval: bootstrap resampling repos. Co-primary comparisons use 97.5% "
        "intervals (Bonferroni over two); secondary ones 95%, uncorrected.", "",
        "| A − B | Role | Strict success (repo-cluster CI) | Task-level CI | Tasks better / worse / tied | First attempt |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cmp in result["comparisons"]:
        o = cmp["overall"]
        lines.append(f"| {o['a']} − {o['b']} | {cmp['role']} ({o['level']:.1%}) | {_ci(o)} | {_ci(o, 'ci_task')} | "
                     f"{o['tasks_better']} / {o['tasks_worse']} / {o['tasks_tied']} | {_ci(cmp['first_attempt'])} |")
    for field, title in (("expected_failure_mode", "bug category"), ("difficulty", "authored difficulty")):
        groups = sorted({g for cmp in result["comparisons"] for g in cmp[f"by_{field}"]})
        lines += ["", f"## By {title} (exploratory, 95% repo-cluster CI)", "",
                  "| A − B | " + " | ".join(groups) + " |", "| --- |" + " --- |" * len(groups)]
        for cmp in result["comparisons"]:
            o = cmp["overall"]
            lines.append(f"| {o['a']} − {o['b']} | " + " | ".join(_ci(cmp[f'by_{field}'].get(g)) for g in groups) + " |")
    conds = list(result["per_condition"])
    lines += ["", "## Per task (strict success over seeds)", "",
              "| Task | " + " | ".join(conds) + " |", "| --- |" + " ---: |" * len(conds)]
    for k in sorted(result["per_task"]):
        lines.append(f"| {k} | " + " | ".join(f"{result['per_task'][k].get(c, float('nan')):.2f}" for c in conds) + " |")
    if result["infra_error_records"]:
        lines += ["", f"Infrastructure-error records excluded: {result['infra_error_records']}."]
    return "\n".join(lines) + "\n"
