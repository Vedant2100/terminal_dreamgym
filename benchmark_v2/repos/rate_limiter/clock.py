"""Clocks. Limiters accept any zero-argument callable that returns seconds as a float."""


class FakeClock:
    """A clock that only moves when told to, for tests and simulations."""

    def __init__(self, start: float = 0.0):
        self.t = float(start)

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("time cannot go backwards")
        self.t += seconds
