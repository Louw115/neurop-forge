"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Throttle Utilities - Pure functions for throttling and debouncing patterns.
All functions are pure, deterministic, and atomic.
"""


def create_throttle_state(window_ms: int, max_calls: int) -> dict:
    """Create throttle state."""
    return {
        "window_ms": window_ms,
        "max_calls": max_calls,
        "calls": [],
        "blocked": 0
    }


def should_throttle(state: dict, timestamp: int) -> bool:
    """Check if call should be throttled."""
    window_start = timestamp - state["window_ms"]
    recent_calls = [t for t in state["calls"] if t >= window_start]
    return len(recent_calls) >= state["max_calls"]


def record_call(state: dict, timestamp: int) -> dict:
    """Record a call in throttle state."""
    window_start = timestamp - state["window_ms"]
    recent_calls = [t for t in state["calls"] if t >= window_start]
    recent_calls.append(timestamp)
    return {
        **state,
        "calls": recent_calls
    }


def record_blocked(state: dict) -> dict:
    """Record a blocked call."""
    return {**state, "blocked": state["blocked"] + 1}


def get_wait_time(state: dict, timestamp: int) -> int:
    """Get wait time until next call allowed."""
    if not should_throttle(state, timestamp):
        return 0
    window_start = timestamp - state["window_ms"]
    recent_calls = sorted([t for t in state["calls"] if t >= window_start])
    if len(recent_calls) >= state["max_calls"]:
        oldest = recent_calls[0]
        return oldest + state["window_ms"] - timestamp
    return 0


def reset_throttle(state: dict) -> dict:
    """Reset throttle state."""
    return {
        **state,
        "calls": [],
        "blocked": 0
    }


def get_throttle_stats(state: dict, timestamp: int) -> dict:
    """Get throttle statistics."""
    window_start = timestamp - state["window_ms"]
    recent_calls = [t for t in state["calls"] if t >= window_start]
    return {
        "current_calls": len(recent_calls),
        "max_calls": state["max_calls"],
        "remaining": max(0, state["max_calls"] - len(recent_calls)),
        "blocked_total": state["blocked"],
        "utilization": len(recent_calls) / state["max_calls"] if state["max_calls"] > 0 else 0
    }


def create_debounce_state(delay_ms: int) -> dict:
    """Create debounce state."""
    return {
        "delay_ms": delay_ms,
        "last_call": 0,
        "pending": False
    }


def should_execute_debounce(state: dict, timestamp: int) -> bool:
    """Check if debounced call should execute."""
    return timestamp - state["last_call"] >= state["delay_ms"]


def schedule_debounce(state: dict, timestamp: int) -> dict:
    """Schedule a debounced call."""
    return {
        **state,
        "last_call": timestamp,
        "pending": True
    }


def execute_debounce(state: dict) -> dict:
    """Mark debounced call as executed."""
    return {**state, "pending": False}


def create_sliding_window(window_ms: int, buckets: int) -> dict:
    """Create sliding window rate limiter."""
    bucket_size = window_ms // buckets
    return {
        "window_ms": window_ms,
        "bucket_size": bucket_size,
        "buckets": [0] * buckets,
        "current_bucket": 0
    }


def get_bucket_index(window: dict, timestamp: int) -> int:
    """Get bucket index for timestamp."""
    return (timestamp // window["bucket_size"]) % len(window["buckets"])


def increment_bucket(window: dict, timestamp: int) -> dict:
    """Increment current bucket count."""
    new_buckets = list(window["buckets"])
    idx = get_bucket_index(window, timestamp)
    new_buckets[idx] += 1
    return {**window, "buckets": new_buckets, "current_bucket": idx}


def get_window_total(window: dict) -> int:
    """Get total count across window."""
    return sum(window["buckets"])


def rotate_buckets(window: dict, current_bucket: int) -> dict:
    """Rotate to new bucket, clearing old."""
    new_buckets = list(window["buckets"])
    steps = (current_bucket - window["current_bucket"]) % len(new_buckets)
    for i in range(steps):
        clear_idx = (window["current_bucket"] + 1 + i) % len(new_buckets)
        new_buckets[clear_idx] = 0
    return {**window, "buckets": new_buckets, "current_bucket": current_bucket}


def create_token_bucket(capacity: int, refill_rate: float, refill_interval_ms: int) -> dict:
    """Create token bucket state."""
    return {
        "capacity": capacity,
        "tokens": capacity,
        "refill_rate": refill_rate,
        "refill_interval_ms": refill_interval_ms,
        "last_refill": 0
    }


def refill_tokens(bucket: dict, timestamp: int) -> dict:
    """Refill tokens based on elapsed time."""
    elapsed = timestamp - bucket["last_refill"]
    intervals = elapsed // bucket["refill_interval_ms"]
    new_tokens = min(bucket["capacity"], bucket["tokens"] + intervals * bucket["refill_rate"])
    return {**bucket, "tokens": new_tokens, "last_refill": timestamp}


def consume_tokens(bucket: dict, count: int) -> dict:
    """Consume tokens from bucket."""
    if bucket["tokens"] >= count:
        return {"success": True, "bucket": {**bucket, "tokens": bucket["tokens"] - count}}
    return {"success": False, "bucket": bucket}


def get_available_tokens(bucket: dict) -> float:
    """Get available tokens."""
    return bucket["tokens"]


def create_leaky_bucket(capacity: int, leak_rate: float, leak_interval_ms: int) -> dict:
    """Create leaky bucket state."""
    return {
        "capacity": capacity,
        "level": 0,
        "leak_rate": leak_rate,
        "leak_interval_ms": leak_interval_ms,
        "last_leak": 0
    }


def leak_bucket(bucket: dict, timestamp: int) -> dict:
    """Leak water from bucket."""
    elapsed = timestamp - bucket["last_leak"]
    intervals = elapsed // bucket["leak_interval_ms"]
    new_level = max(0, bucket["level"] - intervals * bucket["leak_rate"])
    return {**bucket, "level": new_level, "last_leak": timestamp}


def add_to_bucket(bucket: dict, amount: float) -> dict:
    """Add water to bucket."""
    new_level = bucket["level"] + amount
    if new_level > bucket["capacity"]:
        return {"success": False, "bucket": bucket, "overflow": new_level - bucket["capacity"]}
    return {"success": True, "bucket": {**bucket, "level": new_level}, "overflow": 0}
