import os
import time
from typing import Callable
from fastapi import HTTPException, Request

try:
    import redis
except Exception:  # redis is optional
    redis = None

REDIS_URL = os.getenv("REDIS_URL")

_redis = redis.StrictRedis.from_url(REDIS_URL) if (redis and REDIS_URL) else None


def rate_limiter_optional(bucket: str, rate: int, per_seconds: int) -> Callable:
    """Return a dependency that rate-limits by IP using Redis if available; no-op otherwise."""
    def dependency(request: Request):
        if not _redis:
            return  # no-op
        ip = request.client.host if request.client else "unknown"
        key = f"rl:{bucket}:{ip}"
        now = int(time.time())
        pipe = _redis.pipeline()
        # Use a fixed window counter
        window = now // per_seconds
        window_key = f"{key}:{window}"
        pipe.incr(window_key, 1)
        pipe.expire(window_key, per_seconds + 1)
        count, _ = pipe.execute()
        if int(count) > rate:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return dependency