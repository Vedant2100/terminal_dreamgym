from __future__ import annotations

import json
import random
import shutil

import pytest

import terminal_dreamgym.gemini_agent as agent_mod
from terminal_dreamgym.benchmark_v2 import build, load_bugs, repo_dirs, task_id, validate_repo
from terminal_dreamgym.matched_eval import load_records, run_matched
from terminal_dreamgym.skill_writer import FAMILIES, select_source_records
from terminal_dreamgym.task_model import load_tasks
from terminal_dreamgym.v2_analysis import calibration_keep, difference


@pytest.mark.parametrize("repo", repo_dirs(), ids=lambda p: p.name)
def test_every_v2_bug_is_valid(repo):
    """Correct repo passes; each bug fails only its target; traps really are traps."""
    assert validate_repo(repo) == []


def test_build_writes_buggy_templates(tmp_path):
    repo = next(r for r in repo_dirs() if r.name == "ledger")
    bug = load_bugs(repo)[0]
    tid = task_id(repo, bug)
    tasks = build([tid], templates_dir=tmp_path / "templates", tasks_file=tmp_path / "tasks.json")
    assert [t["id"] for t in tasks] == [tid]
    (loaded,) = load_tasks(tmp_path / "tasks.json")
    assert loaded.template_path == tmp_path / "templates" / tid
    edit = bug["edits"][0]
    assert edit["new"] in (loaded.template_path / edit["file"]).read_text()
    assert not (loaded.template_path / "bugs.json").exists()
    with pytest.raises(ValueError):
        build(["no_such_task"], templates_dir=tmp_path / "t2", tasks_file=tmp_path / "t2.json")


def _cal(task, successes):
    return [{"condition": "no_skill", "task_id": task, "success": i < successes, "infra_error": False} for i in range(5)]


def test_calibration_keep_band():
    recs = _cal("a", 0) + _cal("b", 1) + _cal("c", 4) + _cal("d", 5) + _cal("e", 3)
    kept, counts = calibration_keep(recs)
    assert kept == ["b", "c", "e"] and counts["d"] == 5
    with pytest.raises(ValueError):
        calibration_keep(recs + [{"condition": "no_skill", "task_id": "a", "success": True, "infra_error": False}])


def test_difference_cluster_ci_is_wider_when_repos_disagree():
    recs = []
    for repo, effect in [("r1", 1.0), ("r2", 0.0), ("r3", 1.0), ("r4", 0.0)]:
        for t in range(5):
            for cond, val in [("a", effect), ("b", 0.0)]:
                recs.append({"condition": cond, "base_task": f"{repo}_{t}", "family": repo, "success": val})
    d = difference(recs, "a", "b", reps=2000)
    assert d["diff"] == 0.5 and d["n_repos"] == 4 and d["n_tasks"] == 20
    width = lambda ci: ci[1] - ci[0]  # noqa: E731
    assert width(d["ci_repo_cluster"]) > width(d["ci_task"])


def test_all_family_selection_draws_from_every_family():
    recs = [{"condition": "no_skill", "seed": 1, "family": f, "infra_error": False, "solved_before_any_edit": False,
             "base_task": f"{f}_{i}", "task_id": f"{f}_{i}_v1", "success": i == 0}
            for f in FAMILIES for i in range(3)]
    chosen = select_source_records(recs, "all", 1, random.Random(0))
    assert len(chosen) == 6 and len({r["base_task"] for r in chosen}) == 6


def test_skill_scope_all_uses_one_skill_for_every_task(tmp_path, monkeypatch):
    (tmp_path / "seed1_all.md").write_text("# Skill: shared\n")
    seen = []

    class Recorder:
        name, model, available = "stub", "stub", True
        last_usage = {}

        def generate_text(self, prompt, seed=None):
            seen.append(prompt)
            return "no edits"

    monkeypatch.setattr(agent_mod, "make_client", lambda provider: Recorder())
    repo = next(r for r in repo_dirs() if r.name == "ledger")
    tid = task_id(repo, load_bugs(repo)[0])
    tasks_file = tmp_path / "tasks.json"
    build([tid], templates_dir=tmp_path / "templates", tasks_file=tasks_file)
    out = tmp_path / "r.jsonl"
    run_matched(out, conditions=["strong_skill"], seeds=[1], concurrency=1, task_ids=[tid],
                strong_skills_dir=tmp_path, tasks_file=tasks_file, skill_scope="all")
    (rec,) = load_records(out)
    shutil.rmtree(rec["run_dir"], ignore_errors=True)
    assert not rec["infra_error"], rec
    assert rec["family"] == "ledger" and not rec["solved_before_any_edit"]
    assert seen and all("# Skill: shared" in p for p in seen)
    assert json.loads(tasks_file.read_text())[0]["split"] in {"heldout", "adversarial"}
