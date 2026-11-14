import pytest

from stock import InsufficientStock, Stock


def test_receive_and_available():
    s = Stock()
    s.receive("bolt", 10)
    s.reserve("bolt", 3)
    assert s.available("bolt") == 7


def test_receive_rejects_zero():
    with pytest.raises(ValueError):
        Stock().receive("bolt", 0)


def test_reserve_too_much_raises():
    s = Stock()
    s.receive("bolt", 4)
    with pytest.raises(InsufficientStock):
        s.reserve("bolt", 5)


def test_reserve_rejects_zero():
    s = Stock()
    s.receive("bolt", 4)
    with pytest.raises(ValueError):
        s.reserve("bolt", 0)


def test_release_more_than_reserved_raises():
    s = Stock()
    s.receive("bolt", 10)
    s.reserve("bolt", 2)
    with pytest.raises(ValueError):
        s.release("bolt", 5)


def test_ship_frees_reservation():
    s = Stock()
    s.receive("bolt", 10)
    s.reserve("bolt", 4)
    s.ship("bolt", 4)
    assert s.available("bolt") == 6
