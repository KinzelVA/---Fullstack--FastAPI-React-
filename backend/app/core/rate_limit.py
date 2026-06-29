from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from time import monotonic

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


RateLimitCallNext = Callable[[Request], Awaitable[Response]]


def parse_rate_limit(limit: str) -> tuple[int, int]:
    try:
        amount_raw, unit_raw = limit.strip().split("/", maxsplit=1)
        amount = int(amount_raw)
    except ValueError as exc:
        raise ValueError(
            "Rate limit must have format like '100/minute'."
        ) from exc

    if amount <= 0:
        raise ValueError("Rate limit amount must be positive.")

    unit = unit_raw.strip().lower()

    seconds_by_unit = {
        "second": 1,
        "seconds": 1,
        "sec": 1,
        "s": 1,
        "minute": 60,
        "minutes": 60,
        "min": 60,
        "m": 60,
        "hour": 3600,
        "hours": 3600,
        "h": 3600,
    }

    if unit not in seconds_by_unit:
        raise ValueError(
            "Rate limit unit must be one of: second, minute, hour."
        )

    return amount, seconds_by_unit[unit]


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        limit: str,
        path_prefix: str = "/api/v1",
    ) -> None:
        super().__init__(app)
        self.max_requests, self.window_seconds = parse_rate_limit(limit)
        self.path_prefix = path_prefix
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(
        self,
        request: Request,
        call_next: RateLimitCallNext,
    ) -> Response:
        if not request.url.path.startswith(self.path_prefix):
            return await call_next(request)

        client_host = request.client.host if request.client else "unknown"
        key = client_host
        now = monotonic()
        window_start = now - self.window_seconds

        timestamps = self._requests[key]

        while timestamps and timestamps[0] <= window_start:
            timestamps.popleft()

        if len(timestamps) >= self.max_requests:
            retry_after = max(1, int(self.window_seconds - (now - timestamps[0])))

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Try again later."
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        timestamps.append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.max_requests - len(timestamps))
        )

        return response
