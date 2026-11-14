"""Per-key limiters (for example one bucket per client) built on demand by a factory."""
from sliding_window import SlidingWindow
from token_bucket import TokenBucket


def token_buckets(capacity: float, per_minute: float):
    """Factory: a full TokenBucket per key, refilled at `per_minute` tokens a minute."""
    return lambda clock: TokenBucket(capacity, per_minute / 60, clock)


def sliding_windows(limit: int, window: float):
    return lambda clock: SlidingWindow(limit, window, clock)


class KeyedLimiter:
    def __init__(self, factory, clock, idle_ttl=None):
        """factory(clock) builds the limiter for a key the first time it is seen."""
        self.factory = factory
        self.clock = clock
        self.idle_ttl = idle_ttl
        self.limiters = {}
        self.last_seen = {}

    def acquire(self, key, cost=1):
        if key not in self.limiters:
            self.limiters[key] = self.factory(self.clock)
        self.last_seen[key] = self.clock()
        return self.limiters[key].acquire(cost)

    def prune(self) -> int:
        """Forget keys not used for idle_ttl seconds or more. Returns how many were dropped."""
        if self.idle_ttl is None:
            return 0
        now = self.clock()
        stale = [key for key, seen in self.last_seen.items() if now - seen >= self.idle_ttl]
        for key in stale:
            del self.limiters[key]
            del self.last_seen[key]
        return len(stale)
