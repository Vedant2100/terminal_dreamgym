"""Aggregate counts and latency percentiles over parsed records."""
import math
from collections import Counter

from filters import status_class


def count_by(records, key) -> list:
    """(value, count) pairs, most common first; ties ordered by value."""
    counts = Counter(key(r) for r in records)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def top_paths(records, n: int = 3) -> list:
    return count_by(records, lambda r: r.path)[:n]


def status_counts(records) -> dict:
    """{'2xx': 10, '4xx': 2, ...}"""
    return dict(Counter(status_class(r.status) for r in records))


def error_rate(records) -> float:
    """Share of server errors (5xx) among all requests; 0.0 when there are none."""
    if not records:
        return 0.0
    return sum(1 for r in records if r.status >= 500) / len(records)


def percentile(values, pct: float):
    """Nearest-rank percentile: the smallest value with at least pct% of values <= it."""
    if not values:
        raise ValueError("no values")
    if not 0 < pct <= 100:
        raise ValueError("pct must be in (0, 100]")
    ordered = sorted(values)
    rank = math.ceil(pct / 100 * len(ordered))
    return ordered[rank - 1]


def latency_summary(records) -> dict:
    """p50, p95 and max response time in milliseconds."""
    durations = [r.duration_ms for r in records]
    return {"p50": percentile(durations, 50), "p95": percentile(durations, 95), "max": max(durations)}
