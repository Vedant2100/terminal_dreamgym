"""Parse access-log lines into records.

A line looks like this (the last field is the response time in seconds):

    10.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326 0.042
"""
import re
from dataclasses import dataclass
from datetime import datetime, timezone

LINE_RE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) [^"]*" '
    r'(?P<status>\d{3}) (?P<size>\d+|-) (?P<duration>\d+(?:\.\d+)?)$'
)
TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


@dataclass
class Record:
    ip: str
    time: datetime  # always in UTC
    method: str
    path: str  # without the query string
    status: int
    size: int  # bytes; '-' in the log means 0
    duration_ms: int


def parse_line(line: str):
    """Parse one line, or return None if it does not look like an access-log line."""
    match = LINE_RE.match(line.strip())
    if not match:
        return None
    size = match["size"]
    return Record(
        ip=match["ip"],
        time=datetime.strptime(match["time"], TIME_FORMAT).astimezone(timezone.utc),
        method=match["method"],
        path=match["path"].split("?", 1)[0],
        status=int(match["status"]),
        size=0 if size == "-" else int(size),
        duration_ms=round(float(match["duration"]) * 1000),
    )


def parse_lines(lines) -> list:
    """Parse many lines, skipping blank and malformed ones."""
    records = []
    for line in lines:
        record = parse_line(line)
        if record is not None:
            records.append(record)
    return records
