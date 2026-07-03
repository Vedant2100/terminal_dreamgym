from __future__ import annotations

from pathlib import Path
from typing import Iterable

from terminal_dreamgym.config import DATA_DIR, DEFAULT_MODE, RUNS_DIR
from terminal_dreamgym.demo_assets import init_demo_assets
from terminal_dreamgym.task_model import TaskSpec, load_tasks, tasks_by_id
from terminal_dreamgym.trace_model import TaskRunTrace
from terminal_dreamgym.utils import model_dump, read_json, success_rate, write_json


def load_splits(path: Path | None = None) -> dict[str, list[str]]:
    return read_json(path or DATA_DIR / "splits.json")


def summarize_traces(traces: Iterable[TaskRunTrace]) -> dict[str, dict[str, float | int]]:
    summary: dict[str, dict[str, float | int]] = {}
    trace_list = list(traces)
    for split in ["train", "heldout", "adversarial"]:
        split_traces = [trace for trace in trace_list if trace.split == split]
        successes = sum(1 for trace in split_traces if trace.success)
        total = len(split_traces)
        summary[split] = {"successes": successes, "total": total, "rate": success_rate(successes, total)}
    return summary


def build_agent(strategy: str, mode: str, active_skills: list[str] | None = None):
    from terminal_dreamgym.gemini_agent import LLMTerminalAgent

    return LLMTerminalAgent(strategy=strategy, provider=mode, active_skills=active_skills)


def run_tasks(
    strategy: str,
    tasks: list[TaskSpec],
    mode: str = DEFAULT_MODE,
    active_skills: list[str] | None = None,
    seed: int | None = None,
) -> list[TaskRunTrace]:
    agent = build_agent(strategy, mode, active_skills=active_skills)
    return [agent.run_task(task, seed=seed) for task in tasks]


def run_strategy(
    strategy: str,
    task_ids: list[str] | None = None,
    mode: str = DEFAULT_MODE,
    active_skills: list[str] | None = None,
    seed: int | None = None,
) -> dict[str, object]:
    all_tasks = load_tasks()
    lookup = tasks_by_id(all_tasks)
    if task_ids is None:
        selected = all_tasks
    else:
        selected = [lookup[task_id] for task_id in task_ids]
    traces = run_tasks(strategy, selected, mode=mode, active_skills=active_skills, seed=seed)
    return {
        "strategy": strategy,
        "mode": mode,
        "seed": seed,
        "summary": summarize_traces(traces),
        "traces": [model_dump(trace) for trace in traces],
    }


def run_baseline(mode: str = DEFAULT_MODE, output_path: Path | None = None) -> dict[str, object]:
    init_demo_assets()
    run = run_strategy("baseline", mode=mode)
    path = output_path or RUNS_DIR / "baseline.json"
    write_json(path, run)
    return run
