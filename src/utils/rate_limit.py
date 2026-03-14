"""Rate limiting middleware."""
import time
from collections import defaultdict
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from .errors import RateLimitError


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Track requests: {identifier: [(timestamp, count)]}
        self.minute_buckets: dict[str, list[float]] = defaultdict(list)
        self.hour_buckets: dict[str, list[float]] = defaultdict(list)

        # Cleanup interval (seconds)
        self.cleanup_interval = 60
        self.last_cleanup = time.time()

    def _get_identifier(self, request: Request) -> str:
        """Get identifier for rate limiting (IP or user ID)."""
        # Try to get user ID first
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"

        # Fall back to IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"

    def _cleanup_old_requests(self):
        """Remove old requests from buckets."""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return

        minute_ago = now - 60
        hour_ago = now - 3600

        # Cleanup minute buckets
        for identifier in list(self.minute_buckets.keys()):
            self.minute_buckets[identifier] = [
                ts for ts in self.minute_buckets[identifier] if ts > minute_ago
            ]
            if not self.minute_buckets[identifier]:
                del self.minute_buckets[identifier]

        # Cleanup hour buckets
        for identifier in list(self.hour_buckets.keys()):
            self.hour_buckets[identifier] = [
                ts for ts in self.hour_buckets[identifier] if ts > hour_ago
            ]
            if not self.hour_buckets[identifier]:
                del self.hour_buckets[identifier]

        self.last_cleanup = now

    def check_rate_limit(self, identifier: str) -> tuple[bool, dict]:
        """Check if request is within rate limit."""
        self._cleanup_old_requests()

        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600

        # Count recent requests
        minute_count = len(
            [ts for ts in self.minute_buckets[identifier] if ts > minute_ago]
        )
        hour_count = len(
            [ts for ts in self.hour_buckets[identifier] if ts > hour_ago]
        )

        # Check limits
        if minute_count >= self.requests_per_minute:
            return False, {
                "retry_after": 60 - (now - min(self.minute_buckets[identifier])),
                "limit": self.requests_per_minute,
                "window": "minute",
            }

        if hour_count >= self.requests_per_hour:
            return False, {
                "retry_after": 3600 - (now - min(self.hour_buckets[identifier])),
                "limit": self.requests_per_hour,
                "window": "hour",
            }

        # Add current request
        self.minute_buckets[identifier].append(now)
        self.hour_buckets[identifier].append(now)

        return True, {
            "remaining_minute": self.requests_per_minute - minute_count - 1,
            "remaining_hour": self.requests_per_hour - hour_count - 1,
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """Rate limiting middleware."""
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
        return await call_next(request)

    identifier = rate_limiter._get_identifier(request)
    allowed, info = rate_limiter.check_rate_limit(identifier)

    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_ERROR",
                    "message": f"Rate limit exceeded ({info['window']})",
                    "details": info,
                },
            },
            headers={
                "Retry-After": str(int(info["retry_after"])),
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": "0",
            },
        )

    response = await call_next(request)

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(info.get("limit", 60))
    response.headers["X-RateLimit-Remaining"] = str(info.get("remaining_minute", 60))

    return response
