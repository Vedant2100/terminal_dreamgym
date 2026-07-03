from __future__ import annotations

import math
from pathlib import Path
from statistics import mean
from typing import Any

from terminal_dreamgym.config import DEFAULT_MODE, RUNS_DIR
from terminal_dreamgym.curriculum_generator import practice_task_specs
from terminal_dreamgym.demo_assets import init_demo_assets
from terminal_dreamgym.promotion import SkillMetrics, decide, naive_promote, promote_skill
from terminal_dreamgym.runner import run_strategy, run_tasks
from terminal_dreamgym.utils import success_rate, write_json

CANDIDATE_SKILLS = [
    "reflection_overfit_skill.md",
    "trace_first_debugging_skill.md",
    "minimal_patch_skill.md",
    "contract_drift_skill.md",
    "error_handling_skill.md",
]


def summarize_successes(successes: int, total: int) -> dict[str, int | float]:
    return {"successes": successes, "total": total, "rate": success_rate(successes, total)}


def score_practice_for_skill(skill_name: str, mode: str, seed: int) -> float:
    """Run evaluation for a skill on its matching curriculum's practice worlds."""
    from terminal_dreamgym.curriculum_generator import CURRICULA
    curriculum = next((c for c in CURRICULA.values() if c.target_skill == skill_name), None)
    if not curriculum:
        # For skills with no curricula (like reflection_overfit), score on all practice worlds
        specs = practice_task_specs()
        strategy = "reflection_only" if skill_name == "reflection_overfit_skill.md" else "baseline"
        traces = run_tasks(strategy, specs, mode=mode, active_skills=[skill_name] if skill_name == "reflection_overfit_skill.md" else None, seed=seed)
        successes = sum(1 for trace in traces if trace.success)
        return successes / len(specs) if specs else 0.0

    specs = practice_task_specs([curriculum])
    # Run the agent with that single skill active on only those curriculum worlds
    traces = run_tasks("dreamgym_skill", specs, mode=mode, active_skills=[skill_name], seed=seed)
    successes = sum(1 for trace in traces if trace.success)
    return successes / len(specs) if specs else 0.0


def detect_regressions(
    baseline_traces: list[dict[str, Any]],
    candidate_traces: list[dict[str, Any]],
    split: str | None = None,
) -> list[str]:
    candidate_by_id = {trace["task_id"]: trace for trace in candidate_traces}
    regressions = []
    for trace in baseline_traces:
        if split and trace["split"] != split:
            continue
        candidate = candidate_by_id.get(trace["task_id"])
        if trace["success"] and candidate and not candidate["success"]:
            regressions.append(trace["task_id"])
    return regressions


def compute_stats(values: list[float]) -> dict[str, float]:
    """Compute mean, standard deviation, and 95% confidence interval using Student's t critical values."""
    if not values:
        return {"mean": 0.0, "stdev": 0.0, "ci95": 0.0}
    n = len(values)
    import statistics
    m = statistics.mean(values)
    if n < 2:
        return {"mean": round(m, 4), "stdev": 0.0, "ci95": 0.0}
    sd = statistics.stdev(values)
    t_table = {
        1: 12.706,
        2: 4.303,
        3: 3.182,
        4: 2.776,
        5: 2.571,
        6: 2.447,
        7: 2.365,
        8: 2.306,
        9: 2.262,
        10: 2.228,
    }
    t_val = t_table.get(n - 1, 1.960)
    ci = t_val * (sd / math.sqrt(n))
    return {
        "mean": round(m, 4),
        "stdev": round(sd, 4),
        "ci95": round(ci, 4),
    }


