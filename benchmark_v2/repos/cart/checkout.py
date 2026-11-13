"""Checkout: choose and apply coupons, then add shipping."""
from coupons import Coupon
from items import Cart

DEFAULTS = {
    "free_shipping_over": 5000,  # cents, compared with the discounted amount
    "flat_shipping": 599,  # cents
}


def select_coupons(coupons, subtotal: int) -> list:
    """Pick the coupons to use, in the order they are applied.

    Coupons whose minimum spend is not met are ignored. At most one
    non-stackable coupon is used (the one giving the largest discount) and it
    is applied first; every stackable coupon is then applied on top of it.
    """
    eligible = [c for c in coupons if c.applies_to(subtotal)]
    exclusive = [c for c in eligible if not c.stackable]
    chosen = []
    if exclusive:
        chosen.append(max(exclusive, key=lambda c: c.discount(subtotal)))
    chosen.extend(c for c in eligible if c.stackable)
    return chosen


def apply_coupons(coupons, subtotal: int) -> int:
    """Total discount; each coupon applies to what the previous ones left."""
    remaining = subtotal
    for coupon in coupons:
        remaining -= coupon.discount(remaining)
    return subtotal - remaining


def shipping(amount: int, settings: dict) -> int:
    return 0 if amount >= settings["free_shipping_over"] else settings["flat_shipping"]


def checkout(cart: Cart, coupons=(), settings=None) -> dict:
    """Totals for `cart`. `settings` overrides individual DEFAULTS."""
    config = {**DEFAULTS, **(settings or {})}
    subtotal = cart.subtotal()
    chosen = select_coupons(coupons, subtotal)
    discount = apply_coupons(chosen, subtotal)
    after = subtotal - discount
    ship = 0 if cart.is_empty() else shipping(after, config)
    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": ship,
        "total": after + ship,
        "coupons": [c.code for c in chosen],
    }
