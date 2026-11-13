from datetime import datetime

import pytest

from events import Event, find_conflicts, free_slots


def at(hour, minute=0, day=9):
    return datetime(2026, 3, day, hour, minute)


def test_zero_length_event_raises():
    with pytest.raises(ValueError):
        Event("empty", at(9), at(9))


def test_duration_spans_days():
    assert Event("offsite", at(9), at(10, day=10)).duration_minutes == 25 * 60


def test_find_conflicts_unsorted_input():
    a = Event("A", at(9), at(11))
    b = Event("B", at(10), at(10, 30))
    c = Event("C", at(10, 45), at(12))
    d = Event("D", at(13), at(14))
    assert find_conflicts([d, c, b, a]) == [("A", "B"), ("A", "C")]


def test_free_slots():
    events = [Event("x", at(10), at(11)), Event("y", at(13), at(14))]
    assert free_slots(events, at(9), at(17)) == [(at(9), at(10)), (at(11), at(13)), (at(14), at(17))]


def test_free_slots_nested_event():
    events = [Event("long", at(10), at(12)), Event("short", at(10, 30), at(11))]
    assert free_slots(events, at(9), at(17)) == [(at(9), at(10)), (at(12), at(17))]


def test_free_slots_back_to_back():
    events = [Event("x", at(10), at(11)), Event("y", at(11), at(12))]
    assert free_slots(events, at(10), at(13)) == [(at(12), at(13))]


def test_free_slots_min_length_is_inclusive():
    events = [Event("x", at(9, 30), at(11)), Event("y", at(11, 10), at(12))]
    assert free_slots(events, at(9), at(12, 45), min_minutes=30) == [(at(9), at(9, 30)), (at(12), at(12, 45))]
