"""Turning single values into Markdown table cell text."""


def escape(text: str) -> str:
    """Escape what would break a table row: pipes are backslash-escaped and
    newlines become spaces."""
    return text.replace("|", "\\|").replace("\n", " ")


def is_numeric(value) -> bool:
    """True for ints and floats. Booleans are not numbers here."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def format_number(value, decimals: int = 2) -> str:
    """Integers with thousands separators ('1,234'); floats always with
    `decimals` places ('2.00'); booleans as 'yes' / 'no'."""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return f"{value:,}"
    return f"{value:,.{decimals}f}"


def format_cell(value, decimals: int = 2) -> str:
    """Cell text for any value. None is an empty cell."""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return format_number(value, decimals)
    return escape(str(value))
