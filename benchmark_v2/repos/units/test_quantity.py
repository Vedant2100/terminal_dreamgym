import pytest

from quantity import Quantity, format_quantity, parse_quantity


def test_parse_simple():
    assert parse_quantity("12.5 km") == Quantity(12.5, "km")


def test_parse_alias_any_case():
    assert parse_quantity("3 Kilometers") == Quantity(3.0, "km")


def test_parse_negative_temperature():
    assert parse_quantity("-40 °F") == Quantity(-40.0, "F")


def test_parse_malformed_raises_value_error():
    with pytest.raises(ValueError):
        parse_quantity("km 12")


def test_to_fahrenheit():
    assert parse_quantity("37 C").to("F").value == pytest.approx(98.6)


def test_add_converts_units():
    total = Quantity(1, "km") + Quantity(500, "m")
    assert total.unit == "km"
    assert total.value == pytest.approx(1.5)


def test_format_with_precision():
    assert format_quantity(Quantity(12.5, "km")) == "12.50 km"
    assert format_quantity(Quantity(21.456, "C"), precision=1) == "21.5 °C"


def test_format_kelvin_has_no_degree_sign():
    assert format_quantity(Quantity(300, "K"), precision=0) == "300 K"


def test_format_never_negative_zero():
    assert format_quantity(Quantity(-0.001, "m")) == "0.00 m"