def evaluate(
    mode: str = DEFAULT_MODE,
    models: list[str] | None = None,
    seeds: list[int] | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    init_demo_assets()
    if models is None:
        models = [mode]
    if seeds is None:
        seeds = [42]

    raw_results = []

    for model in models:
        for seed in seeds:
            # 1. Run baseline (no skills injected)
            baseline_run = run_strategy("baseline", mode=model, seed=seed)
            base_scores = {
                "train": baseline_run["summary"]["train"]["rate"],
                "heldout": baseline_run["summary"]["heldout"]["rate"],
                "adversarial": baseline_run["summary"]["adversarial"]["rate"],
            }

            # 2. Run each candidate skill individually
            evaluations = []
            for skill in CANDIDATE_SKILLS:
                strategy = "reflection_only" if skill == "reflection_overfit_skill.md" else "dreamgym_skill"
                skill_run = run_strategy(strategy, mode=model, active_skills=[skill], seed=seed)
                practice_score = score_practice_for_skill(skill, model, seed)

                # Compute deltas relative to baseline of this model and seed
                train_delta = round(skill_run["summary"]["train"]["rate"] - base_scores["train"], 4)
                heldout_delta = round(skill_run["summary"]["heldout"]["rate"] - base_scores["heldout"], 4)
                adversarial_delta = round(skill_run["summary"]["adversarial"]["rate"] - base_scores["adversarial"], 4)

                regressed_ids = detect_regressions(baseline_run["traces"], skill_run["traces"], split="adversarial")
                adversarial_regressions = len(regressed_ids)

                metrics = SkillMetrics(
                    name=skill,
                    train_delta=train_delta,
                    heldout_delta=heldout_delta,
                    adversarial_delta=adversarial_delta,
                    adversarial_regressions=adversarial_regressions,
                    practice_score=practice_score,
                )
                decision = decide(metrics)

                evaluations.append({
                    "name": skill,
                    "train_delta": train_delta,
                    "heldout_delta": heldout_delta,
                    "adversarial_delta": adversarial_delta,
                    "adversarial_regressions": adversarial_regressions,
                    "practice_score": practice_score,
                    "naive_promote": decision.naive,
                    "gated_promote": decision.gated,
                    "disagree": decision.disagree,
                    "false_promotion": decision.false_promotion,
                    "wrongly_rejected": decision.wrongly_rejected,
                    "scores": {
                        "train": skill_run["summary"]["train"]["rate"],
                        "heldout": skill_run["summary"]["heldout"]["rate"],
                        "adversarial": skill_run["summary"]["adversarial"]["rate"],
                    }
                })

            # 3. Stacked skills interference
            interference = {}
            for policy_name in ["naive", "gated"]:
                promoted = [e["name"] for e in evaluations if e[f"{policy_name}_promote"]]
                if len(promoted) >= 2:
                    stacked_run = run_strategy("dreamgym_skill", mode=model, active_skills=promoted, seed=seed)
                    stacked_heldout = stacked_run["summary"]["heldout"]["rate"]
                    stacked_adversarial = stacked_run["summary"]["adversarial"]["rate"]

                    best_heldout = max(e["scores"]["heldout"] for e in evaluations if e["name"] in promoted)
                    best_adversarial = max(e["scores"]["adversarial"] for e in evaluations if e["name"] in promoted)

                    interferes = stacked_heldout < best_heldout
                    interference[policy_name] = {
                        "promoted": promoted,
                        "stacked_heldout": stacked_heldout,
                        "stacked_adversarial": stacked_adversarial,
                        "best_individual_heldout": best_heldout,
                        "best_individual_adversarial": best_adversarial,
                        "interferes": interferes,
                        "interference_delta": round(stacked_heldout - best_heldout, 4),
                    }
                else:
                    interference[policy_name] = {
                        "promoted": promoted,
                        "stacked_heldout": base_scores["heldout"],
                        "stacked_adversarial": base_scores["adversarial"],
                        "best_individual_heldout": base_scores["heldout"],
                        "best_individual_adversarial": base_scores["adversarial"],
                        "interferes": False,
                        "interference_delta": 0.0,
                    }

            raw_results.append({
                "model": model,
                "seed": seed,
                "baseline_scores": base_scores,
                "evaluations": evaluations,
                "interference": interference,
            })

    # 4. Aggregation across seeds per model
    aggregated = {}
    for model in models:
        model_runs = [r for r in raw_results if r["model"] == model]
        if not model_runs:
            continue

        base_train_vals = [r["baseline_scores"]["train"] for r in model_runs]
        base_heldout_vals = [r["baseline_scores"]["heldout"] for r in model_runs]
        base_adv_vals = [r["baseline_scores"]["adversarial"] for r in model_runs]

        baseline_stats = {
            "train": compute_stats(base_train_vals),
            "heldout": compute_stats(base_heldout_vals),
            "adversarial": compute_stats(base_adv_vals),
        }

        eval_stats = []
        passed_dreamed_gate_count = 0
        failed_reality_passed_gate_count = 0

        for skill in CANDIDATE_SKILLS:
            skill_runs_data = []
            for r in model_runs:
                se = next(e for e in r["evaluations"] if e["name"] == skill)
                skill_runs_data.append(se)

                # Dreamed-curriculum trust checks
                if se["practice_score"] >= 0.60:
                    passed_dreamed_gate_count += 1
                    if se["heldout_delta"] <= 0:
                        failed_reality_passed_gate_count += 1

            train_deltas = [s["train_delta"] for s in skill_runs_data]
            heldout_deltas = [s["heldout_delta"] for s in skill_runs_data]
            adv_deltas = [s["adversarial_delta"] for s in skill_runs_data]
            adv_regs = [s["adversarial_regressions"] for s in skill_runs_data]
            practice_scores = [s["practice_score"] for s in skill_runs_data]

            naive_promotes = sum(1 for s in skill_runs_data if s["naive_promote"])
            gated_promotes = sum(1 for s in skill_runs_data if s["gated_promote"])
            disagreements = sum(1 for s in skill_runs_data if s["disagree"])

            naive_promoted_runs = [s for s in skill_runs_data if s["naive_promote"]]
            gated_promoted_runs = [s for s in skill_runs_data if s["gated_promote"]]

            naive_false_prom_rate = (sum(1 for s in naive_promoted_runs if s["heldout_delta"] <= 0) / len(naive_promoted_runs)) if naive_promoted_runs else 0.0
            gated_false_prom_rate = (sum(1 for s in gated_promoted_runs if s["heldout_delta"] <= 0) / len(gated_promoted_runs)) if gated_promoted_runs else 0.0

            wrongly_rejected_count = sum(1 for s in skill_runs_data if s["wrongly_rejected"])
            wrongly_rejected_rate = wrongly_rejected_count / len(skill_runs_data)

            eval_stats.append({
                "name": skill,
                "train_delta": compute_stats(train_deltas),
                "heldout_delta": compute_stats(heldout_deltas),
                "adversarial_delta": compute_stats(adv_deltas),
                "adversarial_regressions": compute_stats(adv_regs),
                "practice_score": compute_stats(practice_scores),
                "naive_promote_rate": round(naive_promotes / len(model_runs), 4),
                "gated_promote_rate": round(gated_promotes / len(model_runs), 4),
                "disagreement_rate": round(disagreements / len(model_runs), 4),
                "naive_false_promotion_rate": round(naive_false_prom_rate, 4),
                "gated_false_promotion_rate": round(gated_false_prom_rate, 4),
                "wrongly_rejected_rate": round(wrongly_rejected_rate, 4),
            })

        self_gating_false_promotion_rate = (
            failed_reality_passed_gate_count / passed_dreamed_gate_count
            if passed_dreamed_gate_count > 0
            else 0.0
        )

        interference_stats = {}
        for policy_name in ["naive", "gated"]:
            policy_runs = [r["interference"][policy_name] for r in model_runs]
            interferes_count = sum(1 for p in policy_runs if p["interferes"])
            interferes_rate = interferes_count / len(model_runs)

            stacked_heldout_deltas = [
                round(p["stacked_heldout"] - r["baseline_scores"]["heldout"], 4)
                for r, p in zip(model_runs, policy_runs)
            ]
            stacked_adv_deltas = [
                round(p["stacked_adversarial"] - r["baseline_scores"]["adversarial"], 4)
                for r, p in zip(model_runs, policy_runs)
            ]
            interference_deltas = [p["interference_delta"] for p in policy_runs]

            interference_stats[policy_name] = {
                "interferes_rate": round(interferes_rate, 4),
                "stacked_heldout_delta": compute_stats(stacked_heldout_deltas),
                "stacked_adversarial_delta": compute_stats(stacked_adv_deltas),
                "interference_delta": compute_stats(interference_deltas),
            }

        aggregated[model] = {
            "baseline_scores": baseline_stats,
            "evaluations": eval_stats,
            "self_gating_false_promotion_rate": round(self_gating_false_promotion_rate, 4),
            "interference": interference_stats,
        }

    payload = {
        "run_id": "terminal_dreamgym_eval",
        "mode": mode,
        "models": models,
        "seeds": seeds,
        "raw_results": raw_results,
        "aggregated": aggregated,
    }
    write_json(output_path or RUNS_DIR / "evaluation.json", payload)
    return payload
