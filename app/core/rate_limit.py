import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.core.config import settings


class RateLimiter:
    """Fixed-window limiter keyed by client IP."""

    def __init__(self, times: int | None = None, window_seconds: int | None = None):
        self.times = times or settings.RATE_LIMIT_TIMES
        self.window = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def __call__(self, request: Request) -> None:
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = self._hits[client]
        while hits and hits[0] < now - self.window:
            hits.popleft()
        if len(hits) >= self.times:
            retry_after = int(self.window - (now - hits[0])) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.times} per {self.window}s",
                headers={"Retry-After": str(retry_after)},
            )
        hits.append(now)
