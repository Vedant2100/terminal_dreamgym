from cache import TTLCache
from clock import ManualClock
from memo import memoize


def counted(cache, **options):
    calls = []

    @memoize(cache, **options)
    def square(x, scale=1, offset=0):
        calls.append(x)
        return x * x * scale + offset

    return square, calls


def test_memoize_caches_calls():
    square, calls = counted(TTLCache(10, ManualClock()))
    assert square(3) == 9
    assert square(3) == 9
    assert calls == [3]


def test_memoize_keyword_order_does_not_matter():
    square, calls = counted(TTLCache(10, ManualClock()))
    square(2, scale=2, offset=1)
    square(2, offset=1, scale=2)
    assert calls == [2]


def test_memoize_caches_none_results():
    calls = []

    @memoize(TTLCache(10, ManualClock()))
    def lookup(name):
        calls.append(name)
        return None

    lookup("x")
    lookup("x")
    assert calls == ["x"]


def test_memoize_records_hits_and_misses():
    cache = TTLCache(10, ManualClock())
    square, _ = counted(cache)
    square(2)
    square(2)
    assert cache.stats()["hits"] == 1
    assert cache.stats()["misses"] == 1


def test_memoize_explicit_ttl_recomputes():
    clock = ManualClock()
    square, calls = counted(TTLCache(10, clock), ttl=5)
    square(4)
    clock.advance(6)
    square(4)
    assert calls == [4, 4]


def test_memoize_uses_cache_default_ttl():
    clock = ManualClock()
    square, calls = counted(TTLCache(10, clock, default_ttl=5))
    square(4)
    clock.advance(6)
    square(4)
    assert calls == [4, 4]
