import pytest

from clock import FakeClock
from sliding_window import SlidingWindow
from token_bucket import TokenBucket


def test_clock_cannot_go_backwards():
    with pytest.raises(ValueError):
        FakeClock(5).advance(-1)


def test_bucket_starts_full():
    bucket = TokenBucket(3, 1, FakeClock())
    assert [bucket.acquire().remaining for _ in range(3)] == [2, 1, 0]
    assert bucket.acquire().allowed is False


def test_retry_after_seconds():
    bucket = TokenBucket(1, 0.5, FakeClock())
    bucket.acquire()
    decision = bucket.acquire()
    assert decision.allowed is False
    assert decision.retry_after == 2.0


def test_refill_capped_at_capacity():
    clock = FakeClock()
    bucket = TokenBucket(2, 1, clock)
    clock.advance(100)
    assert bucket.acquire().remaining == 1


def test_refill_not_double_counted():
    clock = FakeClock()
    bucket = TokenBucket(4, 1, clock)
    for _ in range(4):
        bucket.acquire()
    clock.advance(1)
    assert bucket.acquire().allowed is True
    assert bucket.acquire().allowed is False


def test_cost_larger_than_capacity_rejected():
    with pytest.raises(ValueError):
        TokenBucket(2, 1, FakeClock()).acquire(cost=3)


def test_window_limits_requests():
    clock = FakeClock()
    window = SlidingWindow(2, 10, clock)
    assert window.acquire().remaining == 1
    clock.advance(1)
    assert window.acquire().remaining == 0
    clock.advance(1)
    decision = window.acquire()
    assert decision.allowed is False
    assert decision.retry_after == 8


def test_slot_frees_exactly_after_window():
    clock = FakeClock()
    window = SlidingWindow(1, 10, clock)
    window.acquire()
    clock.advance(10)
    assert window.acquire().allowed is True
