# Terminal DreamGym: Sweep Evaluation Report

## 1. Research Overview

Self-improving agent systems struggle with the proxy-reality gap: a skill can raise the score on visible training failures while regressing or failing to transfer to held-out situations. Terminal DreamGym studies how naive training-only gates compare to transfer gates under multi-seed and multi-model settings.
- **Models Swept**: qwen
- **Seeds Swept**: 42, 43 (2 total)

## Model: qwen

### Baseline Scores

The baseline agent uses only the SOP (no generated skills active). Scores represent mean ± 95% confidence intervals:
- **Train**: 20.0% ± 0.0%
- **Heldout**: 30.0% ± 0.0%
- **Adversarial**: 10.0% ± 0.0%

### Per-Skill Sweep Results

Each candidate skill is evaluated individually. Delts represent mean ± 95% confidence intervals relative to the baseline of each seed:

| Skill | Train Δ | Heldout Δ | Adv Δ | Adv Regressions | Practice Score | Naive Rate | Gated Rate | Disagree Rate | Wrongly Rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `reflection_overfit_skill.md` | +0.0% ± 0.0% | +0.0% ± 0.0% | +0.0% ± 0.0% | 0.00 ± 0.00 | 80.0% ± 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| `trace_first_debugging_skill.md` | +0.0% ± 0.0% | +0.0% ± 0.0% | +0.0% ± 0.0% | 0.00 ± 0.00 | 80.0% ± 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| `minimal_patch_skill.md` | +0.0% ± 0.0% | +0.0% ± 0.0% | +0.0% ± 0.0% | 0.00 ± 0.00 | 80.0% ± 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| `contract_drift_skill.md` | +0.0% ± 0.0% | +0.0% ± 0.0% | +0.0% ± 0.0% | 0.00 ± 0.00 | 80.0% ± 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| `error_handling_skill.md` | +0.0% ± 0.0% | +0.0% ± 0.0% | +0.0% ± 0.0% | 0.00 ± 0.00 | 80.0% ± 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

**Dreamed-Curriculum trust metric**: The False-Promotion Rate of self-gating is **100.0%**. This represents the percentage of runs where a skill passed the dreamed gate (practice score ≥ 60.0%) but failed to generalize in reality (held-out delta ≤ 0.0%).

### Stacking & Interference Diagnostics

When multiple skills are promoted by a policy, they are stacked together. If the stacked heldout score is below the best single promoted skill, we observe skill interference. Stats represent mean ± 95% confidence intervals:

#### Policy: NAIVE
- **Interference Rate**: 0.0% of seeds
- **Stacked Heldout Δ**: +0.0% ± 0.0%
- **Stacked Adversarial Δ**: +0.0% ± 0.0%
- **Interference Delta (Stacked vs Best)**: +0.0% ± 0.0%

#### Policy: GATED
- **Interference Rate**: 0.0% of seeds
- **Stacked Heldout Δ**: +0.0% ± 0.0%
- **Stacked Adversarial Δ**: +0.0% ± 0.0%
- **Interference Delta (Stacked vs Best)**: +0.0% ± 0.0%

