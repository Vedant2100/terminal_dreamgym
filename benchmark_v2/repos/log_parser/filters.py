"""Select records by status and time."""


def status_class(status: int) -> str:
    """404 -> '4xx'."""
    return f"{status // 100}xx"


def errors(records) -> list:
    """Records that failed: client (4xx) and server (5xx) errors."""
    return [r for r in records if r.status >= 400]


def with_status(records, *classes) -> list:
    """Keep records whose status class ('2xx', '5xx', ...) is one of `classes`."""
    return [r for r in records if status_class(r.status) in classes]


def in_window(records, start, end) -> list:
    """Records with start <= time < end. start and end are timezone-aware datetimes."""
    return [r for r in records if start <= r.time < end]
