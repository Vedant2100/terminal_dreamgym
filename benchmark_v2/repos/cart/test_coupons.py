import pytest

from coupons import Coupon, parse_coupon


def test_percent_discount_rounds_down():
    assert Coupon("TEN", "percent", 10).discount(2599) == 259


def test_parse_percent_coupon():
    c = parse_coupon("save10:10%")
    assert (c.code, c.kind, c.value, c.stackable) == ("SAVE10", "percent", 10, False)


def test_parse_fixed_stackable_coupon():
    c = parse_coupon("FIVE:5:stack")
    assert (c.kind, c.value, c.stackable) == ("fixed", 500, True)


def test_parse_rejects_percent_over_100():
    with pytest.raises(ValueError):
        parse_coupon("HUGE:150%")
