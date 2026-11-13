"""Render a plain-text sales report from CSV text."""
from aggregate import group_totals, top_groups
from records import parse


def format_money(amount: float) -> str:
    """1234.5 -> '1,234.50'."""
    return f"{amount:,.2f}"


def render(text: str, key: str = "region", top: int = 0) -> str:
    """One row per group, then a TOTAL row.

    `key` is a column name and, like the CSV header, is case-insensitive.
    Groups are listed by name, or only the `top` groups by revenue when top > 0.
    The TOTAL row always covers every group, shown or not.
    """
    key = key.strip().lower()
    totals = group_totals(parse(text), key)
    names = top_groups(totals, top) if top > 0 else sorted(totals)
    lines = [f"{key.upper():<10}{'UNITS':>8}{'REVENUE':>12}"]
    for name in names:
        t = totals[name]
        lines.append(f"{name:<10}{t['units']:>8}{format_money(t['revenue']):>12}")
    units = sum(t["units"] for t in totals.values())
    money = sum(t["revenue"] for t in totals.values())
    lines.append(f"{'TOTAL':<10}{units:>8}{format_money(money):>12}")
    return "\n".join(lines)
