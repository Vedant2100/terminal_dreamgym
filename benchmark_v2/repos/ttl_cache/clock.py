"""Clocks. Code that needs the time takes a clock: a callable returning seconds."""


class ManualClock:
    """A clock that only moves when told to, for tests and simulations."""

    def __init__(self, start: float = 0.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        """Move the clock forward by `seconds`."""
        if seconds < 0:
            raise ValueError("time cannot go backwards")
        self.now += seconds
