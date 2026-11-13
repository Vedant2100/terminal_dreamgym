"""Model-written skills (protocol: docs/model_skills_protocol.md).

The solver model reads traces of its own earlier attempts (no-skill runs from a
previous matched evaluation) and writes one SKILL.md of general debugging
guidance. Skills are written leave-one-family-out: the skill used on family F's
tasks is written only from traces of the other three families (any split), so it
never sees F's repository.
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path
from typing import Any

from terminal_dreamgym.config import TASK_TEMPLATE_DIR
from terminal_dreamgym.matched_eval import load_records

FAMILIES = ["cli_edge_case", "config_env_failure", "dependency_mismatch", "python_test_failure"]
MAX_SKILL_CHARS = 1700  # the four handwritten skills total 1,676 characters
N_FAILURES = 5
N_SUCCESSES = 1


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + "\n...[truncated]"


def trace_digest(record: dict[str, Any]) -> str:
    """A compact view of one earlier attempt: first failure, the model's edit, the result."""
    trace = json.loads((Path(record["run_dir"]) / "trace.json").read_text(encoding="utf-8"))
    commands = trace.get("commands", [])
    first = commands[0] if commands else {}
    last = commands[-1] if commands else {}
    outcome = "SUCCEEDED" if record["success"] else (
        "target test passed but broke another test" if record["score_passed"] else "FAILED"
    )
    return (
        f"Outcome: {outcome} after {record['model_calls']} attempt(s)\n"
        f"Initial failing output:\n{_truncate((first.get('stdout') or '') + (first.get('stderr') or ''), 1200)}\n"
        f"Your final edit (diff):\n{_truncate(trace.get('diff') or '(no edit applied)', 1500)}\n"
        f"Final test output:\n{_truncate((last.get('stdout') or '') + (last.get('stderr') or ''), 800)}"
    )


def select_source_records(records, held_out_family: str, source_seed: int, rng: random.Random):
    """No-skill runs from the other families (any split); at most one run per base task."""
    pool = [
        r for r in records
        if r.get("condition") == "no_skill" and not r.get("infra_error")
        and r["seed"] == source_seed and r["family"] != held_out_family
        and not r["solved_before_any_edit"]
    ]
    rng.shuffle(pool)
    failures, successes, seen = [], [], set()
    for r in pool:
        if r["base_task"] in seen:
            continue
        bucket = successes if r["success"] else failures
        limit = N_SUCCESSES if r["success"] else N_FAILURES
        if len(bucket) < limit:
            bucket.append(r)
            seen.add(r["base_task"])
    return failures + successes


def writer_prompt(digests: list[str]) -> str:
    body = "\n\n".join(f"=== Attempt {i + 1} ===\n{d}" for i, d in enumerate(digests))
    return (
        "You are a terminal coding agent. Below are records of your own earlier attempts to fix "
        "failing pytest tests in small Python repositories by rewriting source files. Most attempts "
        "failed.\n\n"
        f"{body}\n\n"
        "Write a SKILL.md for yourself: general, reusable guidance that would have helped you avoid "
        "these failures. It will be shown to you when fixing DIFFERENT repositories that you have not "
        "seen, so do not mention file names, function names, test names or literal values from these "
        "records. Use a '# Skill: <title>' heading and numbered steps. Stay under 1,500 characters. "
        "Output only the SKILL.md text."
    )


def _clean(reply: str) -> str:
    text = re.sub(r"^```[a-zA-Z]*\n", "", reply.strip())
    text = re.sub(r"\n```\s*$", "", text).strip()
    if len(text) <= MAX_SKILL_CHARS:
        return text
    # Over the cap: keep whole lines only, so no step is cut off mid-sentence.
    cut = text[:MAX_SKILL_CHARS]
    return cut[: cut.rfind("\n")].rstrip() if "\n" in cut else cut


def family_identifiers(family: str) -> set[str]:
    """Function and test names in a family's repo, to check that a skill did not leak them."""
    names: set[str] = set()
    for path in (TASK_TEMPLATE_DIR / family).glob("*.py"):
        names.update(re.findall(r"def (\w+)", path.read_text(encoding="utf-8")))
    return {n for n in names if len(n) > 4 and n != "main"}


def write_model_skills(
    source: Path, seeds: list[int], out_dir: Path, mode: str = "qwen", client=None, writer_model: str | None = None
) -> list[dict]:
    """writer_model: an OpenAI-compatible model name to write with instead of the solver model."""
    from terminal_dreamgym.gemini_agent import OpenAICompatClient, make_client

    if client is None:
        client = OpenAICompatClient(model=writer_model) if writer_model else make_client(mode)
    records = load_records(source)
    source_seeds = sorted({r["seed"] for r in records if r.get("condition") == "no_skill"})
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for seed in seeds:
        source_seed = source_seeds[(seed - 1) % len(source_seeds)]
        for family in FAMILIES:
            path = out_dir / f"seed{seed}_{family}.md"
            if path.exists():
                manifest.append(json.loads((out_dir / f"seed{seed}_{family}.json").read_text()))
                continue
            rng = random.Random(f"{seed}-{family}")
            chosen = select_source_records(records, family, source_seed, rng)
            prompt = writer_prompt([trace_digest(r) for r in chosen])
            reply = client.generate_text(prompt, seed=7000 + seed * 10 + FAMILIES.index(family))
            skill = _clean(reply)
            leaks = sorted(n for n in family_identifiers(family) if n in skill)
            meta = {
                "seed": seed,
                "held_out_family": family,
                "writer_model": getattr(client, "model", None),
                "source_seed": source_seed,
                "source_task_ids": [r["task_id"] for r in chosen],
                "source_families": sorted({r["family"] for r in chosen}),
                "chars": len(skill),
                "raw_reply_chars": len(reply),
                "leaked_identifiers": leaks,
                "usage": dict(getattr(client, "last_usage", {}) or {}),
            }
            path.write_text(skill + "\n", encoding="utf-8")
            (out_dir / f"seed{seed}_{family}.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
            (out_dir / f"seed{seed}_{family}.prompt.txt").write_text(prompt, encoding="utf-8")
            manifest.append(meta)
    return manifest


def load_model_skill(skills_dir: Path, seed: int, family: str) -> str:
    return (skills_dir / f"seed{seed}_{family}.md").read_text(encoding="utf-8").strip()
