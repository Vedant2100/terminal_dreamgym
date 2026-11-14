"""memoize: cache a function's results in a TTLCache."""
import functools

from cache import DEFAULT_TTL, TTLCache

_NOT_FOUND = object()


def make_key(name: str, args: tuple, kwargs: dict) -> tuple:
    """A hashable key for one call; keyword argument order does not matter."""
    return (name, args, tuple(sorted(kwargs.items())))


def memoize(cache: TTLCache, ttl=DEFAULT_TTL):
    """Decorator caching results in `cache` (None results are cached too).

    `ttl` applies to every stored result; by default the cache's own
    default_ttl is used. Each call is one cache lookup, so cache.stats()
    reflects how often the function was spared.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = make_key(func.__name__, args, kwargs)
            result = cache.get(key, _NOT_FOUND)
            if result is _NOT_FOUND:
                result = func(*args, **kwargs)
                cache.set(key, result, ttl)
            return result

        wrapper.cache = cache
        return wrapper

    return decorator
