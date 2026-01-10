"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Rate Limiter - Pure functions for rate limiting algorithms.
All functions are pure, deterministic, and atomic.
"""

def create_token_bucket(capacity: int, refill_rate: float, current_tokens: float, last_refill: float) -> dict:
    """Create a token bucket rate limiter."""
    return {
        "capacity": capacity,
        "refill_rate": refill_rate,
        "tokens": current_tokens,
        "last_refill": last_refill
    }


def refill_tokens(bucket: dict, current_time: float) -> dict:
    """Refill tokens based on elapsed time."""
    elapsed = current_time - bucket["last_refill"]
    new_tokens = min(bucket["capacity"], bucket["tokens"] + elapsed * bucket["refill_rate"])
    return {
        "capacity": bucket["capacity"],
        "refill_rate": bucket["refill_rate"],
        "tokens": new_tokens,
        "last_refill": current_time
    }


def consume_tokens(bucket: dict, count: int, current_time: float) -> dict:
    """Attempt to consume tokens."""
    refilled = refill_tokens(bucket, current_time)
    if refilled["tokens"] >= count:
        return {
            "bucket": {**refilled, "tokens": refilled["tokens"] - count},
            "allowed": True,
            "tokens_remaining": refilled["tokens"] - count
        }
    return {
        "bucket": refilled,
        "allowed": False,
        "tokens_remaining": refilled["tokens"]
    }


def tokens_available(bucket: dict, current_time: float) -> float:
    """Get current available tokens."""
    refilled = refill_tokens(bucket, current_time)
    return refilled["tokens"]


def time_until_tokens(bucket: dict, count: int, current_time: float) -> float:
    """Calculate time until tokens are available."""
    refilled = refill_tokens(bucket, current_time)
    if refilled["tokens"] >= count:
        return 0
    needed = count - refilled["tokens"]
    return needed / refilled["refill_rate"]


def create_sliding_window(window_size: float, max_requests: int) -> dict:
    """Create a sliding window rate limiter."""
    return {
        "window_size": window_size,
        "max_requests": max_requests,
        "requests": []
    }


def sliding_window_allow(window: dict, current_time: float) -> dict:
    """Check if request is allowed in sliding window."""
    window_start = current_time - window["window_size"]
    requests = [t for t in window["requests"] if t > window_start]
    if len(requests) < window["max_requests"]:
        requests.append(current_time)
        return {
            "window": {**window, "requests": requests},
            "allowed": True,
            "remaining": window["max_requests"] - len(requests)
        }
    return {
        "window": {**window, "requests": requests},
        "allowed": False,
        "remaining": 0
    }


def sliding_window_remaining(window: dict, current_time: float) -> int:
    """Get remaining requests in window."""
    window_start = current_time - window["window_size"]
    requests = [t for t in window["requests"] if t > window_start]
    return max(0, window["max_requests"] - len(requests))


def create_fixed_window(window_size: float, max_requests: int) -> dict:
    """Create a fixed window rate limiter."""
    return {
        "window_size": window_size,
        "max_requests": max_requests,
        "window_start": 0,
        "count": 0
    }


def fixed_window_allow(window: dict, current_time: float) -> dict:
    """Check if request is allowed in fixed window."""
    window_start = window["window_start"]
    count = window["count"]
    if current_time >= window_start + window["window_size"]:
        window_start = current_time - (current_time % window["window_size"])
        count = 0
    if count < window["max_requests"]:
        return {
            "window": {**window, "window_start": window_start, "count": count + 1},
            "allowed": True,
            "remaining": window["max_requests"] - count - 1
        }
    return {
        "window": {**window, "window_start": window_start, "count": count},
        "allowed": False,
        "remaining": 0
    }


def create_leaky_bucket(capacity: int, leak_rate: float) -> dict:
    """Create a leaky bucket rate limiter."""
    return {
        "capacity": capacity,
        "leak_rate": leak_rate,
        "water": 0,
        "last_leak": 0
    }


def leaky_bucket_add(bucket: dict, amount: int, current_time: float) -> dict:
    """Add water to leaky bucket."""
    elapsed = current_time - bucket["last_leak"]
    leaked = elapsed * bucket["leak_rate"]
    current_water = max(0, bucket["water"] - leaked)
    if current_water + amount <= bucket["capacity"]:
        return {
            "bucket": {**bucket, "water": current_water + amount, "last_leak": current_time},
            "allowed": True,
            "overflow": 0
        }
    overflow = (current_water + amount) - bucket["capacity"]
    return {
        "bucket": {**bucket, "water": bucket["capacity"], "last_leak": current_time},
        "allowed": False,
        "overflow": overflow
    }


def create_rate_limit_config(requests_per_second: float, burst: int) -> dict:
    """Create rate limit configuration."""
    return {
        "requests_per_second": requests_per_second,
        "burst": burst,
        "window_ms": 1000 / requests_per_second if requests_per_second > 0 else float("inf")
    }


def calculate_retry_after(remaining: int, window_reset_time: float, current_time: float) -> float:
    """Calculate retry-after header value."""
    if remaining > 0:
        return 0
    return window_reset_time - current_time


def build_rate_limit_headers(limit: int, remaining: int, reset_time: float) -> dict:
    """Build standard rate limit headers."""
    return {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(reset_time))
    }


def parse_rate_limit_headers(headers: dict) -> dict:
    """Parse rate limit headers."""
    return {
        "limit": int(headers.get("X-RateLimit-Limit", 0)),
        "remaining": int(headers.get("X-RateLimit-Remaining", 0)),
        "reset": int(headers.get("X-RateLimit-Reset", 0))
    }


def should_throttle(remaining: int, threshold: float, limit: int) -> bool:
    """Check if we should throttle based on remaining quota."""
    return remaining < limit * threshold


def calculate_backoff_delay(attempt: int, base_delay: float, max_delay: float, jitter_seed: int) -> float:
    """Calculate exponential backoff delay with jitter."""
    import hashlib
    delay = min(base_delay * (2 ** attempt), max_delay)
    h = hashlib.sha256(str(jitter_seed).encode()).digest()
    jitter = (h[0] / 255.0) * delay * 0.5
    return delay + jitter


def create_composite_limiter(limiters: list) -> dict:
    """Create a composite rate limiter."""
    return {"limiters": limiters, "type": "composite"}


def composite_allow(composite: dict, check_fn) -> dict:
    """Check all limiters in composite."""
    results = [check_fn(limiter) for limiter in composite["limiters"]]
    all_allowed = all(r["allowed"] for r in results)
    min_remaining = min(r.get("remaining", float("inf")) for r in results)
    return {
        "allowed": all_allowed,
        "remaining": min_remaining,
        "results": results
    }


def estimate_quota_depletion(current_remaining: int, rate_per_second: float, current_time: float) -> float:
    """Estimate when quota will be depleted."""
    if rate_per_second <= 0:
        return float("inf")
    return current_time + (current_remaining / rate_per_second)
