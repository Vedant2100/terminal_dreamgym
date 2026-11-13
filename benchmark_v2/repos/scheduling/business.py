"""Business-day arithmetic. Saturdays, Sundays and listed holidays are not business days."""
from datetime import date, timedelta


def is_business_day(day: date, holidays=()) -> bool:
    return day.weekday() < 5 and day not in holidays


def add_business_days(start: date, n: int, holidays=()) -> date:
    """The date n business days after start; start itself is not counted.
    A negative n counts backwards and n == 0 returns start unchanged."""
    step = 1 if n >= 0 else -1
    remaining = abs(n)
    day = start
    while remaining > 0:
        day += timedelta(days=step)
        if is_business_day(day, holidays):
            remaining -= 1
    return day


def business_days_between(start: date, end: date, holidays=()) -> int:
    """Number of business days d with start <= d < end."""
    count = 0
    day = start
    while day < end:
        if is_business_day(day, holidays):
            count += 1
        day += timedelta(days=1)
    return count
