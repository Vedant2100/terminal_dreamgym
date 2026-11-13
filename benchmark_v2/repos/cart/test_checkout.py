from checkout import checkout
from coupons import Coupon, parse_coupon
from items import Cart


def cart_of(cents):
    cart = Cart()
    cart.add("thing", cents)
    return cart


def test_best_exclusive_coupon_wins():
    coupons = [Coupon("TWENTY", "percent", 20), Coupon("FIFTEEN", "fixed", 1500)]
    result = checkout(cart_of(10000), coupons)
    assert result["discount"] == 2000


def test_stackable_coupon_applies_after_exclusive():
    coupons = [Coupon("FIVE", "fixed", 500, stackable=True), Coupon("TEN", "percent", 10)]
    # 10% of 10000 = 1000 first, then 500 off the remaining 9000
    assert checkout(cart_of(10000), coupons)["discount"] == 1500


def test_discount_never_exceeds_subtotal():
    coupons = [Coupon("A", "fixed", 3000), Coupon("B", "fixed", 3000, stackable=True)]
    result = checkout(cart_of(4000), coupons)
    assert result["discount"] == 4000
    assert result["total"] == 599


def test_parsed_minimum_spend_is_in_dollars():
    coupon = parse_coupon("BIG:10%:min=30")
    result = checkout(cart_of(2500), [coupon])
    assert result["discount"] == 0
    assert result["coupons"] == []


def test_free_shipping_uses_discounted_amount():
    result = checkout(cart_of(5500), [Coupon("TEN", "fixed", 1000)])
    assert result["shipping"] == 599
    assert checkout(cart_of(5000))["shipping"] == 0


def test_emptied_cart_has_no_shipping():
    cart = Cart()
    cart.add("apple", 120, 2)
    cart.remove("apple", 2)
    assert checkout(cart) == {"subtotal": 0, "discount": 0, "shipping": 0, "total": 0, "coupons": []}


def test_settings_override_single_default():
    result = checkout(cart_of(1000), settings={"flat_shipping": 300})
    assert result["shipping"] == 300
    assert checkout(cart_of(6000), settings={"flat_shipping": 300})["shipping"] == 0
