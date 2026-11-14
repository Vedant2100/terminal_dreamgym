from clock import FakeClock
from keyed import KeyedLimiter, sliding_windows, token_buckets


def test_keys_are_independent():
    limiter = KeyedLimiter(sliding_windows(1, 10), FakeClock())
    assert limiter.acquire("a").allowed is True
    assert limiter.acquire("a").allowed is False
    assert limiter.acquire("b").allowed is True


def test_keyed_bucket_allows_burst_of_capacity():
    limiter = KeyedLimiter(token_buckets(capacity=3, per_minute=60), FakeClock())
    assert [limiter.acquire("a").allowed for _ in range(4)] == [True, True, True, False]


def test_keyed_rate_is_per_minute():
    clock = FakeClock()
    limiter = KeyedLimiter(token_buckets(capacity=3, per_minute=60), clock)
    for _ in range(3):
        limiter.acquire("a")
    clock.advance(1)
    decision = limiter.acquire("a")
    assert decision.allowed is True
    assert decision.remaining == 0


def test_keyed_cost():
    limiter = KeyedLimiter(sliding_windows(3, 10), FakeClock())
    assert limiter.acquire("a", cost=3).remaining == 0


def test_prune_removes_idle_keys():
    clock = FakeClock()
    limiter = KeyedLimiter(sliding_windows(5, 10), clock, idle_ttl=60)
    limiter.acquire("a")
    clock.advance(30)
    limiter.acquire("b")
    clock.advance(40)
    assert limiter.prune() == 1
    assert list(limiter.limiters) == ["b"]


def test_prune_keeps_active_keys():
    clock = FakeClock()
    limiter = KeyedLimiter(sliding_windows(5, 10), clock, idle_ttl=60)
    limiter.acquire("a")
    clock.advance(50)
    limiter.acquire("a")
    clock.advance(20)
    assert limiter.prune() == 0
