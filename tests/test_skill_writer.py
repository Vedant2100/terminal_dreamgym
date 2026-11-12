from __future__ import annotations

import json
import random
import shutil
from pathlib import Path

import pytest

import terminal_dreamgym.gemini_agent as agent_mod
from terminal_dreamgym.matched_eval import load_records, run_matched
from terminal_dreamgym.skill_writer import (
    FAMILIES,
    MAX_SKILL_CHARS,
    family_identifiers,
    select_source_records,
    write_model_skills,
)

SOURCE = Path("runs/matched_eval.jsonl")
needs_source = pytest.mark.skipif(
    not SOURCE.exists() or not any(Path(r["run_dir"]).exists() for r in load_records(SOURCE)[:20]),
    reason="needs the committed run-2 results and their local sandboxes",
)


def _fake_records():
    recs = []
    for fam in FAMILIES:
        for i in range(4):
            for split in ["train", "heldout"]:
                recs.append({
                    "condition": "no_skill", "seed": 1, "split": split, "family": fam, "infra_error": False,
                    "base_task": f"{fam}_{split}_{i}", "task_id": f"{fam}_{split}_{i}_v1",
                    "success": i == 0, "score_passed": i == 0, "solved_before_any_edit": False,
                })
    recs.append({**recs[0], "condition": "handwritten_skills"})
    return recs


@pytest.mark.parametrize("family", FAMILIES)
def test_selection_is_leave_one_family_out(family):
    chosen = select_source_records(_fake_records(), family, 1, random.Random(0))
    assert chosen
    assert all(r["family"] != family for r in chosen)
    assert all(r["condition"] == "no_skill" for r in chosen)
    assert len({r["base_task"] for r in chosen}) == len(chosen)
    assert sum(not r["success"] for r in chosen) <= 5 and sum(r["success"] for r in chosen) <= 1


class EchoClient:
    name, model, available = "stub", "stub", True

    def __init__(self):
        self.prompts = []
        self.last_usage = {}

    def generate_text(self, prompt, seed=None):
        self.prompts.append(prompt)
        return "```markdown\n# Skill: Read first\n1. Read the traceback. load_settings normalize_email\n" + "x" * 3000 + "\n```"


@needs_source
def test_write_model_skills_files_cap_and_leak_check(tmp_path):
    client = EchoClient()
    manifest = write_model_skills(SOURCE, [1], tmp_path, client=client)
    assert len(manifest) == 4 and len(client.prompts) == 4
    for meta in manifest:
        fam = meta["held_out_family"]
        text = (tmp_path / f"seed1_{fam}.md").read_text()
        assert text.startswith("# Skill") and len(text.strip()) <= MAX_SKILL_CHARS
        assert fam not in meta["source_families"]
        expected_leaks = sorted(n for n in family_identifiers(fam) if n in {"load_settings", "normalize_email"})
        assert meta["leaked_identifiers"] == expected_leaks
    # The prompt for a family must not contain that family's source.
    cfg_prompt = (tmp_path / "seed1_config_env_failure.prompt.txt").read_text()
    assert "load_settings" not in cfg_prompt
    # Resume: existing skills are not rewritten.
    write_model_skills(SOURCE, [1], tmp_path, client=client)
    assert len(client.prompts) == 4


def test_model_skill_condition_uses_the_family_skill(tmp_path, monkeypatch):
    for fam in FAMILIES:
        (tmp_path / f"seed1_{fam}.md").write_text(f"# Skill: for {fam}\n")
    seen = []

    class Recorder:
        name, model, available = "stub", "stub", True
        last_usage = {}

        def generate_text(self, prompt, seed=None):
            seen.append(prompt)
            return "no edits"

    monkeypatch.setattr(agent_mod, "make_client", lambda provider: Recorder())
    out = tmp_path / "r.jsonl"
    run_matched(out, conditions=["model_skill"], seeds=[1], concurrency=1,
                task_ids=["config_timeout_key_v1"], skills_dir=tmp_path)
    (rec,) = load_records(out)
    shutil.rmtree(rec["run_dir"], ignore_errors=True)
    assert seen and all("# Skill: for config_env_failure" in p for p in seen)
    assert not any("for python_test_failure" in p for p in seen)


def test_model_skill_without_skills_dir_is_an_error(tmp_path):
    with pytest.raises(ValueError):
        run_matched(tmp_path / "r.jsonl", conditions=["model_skill"], seeds=[1], task_ids=["config_timeout_key_v1"])
