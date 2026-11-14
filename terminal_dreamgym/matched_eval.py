"""Matched-condition evaluation (protocol: docs/matched_eval_protocol.md).

Every condition runs the same 100 tasks with the same model, sampling settings,
attempt budget and scoring. Conditions differ only in the ACTIVE SKILLS block of
the prompt. Results go to a JSONL file, one line per (condition, seed, task), so a
crashed run can resume without redoing finished work.
"""
from __future__ import annotations

import json
import random
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean
from typing import Any

from terminal_dreamgym.config import LLM_MAX_OUTPUT_TOKENS, LLM_MAX_STEPS, LLM_TEMPERATURE
from terminal_dreamgym.task_model import TaskSpec, load_tasks

CONDITIONS = ["no_skill", "handwritten_skills", "placebo", "symptom_patch", "model_skill", "strong_skill"]
PRIMARY = ("handwritten_skills", "no_skill")
SECONDARY = [("handwritten_skills", "placebo"), ("placebo", "no_skill"), ("symptom_patch", "no_skill")]
SPLITS = ["train", "heldout", "adversarial"]


def base_task(task_id: str) -> str:
    """`python_email_whitespace_v3` -> `python_email_whitespace` (the cluster unit)."""
    stem, _, suffix = task_id.rpartition("_v")
    return stem if suffix.isdigit() else task_id


def _record(condition: str, seed: int, task: TaskSpec, trace) -> dict[str, Any]:
    meta = trace.metadata
    attempts = meta.get("attempts", [])
    return {
        "condition": condition,
        "seed": seed,
        "task_id": task.id,
        "base_task": base_task(task.id),
        "split": task.split,
        "family": task.family,
        "success": trace.success,
        "score_passed": meta["score_passed"],
        "regressions": meta["regressions"],
        "first_attempt_success": meta["first_attempt_success"],
        "first_attempt_score_passed": meta["first_attempt_score_passed"],
        "solved_before_any_edit": meta["solved_before_any_edit"],
        "model_calls": meta["model_calls"],
        "parsed_edits": sum(1 for a in attempts if a.get("parsed_edit")),
        "prompt_tokens": sum(a.get("prompt_tokens") or 0 for a in attempts),
        "completion_tokens": sum(a.get("completion_tokens") or 0 for a in attempts),
        "max_prompt_tokens": max((a.get("prompt_tokens") or 0 for a in attempts), default=0),
        "length_truncated": any(a.get("finish_reason") == "length" for a in attempts),
        "infra_error": meta["infra_error"],
        "notes": meta["notes"],
        "model": meta["model"],
        "temperature": meta["temperature"],
        "max_steps": meta["max_steps"],
        "duration_seconds": trace.duration_seconds,
        "diff": trace.diff,
        "run_dir": trace.run_dir,
    }


def _infra_record(condition: str, seed: int, task: TaskSpec, exc: Exception) -> dict[str, Any]:
    return {
        "condition": condition, "seed": seed, "task_id": task.id, "base_task": base_task(task.id),
        "split": task.split, "family": task.family, "infra_error": True, "notes": [f"harness error: {exc!r}"],
    }


