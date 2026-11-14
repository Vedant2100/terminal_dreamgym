import pytest

from cache import TTLCache
from clock import ManualClock


def make(capacity=3, default_ttl=None):
    clock = ManualClock()
    return TTLCache(capacity, clock, default_ttl), clock


def test_get_and_set():
    cache, _ = make()
    cache.set("a", 1)
    assert cache.get("a") == 1
    assert cache.get("nope") is None


def test_entry_expires_exactly_at_ttl():
    cache, clock = make()
    cache.set("a", 1, ttl=10)
    clock.advance(9.5)
    assert cache.get("a") == 1
    clock.advance(0.5)
    assert cache.get("a") is None


def test_default_ttl_and_none_never_expires():
    cache, clock = make(default_ttl=5)
    cache.set("a", 1)
    cache.set("b", 2, ttl=None)
    clock.advance(100)
    assert cache.get("a") is None
    assert cache.get("b") == 2


def test_least_recently_read_is_evicted():
    cache, _ = make(capacity=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.get("a")
    cache.set("c", 3)
    assert "b" not in cache
    assert "a" in cache and "c" in cache


def test_overwriting_a_key_counts_as_use():
    cache, _ = make(capacity=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("a", 10)
    cache.set("c", 3)
    assert cache.get("a") == 10
    assert "b" not in cache


def test_expired_entries_are_dropped_before_lru():
    cache, clock = make(capacity=2)
    cache.set("b", 2)
    cache.set("a", 1, ttl=1)
    clock.advance(2)
    cache.set("c", 3)
    assert "b" in cache


def test_stats_hits_and_misses():
    cache, _ = make()
    assert cache.stats()["hit_rate"] == 0.0
    cache.get("x")
    cache.set("x", 1)
    cache.get("x")
    assert cache.stats() == {"hits": 1, "misses": 1, "hit_rate": 0.5}


def test_expired_read_counts_as_miss():
    cache, clock = make()
    cache.set("a", 1, ttl=1)
    clock.advance(2)
    assert cache.get("a") is None
    assert cache.stats()["misses"] == 1


def test_contains_does_not_touch_stats_or_order():
    cache, _ = make(capacity=2)
    cache.set("a", 1)
    cache.set("b", 2)
    assert "a" in cache
    assert "zzz" not in cache
    cache.set("c", 3)
    assert "a" not in cache
    assert (cache.hits, cache.misses) == (0, 0)


def test_capacity_must_be_positive():
    with pytest.raises(ValueError):
        TTLCache(0, ManualClock())
