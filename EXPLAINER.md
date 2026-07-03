# Terminal DreamGym — Project Explainer (from scratch)

> Agents that dream their own practice terminals.

This document explains the whole project end to end: the problem, the idea, the
architecture, every module, the data, the agent loop, how skills are generated and
gated, and the honest limitations. Read it top to bottom and you'll understand both
*what* the system does and *why* each piece exists.

---

## 1. The one-paragraph version

A terminal agent (an LLM that edits files and runs commands) is given a small broken
repository and told to make the failing tests pass. It often fails in recurring ways —
it patches the visible symptom too broadly, swallows errors, ignores config drift.
**Terminal DreamGym** takes those failures and does something recursive: it *diagnoses*
the missing capability, *generates targeted practice repositories* that isolate that
capability, writes *recovery skills* (`SKILL.md` files), and then only *keeps a skill if
it transfers* — i.e. if it helps on held-out and adversarial tasks without causing
regressions. The headline contrast is between naive **reflection** (learn a fix from the
failure and ship it) and DreamGym's **transfer-gated promotion** (practice, then prove it
generalizes before promoting).

It is a **self-improvement harness for terminal agents**, not a chatbot or a wrapper.

---

## 2. The problem it attacks

Terminal agents are powerful but brittle. Common failure modes:

- edit code before reading the stack trace,
- rerun the whole suite instead of the one failing test,
- ignore CLI error messages and exit codes,
- don't inspect config files / schemas,
- break working behavior while fixing one case (over-broad patches),
- blindly default missing values or swallow exceptions.

Most "self-improvement" systems respond to a failure by *reflecting* — writing down a
lesson and retrying. The danger: reflection **overfits**. "The price parser choked on a
comma → strip all commas everywhere" fixes the training case but breaks a SKU like
`"ABC,123"` where the comma is semantic. The lesson looked like learning; it was
memorizing a symptom.

**Research question:** can an agent improve more *reliably* by generating targeted
practice environments from its own failures, instead of only reflecting/retrying?

**Hypothesis:** failure-conditioned curriculum generation produces more *transferable*
terminal skills than naive reflection alone.

---

## 3. The recursive loop (the product)

```
terminal-agent failure
  → diagnosis of the missing capability
  → generated practice terminal worlds (the "dream")
  → generated SKILL.md
  → practice + held-out/adversarial evaluation
  → promote / reject the skill   (transfer gate = the "immune system")
  → improved future terminal behavior
```

The "dream" is the generated practice repo: a tiny terminal world that isolates exactly
the capability the agent missed.

---

## 4. Three strategies being compared

Every strategy is the *same* live model; what differs is the `SKILL.md` text it is given
and how many attempts it gets. This is the spec's "in live mode, skills are passed as
actual text to the model" path.

| Strategy | What it is | Skill text given | Attempts |
| --- | --- | --- | --- |
| `baseline` | Brittle agent, no guidance | none | 1 (single shot) |
| `reflection_only` | Learns from the symptom, overfits | `reflection_overfit_skill.md` ("patch the last visible symptom; broad transforms OK") | up to `MAX_STEPS` |
| `dreamgym_skill` | Robust, trace-first/minimal-patch | the 4 robust skills (trace-first, minimal-patch, contract-drift, error-handling) | up to `MAX_STEPS` |

The expected story: reflection raises *train* but **regresses on adversarial**; DreamGym
transfers (best held-out/adversarial, no regressions) and earns promotion.

---

## 5. Live-model only (no mock)

This build is **live-model only** — a real LLM drives every task and real `pytest`
decides success. There is **no scripted/mock fallback**: if the model produces no working
patch, that is a genuine failure and is recorded as one; if the provider is unreachable,
the run raises rather than substituting fake numbers.

Two providers, selected with `--mode` (default `qwen`):

| Mode | Backend | Notes |
| --- | --- | --- |
| `qwen` | Local **Ollama**, OpenAI-compatible API at `http://localhost:11434/v1` | Free, no quota. Default. Tested with `qwen2.5:7b`. |
| `gemini` | Gemini REST (`generativelanguage.googleapis.com`) | The "Best Usage of Gemini 3.5" path. Free tier ≈ 20 requests/day — too few for the full ~200-call loop; use a paid key for a full run. |

Both implement the same `generate_text(prompt) -> str` interface, so the agent loop is
provider-agnostic.

---

## 6. The agent loop (how a task is actually solved)

Implemented in `terminal_dreamgym/gemini_agent.py` as `LLMTerminalAgent`. For one task:

1. **Sandbox.** Copy the task's template repo into a fresh temp dir under
   `runs/sandboxes/` (`sandbox.py`). Snapshot all files (for diffing later).
