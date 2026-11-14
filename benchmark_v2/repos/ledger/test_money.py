import pytest

from money import format_cents, to_cents


def test_to_cents_plain():
    assert to_cents("12.34") == 1234


def test_to_cents_thousands_and_symbol():
    assert to_cents("$1,234.50") == 123450


def test_to_cents_rounds_half_up():
    assert to_cents("0.125") == 13


def test_to_cents_negative():
    assert to_cents("-3.5") == -350


def test_to_cents_empty_raises():
    with pytest.raises(ValueError):
        to_cents("   ")


def test_format_cents():
    assert format_cents(123450) == "$1,234.50"
    assert format_cents(5) == "$0.05"


def test_format_negative_cents():
    assert format_cents(-250) == "-$2.50"
