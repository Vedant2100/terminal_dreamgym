"""Column specs: which columns appear, in what order, and how they are aligned."""
from dataclasses import dataclass

from cells import is_numeric

SYMBOLS = {"<": "left", ">": "right", "^": "center"}


@dataclass
class Column:
    key: str
    title: str
    align: str = "left"  # "left", "right" or "center"


def title_for(key: str) -> str:
    """'unit_price' -> 'Unit Price'."""
    return key.replace("_", " ").title()


def infer_columns(rows, order=None) -> list:
    """Columns for `rows`.

    With `order`, exactly those keys in that order; otherwise every key, in
    order of first appearance across the rows. A column is right-aligned when
    it has at least one value and all of its non-None values are numbers.
    """
    if order is None:
        order = []
        for row in rows:
            for key in row:
                if key not in order:
                    order.append(key)
    columns = []
    for key in order:
        values = [row.get(key) for row in rows if row.get(key) is not None]
        numeric = bool(values) and all(is_numeric(v) for v in values)
        columns.append(Column(key, title_for(key), "right" if numeric else "left"))
    return columns


def parse_spec(spec: str) -> list:
    """Parse 'name, price:>, note:^' into Columns.

    '<' is left (the default), '>' right and '^' center.
    """
    columns = []
    for part in spec.split(","):
        key, _, symbol = part.strip().partition(":")
        if symbol and symbol not in SYMBOLS:
            raise ValueError(f"unknown alignment {symbol!r} for column {key!r}")
        columns.append(Column(key, title_for(key), SYMBOLS[symbol or "<"]))
    return columns


def marker(align: str, width: int) -> str:
    """The separator-row cell, e.g. ':--', '--:' or ':-:' at width 3."""
    if align == "right":
        return "-" * (width - 1) + ":"
    if align == "center":
        return ":" + "-" * (width - 2) + ":"
    return ":" + "-" * (width - 1)
