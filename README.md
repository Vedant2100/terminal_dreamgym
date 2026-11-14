# Terminal DreamGym

A small harness for testing whether instructions in a terminal coding agent's prompt
("skills") help it repair failing tests. A real LLM reads the failing pytest output
and proposes full-file edits, the harness applies them in a sandbox, and pytest
decides success. It started as a hackathon project (July 2026) whose pitch was a
self-improving agent: diagnose a failure, generate practice repos, write a
`SKILL.md`, and promote the skill only if it transfers to held-out tasks.

## Status (2026-11-13)

Deprioritised on 2026-11-13 after the results below; no further runs are planned.

Four preregistered experiments on Qwen2.5-7B, all scored by strict success (the
target test passes and nothing that passed before breaks), found no detectable
gain from skill text. Each experiment was repeated over several seeds; a seed is
one independent repetition of the whole run, with its own sampled skills and
agent replies. The first three used the original benchmark:

- **Handwritten skills** (four fixed texts) over no skill text: +0.060, 95% CI
  −0.028 to +0.151, in the [matched evaluation](#matched-evaluation-method-and-results)
  (3 seeds), and +0.017, CI −0.072 to +0.114, when run again alongside the
  model-written skills (5 seeds). Neither shows a gain.
- **[Model-written skills](#model-written-skills)**: the model writes its own
  `SKILL.md` from records of its earlier failed attempts (the failing test output,
  its edit, and the result), never seeing the repo it is tested on. Over no skill
  text: +0.000, CI −0.088 to +0.097 (5 seeds).
- **[Skills from a larger writer](#skills-from-a-larger-writer)**: `qwen3-coder:30b`
  writes the skill from the same records of Qwen2.5-7B's attempts, and Qwen2.5-7B
  still solves the tasks. Over no skill text: +0.023, CI −0.072 to +0.118 (5 seeds).

A fourth experiment reran the comparison on **[benchmark v2](#benchmark-v2)**: 52
tasks in 16 new repos, selected by a preregistered calibration run. It has two
primary comparisons, so each uses a 97.5% interval. Handwritten skills over no
skill text: −0.035, CI −0.129 to +0.053, no detectable difference. 30B-written
skills, learnt from failures on the original repos: −0.100, CI −0.187 to −0.018, a
small harm. A placebo (background text about as long as a skill, with no
debugging advice) also scored lower than no skill text (−0.065, not significant), so the harm
may come from extra prompt text rather than the skills' content.

A July demo had reported a large gain from the handwritten skills; it gave them
three times as many model attempts as the baseline (see
[History](#history-the-july-results)). In the original hackathon pipeline the
skills, and the failure diagnoses they were meant to be written from, are fixed
text and rules rather than model output. The model-written skill experiment is the
first test in this repo of the model learning from its own failures.

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
  or none does, and four of the five cli base tasks are never solved. Those are
  solvable (a reference fix passes them); in the failures inspected, the model's
  edits printed errors to stdout instead of stderr, returned the wrong exit code,
  or broke the file.
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
from the matched evaluation and wrote a `SKILL.md` of general guidance. The six are
drawn at random, at most one per base task: five failures, plus one success so
the writer also sees what worked. Each is shown as the initial failing output, the
model's final diff and the final test output. Skills are written leave-one-family-out: the skill
used on a family's tasks comes only from attempts in the other three families, so
the writer never sees the repo the skill is tested on. The matched evaluation
had 3 seeds, so seeds 4 and 5 reuse the attempts of seeds 1 and 2. For each of
the 5 seeds the model writes four skills, one per family, each from a fresh draw
of attempts and a fresh model sample, and that seed's evaluation runs use them: 20 skills, 1,544–1,693 characters
each. None contains a function name from the repo it is tested on, and none was
edited or filtered.

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
| model_skill − placebo | +0.021 [−0.088, +0.139] | 6 / 8 / 5 (a few large gains, more small losses) |
| handwritten_skills − no_skill | +0.017 [−0.072, +0.114] | 7 / 7 / 5 |

What the results show:

- The model-written skills made no detectable difference. By the preregistered
  rule this is a null result. The interval's upper end is about +10 points, so a
  large gain on this benchmark is unlikely (the interval is somewhat too narrow,
  because base tasks within a family share a repo).
- Both kinds of skill text cut replies with no usable edit roughly in half (11–12%
  against 24% with no skill text), while the placebo did not (31%), and the
  placebo also had the lowest first-attempt success (0.194). Numbered
  instructions seem to help the model follow the reply format, but that did not
  raise final success.
- The handwritten-skill gain from the matched evaluation (+0.060) shrank to +0.017.
  The `no_skill` rate itself moved from 0.512 to 0.558 between the two jobs, and
  per-seed rates ranged from 0.505 to 0.611, so differences of a few points are
  within run-to-run variation.
- The skills are generic. No skill says to keep existing functions and imports
  when rewriting a file, though of the 20 prompts given to the writer, 6 showed an
  import error after a rewrite and 7 an attempt that broke another test. Only 2
  skills mention stderr or exit codes, though 15 prompts included stderr-related
  test output. 8 of the 20 advise changing the tests or assertions; the harness
  ignores any edit to a test file.

A 7B model asked to reflect on its failures wrote textbook debugging advice
rather than lessons from those failures, and that advice did not change how often
it solved tasks.

## Skills from a larger writer

Protocol: [`docs/strong_writer_protocol.md`](docs/strong_writer_protocol.md),
written before the run. Results:
[`reports/strong_writer_eval.md`](reports/strong_writer_eval.md), raw records in
`runs/strong_writer_eval.jsonl`, the 20 skills with their prompts in
`skills/strong_written/`.

This tests whether the model-written skills failed because Qwen2.5-7B is a weak
writer. `qwen3-coder:30b` wrote the skills instead, from exactly the same six
attempts per skill, with the same prompt and settings as the 7B writer. The
solver is still Qwen2.5-7B. The 20 skills are 1,116–1,698 characters; none
contains a function name from the repo it is tested on.

**Run.** `no_skill`, `strong_skill` (30B-written), `model_skill` (the unchanged
7B-written skills from the previous section) and `placebo`, all 100 tasks, seeds
1–5, the same settings as before, run together in one job: 2,000 runs, no
infrastructure errors. The job ran on an RTX 6000 Ada rather than the RTX 2080 Ti
used earlier, because the 30B writer needs about 19 GB; every condition shared that
GPU. Every run
was re-scored from its saved sandbox.

| Condition | Strict success | First attempt | Unparseable replies | Passed but broke another test |
| --- | ---: | ---: | ---: | ---: |
| no_skill | 0.568 | 0.312 | 23.1% | 10 |
| strong_skill | 0.592 | 0.335 | 6.9% | 17 |
| model_skill | 0.549 | 0.297 | 11.9% | 5 |
| placebo | 0.571 | 0.217 | 27.9% | 4 |

| A − B | Strict success, 95% CI | Base tasks better / worse / tied |
| --- | --- | --- |
| strong_skill − no_skill (primary) | +0.023 [−0.072, +0.118] | 8 / 4 / 7 |
| strong_skill − model_skill | +0.042 [−0.008, +0.095] | 9 / 4 / 6 |
| strong_skill − placebo | +0.021 [−0.082, +0.118] | 9 / 4 / 6 |
| model_skill − no_skill | −0.019 [−0.084, +0.055] | 6 / 8 / 5 |

What the results show:

- Skills from the 30B writer made no detectable difference either. By the
  preregistered rule this is a null result.
- They may be slightly better than the 7B skills (+0.042), but that interval also
  includes zero, and this comparison was exploratory.
- The 30B skills cut replies with no usable edit to 6.9%, against 23.1% with no
  skill text and 11.9% with the 7B skills. As before, a better-formed reply did
  not lead to more solved tasks. 13 of the 17 runs that passed the target test but
  broke another were on one base task, `python_email_whitespace`.
- The model-written result replicated: 7B skills against no skill text,
  −0.019 here and +0.000 before.
- Both kinds of model-written skill move the same tasks the same way, and the
  placebo does not. `python_slug_punctuation` rose from 0.44 with no skill text to
  0.92 (7B) and 0.96 (30B); `python_sku_preserve_comma` fell from 0.84 to 0.56 and
  0.36. Skill text changes what the model does on particular tasks, but the gains
  and losses cancel.

The 30B skills are cleaner than the 7B ones, but mostly still generic advice.
Counted by hand before the results were in:

| Skill content | 7B writer | 30B writer |
| --- | ---: | ---: |
| Says to keep existing functions, signatures or imports | 0 / 20 | 4 / 20 |
| Advises writing or changing tests | 8 / 20 | 2 / 20 |

11 of the 30B skills tell the solver to run the tests after each edit, which it
cannot do. 11 recommend `.get()` with a default to avoid a `KeyError` (1 of the 7B
skills does), which is wrong for tasks where a missing required setting should
raise an error.

A stronger writer did not make the learn-from-failures loop work. With both a 7B
and a 30B writer, the skills were generic, and neither set changed how often
Qwen2.5-7B solved tasks.

## Benchmark v2

Protocol: [`docs/benchmark_v2_protocol.md`](docs/benchmark_v2_protocol.md),
committed before any model run on the new tasks. Results:
[`reports/v2_eval.md`](reports/v2_eval.md), raw records in `runs/v2_eval.jsonl`
(calibration in `runs/v2_calibration.jsonl`), the five 30B skills in
`skills/strong_written_v2/`.

The first three experiments ran on a benchmark with three problems. Its held-out
tasks shared repos with the training tasks, the check that no passing test breaks
was empty for most tasks, and nearly half the base tasks were solved by every
condition or by none. Benchmark v2 replaces it.

**Tasks.** 16 new small Python repos (`benchmark_v2/repos/`), none related to the
original four, each correct and with 8–16 passing tests. Each repo lists 7–9 bugs,
140 in all; a task is the repo with one bug injected. A validator
(`terminal_dreamgym/benchmark_v2.py`) checks that each bug makes exactly one test
fail and leaves at least 3 others passing, so every task is solvable (the reference
fix is the original code) and every task can catch a fix that breaks other code.
Each bug has a category (logic, error handling, contract between modules, config,
or trap) and an authored difficulty. A trap bug comes with a tempting wrong fix that
the validator confirms passes the target test and breaks another. Claude agents
wrote the repos and bugs before any model run. The commands are under
[Running it](#running-it).

**Calibration.** Qwen2.5-7B with no skill text ran every candidate task 5 times
(seeds 101–105, not reused later). The preregistered rule kept a task if it was
solved in 1–4 of the 5 runs: 52 of 140 tasks, from all 16 repos (70 were never
solved, 18 always). The kept tasks are 25 logic, 14 error handling, 6 contract,
6 trap and 1 config bug.

**Run.** `no_skill`, `handwritten_skills` (the four fixed texts), `strong_skill`
(written by `qwen3-coder:30b` from Qwen2.5-7B's failed attempts on the *original*
benchmark, one skill per seed, used on every v2 task) and `placebo`, on the 52 kept
tasks, seeds 1–5, all in one job: 1,040 runs, no infrastructure errors, every run
re-scored from its saved sandbox with no mismatch. Intervals resample repos, since
tasks in one repo share code; the two comparisons with no skill text are
co-primary and use 97.5% intervals.

| Condition | Strict success | First attempt | Passed but broke another test |
| --- | ---: | ---: | ---: |
| no_skill | 0.488 | 0.346 | 20 |
| handwritten_skills | 0.454 | 0.323 | 31 |
| strong_skill | 0.389 | 0.292 | 24 |
| placebo | 0.423 | 0.319 | 15 |

| A − B | Strict success, CI over repos | Tasks better / worse / tied |
| --- | --- | --- |
| handwritten_skills − no_skill (co-primary, 97.5%) | −0.035 [−0.129, +0.053] | 13 / 17 / 22 |
| strong_skill − no_skill (co-primary, 97.5%) | −0.100 [−0.187, −0.018] | 14 / 26 / 12 |
| strong_skill − placebo (95%) | −0.035 [−0.162, +0.073] | 18 / 18 / 16 |
| placebo − no_skill (95%) | −0.065 [−0.157, +0.033] | 11 / 21 / 20 |

What the results show:

- The handwritten skills made no detectable difference, as on the original
  benchmark.
- The 30B-written skills lowered strict success by 0.100. The upper bound of the
  97.5% interval is below zero, so by the preregistered rule this is harm. The
  effect is in the same direction on all five seeds, each with a different skill
  (−0.019 to −0.173).
- The harm cannot be pinned on the skills' content. The placebo, a length-matched
  text with no debugging advice, also scored below no skill text (−0.065), and the
  30B skills did not differ detectably from it (−0.035). On these tasks, extra
  text in the prompt may hurt by itself; this run cannot separate the two.
- No condition scored above no skill text. The no-skill rate itself fell from
  0.523 on these tasks in calibration to 0.488 here, as expected when tasks are
  selected on a noisy rate; every condition runs on the same tasks, so the
  comparisons are not affected.

The five 30B skills are generic debugging checklists (read after the results were
in). Their specific advice echoes the original benchmark's tasks, such as a CLI
`--json` flag, email normalisation and config keys: 4 of 5 talk about JSON output,
3 about stderr and exit codes, one about `+` tags in email addresses and one
recommends `.get()` for config keys. 3 tell the solver to run tests after each
edit, which it cannot do.

On repos it had not seen, neither handwritten skills nor skills written by a
stronger model from a weaker model's failures helped Qwen2.5-7B. v2 removes the
validity problems listed above, but its intervals are about as wide as the original
benchmark's (roughly ±0.09): it still cannot detect an effect much smaller than
0.1.

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
so its output says nothing about self-improvement. `evaluate` reports `gated_false_promotion_rate` (promoted by the transfer gate, held-out
not improved) and `practice_gate_false_pass_rate` (cleared the practice floor, held-out
not improved).

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

Skills from a larger writer: `write-skills --writer-model qwen3-coder:30b` writes
with that model, and `matched-eval --strong-skills-dir DIR` supplies the
`strong_skill` condition. On the cluster, `sbatch scripts/strong_writer.sbatch
skills/strong_written runs/strong_writer_eval.jsonl 1,2,3,4,5` does both on one
RTX 6000 Ada (about 2 h 16 min). The writer model needs about 19 GB of GPU memory.

`matched-eval` resumes from its output file and reruns only records marked
`infra_error`. On the UCR cluster, `sbatch scripts/matched_eval.sbatch
runs/matched_eval.jsonl --seeds 1,2,3` starts Ollama in the FrontierMemory Apptainer
image on one GPU and runs the same command. A full run took 71 minutes on an RTX
2080 Ti.

Benchmark v2:

```bash
python -m terminal_dreamgym.cli build-v2                     # validate every bug, write task_templates_v2/ and data/tasks_v2.json
sbatch scripts/v2.sbatch calibrate runs/v2_calibration.jsonl 101,102,103,104,105
python -m terminal_dreamgym.cli v2-select --results runs/v2_calibration.jsonl --out benchmark_v2/kept_tasks.txt
python -m terminal_dreamgym.cli build-v2 --keep benchmark_v2/kept_tasks.txt
sbatch scripts/v2.sbatch evaluate runs/v2_eval.jsonl 1,2,3,4,5  # writes the 30B skills, then runs the four conditions
python -m terminal_dreamgym.cli v2-report --results runs/v2_eval.jsonl --tasks-file data/tasks_v2.json --name v2_eval
python scripts/reverify_matched.py runs/v2_eval.jsonl data/tasks_v2.json
```

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
terminal_dreamgym/   agent, sandbox, pipeline steps, matched_eval.py, benchmark_v2.py, v2_analysis.py, cli.py
task_templates/      20 task repos (*_v1..v5), generated by demo_assets.py from the 4 base repos
benchmark_v2/        repos/ (16 correct repos, each with bugs.json), AUTHORING.md, kept_tasks.txt
task_templates_v2/   built from benchmark_v2 by `cli build-v2`; ignored by git
data/                tasks.json (100 tasks), splits.json, tasks_v2.json (52 kept), tasks_v2_candidates.json (140)
docs/                matched_eval_protocol.md, model_skills_protocol.md, strong_writer_protocol.md, benchmark_v2_protocol.md
reports/             matched_eval, model_skills_eval, strong_writer_eval, v2_eval (.md and .json); live_model_run_qwen.md (July, superseded)
runs/                matched_eval.jsonl, model_skills_eval.jsonl, strong_writer_eval.jsonl, v2_calibration.jsonl, v2_eval.jsonl, aborted/, baseline.json (July); sandboxes/ is ignored
scripts/             matched_eval.sbatch, model_skills.sbatch, strong_writer.sbatch, v2.sbatch, reverify_matched.py
skills/model_written/ the 20 skills written by Qwen2.5-7B, their prompts and metadata
skills/strong_written/ the 20 skills written by qwen3-coder:30b, same layout
skills/strong_written_v2/ the 5 skills (one per seed) used on benchmark v2
tests/               provider-free unit tests, including task solvability and v2 bug validation
```

`init_demo_assets()` deletes and rebuilds `task_templates/*_vN` and `data/`. To change
a task, edit `demo_assets.py`.

## Next steps

The question this project was built for is whether an agent can improve itself by
practising its failures. In the simplest version tested here, a skill the model
writes from its own failures, the answer for Qwen2.5-7B is no detectable gain, and
the skills it wrote did not reflect its actual failures. Skills written from the
same failures by a 30B model gave no detectable gain either. On benchmark v2, with
new repos, handwritten skills gave no detectable gain and 30B skills learnt on other
repos lowered success slightly. Adding RL on top of this loop is not
justified by this evidence.

This workstream was deprioritised on 2026-11-13; no further runs are planned. If it
is resumed, two experiments would be most informative:

1. Separate the effect of extra prompt text from the effect of skill content (for
   example, several placebo lengths), since on v2 the placebo also scored lower
   than no skill text.
2. Test skills written from failures on the *same* v2 repos (held-out bugs, same
   code), which is the setting where specific advice could help. Independent
   terminal tasks such as
   [Endless Terminals](https://github.com/kanishkg/endless-terminals) are another
   source of new tasks.
