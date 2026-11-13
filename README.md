# Terminal DreamGym

A small harness for testing whether instructions in a terminal coding agent's prompt
("skills") help it repair failing tests. A real LLM reads the failing pytest output
and proposes full-file edits, the harness applies them in a sandbox, and pytest
decides success. It started as a hackathon project (July 2026) whose pitch was a
self-improving agent: diagnose a failure, generate practice repos, write a
`SKILL.md`, and promote the skill only if it transfers to held-out tasks.

## Status (2026-11-12)

Two preregistered experiments on Qwen2.5-7B, both scored by strict success (the
target test passes and nothing that passed before breaks), found no detectable
gain from skill text:

- **Handwritten skills** (four fixed texts): +0.060 over no skill text, 95% CI
  −0.028 to +0.151 (3 seeds). Rerun with 5 seeds alongside the next experiment:
  +0.017, CI −0.072 to +0.114.
- **Model-written skills** (the model writes its own `SKILL.md` from traces of its
  earlier failures, never seeing the repo it is tested on): +0.000, CI −0.088 to
  +0.097 (5 seeds, a new skill per seed).

A July demo had reported a large gain from the handwritten skills; it gave them
three times as many model attempts as the baseline (see
[History](#history-the-july-results)). In the original hackathon pipeline the
skills and diagnoses are fixed text and rules, not model output; the model-written
skill experiment is the first test in this repo of the model learning from its own
failures.

## The tasks

There are four task families, each built on one small Python repo:

| Family | Base tasks | Repo contents | Example target test |
| --- | ---: | --- | --- |
| `python_test_failure` | 6 | string helpers: email normalisation, price parsing, slugify, SKU parsing | `normalize_email("  USER@Example.COM  ")` returns `user@example.com` |
| `cli_edge_case` | 5 | an argparse CLI | empty input exits 0; invalid input exits non-zero with "invalid input" on stderr |
| `config_env_failure` | 5 | a settings loader reading `config.json` | the renamed `request_timeout` key is read; a missing API key raises |
| `dependency_mismatch` | 4 | an app calling a package whose function signatures changed | `render_user` adapts to the new `format_user(dict)` signature |

Each repo contains several deliberate bugs, one per test, so most tests fail at
the start. A **base task** is one test in one family's repo: fix the code so that
test passes. There are 20 base tasks, and each is labelled train (8), held-out (6)
or adversarial (6). The labels come from the hackathon design, where skills were
to be chosen on train and checked on the other two. Each family repo is copied
into five variants (`_v1`–`_v5`) that differ only in literal values such as
names and numbers. That gives 20 repos (`task_templates/`) and 100 tasks
(`data/tasks.json`).

For each task the agent gets a prompt with the instruction, an ACTIVE SKILLS block
(empty, or the text of one or more skills), the failing test output, every test
file in the repo (read-only) and the editable source files. It replies with
whole-file replacements, which the harness applies before rerunning the target
test. It has up to 3 attempts.

## Matched evaluation: method and results

Protocol, written before the run: [`docs/matched_eval_protocol.md`](docs/matched_eval_protocol.md).
Full output: [`reports/matched_eval.md`](reports/matched_eval.md), raw records in
`runs/matched_eval.jsonl`.

Four conditions (called strategies in the code) differ only in the prompt's
ACTIVE SKILLS block:

| Condition | Text in the prompt |
| --- | --- |
| `no_skill` | none |
| `handwritten_skills` | four handwritten skills: trace-first debugging, minimal patches, contract drift, error handling (1,676 characters) |
| `placebo` | length-matched background text with no debugging advice |
| `symptom_patch` | handwritten bad advice: "patch the last visible symptom", even with a broad change |

Everything else is fixed: `qwen2.5:7b` through Ollama, temperature 0.7, up to 3
model attempts per task for every condition, a different seed for each attempt,
all 100 tasks, seeds 1–3. That is 1,200 runs, with no infrastructure errors and
no truncated replies.

A run counts as a **strict success** when the task's target test passes and no test
that passed in the untouched repo fails after the edit. One held-out base task
(`python_price_currency_spacing`) passes before any edit and is excluded, which
leaves 19 base tasks and 285 scored runs per condition.

| Condition | Strict success | Target test only | First attempt | Train | Held-out | Adversarial | Unparseable replies |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_skill | 0.512 | 0.537 | 0.284 | 0.717 | 0.453 | 0.289 | 27.2% |
| handwritten_skills | 0.572 | 0.621 | 0.291 | 0.658 | 0.600 | 0.433 | 11.2% |
| placebo | 0.530 | 0.533 | 0.253 | 0.683 | 0.413 | 0.422 | 32.0% |
| symptom_patch | 0.442 | 0.446 | 0.217 | 0.625 | 0.400 | 0.233 | 39.0% |

Train, held-out and adversarial columns are strict success within that split.
Unparseable replies is the share of model replies with no usable file edit.

Paired differences in strict success, averaged over base tasks, with 95% bootstrap
intervals that resample base tasks:

| A − B | All tasks | Base tasks better / worse / tied |
| --- | --- | --- |
| handwritten_skills − no_skill (primary) | +0.060 [−0.028, +0.151] | 6 / 4 / 9 |
| handwritten_skills − placebo | +0.042 [−0.049, +0.147] | 7 / 5 / 7 |
| placebo − no_skill | +0.018 [−0.039, +0.077] | 5 / 4 / 10 |
| symptom_patch − no_skill | −0.070 [−0.179, +0.025] | 5 / 5 / 9 |

How to read these numbers:

- The primary comparison's interval includes zero, so by the preregistered rule
  there is no detectable difference. The point estimate is positive, and the test
  has little power: 9 of the 19 base tasks tie because every condition solves them
  or none does, and four of the five cli base tasks are never solved.
- The clearest effect of the skill text is on output format. With the handwritten
  skills, 11% of replies had no usable file edit, against 27% with no skill text
  and 32% with the placebo. That did not show up as a first-attempt gain (+0.007).
- By split (secondary, 6–8 base tasks each), handwritten skills were higher on
  held-out (+0.147 [−0.053, +0.373]) and adversarial (+0.144 [+0.044, +0.256]) and
  lower on train (−0.058 [−0.150, +0.008]). The placebo shows the same adversarial
  gain over no skill (+0.133 [+0.033, +0.244]), and handwritten minus placebo on
  adversarial is +0.011. That pattern suggests the adversarial gain comes from
  having more text in the prompt rather than from what the skills say. None of
  these were corrected for multiple comparisons.
- By family, handwritten minus no skill was +0.227 on the Python tasks, +0.080 on
  config, 0 on cli and −0.100 on dependency tasks.
- Handwritten skills produced the most runs where the target test passed but a
  previously passing test broke (14, against 7 for no skill). Across all four
  conditions there were 23 such runs, all in the two Python email-normalisation
  tasks, and the test that broke was always
  `test_parse_price_currency_spacing`, the only test that passes before any edit.
- `symptom_patch` scored lowest, but its interval also includes zero.

### Checks on the results

- Every one of the 1,200 runs was re-scored from its saved sandbox by
  `scripts/reverify_matched.py`, which reruns the target test and the whole suite.
  All matched the recorded result.
- `tests/test_task_solvability.py` applies a hand-written correct fix to each of
  the 20 task repos and requires the whole suite to pass, so every task can be
  solved honestly.
- In 30 successful runs, spread across all four conditions (5–10 each), the model
  copied the auth token from the config repo's `config.json` into the code as a
  hard-coded default for `api_key`. The target
  test still passes, so these count as successes, but it is the "silently default
  a secret" pattern that one of the handwritten skills warns against. In one more
  successful run (placebo, `dependency_format_user_signature_v4`) the model
  hard-coded another test's expected output, `return "A-4: $16.50"`; that test
  was not the run's target.
- A first attempt at this run was stopped at 108 of 1,200 records, before any
  analysis, after a code review found three unsolvable tasks, a timeout path that
  could crash the run, and retries that reused the same seed. The protocol's
  Deviations section records this; the partial file is in `runs/aborted/`.

### Limits of this benchmark

- **Unit of analysis.** The 100 tasks are 20 base tasks × 5 near-identical variants
  (`_v1`–`_v5`), so the base task is the unit. Base tasks in one family are
  different tests on the same repository and source file, so even they are not
  fully independent, and the intervals above are somewhat too narrow.
- **Held-out is not really held out.** Train, held-out and adversarial tasks share
  the same repos. No condition is trained on anything, so here all three splits
  are evaluation data.
- **Weak regression check.** Each repo carries the other tasks' bugs, so almost no
  test passes in the untouched repos. The
  only one is `test_parse_price_currency_spacing` in the Python repos. For 14 of
  the 19 analysed base tasks (all cli, config and dependency tasks), strict
  success is the same as target-only success.
- **Visible tests.** The agent sees every test file in the repo, including the
  tests of other tasks, though it cannot edit them.

## Model-written skills

Protocol: [`docs/model_skills_protocol.md`](docs/model_skills_protocol.md), written
before the run. Results: [`reports/model_skills_eval.md`](reports/model_skills_eval.md),
raw records in `runs/model_skills_eval.jsonl`, the 20 skills with their prompts in
`skills/model_written/`.

**How the skills were written.** Qwen2.5-7B read six of its own `no_skill` attempts
from the matched evaluation (five failures and one success, each shown as the
initial failing output, its final diff and the final test output) and wrote a
`SKILL.md` of general guidance. Skills are written leave-one-family-out: the skill
used on a family's tasks comes only from attempts in the other three families, so
the writer never sees the repo the skill is tested on. One skill per family per
seed, 20 in all, 1,544–1,693 characters each; none contains a function name from
the repo it is tested on. Skills were used as written.

**Run.** `no_skill`, `model_skill`, `handwritten_skills` and `placebo`, all 100
tasks, seeds 1–5, the same settings as the matched evaluation, run together in one
job: 2,000 runs, no infrastructure errors. Every run was re-scored from its saved
sandbox with `scripts/reverify_matched.py`.

| Condition | Strict success | First attempt | Unparseable replies |
| --- | ---: | ---: | ---: |
| no_skill | 0.558 | 0.290 | 24.2% |
| model_skill | 0.558 | 0.293 | 11.1% |
| handwritten_skills | 0.575 | 0.299 | 12.1% |
| placebo | 0.537 | 0.194 | 30.6% |

| A − B | Strict success, 95% CI | Base tasks better / worse / tied |
| --- | --- | --- |
| model_skill − no_skill (primary) | +0.000 [−0.088, +0.097] | 6 / 8 / 5 |
| model_skill − handwritten_skills | −0.017 [−0.105, +0.059] | 6 / 7 / 6 |
| model_skill − placebo | +0.021 [−0.088, +0.139] | 6 / 8 / 5 |
| handwritten_skills − no_skill | +0.017 [−0.072, +0.114] | 7 / 7 / 5 |

What the results show:

- The model-written skills made no detectable difference. By the preregistered
  rule this is a null result. The interval's upper end is about +10 points, so a
  large gain on this benchmark is unlikely (the interval is somewhat too narrow,
  because base tasks within a family share a repo).
- Both kinds of skill text cut replies with no usable edit roughly in half (11–12%
  against 24% with no skill text), while the placebo did not (31%). Numbered
  instructions seem to help the model follow the reply format, but that did not
  raise success.
- The handwritten-skill gain from the matched evaluation (+0.060) shrank to +0.017.
  The `no_skill` rate itself moved from 0.512 to 0.558 between the two jobs, and
  per-seed rates ranged from 0.505 to 0.611, so differences of a few points are
  within run-to-run variation.
- The skills are generic. No skill says to keep existing functions and imports
  when rewriting a file, though 6 writer prompts showed an import error after a
  rewrite and 7 showed an attempt that broke another test. Only 2 mention stderr or
  exit codes, though 15 prompts included stderr-related test output. 8 of the 20
  advise changing the tests or assertions, which the agent is not allowed to do.

A 7B model asked to reflect on its failures wrote textbook debugging advice
rather than lessons from those failures, and that advice did not change how often
it solved tasks.

## The hackathon pipeline

```text
run tasks -> diagnose failures -> practice repos -> SKILL.md -> evaluate -> promote or reject
```

| Step | Module | Implementation |
| --- | --- | --- |
| Run tasks | `gemini_agent.py`, `sandbox.py` | Live model (Qwen via Ollama, or Gemini). Up to `TERMINAL_DREAMGYM_MAX_STEPS` attempts (default 3) for every strategy; strict success |
| Diagnose | `diagnosis.py` | Fixed rules from the task's expected failure mode; four diagnoses (overbroad patch, contract drift, interface drift, swallowed error) are always added. No model call |
| Practice repos | `curriculum_generator.py` | Fixed "practice worlds": copies of the existing task repos, grouped by the skill they are meant to teach |
| Skills | `skill_generator.py` | Writes the fixed texts in `SKILL_TEXTS`. No model call |
| Evaluate and promote | `evaluator.py`, `promotion.py` | Runs each skill on all tasks and practice repos, then applies a naive gate (train success above the no-skill baseline) and a transfer gate (held-out improved, no adversarial regression, practice score ≥ 0.60) |

The pipeline still runs (`python -m terminal_dreamgym.cli demo` or `evaluate`; see
[Running it](#running-it)), but it promotes or rejects the fixed handwritten skills,
so its output says nothing about self-improvement. `evaluate` reports `gated_false_promotion_rate` (the transfer gate promoted a skill
whose held-out score did not improve) and `practice_gate_false_pass_rate` (a skill
cleared the practice floor alone but its held-out score did not improve). These
are different measures.

## History: the July results

The July demo (`reports/live_model_run_qwen.md`) reported baseline 2/8, 1/6, 2/6
against Terminal DreamGym 6/8, 3/6, 4/6 on train, held-out and adversarial, and a
later "two-seed sweep" reported zero deltas for every skill. Neither result stands:

- The baseline got 1 model attempt and the skill strategies got 3.
- It was one run of 20 tasks at temperature 0.1, and one of the 6 held-out tasks
  passes before any edit.
- Three tests in each dependency repo could not be solved without hard-coding,
  because the variant generator renamed the inputs but not the expected outputs.
- The "sweep" in `runs/evaluation.json` was not a model run. The unit test
  `test_evaluate_sweep_logic` wrote its mock numbers to that file, and the file
  was committed. It has been removed, and the test now writes to a temporary
  directory.
- Its "false promotion" count included skills that were never promoted: it was
  true for any skill with a flat held-out score. It now requires a promotion.
- The `symptom_patch` condition was called `reflection_only`, though it is a fixed
  bad-advice text rather than model reflection. The old name still works.

`runs/baseline.json` is a real July baseline run (Qwen2.5-7B, 20 tasks, 1 attempt)
and is kept for reference.

## Running it

```bash
python -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest -q          # provider-free; no model needed
```

Matched evaluation against a local Ollama server:

```bash
ollama pull qwen2.5:7b
export TERMINAL_DREAMGYM_TEMPERATURE=0.7 TERMINAL_DREAMGYM_MAX_STEPS=3
python -m terminal_dreamgym.cli matched-eval --out runs/matched_eval.jsonl --seeds 1,2,3
python -m terminal_dreamgym.cli matched-report   # writes reports/matched_eval.{md,json}
```

Model-written skills (writes the skills into the given directory, then evaluates
four conditions):

```bash
python -m terminal_dreamgym.cli write-skills --source runs/matched_eval.jsonl --out-dir skills/model_written --seeds 1,2,3,4,5
python -m terminal_dreamgym.cli matched-eval --out runs/model_skills_eval.jsonl --seeds 1,2,3,4,5 \
  --skills-dir skills/model_written --conditions no_skill,model_skill,handwritten_skills,placebo
python -m terminal_dreamgym.cli matched-report --results runs/model_skills_eval.jsonl --name model_skills_eval \
  --primary model_skill,no_skill --secondary "model_skill,handwritten_skills;model_skill,placebo;handwritten_skills,no_skill"
```

On the cluster: `sbatch scripts/model_skills.sbatch skills/model_written runs/model_skills_eval.jsonl 1,2,3,4,5`
(about 2 h 15 min for 2,000 runs on an RTX 2080 Ti).

`matched-eval` resumes from its output file and reruns only records marked
`infra_error`. On the UCR cluster, `sbatch scripts/matched_eval.sbatch
runs/matched_eval.jsonl --seeds 1,2,3` starts Ollama in the FrontierMemory Apptainer
image on one GPU and runs the same command. A full run took 71 minutes on an RTX
2080 Ti.

The original pipeline:

```bash
python -m terminal_dreamgym.cli demo               # baseline, diagnose, curricula, skills, evaluate, report
python -m terminal_dreamgym.cli evaluate --seeds 1,2,3
python -m terminal_dreamgym.cli report             # reports/report.{md,html} from runs/evaluation.json
```

Providers: `--mode qwen` (default) uses an OpenAI-compatible endpoint
(`QWEN_BASE_URL`, default `http://localhost:11434/v1`; `QWEN_MODEL`, default
`qwen2.5:7b`). `--mode gemini` uses `GEMINI_API_KEY` and `GEMINI_MODEL`; its free
tier allows about 20 requests a day, too few for a full run.

Other settings: `TERMINAL_DREAMGYM_MAX_OUTPUT_TOKENS` (default 2048), and
`TERMINAL_DREAMGYM_TEMPERATURE` (default 0.1, kept from the original code; the
matched evaluation uses 0.7).

## Layout

```text
terminal_dreamgym/   agent, sandbox, pipeline steps, matched_eval.py, cli.py
task_templates/      20 task repos (*_v1..v5), generated by demo_assets.py from the 4 base repos
data/                tasks.json (100 tasks), splits.json
docs/                matched_eval_protocol.md, model_skills_protocol.md
reports/             matched_eval.{md,json}; model_skills_eval.{md,json}; live_model_run_qwen.md (July, superseded)
runs/                matched_eval.jsonl, model_skills_eval.jsonl, aborted/, baseline.json (July); sandboxes/ is ignored
scripts/             matched_eval.sbatch, model_skills.sbatch, reverify_matched.py
skills/model_written/ the 20 model-written skills, their prompts and metadata
tests/               provider-free unit tests, including task solvability
```

`init_demo_assets()` deletes and rebuilds `task_templates/*_vN` and `data/`. To change
a task, edit `demo_assets.py`.

## Next steps

The question this project was built for is whether an agent can improve itself by
practising its failures. In the simplest version tested here, a skill the model
writes from its own failures, the answer for Qwen2.5-7B is no detectable gain, and
the skills it wrote did not reflect its actual failures. Adding RL on top of this
loop is not justified by this evidence. Options, roughly in order of cost:

1. Test whether a stronger writer helps: have a larger model write the skills from
   the same 7B traces. If its skills carry the specific lessons the 7B skills
   missed and still produce no gain, prompt-level skills are the bottleneck, not
   the writer.
2. Make the benchmark able to show a difference: add tasks in new repos for
   held-out evaluation, add pass-to-pass tests that pass at baseline, and replace
   tasks that every condition solves or none does. Independent terminal tasks
   such as [Endless Terminals](https://github.com/kanishkg/endless-terminals)
   would avoid sharing repos with the training tasks.
3. Only if some skill text beats no skill text on held-out repos, test
   accumulating skills over successive task batches, with forgetting measured.
4. Otherwise, deprioritise this workstream: on this evidence, prompt-level
   skills do not move a 7B model's repair success.