def load_records(path: Path) -> list[dict[str, Any]]:
    """Read results; a partial last line (job killed mid-write) is skipped."""
    if not path.exists():
        return []
    records = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def run_matched(
    out_path: Path,
    conditions: list[str] | None = None,
    seeds: list[int] | None = None,
    mode: str = "qwen",
    concurrency: int = 4,
    task_ids: list[str] | None = None,
    skills_dir: Path | None = None,
    strong_skills_dir: Path | None = None,
    tasks_file: Path | None = None,
    skill_scope: str | None = None,
) -> int:
    """skill_scope="all": use one model-written skill per seed (seed{s}_all.md) for every task."""
    from terminal_dreamgym.gemini_agent import LLMTerminalAgent

    conditions = conditions or CONDITIONS[:4]
    if "model_skill" in conditions and skills_dir is None:
        raise ValueError("model_skill needs skills_dir (see skill_writer.py)")
    if "strong_skill" in conditions and strong_skills_dir is None:
        raise ValueError("strong_skill needs strong_skills_dir (see skill_writer.py)")
    seeds = seeds or [1, 2, 3]
    tasks = load_tasks(tasks_file)
    if task_ids:
        wanted = set(task_ids)
        tasks = [t for t in tasks if t.id in wanted]

    # Resume: keep finished records, redo only missing ones and infrastructure failures.
    existing = load_records(out_path)
    done = {(r["condition"], r["seed"], r["task_id"]) for r in existing if not r["infra_error"]}
    if any(r["infra_error"] for r in existing):
        kept = [r for r in existing if not r["infra_error"]]
        out_path.write_text("".join(json.dumps(r) + "\n" for r in kept), encoding="utf-8")

    jobs = [(c, s, t) for s in seeds for c in conditions for t in tasks if (c, s, t.id) not in done]
    random.Random(0).shuffle(jobs)  # interleave conditions so server drift hits all equally
    lock = threading.Lock()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def work(job):
        condition, seed, task = job
        try:
            texts = None
            if condition in ("model_skill", "strong_skill"):
                from terminal_dreamgym.skill_writer import load_model_skill

                folder = skills_dir if condition == "model_skill" else strong_skills_dir
                texts = [load_model_skill(folder, seed, skill_scope or task.family)]
            agent = LLMTerminalAgent(strategy=condition, provider=mode, skill_texts=texts)
            return _record(condition, seed, task, agent.run_task(task, seed=seed))
        except Exception as exc:  # never lose the rest of the run to one job
            return _infra_record(condition, seed, task, exc)

    finished = 0
    with ThreadPoolExecutor(max_workers=concurrency) as pool, out_path.open("a", encoding="utf-8") as handle:
        futures = [pool.submit(work, job) for job in jobs]
        for future in as_completed(futures):
            record = future.result()
            with lock:
                handle.write(json.dumps(record) + "\n")
                handle.flush()
                finished += 1
                if finished % 25 == 0 or finished == len(jobs):
                    print(f"[matched-eval] {finished}/{len(jobs)} done", flush=True)
    return finished


# -- analysis -----------------------------------------------------------------


def _per_base_task(records, condition, metric, include):
    """Mean of `metric` per base task, over its variants and all seeds."""
    values = defaultdict(list)
    for r in records:
        if r["condition"] == condition and include(r):
            values[r["base_task"]].append(float(r[metric]))
    return {k: mean(v) for k, v in values.items()}


def paired_difference(records, a, b, metric="success", include=lambda r: True, reps=10000, seed=0):
    """Mean over base tasks of (a - b), with a 95% bootstrap CI that resamples base tasks.

    Variants of one base task are near-copies, and seeds reuse the same tasks, so the
    base task is the independent unit; resampling individual runs would understate
    the uncertainty.
    """
    pa = _per_base_task(records, a, metric, include)
    pb = _per_base_task(records, b, metric, include)
    keys = sorted(set(pa) & set(pb))
    unpaired = sorted(set(pa) ^ set(pb))
    if not keys:
        return None
    diffs = [pa[k] - pb[k] for k in keys]
    rng = random.Random(seed)
    boots = sorted(mean(rng.choice(diffs) for _ in diffs) for _ in range(reps))
    return {
        "a": a,
        "b": b,
        "metric": metric,
        "n_base_tasks": len(keys),
        "mean_a": round(mean(pa[k] for k in keys), 4),
        "mean_b": round(mean(pb[k] for k in keys), 4),
        "diff": round(mean(diffs), 4),
        "ci95": [round(boots[int(0.025 * reps)], 4), round(boots[int(0.975 * reps) - 1], 4)],
        "base_tasks_better": sum(d > 0 for d in diffs),
        "base_tasks_worse": sum(d < 0 for d in diffs),
        "base_tasks_tied": sum(d == 0 for d in diffs),
        "unpaired_base_tasks_dropped": unpaired,
        "per_base_task_diff": {k: round(pa[k] - pb[k], 4) for k in keys},
    }


