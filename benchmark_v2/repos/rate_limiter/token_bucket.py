"""Token bucket: up to `capacity` tokens, refilled continuously at `rate` tokens per second."""
from dataclasses import dataclass


@dataclass
class Decision:
    allowed: bool
    remaining: int  # whole requests still available right after this one
    retry_after: float  # seconds until this request would be allowed; 0.0 when allowed


class TokenBucket:
    def __init__(self, capacity: float, rate: float, clock):
        if capacity <= 0 or rate <= 0:
            raise ValueError("capacity and rate must be positive")
        self.capacity = capacity
        self.rate = rate
        self.clock = clock
        self.tokens = float(capacity)  # a new bucket starts full
        self.updated = clock()

    def _refill(self) -> None:
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
        self.updated = now

    def acquire(self, cost: float = 1) -> Decision:
        """Take `cost` tokens if there are enough. A refused request takes nothing."""
        if cost > self.capacity:
            raise ValueError("cost exceeds capacity; it could never be allowed")
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return Decision(True, int(self.tokens), 0.0)
        return Decision(False, int(self.tokens), (cost - self.tokens) / self.rate)
