from datetime import datetime, timezone

import pytest

from filters import errors, in_window, with_status
from parse import parse_lines
from stats import error_rate, latency_summary, percentile, status_counts, top_paths


def line(path="/", status=200, duration="0.050", time="10/Oct/2023:13:55:00 +0000"):
    return f'10.0.0.1 - - [{time}] "GET {path} HTTP/1.1" {status} 100 {duration}'


def utc(hour, minute):
    return datetime(2023, 10, 10, hour, minute, tzinfo=timezone.utc)


def test_window_end_is_exclusive():
    records = parse_lines([line(time="10/Oct/2023:13:55:00 +0000"), line(time="10/Oct/2023:14:00:00 +0000")])
    assert len(in_window(records, utc(13, 55), utc(14, 0))) == 1


def test_window_compares_in_utc():
    records = parse_lines([line(time="10/Oct/2023:15:59:00 +0200")])
    assert len(in_window(records, utc(13, 55), utc(14, 0))) == 1


def test_errors_include_client_errors():
    records = parse_lines([line(status=200), line(status=404), line(status=503)])
    assert [r.status for r in errors(records)] == [404, 503]


def test_with_status_and_counts():
    records = parse_lines([line(status=200), line(status=201), line(status=404)])
    assert [r.status for r in with_status(records, "4xx", "5xx")] == [404]
    assert status_counts(records) == {"2xx": 2, "4xx": 1}


def test_error_rate_counts_server_errors_only():
    records = parse_lines([line(status=200), line(status=404), line(status=500), line(status=200)])
    assert error_rate(records) == 0.25


def test_top_paths_ignore_query_string():
    records = parse_lines([line("/search?q=a"), line("/home"), line("/search?q=b")])
    assert top_paths(records, 1) == [("/search", 2)]


def test_top_paths_ties_alphabetical():
    records = parse_lines([line("/b"), line("/c"), line("/a"), line("/c")])
    assert top_paths(records) == [("/c", 2), ("/a", 1), ("/b", 1)]


def test_percentile_nearest_rank():
    assert percentile([50, 10, 40, 20, 30], 50) == 30
    assert percentile([50, 10, 40, 20, 30], 100) == 50


def test_percentile_rejects_zero():
    with pytest.raises(ValueError):
        percentile([1, 2, 3], 0)


def test_latency_summary_in_ms():
    records = parse_lines([line(duration=f"0.{n:02d}0") for n in range(20, 0, -1)])
    assert latency_summary(records) == {"p50": 100, "p95": 190, "max": 200}
