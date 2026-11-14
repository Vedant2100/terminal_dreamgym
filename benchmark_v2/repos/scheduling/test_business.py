from datetime import date

from business import add_business_days, business_days_between


def test_add_business_days_over_weekend():
    friday = date(2026, 3, 6)
    assert add_business_days(friday, 1) == date(2026, 3, 9)
    assert add_business_days(friday, 3) == date(2026, 3, 11)


def test_add_business_days_backwards():
    monday = date(2026, 3, 9)
    assert add_business_days(monday, -1) == date(2026, 3, 6)


def test_add_zero_business_days_returns_start():
    saturday = date(2026, 3, 7)
    assert add_business_days(saturday, 0) == saturday


def test_business_days_between_with_holiday():
    # Mon 2 March .. Fri 13 March is ten weekdays; the 4th is a holiday.
    assert business_days_between(date(2026, 3, 2), date(2026, 3, 14), [date(2026, 3, 4)]) == 9