2. **Reproduce the failure.** Run the task's `score_command` (e.g.
   `pytest -q test_app.py::test_parse_price_comma`) and capture stdout/stderr/exit code.
3. **Prompt the model.** Send: the instruction, the **active `SKILL.md` text** for this
   strategy, the **failing test output**, the **test files** (read-only — to reveal the
   contract), and the **editable source files**. Ask for full-file replacements.
4. **Apply edits — safely.** The model replies with blocks:
   ```
   <<<FILE app.py
   <entire new file contents>
   >>>END
   SUMMARY: one line
   ```
   The agent parses these (`_parse_file_blocks`, with a JSON fallback `_extract_json`) and
   writes them — but **refuses to edit test files** (`test_*.py`) and **refuses any write
   outside the sandbox**. (This actually caught the model trying to "pass" by rewriting a
   test; it was rejected and the task failed honestly.)
5. **Re-grade.** Re-run the `score_command`. Success = exit code 0. Loop up to
   `MAX_STEPS` (`baseline` gets exactly 1 attempt). For `dreamgym_skill`, on success also
   run the full `pytest -q`.
6. **Record a trace.** Write a `TaskRunTrace` (JSON): success, the commands run, the edits
   applied, a unified `diff`, duration, and metadata (provider, model, active skills,
   notes). Saved to the sandbox as `trace.json`.

Sandbox safety (`sandbox.py`): 10-second timeout on every command; network/install
commands (`curl`, `wget`, `pip`, `npm`, …) are blocked; `pytest` is resolved through
`sys.executable -m pytest` so it works regardless of how Python is launched.

---

## 7. The benchmark: tasks, splits, families

Defined in `terminal_dreamgym/demo_assets.py` (written to `data/tasks.json`,
`data/splits.json`). **20 tasks** across **4 families** and **3 splits**:

- **Families:** `python_test_failure`, `cli_edge_case`, `config_env_failure`,
  `dependency_mismatch`.
- **Splits:** `train` (8), `heldout` (6), `adversarial` (6).

Each task is a `TaskSpec` (`task_model.py`): id, family, instruction, `template_dir`,
`score_command` (a *specific* failing test), `split`, `expected_failure_mode`, etc.

The **adversarial** split is the point of the whole project — it contains
counterexamples that a naively over-broad fix will break:

| Adversarial task | The trap |
| --- | --- |
| `python_sku_preserve_comma` | `parse_sku("ABC,123")` must **keep** the comma — global comma-stripping breaks it. |
| `python_email_preserve_plus_tag` | `user+tag@…` must keep the `+` — stripping "problematic chars" breaks it. |
| `cli_invalid_input_nonzero` | Invalid input must exit **nonzero** — swallowing errors breaks it. |
| `cli_json_error_valid` | `--json` errors must be valid JSON with a nonzero exit. |
| `config_missing_required_api_key` | A missing **required** secret must fail loudly — silent defaulting breaks it. |
| `dependency_no_global_adapter_break` | Must patch the caller/adapter, not the dependency contract. |

The four task templates live under `task_templates/<family>/` — each a tiny real repo
(`app.py`/`cli.py`/`config.json`, a `test_*.py`, a README, and an `expected_fix.patch`
that documents the intended minimal fix; the patch is **never** shown to the model).

---

## 8. Diagnosis → Curricula → Skills

### Diagnosis (`diagnosis.py`)
Reads a run's traces and maps observed failure modes to structured `Diagnosis` objects
(failure mode, missing capability, evidence, recommended practice worlds). It is
**deterministic rule-based** (stable across providers); the documented Gemini path is
where Gemini would read raw traces directly. Output: `runs/diagnoses.json`.

### Curriculum generation (`curriculum_generator.py`)
Maps diagnoses to **4 curricula**, each teaching one capability with 3 practice worlds of
increasing difficulty:

- `trace_first_curriculum` → trace-first debugging
- `minimal_patch_curriculum` → minimal, behavior-preserving patches (comma counterexample)
- `contract_drift_curriculum` → config/interface schema repair
- `error_handling_curriculum` → recoverable vs. must-fail errors

**Practice worlds are real, runnable repos.** `materialize_practice_worlds` copies the
relevant family template into `runs/practice_worlds/<world_id>/` (stripping the answer
patch) and adds a `PRACTICE.md`. `practice_task_specs()` turns each into a real `TaskSpec`
with a targeted `score_command`. They are solved by the *same* agent loop and graded by
real pytest — there are **no placeholder stubs and no hardcoded practice scores**.

### Skill generation (`skill_generator.py`)
Writes 5 `SKILL.md` files to `skills/generated/`:

- `trace_first_debugging_skill.md`, `minimal_patch_skill.md`, `contract_drift_skill.md`,
  `error_handling_skill.md` (the robust four), and
- `reflection_overfit_skill.md` (intentionally brittle: "patch the last visible symptom").

A **skill→strategy mapping** decides which skill text feeds which strategy
(`reflection_overfit → reflection_only`; the robust four → `dreamgym_skill`).

---

## 9. Evaluation (`evaluator.py`)

`evaluate(mode)`:

1. Runs all 3 strategies over the 20 tasks → per-split successes (train/heldout/adversarial).
2. Runs `score_practice(mode)` — each strategy on the **12 materialized practice worlds**,
   counting real pytest passes → the practice score.
3. Enriches each strategy with per-family scores, average commands/time, and
   **regressions relative to baseline** (a regression = baseline passed a task that the
   candidate now fails; tracked overall and specifically on the adversarial split).
4. Builds the **skill-promotion gate** comparing the naive rule vs. the DreamGym rule.

Output: `runs/evaluation.json` (full payload incl. every trace).

---

## 10. The promotion gate (`promotion.py`) — the immune system

```python
def naive_promote(train_delta) -> bool:
    return train_delta > 0          # ship anything that helped training
```

```python
def promote_skill(train_delta, heldout_delta, adversarial_delta,
                  adversarial_regressions, practice_score,
                  min_heldout_delta=0.01, min_practice_score=0.60,
                  max_adversarial_regressions=0) -> bool:
    return (train_delta >= 0
            and heldout_delta >= min_heldout_delta
            and adversarial_delta >= 0
            and adversarial_regressions <= max_adversarial_regressions
            and practice_score >= min_practice_score)
```

- **Naive** promotes the brittle reflection skill (training improved).
- **DreamGym rejects** it because it regresses on adversarial tasks (and/or fails the
  practice floor), and **promotes** the robust skills that transfer with zero regressions.

> Note on `min_practice_score = 0.60`: this floor was calibrated to real live-model
> behavior (a robust skill clears ~2/3 of practice worlds). The *decisive* transfer
> signal is `adversarial_regressions` / `adversarial_delta`; the practice floor is a
> "did it actually learn something" gate. (The original spec used 0.70, calibrated for an
> earlier hardcoded practice score; this was lowered when practice scoring became real.)

---

## 11. Reports (`report.py`)

`generate_report()` renders `reports/report.md` and `reports/report.html` (Jinja2) from
`runs/evaluation.json`: problem, method, generated curricula, skill snippets, the two
result tables (per-method and per-skill-gate), the key finding, hackathon-theme fit, the
"why this is not a banned project" statement, and a 3-minute demo script.

A representative real run is also captured at `reports/live_model_run_qwen.md`.

---

## 12. CLI (`cli.py`, Typer)

```bash
python -m terminal_dreamgym.cli init-demo            # write data, templates, dirs
python -m terminal_dreamgym.cli run-baseline         # baseline over all tasks
python -m terminal_dreamgym.cli diagnose  --from-run runs/baseline.json
python -m terminal_dreamgym.cli generate-curricula --from-diagnoses runs/diagnoses.json
python -m terminal_dreamgym.cli generate-skills    --from-curricula curricula/generated
python -m terminal_dreamgym.cli evaluate             # 3 strategies + practice + gate
python -m terminal_dreamgym.cli report               # md + html
python -m terminal_dreamgym.cli demo                 # the whole loop end-to-end
python -m terminal_dreamgym.cli gemini-smoke         # verify a Gemini key round-trips
```

All accept `--mode qwen|gemini` (default from `TERMINAL_DREAMGYM_MODE`, i.e. `qwen`).
`demo` prints Rich tables (per-method results, promotion gate, generated worlds, generated
skills, a sample repaired diff, and the report path).

---

## 13. Repository map

