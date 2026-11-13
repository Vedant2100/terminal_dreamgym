"""An LRU cache whose entries expire after a time-to-live."""
from collections import OrderedDict

# Passed as `ttl` to mean "use the cache's default_ttl".
DEFAULT_TTL = object()


class TTLCache:
    """Holds at most `capacity` entries.

    Each entry expires `ttl` seconds after it was set: an entry set at t=0 with
    ttl=10 is gone at t=10. A per-entry ttl overrides `default_ttl`; None means
    never expire. When the cache is full, expired entries are dropped first,
    then the least recently used ones. Reads and writes both count as use.
    """

    def __init__(self, capacity: int, clock, default_ttl=None):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.clock = clock
        self.default_ttl = default_ttl
        self._data = OrderedDict()  # key -> (value, expires_at or None)
        self.hits = 0
        self.misses = 0

    def _expired(self, expires_at) -> bool:
        return expires_at is not None and self.clock() >= expires_at

    def get(self, key, default=None):
        """Return the live value for `key`, or `default`. Expired reads are misses."""
        entry = self._data.get(key)
        if entry is None or self._expired(entry[1]):
            if entry is not None:
                del self._data[key]
            self.misses += 1
            return default
        self._data.move_to_end(key)
        self.hits += 1
        return entry[0]

    def set(self, key, value, ttl=DEFAULT_TTL) -> None:
        if ttl is DEFAULT_TTL:
            ttl = self.default_ttl
        expires_at = None if ttl is None else self.clock() + ttl
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = (value, expires_at)
        self._evict()

    def _evict(self) -> None:
        for key in [k for k, (_, exp) in self._data.items() if self._expired(exp)]:
            del self._data[key]
        while len(self._data) > self.capacity:
            self._data.popitem(last=False)

    def __contains__(self, key) -> bool:
        """Membership test. Does not count as a hit, a miss or a use."""
        entry = self._data.get(key)
        return entry is not None and not self._expired(entry[1])

    def __len__(self) -> int:
        """Number of live (unexpired) entries."""
        return sum(1 for _, exp in self._data.values() if not self._expired(exp))

    def stats(self) -> dict:
        total = self.hits + self.misses
        rate = self.hits / total if total else 0.0
        return {"hits": self.hits, "misses": self.misses, "hit_rate": rate}
