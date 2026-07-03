# Live-model run: Qwen2.5-7B (Ollama)

This is a real, non-mock run of the Terminal DreamGym loop where an actual LLM
(`qwen2.5:7b` served locally by Ollama, OpenAI-compatible API) drove every task:
it read the failing pytest output + active `SKILL.md` text, proposed full-file
edits, and was graded by real pytest. **All 60 strategy runs + 36 practice-world
runs were model-driven (20/20 per strategy, zero call failures, zero mock
fallbacks).**

Reproduce with:

```bash
QWEN_MODEL=qwen2.5:7b python -m terminal_dreamgym.cli demo --mode qwen
```

## Results (real model, real pytest)

| Method | Train | Heldout | Adversarial | Practice | Regressions | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Baseline | 2/8 | 1/6 | 2/6 | 6/12 | 0 | - |
| Reflection-only | 4/8 | 2/6 | 1/6 | 5/12 | 1 | REJECTED — overfit detected |
| Terminal DreamGym | 6/8 | 3/6 | 4/6 | 8/12 | 0 | PROMOTED — transfer verified |

| Skill | Practice | Train Δ | Heldout Δ | Adv Δ | Adv regr. | Naive | DreamGym |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| reflection_overfit_skill.md | 0.42 | +0.25 | +0.17 | -0.17 | 1 | PROMOTE | REJECT |
| trace_first_debugging_skill.md | 0.67 | +0.50 | +0.33 | +0.33 | 0 | PROMOTE | PROMOTE |
| minimal_patch_skill.md | 0.67 | +0.50 | +0.33 | +0.33 | 0 | PROMOTE | PROMOTE |
| contract_drift_skill.md | 0.67 | +0.50 | +0.33 | +0.33 | 0 | PROMOTE | PROMOTE |
| error_handling_skill.md | 0.67 | +0.50 | +0.33 | +0.33 | 0 | PROMOTE | PROMOTE |

## Why this matters

The headline thesis reproduced on a real model, not a script:

- **Reflection-only genuinely overfit.** It raised train (2→4) but *regressed*
  on the adversarial split (`python_sku_preserve_comma` — the semantic-comma
  counterexample), dropping adversarial from 2/6 to 1/6. Naive promotion (train
  improved) would have shipped it; the transfer gate rejected it for the real
  adversarial regression.
- **Terminal DreamGym transferred.** It led every split (6/8, 3/6, 4/6) with
  zero adversarial regressions, and the robust skills cleared the practice floor.

## Notes / honesty caveats

- The clean monotonic pattern in the deterministic **mock** mode
  (`2/8 → 5/8 → 6/8`) is an artifact of a scripted agent. Live-model numbers are
  noisier; the contrast lives in **transfer + regressions**, which is the part the
  promotion gate actually checks.
- `min_practice_score` is set to **0.60** (a majority of practice worlds). It was
  calibrated to live-model behaviour, where a robust skill clears ~2/3 of worlds;
  the decisive promotion signal is `adversarial_regressions` / `adversarial_delta`,
  not the practice floor.
- Gemini mode is wired and works (`gemini-smoke` passes), but the free tier caps
  `gemini-2.5-flash` at 20 requests/day, which is too few for the ~200-call full
  loop. Use a paid key or `--mode qwen` for a full live run.
