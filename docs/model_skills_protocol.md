# Model-written skills: protocol

Written and committed before any model run under this protocol (2026-11-12).
Changes are listed under Deviations at the bottom.

## Question

When Qwen2.5-7B writes its own `SKILL.md` from traces of its earlier failed
attempts, does that skill raise its strict success on repositories it has not
seen, compared with no skill text?

This is the smallest version of the project's self-improvement loop: failures,
then a model-written skill, then better behaviour on new tasks. It does not
include practice repos, promotion gates or weight updates.

The earlier matched evaluation (`docs/matched_eval_protocol.md`,
`reports/matched_eval.md`) found no detectable gain from four handwritten skills
(+0.060, 95% CI −0.028 to +0.151).

## Writing the skills

- **Source traces:** the `no_skill` runs of the earlier matched evaluation
  (`runs/matched_eval.jsonl`, seeds 1–3). Evaluation seed *s* uses source seed
  ((*s* − 1) mod 3) + 1, so seeds 4 and 5 reuse the traces of seeds 1 and 2 with a
  new writing sample.
- **Leave one family out:** the skill used on family F's tasks is written only
  from traces of the other three families, from any split. The writer never sees
  F's repository, so a gain on F cannot come from repository knowledge.
- **Selection:** per (seed, F), up to 5 failed runs and 1 successful run,
  at most one per base task, drawn in a seeded random order. Each trace shows
  the initial failing output, the model's final diff and the final test output.
- **Writer:** the same `qwen2.5:7b` model, temperature 0.7, max 2,048 output
  tokens, one call per (seed, F). The prompt asks for general guidance with no
  file, function, test names or literal values from the traces, and at most
  1,500 characters. A reply over 1,700 characters (the four handwritten skills
  total 1,676) is cut at the last line break before 1,700, so no step ends
  mid-sentence. (Set after the smoke run, before the counted run: all four smoke
  skills overran the request, at 2,000–2,500 characters.)
- 5 seeds × 4 families = 20 skills, saved in `skills/model_written/` with the
  prompt and metadata. A leak check lists any function name from F's repo that
  appears in F's skill. Skills are used as written; none are edited or filtered.

## Conditions

| Condition | ACTIVE SKILLS block |
| --- | --- |
| `no_skill` | none |
| `model_skill` | the model-written skill for this task's family and seed |
| `handwritten_skills` | the four handwritten skills |
| `placebo` | length-matched background text with no debugging advice |

All other settings are those of the matched evaluation: up to 3 attempts per
task, temperature 0.7, a distinct seed per attempt, max 2,048 output tokens,
context 16,384, all 100 tasks. Seeds 1–5, so 4 × 100 × 5 = 2,000 runs in a
shuffled order. All conditions are rerun together in one job; results from the
earlier evaluation are not reused for the comparison.

## Outcome and analysis

As in the matched evaluation: strict success (target test passes and no
previously passing test breaks); base tasks that pass before any edit are
excluded (`python_price_currency_spacing`); per condition, a base task's score is
its mean over variants and seeds; 95% bootstrap CIs resample the 19 base tasks.

**Primary:** `model_skill − no_skill`. Claim an improvement only if the CI lower
bound is above 0 and harm only if the upper bound is below 0.

**Secondary (exploratory, uncorrected):** `model_skill − handwritten_skills`,
`model_skill − placebo`, `handwritten_skills − no_skill` (a replication of the
earlier primary with 5 seeds), per-split and per-family differences, first-attempt
success, unparseable replies, per-seed results (each seed has its own skill), and
the leak check.

## Run rules

- Smoke run first: seed 99, separate skills directory and output file, 4 tasks.
  Not analysed.
- One GPU job runs `write-skills` then `matched-eval`
  (`scripts/model_skills.sbatch`).
- Records with `infra_error` are rerun by resuming; nothing else is rerun. A
  skill is never rewritten once its file exists.

## Deviations

- Job 311228 was submitted while a unit test of the line-break cut was failing
  and was cancelled after 5 seconds, before any skill or result was written. The
  test, not the code, was wrong; it was fixed and the counted run is job 311230
  (commit `9f2974f`).
