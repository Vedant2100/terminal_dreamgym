# Benchmark v2: protocol

Written and committed before any model run on benchmark v2 (2026-11-13), and
before calibration. Changes are listed under Deviations at the bottom.

## Why a new benchmark

Three preregistered experiments on the original benchmark found no detectable
gain from skill text (handwritten, 7B-written, 30B-written). That benchmark could
show only a large effect:

1. Held-out tasks share repos with train tasks (4 repos, 20 base tasks, each with
   5 near-identical variants).
2. The pass-to-pass check (no previously passing test breaks) is empty for 14 of
   19 base tasks, because all of a repo's target tests fail at once.
3. 9 of 19 base tasks tie in every condition (all conditions solve them, or none
   does).
4. With 19 independent units, the 95% interval is about ±0.09.

## Construction

Benchmark v2 (`benchmark_v2/`, rules in `benchmark_v2/AUTHORING.md`) is 16 new,
small, correct Python repos in new domains, each with 8–16 tests. Each repo lists
7–9 bugs, 140 in all; each bug is one candidate task: the repo with that bug
injected. By category: 72 logic, 27 error handling, 20 contract, 17 trap, 4
config.
`terminal_dreamgym/benchmark_v2.py` validates every bug:

- the correct repo passes all its tests;
- with the bug, the target test fails and every other test still passes, with
  at least 3 others (so the pass-to-pass check is never empty);
- bugs edit source files only; the reference fix is the original code;
- a `trap` bug ships a tempting wrong fix, which must make the target pass and
  break another test.

The repos and bugs were written by Claude agents (the example repo `ledger/` by
the coordinating session, the other 15 by three sub-agents). They were written
before any model run on them and are not edited after calibration starts, except
to remove a task (recorded below).

## Stage 1: calibration (selection only)

- Condition `no_skill` only, every candidate task, seeds 101–105.
- Settings as in all earlier evaluations: `qwen2.5:7b` via Ollama, up to 3
  attempts, temperature 0.7, a distinct seed per attempt, max 2,048 output tokens,
  context 16,384 tokens.
- **Keep rule:** keep a task if it is strictly solved in 1, 2, 3 or 4 of its 5
  calibration runs. Tasks solved in 0 or 5 are dropped. This band is fixed now.
- If fewer than 50 tasks are kept, stop and report; the band is not widened
  without a new protocol entry.
- Calibration results are used only for selection. They are never pooled with
  the stage 2 results.

Selecting on `no_skill` alone, with seeds that stage 2 does not reuse, means the
selection cannot favour any skill condition. Regression to the mean affects
`no_skill`'s stage 2 rate, but equally for all conditions, since every condition
runs on the same kept tasks with fresh seeds.

## Stage 2: evaluation

Conditions, all on the kept tasks, seeds 1–5, same settings as stage 1, one job,
shuffled order:

| Condition | ACTIVE SKILLS block |
| --- | --- |
| `no_skill` | none |
| `handwritten_skills` | the four handwritten skills |
| `strong_skill` | a skill written by `qwen3-coder:30b`, one per seed |
| `placebo` | length-matched background text with no debugging advice |

**Strong skills for v2.** Same writer, prompt, settings and length cap as
`docs/strong_writer_protocol.md`, with one change: because no v2 repo appears in
the original benchmark, each seed's skill is written from Qwen2.5-7B `no_skill`
attempts drawn from all four original families (`runs/matched_eval.jsonl`; 5
failures and 1 success, at most one per base task; seed *s* uses source seed
((*s* − 1) mod 3) + 1). One skill per seed is used on every v2 task. This is a
clean transfer test: the skill is learnt on one set of repos and tested on
entirely different ones.

## Outcome and analysis

- Strict success: the target test passes and no test that passed before the edit
  fails afterwards.
- A task's score per condition is its mean over seeds; differences are means over
  tasks of (A − B).
- **Primary interval:** a cluster bootstrap that resamples repos (10,000
  repetitions), because tasks in one repo share code. Task-level bootstrap
  intervals are reported too, as secondary.
- **Two co-primary comparisons**, each at 97.5% (Bonferroni over the two):
  `handwritten_skills − no_skill` and `strong_skill − no_skill`. Claim an
  improvement only if the lower bound is above 0; harm only if the upper bound is
  below 0.
- **Secondary (exploratory, uncorrected):** `strong_skill − handwritten_skills`,
  `handwritten_skills − placebo`, `strong_skill − placebo`, `placebo − no_skill`;
  by category (logic, contract, error_handling, config, trap) and difficulty;
  first-attempt success; unparseable replies; runs that pass the target but
  break another test.

## Run rules

- Smoke run first: 4 tasks, seed 99, not analysed.
- Records with `infra_error` are rerun by resuming; nothing else is rerun.
- Strong skills are written once (`skills/strong_written_v2/`) and never
  rewritten.

## Deviations

None yet.
