from datetime import datetime, timezone

from parse import parse_line, parse_lines

SAMPLE = '10.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326 0.042'


def test_parse_line_fields():
    record = parse_line(SAMPLE)
    assert record.ip == "10.0.0.1"
    assert record.time == datetime(2023, 10, 10, 13, 55, 36, tzinfo=timezone.utc)
    assert (record.method, record.path, record.status, record.size) == ("GET", "/index.html", 200, 2326)


def test_dash_size_is_zero():
    line = '10.0.0.2 - - [10/Oct/2023:13:56:00 +0000] "HEAD / HTTP/1.1" 304 - 0.001'
    assert parse_line(line).size == 0


def test_malformed_lines_skipped():
    records = parse_lines(["garbage", "", SAMPLE + "\n"])
    assert [r.ip for r in records] == ["10.0.0.1"]
