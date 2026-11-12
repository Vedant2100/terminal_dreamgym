# Matched-condition evaluation: protocol

Written and committed before any model run under this protocol (2026-11-12).
Changes after the run starts are listed at the bottom with a reason.

## Question

Does putting the four handwritten skill texts in the prompt raise Qwen2.5-7B's
strict success on the 100 Terminal DreamGym tasks, compared with no skill text,
when every condition gets the same model, sampling settings, attempts and scoring?

This tests the skill texts, not self-improvement. In this repository no model
writes skills: `generate_skills()` writes fixed strings, and `diagnose_run()`
applies fixed rules. A positive result would justify building real skill
generation next; it would not show that the system improves itself.

## Why a new protocol

- The July demo gave the baseline 1 model attempt and the skill strategies up to 3,
  so a skill effect was confounded with extra attempts.
- Success counted only the target test. A fix that broke other behaviour still
  counted.
- The committed "two-seed sweep" (`runs/evaluation.json`) was mock data written by
  the unit test `test_evaluate_sweep_logic`, not a model run.
- Temperature 0.1 with a fixed seed made "seeds" near-duplicates.

## Conditions

All differ only in the prompt's ACTIVE SKILLS block.

| Condition | Skill text |
| --- | --- |
| `no_skill` | none |
| `handwritten_skills` | the four handwritten skills (trace-first, minimal patch, contract drift, error handling), 1,676 characters |
| `placebo` | length-matched background text with no debugging advice |
| `symptom_patch` | the handwritten "patch the last visible symptom" text, formerly called `reflection_only` |

## Fixed settings

- Model `qwen2.5:7b` via Ollama (OpenAI-compatible API), context 16,384 tokens.
- Temperature 0.7, max 2,048 output tokens, Ollama seed = run seed.
- Up to 3 model attempts per task for every condition. A reply with no parseable
  edit uses an attempt. The loop stops early only when the target test passes.
- Seeds 1, 2, 3. All 100 tasks × 4 conditions × 3 seeds = 1,200 runs, in a
  shuffled order so server-side drift affects all conditions alike.

## Outcome

**Strict success:** the task's scoring command exits 0 **and** no test that passed
in the untouched repo fails after the agent's edits (pass-to-pass check over the
whole suite, run by the harness and not shown to the agent). A full-suite pass
is not required because every template repo contains other tasks' bugs by design.

## Unit of analysis

The 100 tasks are 20 base tasks × 5 near-identical variants (`_v1`–`_v5`). The base
task is the independent unit: per condition, a base task's score is its mean over
variants and seeds; confidence intervals resample base tasks (10,000 bootstrap
draws, percentile 95% CI).

Base tasks whose target test already passes before any edit are excluded from the
analysis (identified mechanically from the run records). Before the run this is
known to be `python_price_currency_spacing` (held-out), leaving 19 base tasks.

## Primary comparison

`handwritten_skills − no_skill` on strict success over all remaining base tasks.
Claim an improvement only if the 95% CI lower bound is above 0. Claim harm only
if the upper bound is below 0. Otherwise report "no detectable difference" with
the interval.

## Secondary (exploratory, no multiplicity correction)

- `handwritten_skills − placebo` (content vs extra text), `placebo − no_skill`,
  `symptom_patch − no_skill`.
- Each comparison per split (train / held-out / adversarial). With 6–8 base
  tasks per split these are imprecise; they are descriptive.
- First-attempt strict success (a single-attempt view of the same runs).
- Target-test-only success, and the count of runs where the target passed but a
  previously passing test broke.
- Unparseable-reply rate, tokens, truncated replies.

Train / held-out / adversarial labels are kept for continuity, but no condition
is trained on anything, so all splits are evaluation data here.

## Run rules

- One GPU, serialized with the user's other jobs
  (`--job-name=fm-serial --dependency=singleton`).
- A smoke run on a few tasks with a separate output file and seed 99 checks the
  pipeline and timing. It is not analysed.
- Runs with a model-call failure (`infra_error`) are rerun automatically by the
  resume logic; nothing else is rerun. If the server stalls, restart the server
  and resume; record it below.
- All 1,200 records are reported; no task, seed or condition is dropped except by
  the exclusion rule above.

## Deviations

(none yet)
