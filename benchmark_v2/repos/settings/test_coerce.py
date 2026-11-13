import pytest

from coerce import to_bool, to_int, to_list


def test_to_bool_words():
    assert to_bool("yes") is True
    assert to_bool("0") is False
    assert to_bool(True) is True


def test_to_bool_rejects_other_words():
    with pytest.raises(ValueError):
        to_bool("maybe")


def test_to_int_rejects_fraction():
    with pytest.raises(ValueError):
        to_int("2.5")


def test_to_list_drops_blanks():
    assert to_list("web, api,,") == ["web", "api"]