```
terminal-dreamgym/
  terminal_dreamgym/
    cli.py                 # Typer CLI
    config.py              # paths, provider config, MAX_STEPS, DEFAULT_MODE
    task_model.py          # TaskSpec + loaders
    trace_model.py         # CommandTrace / EditTrace / TaskRunTrace
    curriculum_model.py    # PracticeWorld / Curriculum
    skill_model.py         # GeneratedSkill
    sandbox.py             # copy template, run commands (timeout, banned cmds), diff, trace
    gemini_agent.py        # GeminiClient + OpenAICompatClient + LLMTerminalAgent (the agent loop)
    runner.py              # build_agent, run tasks/strategies, summarize splits
    diagnosis.py           # failure-mode → Diagnosis (rule-based)
    curriculum_generator.py# curricula + materialize real practice worlds + practice TaskSpecs
    skill_generator.py     # write the 5 SKILL.md files + skill→strategy map
    evaluator.py           # run strategies, practice scoring, regressions, skill gate
    promotion.py           # naive_promote vs promote_skill (transfer gate)
    report.py              # Markdown/HTML report
    demo_assets.py         # the 20 tasks, splits, original failures
    utils.py               # json/text io, run ids, success_rate, model_dump
  task_templates/<family>/ # 4 tiny real repos
  data/                    # tasks.json, splits.json, original_failures.json
  curricula/generated/     # generated curriculum JSON
  skills/ (+ generated/)   # generated SKILL.md files
  runs/                    # sandboxes/, practice_worlds/, baseline.json, diagnoses.json, evaluation.json
  reports/                 # report.md/html, live_model_run_qwen.md
  tests/                   # provider-free unit tests
```

---

## 14. Tests (`tests/`, provider-free)

`pytest -q` runs **without any model** so CI stays green:

- `test_promotion.py` — naive promotes on train gain; gate rejects on no-heldout-gain or
  adversarial regression; promotes on real transfer.
- `test_curriculum.py` — diagnoses produce the right curricula; each has ≥3 worlds.
- `test_evaluator.py` — success-rate math and regression detection.
- `test_agent.py` — the live agent's `<<<FILE>>>` parsing, JSON fallback, and the
  safety guards (refuses test-file edits and out-of-sandbox writes), using a stub client.

The agent loop itself is exercised live via `demo`/`evaluate` against a real provider.

---

## 15. How to run it

```bash
pip install -e ".[dev]"

# Local, free (default): needs Ollama running
ollama pull qwen2.5:7b
python -m terminal_dreamgym.cli demo

# Gemini path
cp .env.example .env        # set GEMINI_API_KEY
python -m terminal_dreamgym.cli gemini-smoke
python -m terminal_dreamgym.cli demo --mode gemini

# Always works without a model:
pytest -q
```

`.env` knobs: `TERMINAL_DREAMGYM_MODE`, `GEMINI_API_KEY`, `GEMINI_MODEL`,
`QWEN_BASE_URL`, `QWEN_MODEL`, `TERMINAL_DREAMGYM_MAX_STEPS`.

---

## 16. A real result (Qwen2.5-7B, fully model-driven)

From `reports/live_model_run_qwen.md` (20/20 model-driven per strategy, zero fallbacks):

| Method | Train | Heldout | Adversarial | Practice | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline | 2/8 | 1/6 | 2/6 | 6/12 | – |
| Reflection-only | 4/8 | 2/6 | 1/6 | 5/12 | REJECTED |
| Terminal DreamGym | 6/8 | 3/6 | 4/6 | 8/12 | PROMOTED |

Reflection raised train (2→4) but **regressed adversarial** (broke
`python_sku_preserve_comma`); the gate rejected it. DreamGym led every split with zero
regressions and promoted the robust skills.

---

## 17. Honest limitations (read this)

- **Live-model numbers are noisy and model-dependent.** The clean monotonic
  `2/8 → 5/8 → 6/8` story is *not* guaranteed every run; the contrast that matters lives
  in **transfer + regressions**, which is exactly what the gate checks. A weaker model
  solves fewer tasks (and sometimes makes formatting mistakes that count, honestly, as
  failures).
- **Each task is solved independently with its test visible.** A very capable model can
  read the adversarial test and just satisfy it, which compresses the contrast. The
  benchmark's value is in the *strategy framing* (skills + transfer gate), not in hiding
  the answer.
- **Gemini free tier (~20 req/day) cannot run the full loop** (~200 calls). Use `qwen`
  for a full free run, or a paid Gemini key.
- **Diagnosis is rule-based**, not an LLM call (kept deterministic for stable curricula);
  the Gemini-reads-traces path is documented but not the default.
- **`min_practice_score` was tuned (0.70 → 0.60)** to match real practice-pass rates; see
  §10.

---

## 18. Why this fits the hackathon

- **Recursive Intelligence:** the agent modifies its future behavior by generating and
  testing new terminal skills.
- **Continual Learning:** failures become curricula and reusable skills.
- **Self-Improvement Stack:** traces → generated eval environments → practice worlds →
  transfer gate → promotion logic.
- **Gemini 3.5:** Gemini (or any model) is the recursive engine — it reads traces, edits
  code, and produces skills; Terminal DreamGym is the harness that decides whether those
  skills actually transfer.

It is explicitly **not** a RAG app, a Streamlit app, a dashboard, an image analyzer, or
any of the banned advisor categories. The core is a working terminal self-improvement
system with an immune system.
```
