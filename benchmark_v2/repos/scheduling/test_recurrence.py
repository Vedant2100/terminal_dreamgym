from datetime import date, datetime, time

import pytest

from events import Event
from recurrence import parse_weekday, weekly


def test_parse_weekday_rejects_unknown():
    assert parse_weekday("Monday") == 0
    with pytest.raises(ValueError):
        parse_weekday("Funday")


def test_weekly_first_occurrence_is_next_matching_day():
    # 4 March 2026 is a Wednesday; the first Monday on or after it is 9 March.
    occ = weekly("standup", "mon", time(9), 15, date(2026, 3, 4), date(2026, 3, 31))
    assert occ[0].start == datetime(2026, 3, 9, 9, 0)
    assert len(occ) == 4


def test_weekly_includes_until_and_honours_skip():
    occ = weekly("standup", "mon", time(9), 15, date(2026, 3, 2), date(2026, 3, 23),
                 skip=[date(2026, 3, 9)])
    assert [e.start.day for e in occ] == [2, 16, 23]


def test_weekly_moves_holiday_to_next_business_day():
    # Thursday 24 and Friday 25 December are both holidays.
    holidays = [date(2026, 12, 24), date(2026, 12, 25)]
    occ = weekly("review", "thu", time(14), 60, date(2026, 12, 17), date(2026, 12, 30), holidays=holidays)
    assert [e.start for e in occ] == [datetime(2026, 12, 17, 14), datetime(2026, 12, 28, 14)]


def test_weekly_drops_busy_but_keeps_back_to_back():
    busy = [
        Event("dentist", datetime(2026, 3, 2, 9, 45), datetime(2026, 3, 2, 10, 30)),
        Event("offsite", datetime(2026, 3, 9, 9, 30), datetime(2026, 3, 9, 17)),
    ]
    occ = weekly("sync", "mon", time(9), 45, date(2026, 3, 2), date(2026, 3, 20), busy=busy)
    assert [e.start.day for e in occ] == [2, 16]
    assert occ[0].duration_minutes == 45
