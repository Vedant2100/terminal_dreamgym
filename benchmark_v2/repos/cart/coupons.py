"""Coupons: a percentage or a fixed amount off, with an optional minimum spend."""
from dataclasses import dataclass


@dataclass
class Coupon:
    code: str
    kind: str  # "percent" or "fixed"
    value: int  # whole percent for "percent", cents for "fixed"
    min_spend: int = 0  # cents; the cart subtotal must be at least this
    stackable: bool = False

    def __post_init__(self):
        if self.kind not in ("percent", "fixed"):
            raise ValueError(f"unknown coupon kind: {self.kind}")
        if self.value < 0:
            raise ValueError("coupon value cannot be negative")
        if self.kind == "percent" and self.value > 100:
            raise ValueError("percent coupons cannot exceed 100%")

    def applies_to(self, subtotal: int) -> bool:
        return subtotal >= self.min_spend

    def discount(self, amount: int) -> int:
        """Discount in cents on `amount` cents, rounded down. Never more than `amount`."""
        if self.kind == "percent":
            off = amount * self.value // 100
        else:
            off = self.value
        return min(off, amount)


def _dollars_to_cents(text: str) -> int:
    return round(float(text) * 100)


def parse_coupon(spec: str) -> Coupon:
    """Parse 'CODE:10%' or 'CODE:5.00', with optional ':min=30' and ':stack'.

    Fixed amounts and minimum spends are written in dollars and stored in cents.
    Codes are case-insensitive and stored upper-case.
    """
    code, amount, *options = spec.split(":")
    if amount.endswith("%"):
        kind, value = "percent", int(amount[:-1])
    else:
        kind, value = "fixed", _dollars_to_cents(amount)
    min_spend, stackable = 0, False
    for opt in options:
        if opt == "stack":
            stackable = True
        elif opt.startswith("min="):
            min_spend = _dollars_to_cents(opt[4:])
        else:
            raise ValueError(f"unknown coupon option: {opt}")
    return Coupon(code.upper(), kind, value, min_spend, stackable)
