import pytest

from constraints import best_match, parse_constraint, resolve, satisfies


def test_range_constraint():
    rng = ">=1.2.0,<2.0.0"
    assert satisfies("1.2.0", rng)
    assert satisfies("1.9.9", rng)
    assert not satisfies("2.0.0", rng)
    assert not satisfies("1.1.9", rng)


def test_caret_partial_version():
    assert satisfies("1.2.0", "^1.2")
    assert satisfies("1.9.0", "^1.2")
    assert not satisfies("2.0.0", "^1.2")
    assert not satisfies("1.1.0", "^1.2")


def test_caret_zero_major():
    assert satisfies("0.2.9", "^0.2.3")
    assert not satisfies("0.3.0", "^0.2.3")
    assert not satisfies("0.2.2", "^0.2.3")


def test_tilde_allows_patch_updates_only():
    assert satisfies("1.4.7", "~1.4.2")
    assert not satisfies("1.5.0", "~1.4.2")
    assert not satisfies("1.4.1", "~1.4.2")


def test_prerelease_excluded_by_default():
    assert not satisfies("2.0.0-rc.1", ">=1.0.0")
    assert satisfies("2.0.0-rc.1", ">=1.0.0", include_pre=True)


def test_bad_operator_raises():
    with pytest.raises(ValueError):
        parse_constraint("=>1.0")


def test_best_match():
    available = ["1.0.0", "1.4.0", "1.10.1", "2.0.0"]
    assert best_match(available, "^1.0.0") == "1.10.1"
    assert best_match(available, ">=3.0.0") is None


def test_best_match_prerelease_ordering():
    available = ["1.9.0", "2.0.0-beta.2", "2.0.0-beta.11"]
    assert best_match(available, ">=1.0.0", include_pre=True) == "2.0.0-beta.11"


def test_resolve():
    index = {"left-pad": ["1.0.0", "1.3.0", "2.0.0"], "colors": ["0.5.0", "0.6.1"]}
    assert resolve({"left-pad": "^1.0.0", "colors": ">=0.6.0"}, index) == {"left-pad": "1.3.0", "colors": "0.6.1"}


def test_resolve_unsatisfiable_raises():
    index = {"left-pad": ["1.0.0", "1.3.0"]}
    with pytest.raises(LookupError, match="left-pad"):
        resolve({"left-pad": ">=2.0.0"}, index)