def analyze(records: list[dict[str, Any]], primary=PRIMARY, secondary=None) -> dict[str, Any]:
    secondary = SECONDARY if secondary is None else secondary
    infra = [r for r in records if r.get("infra_error")]
    records = [r for r in records if not r.get("infra_error")]
    free = {r["base_task"] for r in records if r["solved_before_any_edit"]}
    primary_include = lambda r: r["base_task"] not in free  # noqa: E731
    conditions = [c for c in CONDITIONS if any(r["condition"] == c for r in records)]

    per_condition = {}
    for c in conditions:
        rs = [r for r in records if r["condition"] == c]
        scored = [r for r in rs if primary_include(r)]
        per_condition[c] = {
            "runs": len(rs),
            "success": round(mean(r["success"] for r in scored), 4) if scored else None,
            "score_passed": round(mean(r["score_passed"] for r in scored), 4) if scored else None,
            "first_attempt_success": round(mean(r["first_attempt_success"] for r in scored), 4) if scored else None,
            "runs_with_regressions": sum(1 for r in scored if r["regressions"]),
            "score_passed_but_regressed": sum(1 for r in scored if r["score_passed"] and r["regressions"]),
            "mean_model_calls": round(mean(r["model_calls"] for r in rs), 3) if rs else None,
            "unparseable_reply_rate": round(
                1 - sum(r["parsed_edits"] for r in rs) / max(1, sum(r["model_calls"] for r in rs)), 4
            ),
            "mean_prompt_tokens": round(mean(r["prompt_tokens"] for r in rs), 1) if rs else None,
            "mean_completion_tokens": round(mean(r["completion_tokens"] for r in rs), 1) if rs else None,
            "length_truncated_runs": sum(1 for r in rs if r["length_truncated"]),
            "infra_errors": sum(1 for r in rs if r["infra_error"]),
            "by_split": {
                s: round(mean(r["success"] for r in scored if r["split"] == s), 4)
                for s in SPLITS
                if any(r["split"] == s for r in scored)
            },
            "by_seed": {
                str(seed): round(mean(r["success"] for r in scored if r["seed"] == seed), 4)
                for seed in sorted({r["seed"] for r in scored})
            },
        }

    comparisons = []
    for a, b in [primary, *secondary]:
        if a not in conditions or b not in conditions:
            continue
        entry = {"primary": (a, b) == tuple(primary)}
        entry["overall"] = paired_difference(records, a, b, include=primary_include)
        entry["first_attempt"] = paired_difference(records, a, b, "first_attempt_success", include=primary_include)
        entry["score_only"] = paired_difference(records, a, b, "score_passed", include=primary_include)
        entry["by_split"] = {
            s: paired_difference(records, a, b, include=lambda r, s=s: primary_include(r) and r["split"] == s)
            for s in SPLITS
        }
        comparisons.append(entry)

    per_base_task = {}
    for c in conditions:
        for k, v in _per_base_task(records, c, "success", lambda r: True).items():
            per_base_task.setdefault(k, {})[c] = round(v, 3)

    by_family = {}
    for a, b in [primary, *secondary]:
        if a in conditions and b in conditions:
            fam = {}
            for family in sorted({r["family"] for r in records}):
                d = paired_difference(
                    records, a, b, include=lambda r, f=family: primary_include(r) and r["family"] == f, reps=1
                )
                if d:
                    fam[family] = {"diff": d["diff"], "n_base_tasks": d["n_base_tasks"]}
            by_family[f"{a} - {b}"] = fam

    return {
        "infra_error_records": len(infra),
        "by_family": by_family,
        "excluded_base_tasks_solved_before_edit": sorted(free),
        "per_condition": per_condition,
        "comparisons": comparisons,
        "per_base_task": per_base_task,
        "settings": {
            "models": sorted({r["model"] for r in records}),
            "temperatures": sorted({r["temperature"] for r in records}),
            "max_steps": sorted({r["max_steps"] for r in records}),
            "seeds": sorted({r["seed"] for r in records}),
        },
    }


