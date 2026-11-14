"""Parse CSV text into typed records."""
import csv
import io

SCHEMA = {"region": str, "product": str, "units": int, "price": float}


class ParseError(ValueError):
    """A row could not be read. The message names the 1-based line number."""


def parse(text: str, schema: dict = SCHEMA) -> list:
    """Parse CSV text with a header row into a list of dicts.

    Column names match case-insensitively; whitespace around names and values
    is stripped. Blank lines are skipped but still count for line numbers.
    Columns not in the schema are dropped; a missing schema column is an error.
    Empty text gives an empty list.
    """
    reader = csv.reader(io.StringIO(text))
    header = next(reader, None)
    if header is None:
        return []
    header = [name.strip().lower() for name in header]
    missing = [name for name in schema if name not in header]
    if missing:
        raise ParseError(f"line 1: missing columns: {', '.join(missing)}")
    records = []
    for line_no, row in enumerate(reader, start=2):
        if not any(cell.strip() for cell in row):
            continue
        record = {}
        for name, cell in zip(header, row):
            if name not in schema:
                continue
            try:
                record[name] = schema[name](cell.strip())
            except ValueError:
                raise ParseError(f"line {line_no}: bad {name} {cell!r}") from None
        records.append(record)
    return records
