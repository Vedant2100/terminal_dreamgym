import pytest

from convert import convert


def test_length_conversion():
    assert convert(12.5, "km", "m") == pytest.approx(12500)
    assert convert(1, "mi", "ft") == pytest.approx(5280)


def test_mass_conversion():
    assert convert(2, "lb", "kg") == pytest.approx(0.90718474)


def test_fahrenheit_to_celsius():
    assert convert(212, "F", "C") == pytest.approx(100)
    assert convert(-40, "F", "C") == pytest.approx(-40)


def test_celsius_to_kelvin():
    assert convert(0, "C", "K") == pytest.approx(273.15)


def test_incompatible_units_raise_value_error():
    with pytest.raises(ValueError):
        convert(1, "m", "kg")


def test_unknown_unit_raises_key_error():
    with pytest.raises(KeyError):
        convert(1, "m", "parsec")