def _fmt_ci(cmp) -> str:
    if not cmp:
        return "n/a"
    lo, hi = cmp["ci95"]
    return f"{cmp['diff']:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Matched-condition evaluation", ""]
    st = result["settings"]
    lines += [
        f"Model {', '.join(st['models'])}; temperature {st['temperatures']}; up to {st['max_steps']} model "
        f"attempts per task for every condition; seeds {st['seeds']}.",
        "",
        "Success is strict: the target test passes and no test that passed before the edit fails afterwards.",
        f"Base tasks excluded because their target test passes before any edit: "
        f"{', '.join(result['excluded_base_tasks_solved_before_edit']) or 'none'}.",
        "",
        "## Success rates",
        "",
        "| Condition | Runs | Strict success | Target test only | First attempt | Train | Held-out | Adversarial | Passed but regressed | Mean calls | Unparseable replies |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for c, v in result["per_condition"].items():
        bs = v["by_split"]
        lines.append(
            f"| {c} | {v['runs']} | {v['success']:.3f} | {v['score_passed']:.3f} | {v['first_attempt_success']:.3f} | "
            f"{bs.get('train', float('nan')):.3f} | {bs.get('heldout', float('nan')):.3f} | {bs.get('adversarial', float('nan')):.3f} | "
            f"{v['score_passed_but_regressed']} | {v['mean_model_calls']:.2f} | {v['unparseable_reply_rate']:.1%} |"
        )
    lines += [
        "",
        "## Paired differences",
        "",
        "Mean over base tasks of (A − B), 95% bootstrap CI resampling base tasks; better/worse/tied counts are base tasks.",
        "",
        "| A − B | Strict success | Better / worse / tied | First attempt | Target test only | Train | Held-out | Adversarial |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for cmp in result["comparisons"]:
        o = cmp["overall"]
        label = f"{o['a']} − {o['b']}" + (" (primary)" if cmp["primary"] else "")
        lines.append(
            f"| {label} | {_fmt_ci(o)} | {o['base_tasks_better']} / {o['base_tasks_worse']} / {o['base_tasks_tied']} | "
            f"{_fmt_ci(cmp['first_attempt'])} | {_fmt_ci(cmp['score_only'])} | "
            f"{_fmt_ci(cmp['by_split']['train'])} | {_fmt_ci(cmp['by_split']['heldout'])} | {_fmt_ci(cmp['by_split']['adversarial'])} |"
        )
    lines += [
        "",
        "## By task family (sensitivity)",
        "",
        "Base tasks within a family share one repository, so they are not fully independent. "
        "Mean (A − B) per family, no interval (only four families):",
        "",
        "| A − B | " + " | ".join(sorted({f for v in result["by_family"].values() for f in v})) + " |",
    ]
    fams = sorted({f for v in result["by_family"].values() for f in v})
    lines.append("| --- |" + " ---: |" * len(fams))
    for label, v in result["by_family"].items():
        lines.append(f"| {label} | " + " | ".join(f"{v[f]['diff']:+.3f}" if f in v else "n/a" for f in fams) + " |")
    if result["infra_error_records"]:
        lines += ["", f"Infrastructure-error records excluded: {result['infra_error_records']}."]
    conds = list(result["per_condition"])
    lines += ["", "## Per base task (strict success, all variants and seeds)", "",
              "| Base task | " + " | ".join(conds) + " |", "| --- |" + " ---: |" * len(conds)]
    for k in sorted(result["per_base_task"]):
        row = result["per_base_task"][k]
        lines.append(f"| {k} | " + " | ".join(f"{row.get(c, float('nan')):.2f}" for c in conds) + " |")
    return "\n".join(lines) + "\n"


def current_settings() -> dict[str, Any]:
    return {"temperature": LLM_TEMPERATURE, "max_steps": LLM_MAX_STEPS, "max_output_tokens": LLM_MAX_OUTPUT_TOKENS}
