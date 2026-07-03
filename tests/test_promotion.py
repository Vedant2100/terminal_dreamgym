from terminal_dreamgym.promotion import SkillMetrics, decide, naive_promote, promote_skill


def test_naive_promotes_if_train_improves():
    assert naive_promote(0.10)


def test_dreamgym_rejects_if_heldout_does_not_improve():
    assert not promote_skill(
        train_delta=0.30,
        heldout_delta=0.0,
        adversarial_delta=0.10,
        adversarial_regressions=0,
        practice_score=0.90,
    )


def test_dreamgym_rejects_if_adversarial_regressions_exist():
    assert not promote_skill(
        train_delta=0.30,
        heldout_delta=0.20,
        adversarial_delta=0.10,
        adversarial_regressions=1,
        practice_score=0.90,
    )


def test_dreamgym_promotes_if_practice_and_transfer_improve():
    assert promote_skill(
        train_delta=0.30,
        heldout_delta=0.20,
        adversarial_delta=0.10,
        adversarial_regressions=0,
        practice_score=0.90,
    )


def test_decide_and_decision_properties():
    metrics = SkillMetrics(
        name="test_skill",
        train_delta=0.0,
        heldout_delta=0.08,
        adversarial_delta=0.04,
        adversarial_regressions=0,
        practice_score=0.75,
    )
    decision = decide(metrics)
    assert not decision.naive
    assert decision.gated
    assert decision.disagree
    assert not decision.false_promotion
    assert decision.wrongly_rejected


def test_false_promotion_detection():
    metrics = SkillMetrics(
        name="false_promoted_skill",
        train_delta=0.10,
        heldout_delta=-0.02,
        adversarial_delta=-0.05,
        adversarial_regressions=1,
        practice_score=0.40,
    )
    decision = decide(metrics)
    assert decision.naive
    assert not decision.gated
    assert decision.disagree
    assert decision.false_promotion
    assert not decision.wrongly_rejected

