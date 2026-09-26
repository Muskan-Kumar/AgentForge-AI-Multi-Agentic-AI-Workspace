import time
from collections import defaultdict


class RateLimiter:

    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, key: str) -> bool:

        now = time.time()

        timestamps = self.requests[key]

        timestamps[:] = [
            timestamp
            for timestamp in timestamps
            if now - timestamp < self.window_seconds
        ]

        if len(timestamps) >= self.max_requests:
            return False

        timestamps.append(now)

        return True
    