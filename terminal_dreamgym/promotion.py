from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillMetrics:
    """Deltas of one skill vs the baseline, plus regression counts and practice score."""

    name: str
    train_delta: float
    heldout_delta: float
    adversarial_delta: float
    adversarial_regressions: int
    practice_score: float


def naive_promote(train_delta: float) -> bool:
    return train_delta > 0


def promote_skill(
    train_delta: float,
    heldout_delta: float,
    adversarial_delta: float,
    adversarial_regressions: int,
    practice_score: float,
    min_heldout_delta: float = 0.01,
    min_practice_score: float = 0.60,
    max_adversarial_regressions: int = 0,
) -> bool:
    return (
        train_delta >= 0
        and heldout_delta >= min_heldout_delta
        and adversarial_delta >= 0
        and adversarial_regressions <= max_adversarial_regressions
        and practice_score >= min_practice_score
    )


@dataclass(frozen=True)
class Decision:
    name: str
    train_delta: float
    heldout_delta: float
    adversarial_delta: float
    adversarial_regressions: int
    practice_score: float
    naive: bool
    gated: bool

    @property
    def disagree(self) -> bool:
        return self.naive != self.gated

    @property
    def false_promotion(self) -> bool:
        """A false promotion happens if the policy promotes but held-out is flat/regressed."""
        return self.heldout_delta <= 0

    @property
    def wrongly_rejected(self) -> bool:
        """A wrongly rejected skill improves held-out but train is flat/down (naive rejects)."""
        return self.heldout_delta > 0 and self.train_delta <= 0


def decide(
    metrics: SkillMetrics,
    min_heldout_delta: float = 0.01,
    min_practice_score: float = 0.60,
    max_adversarial_regressions: int = 0,
) -> Decision:
    return Decision(
        name=metrics.name,
        train_delta=metrics.train_delta,
        heldout_delta=metrics.heldout_delta,
        adversarial_delta=metrics.adversarial_delta,
        adversarial_regressions=metrics.adversarial_regressions,
        practice_score=metrics.practice_score,
        naive=naive_promote(metrics.train_delta),
        gated=promote_skill(
            train_delta=metrics.train_delta,
            heldout_delta=metrics.heldout_delta,
            adversarial_delta=metrics.adversarial_delta,
            adversarial_regressions=metrics.adversarial_regressions,
            practice_score=metrics.practice_score,
            min_heldout_delta=min_heldout_delta,
            min_practice_score=min_practice_score,
            max_adversarial_regressions=max_adversarial_regressions,
        ),
    )

