"""Sliding-window log: at most `limit` requests in any `window` seconds."""
from collections import deque

from token_bucket import Decision


class SlidingWindow:
    def __init__(self, limit: int, window: float, clock):
        self.limit = limit
        self.window = window
        self.clock = clock
        self.hits = deque()  # times of allowed requests, oldest first

    def acquire(self, cost: int = 1) -> Decision:
        now = self.clock()
        # A request made at time t stops counting at exactly t + window.
        while self.hits and self.hits[0] <= now - self.window:
            self.hits.popleft()
        if len(self.hits) + cost <= self.limit:
            self.hits.extend([now] * cost)
            return Decision(True, self.limit - len(self.hits), 0.0)
        return Decision(False, self.limit - len(self.hits), self.hits[0] + self.window - now)
