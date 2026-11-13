# Skills from a larger writer: protocol

Written and committed before any model run under this protocol (2026-11-13).
Changes are listed under Deviations at the bottom.

## Question

When a larger model, `qwen3-coder:30b`, writes the `SKILL.md` from the same
Qwen2.5-7B traces, does that skill raise Qwen2.5-7B's strict success on
repositories the writer has not seen, compared with no skill text?

The model-written skills experiment (`docs/model_skills_protocol.md`,
`reports/model_skills_eval.md`) found no gain when Qwen2.5-7B wrote its own
skills: +0.000 (95% CI −0.088 to +0.097). Those skills were generic advice. None
said to keep existing functions and imports when rewriting a file, although six
of the writer's prompts showed an import error after a rewrite. This experiment
asks whether that null comes from a weak writer. If skills from a stronger
writer also give no gain, the limit is skill text in the prompt, not the 7B
model's skill writing.

## Writing the skills

Everything is as in the model-written skills protocol except the writer model:

- Same source traces (`runs/matched_eval.jsonl`, `no_skill`, seeds 1–3; seed *s*
  uses source seed ((*s* − 1) mod 3) + 1).
- Same leave-one-family-out selection, the same random draw per (seed, family),
  so each strong skill is written from exactly the attempts the matching 7B
  skill was written from.
- Same prompt, temperature 0.7, max 2,048 output tokens, the same per-call seed,
  and the same 1,700-character cut at a line break.
- Writer: `qwen3-coder:30b` (Ollama, 18.6 GB, on two RTX 2080 Ti GPUs). It was
  chosen before any run as the largest coding model already in the local model
  store. No other writer is tried under this protocol.
- 5 seeds × 4 families = 20 skills, saved in `skills/strong_written/` with
  prompts and metadata. Leak check as before. Skills are used as written.

## Conditions

| Condition | ACTIVE SKILLS block |
| --- | --- |
| `no_skill` | none |
| `strong_skill` | the 30B-written skill for this task's family and seed |
| `model_skill` | the 7B-written skill from `skills/model_written/` (unchanged files) |
| `placebo` | length-matched background text with no debugging advice |

The solver is `qwen2.5:7b` in every condition. All other settings are those of
the earlier evaluations: up to 3 attempts per task, temperature 0.7, a distinct
seed per attempt, max 2,048 output tokens, context 16,384, all 100 tasks, seeds
1–5, so 4 × 100 × 5 = 2,000 runs in a shuffled order, in one job. Results from
earlier runs are not reused.

## Outcome and analysis

As before: strict success; `python_price_currency_spacing` excluded; per
condition, a base task's score is its mean over variants and seeds; 95%
bootstrap CIs resample the 19 base tasks.

**Primary:** `strong_skill − no_skill`. Claim an improvement only if the CI
lower bound is above 0 and harm only if the upper bound is below 0.

**Secondary (exploratory, uncorrected):** `strong_skill − model_skill`,
`strong_skill − placebo`, `model_skill − no_skill` (a replication),
per-split and per-family differences, first-attempt success, unparseable
replies, per-seed results, and the leak check. A hand count of how many of the
20 strong skills say to keep existing functions and imports, and how many advise
changing tests, compared with the 7B skills (0 of 20 and 8 of 20).

## Run rules

- Smoke run first: seed 99, `skills/strong_written_smoke/`,
  `runs/smoke_strong_writer.jsonl`, conditions `no_skill,strong_skill`, 4 tasks.
  Not analysed.
- One GPU job (`scripts/strong_writer.sbatch`, two GPUs) runs `write-skills`
  with the 30B writer, unloads it, then runs `matched-eval`.
- Records with `infra_error` are rerun by resuming; nothing else is rerun. A
  skill is never rewritten once its file exists.

## Deviations

None yet.
