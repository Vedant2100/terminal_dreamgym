"""Weekly recurring events expanded into concrete occurrences."""
from datetime import date, datetime, time, timedelta

from business import add_business_days
from events import Event

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def parse_weekday(name: str) -> int:
    """'Monday', 'mon' or 'MON' -> 0 (same numbering as date.weekday())."""
    key = name.strip().lower()[:3]
    if key not in WEEKDAYS:
        raise ValueError(f"unknown weekday: {name}")
    return WEEKDAYS.index(key)


def weekly(title: str, weekday: str, start_time: time, minutes: int,
           first_day: date, until: date, skip=(), holidays=(), busy=()) -> list:
    """Occurrences on `weekday` from first_day up to and including `until`.

    - dates in `skip` are left out;
    - an occurrence on a holiday moves to the next business day;
    - occurrences that overlap any event in `busy` are dropped.
    """
    wd = parse_weekday(weekday)
    day = first_day + timedelta(days=(wd - first_day.weekday()) % 7)
    out = []
    while day <= until:
        if day not in skip:
            when = add_business_days(day, 1, holidays) if day in holidays else day
            start = datetime.combine(when, start_time)
            event = Event(title, start, start + timedelta(minutes=minutes))
            if not any(event.overlaps(other) for other in busy):
                out.append(event)
        day += timedelta(days=7)
    return out
