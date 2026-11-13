"""Benchmark v2: correct repos with one injected bug per task.

Each repo in `benchmark_v2/repos/<repo>/` is a small, flat Python project whose
tests all pass. Its `bugs.json` lists bugs; each bug is one or more exact text
replacements in source files (never tests) that make one target test fail while
every other test in the repo still passes. A task is the repo with one bug
applied, so:

- the reference fix is the original code (every task is solvable), and
- the tests other than the target pass before any edit, so the pass-to-pass
  check (no previously passing test breaks) is never empty.

`build()` writes `task_templates_v2/<task_id>/` and `data/tasks_v2.json`.
`validate_repo()` checks every bug against those rules.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from terminal_dreamgym.config import DATA_DIR, PROJECT_ROOT

REPOS_DIR = PROJECT_ROOT / "benchmark_v2" / "repos"
TEMPLATES_DIR = PROJECT_ROOT / "task_templates_v2"
TASKS_FILE = DATA_DIR / "tasks_v2.json"
CATEGORIES = {"logic", "contract", "error_handling", "config", "trap"}
MIN_PASS_TO_PASS = 3
_IGNORE = shutil.ignore_patterns("bugs.json", "__pycache__", "*.pyc", ".pytest_cache")


def repo_dirs() -> list[Path]:
    return sorted(p for p in REPOS_DIR.iterdir() if (p / "bugs.json").exists()) if REPOS_DIR.exists() else []


def load_bugs(repo: Path) -> list[dict[str, Any]]:
    return json.loads((repo / "bugs.json").read_text(encoding="utf-8"))


def task_id(repo: Path, bug: dict[str, Any]) -> str:
    return f"{repo.name}__{bug['id']}"


def apply_bug(dst: Path, bug: dict[str, Any]) -> None:
    for edit in bug["edits"]:
        path = dst / edit["file"]
        text = path.read_text(encoding="utf-8")
        if text.count(edit["old"]) != 1:
            raise ValueError(f"{bug['id']}: 'old' must occur exactly once in {edit['file']} (found {text.count(edit['old'])})")
        path.write_text(text.replace(edit["old"], edit["new"]), encoding="utf-8")


def _pytest_outcomes(root: Path) -> dict[str, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-rA", "-p", "no:cacheprovider"],
        cwd=root, capture_output=True, text=True, timeout=120,
        # No bytecode cache: an edit that keeps a file's size and lands in the same
        # second as the last compile would otherwise run the stale .pyc.
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    out = {}
    for line in proc.stdout.splitlines():
        m = re.match(r"^(PASSED|FAILED|ERROR) (\S+)", line)
        if m:
            out[m.group(2)] = m.group(1)
    if not out:
        raise RuntimeError(f"pytest collected nothing in {root}:\n{proc.stdout[-2000:]}{proc.stderr[-2000:]}")
    return out


def validate_repo(repo: Path) -> list[str]:
    """Return a list of problems (empty if the repo and all its bugs are valid)."""
    problems = []
    bugs = load_bugs(repo)
    ids = [b["id"] for b in bugs]
    if len(ids) != len(set(ids)):
        problems.append(f"{repo.name}: duplicate bug ids")
    sources = [p for p in repo.glob("*.py") if not p.name.startswith("test_")]
    if any(p.name in {"conftest.py"} for p in repo.iterdir()):
        problems.append(f"{repo.name}: conftest.py is not allowed")
    if any(p.is_dir() and p.name not in {"__pycache__", ".pytest_cache"} for p in repo.iterdir()):
        problems.append(f"{repo.name}: repos must be flat (no subdirectories)")
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean"
        shutil.copytree(repo, clean, ignore=_IGNORE)
        base = _pytest_outcomes(clean)
        failing = [t for t, o in base.items() if o != "PASSED"]
        if failing:
            return problems + [f"{repo.name}: correct repo has failing tests: {failing}"]
        for bug in bugs:
            where = f"{repo.name}/{bug['id']}"
            if bug.get("category") not in CATEGORIES:
                problems.append(f"{where}: category must be one of {sorted(CATEGORIES)}")
            if any(Path(e["file"]).name.startswith("test_") for e in bug["edits"]):
                problems.append(f"{where}: bugs may not edit test files")
                continue
            if not any(Path(e["file"]).name == p.name for e in bug["edits"] for p in sources):
                problems.append(f"{where}: edits must target source files")
            target = bug["target_test"]
            if target not in base:
                problems.append(f"{where}: target test {target} not found")
                continue
            work = Path(tmp) / bug["id"]
            shutil.copytree(clean, work)
            try:
                apply_bug(work, bug)
            except ValueError as exc:
                problems.append(f"{where}: {exc}")
                continue
            try:
                out = _pytest_outcomes(work)
            except RuntimeError as exc:
                problems.append(f"{where}: {exc}")
                continue
            if out.get(target) == "PASSED":
                problems.append(f"{where}: target test still passes with the bug")
            others = {t: o for t, o in out.items() if t != target}
            broken = [t for t, o in others.items() if o != "PASSED"]
            if broken:
                problems.append(f"{where}: bug also breaks {broken}")
            if sum(o == "PASSED" for o in others.values()) < MIN_PASS_TO_PASS:
                problems.append(f"{where}: fewer than {MIN_PASS_TO_PASS} other tests pass with the bug")
            # A trap must come with the tempting wrong fix: applied on top of the bug,
            # it makes the target pass but breaks a test that passed before.
            if bug["category"] == "trap":
                if not bug.get("tempting_fix"):
                    problems.append(f"{where}: trap bugs need a tempting_fix")
                    continue
                try:
                    apply_bug(work, {"id": bug["id"] + "/tempting_fix", "edits": bug["tempting_fix"]})
                    tempted = _pytest_outcomes(work)
                except (ValueError, RuntimeError) as exc:
                    problems.append(f"{where}: tempting_fix: {exc}")
                    continue
                if tempted.get(target) != "PASSED":
                    problems.append(f"{where}: tempting_fix does not make the target pass")
                if not any(o != "PASSED" for t, o in tempted.items() if t != target):
                    problems.append(f"{where}: tempting_fix breaks no other test, so this is not a trap")
    return problems


def build_tasks() -> list[dict[str, Any]]:
    tasks = []
    for repo in repo_dirs():
        for bug in load_bugs(repo):
            tid = task_id(repo, bug)
            tasks.append({
                "id": tid,
                "family": repo.name,
                "instruction": "Fix the failing tests in this repo. Make the smallest safe change.",
                "template_dir": f"task_templates_v2/{tid}",
                "scorer": "pytest",
                "score_command": f"pytest -q {bug['target_test']}",
                "success_condition": "all_tests_pass",
                "max_steps": 8,
                "expected_failure_mode": bug["category"],
                "split": "adversarial" if bug["category"] == "trap" else "heldout",
                "tags": [bug["category"]],
                "difficulty": bug.get("difficulty", ""),
            })
    return tasks


def build(task_ids: list[str] | None = None, templates_dir: Path = TEMPLATES_DIR, tasks_file: Path = TASKS_FILE) -> list[dict[str, Any]]:
    """Materialise task templates and write data/tasks_v2.json (optionally a subset)."""
    tasks = build_tasks()
    if task_ids is not None:
        keep = set(task_ids)
        missing = keep - {t["id"] for t in tasks}
        if missing:
            raise ValueError(f"unknown task ids: {sorted(missing)}")
        tasks = [t for t in tasks if t["id"] in keep]
    if templates_dir != TEMPLATES_DIR:
        for t in tasks:
            t["template_dir"] = str(templates_dir / t["id"])
    if templates_dir.exists():
        shutil.rmtree(templates_dir)
    by_id = {task_id(repo, bug): (repo, bug) for repo in repo_dirs() for bug in load_bugs(repo)}
    for t in tasks:
        repo, bug = by_id[t["id"]]
        dst = templates_dir / t["id"]
        shutil.copytree(repo, dst, ignore=_IGNORE)
        apply_bug(dst, bug)
    tasks_file.parent.mkdir(parents=True, exist_ok=True)
    tasks_file.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
    return tasks
