"""Calendar events with fixed start and end datetimes."""
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class Event:
    title: str
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError(f"{self.title}: end must be after start")

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)

    def overlaps(self, other: "Event") -> bool:
        """True if the two events share any time. Back-to-back events (one ends
        exactly when the other starts) do not overlap."""
        return self.start < other.end and other.start < self.end


def find_conflicts(events) -> list:
    """(earlier.title, later.title) pairs of overlapping events, ordered by start."""
    ordered = sorted(events, key=lambda e: e.start)
    conflicts = []
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            if b.start >= a.end:
                break  # every later event starts even later
            conflicts.append((a.title, b.title))
    return conflicts


def free_slots(events, day_start: datetime, day_end: datetime, min_minutes: int = 0) -> list:
    """Gaps between day_start and day_end not covered by any event, as
    (start, end) pairs. Only gaps at least min_minutes long are returned."""
    slots = []
    cursor = day_start
    for event in sorted(events, key=lambda e: e.start):
        if event.start > cursor:
            slots.append((cursor, event.start))
        cursor = max(cursor, event.end)
    if cursor < day_end:
        slots.append((cursor, day_end))
    return [(s, e) for s, e in slots if e - s >= timedelta(minutes=min_minutes)]
