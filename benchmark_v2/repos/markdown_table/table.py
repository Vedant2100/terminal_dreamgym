"""Render rows of dicts as a GitHub-flavoured Markdown table."""
from cells import format_cell
from columns import infer_columns, marker, parse_spec

MIN_WIDTH = 3  # the narrowest separator cell, ':-:'


def _pad(text: str, width: int, align: str) -> str:
    if align == "right":
        return text.rjust(width)
    if align == "center":
        return text.center(width)
    return text.ljust(width)


def _line(cells) -> str:
    return "| " + " | ".join(cells) + " |"


def render(rows, columns=None, decimals: int = 2) -> str:
    """Markdown table for `rows` (a list of dicts).

    `columns` is a list of keys or a spec string (see columns.parse_spec).
    Missing values are blank. Each column is as wide as its widest cell,
    header included, and never narrower than MIN_WIDTH.
    """
    cols = parse_spec(columns) if isinstance(columns, str) else infer_columns(rows, columns)
    if not cols:
        return ""
    header = [c.title for c in cols]
    body = [[format_cell(row.get(c.key), decimals) for c in cols] for row in rows]
    widths = [max([MIN_WIDTH, len(title)] + [len(r[i]) for r in body]) for i, title in enumerate(header)]
    lines = [
        _line(_pad(t, w, c.align) for t, w, c in zip(header, widths, cols)),
        _line(marker(c.align, w) for w, c in zip(widths, cols)),
    ]
    for r in body:
        lines.append(_line(_pad(t, w, c.align) for t, w, c in zip(r, widths, cols)))
    return "\n".join(lines)
