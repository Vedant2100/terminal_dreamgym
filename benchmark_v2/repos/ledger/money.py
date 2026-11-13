"""Parse and format money amounts as integer cents."""
from decimal import ROUND_HALF_UP, Decimal


def to_cents(amount: str) -> int:
    """Parse '1,234.56', '$12' or '-3.5' into integer cents (half-up rounding)."""
    text = amount.strip().replace("$", "").replace(",", "")
    if not text:
        raise ValueError("empty amount")
    value = Decimal(text)
    return int((value * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def format_cents(cents: int) -> str:
    """Format integer cents as '$1,234.50' or '-$2.50'."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100:,}.{cents % 100:02d}"
