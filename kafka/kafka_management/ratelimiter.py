import time
from collections import defaultdict


class TokenBucket:
    """Simple in-memory token bucket per peer."""
    def __init__(self, rate: int, capacity: int | None = None) -> None:
        self.rate = rate
        self.capacity = capacity or rate
        self._state: dict[str, tuple[float, float]] = defaultdict(lambda: (time.time(), self.capacity))

    def __call__(self, peer: str, cost: int = 1) -> bool:
        now = time.time()
        ts, tokens = self._state[peer]
        # leak entire bucket since last check
        tokens = min(self.capacity, tokens + (now - ts) * self.rate)
        if tokens >= cost:
            self._state[peer] = (now, tokens - cost)
            return True            # allowed
        self._state[peer] = (now, tokens)
        return False               # throttled
