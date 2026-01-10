"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Retry Patterns - Pure functions for retry logic and backoff strategies.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def calculate_constant_delay(base_delay: float, attempt: int) -> float:
    """Calculate constant delay."""
    return base_delay


def calculate_linear_delay(base_delay: float, attempt: int, increment: float) -> float:
    """Calculate linear backoff delay."""
    return base_delay + (attempt - 1) * increment


def calculate_exponential_delay(base_delay: float, attempt: int, multiplier: float) -> float:
    """Calculate exponential backoff delay."""
    return base_delay * (multiplier ** (attempt - 1))


def calculate_fibonacci_delay(base_delay: float, attempt: int) -> float:
    """Calculate Fibonacci backoff delay."""
    def fib(n):
        if n <= 1:
            return 1
        a, b = 1, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    return base_delay * fib(attempt)


def apply_jitter(delay: float, jitter_factor: float, seed: int) -> float:
    """Apply random jitter to delay."""
    h = hashlib.sha256(str(seed).encode()).digest()
    random_val = (h[0] / 255.0) * 2 - 1
    return delay * (1 + jitter_factor * random_val)


def apply_full_jitter(max_delay: float, seed: int) -> float:
    """Apply full jitter (0 to max_delay)."""
    h = hashlib.sha256(str(seed).encode()).digest()
    return max_delay * (h[0] / 255.0)


def apply_equal_jitter(delay: float, seed: int) -> float:
    """Apply equal jitter (delay/2 to delay)."""
    h = hashlib.sha256(str(seed).encode()).digest()
    return delay / 2 + delay / 2 * (h[0] / 255.0)


def apply_decorrelated_jitter(prev_delay: float, base_delay: float, max_delay: float, seed: int) -> float:
    """Apply decorrelated jitter."""
    h = hashlib.sha256(str(seed).encode()).digest()
    random_val = h[0] / 255.0
    return min(max_delay, base_delay + random_val * (prev_delay * 3 - base_delay))


def cap_delay(delay: float, max_delay: float) -> float:
    """Cap delay at maximum."""
    return min(delay, max_delay)


def should_retry(attempt: int, max_attempts: int) -> bool:
    """Check if should retry based on attempt count."""
    return attempt < max_attempts


def should_retry_error(error_type: str, retryable_errors: list) -> bool:
    """Check if error type is retryable."""
    return error_type in retryable_errors


def should_retry_status(status_code: int, retryable_codes: list) -> bool:
    """Check if HTTP status code is retryable."""
    return status_code in retryable_codes


def get_default_retryable_status_codes() -> list:
    """Get default retryable HTTP status codes."""
    return [408, 429, 500, 502, 503, 504]


def create_retry_state(max_attempts: int, base_delay: float) -> dict:
    """Create initial retry state."""
    return {
        "attempt": 0,
        "max_attempts": max_attempts,
        "base_delay": base_delay,
        "last_delay": 0,
        "total_delay": 0,
        "errors": []
    }


def record_attempt(state: dict, success: bool, error: str, delay: float) -> dict:
    """Record an attempt in retry state."""
    errors = list(state["errors"])
    if not success:
        errors.append({"attempt": state["attempt"] + 1, "error": error})
    return {
        "attempt": state["attempt"] + 1,
        "max_attempts": state["max_attempts"],
        "base_delay": state["base_delay"],
        "last_delay": delay,
        "total_delay": state["total_delay"] + delay,
        "errors": errors
    }


def is_exhausted(state: dict) -> bool:
    """Check if retries are exhausted."""
    return state["attempt"] >= state["max_attempts"]


def get_next_delay(state: dict, strategy: str, max_delay: float) -> float:
    """Get next delay based on strategy."""
    attempt = state["attempt"] + 1
    base = state["base_delay"]
    if strategy == "constant":
        delay = calculate_constant_delay(base, attempt)
    elif strategy == "linear":
        delay = calculate_linear_delay(base, attempt, base)
    elif strategy == "exponential":
        delay = calculate_exponential_delay(base, attempt, 2.0)
    elif strategy == "fibonacci":
        delay = calculate_fibonacci_delay(base, attempt)
    else:
        delay = base
    return cap_delay(delay, max_delay)


def create_retry_result(success: bool, value, state: dict) -> dict:
    """Create retry result."""
    return {
        "success": success,
        "value": value,
        "attempts": state["attempt"],
        "total_delay": state["total_delay"],
        "errors": state["errors"]
    }


def calculate_total_max_delay(base_delay: float, max_attempts: int, strategy: str, max_delay: float) -> float:
    """Calculate maximum possible total delay."""
    total = 0
    for attempt in range(1, max_attempts + 1):
        delay = get_next_delay(
            {"attempt": attempt - 1, "base_delay": base_delay, "max_attempts": max_attempts},
            strategy,
            max_delay
        )
        total += delay
    return total


def format_retry_stats(state: dict) -> dict:
    """Format retry statistics."""
    return {
        "total_attempts": state["attempt"],
        "max_attempts": state["max_attempts"],
        "remaining_attempts": state["max_attempts"] - state["attempt"],
        "total_delay_ms": state["total_delay"],
        "error_count": len(state["errors"]),
        "is_exhausted": is_exhausted(state)
    }


def create_circuit_breaker_state(failure_threshold: int, reset_timeout: float) -> dict:
    """Create circuit breaker state."""
    return {
        "state": "closed",
        "failures": 0,
        "failure_threshold": failure_threshold,
        "reset_timeout": reset_timeout,
        "last_failure_time": 0,
        "success_count": 0
    }


def update_circuit_breaker(breaker: dict, success: bool, current_time: float) -> dict:
    """Update circuit breaker state."""
    if breaker["state"] == "open":
        if current_time - breaker["last_failure_time"] >= breaker["reset_timeout"]:
            return {**breaker, "state": "half-open", "success_count": 0}
        return breaker
    if breaker["state"] == "half-open":
        if success:
            return {**breaker, "state": "closed", "failures": 0, "success_count": breaker["success_count"] + 1}
        else:
            return {**breaker, "state": "open", "last_failure_time": current_time}
    if success:
        return {**breaker, "failures": 0}
    else:
        new_failures = breaker["failures"] + 1
        if new_failures >= breaker["failure_threshold"]:
            return {**breaker, "state": "open", "failures": new_failures, "last_failure_time": current_time}
        return {**breaker, "failures": new_failures}


def is_circuit_open(breaker: dict) -> bool:
    """Check if circuit is open."""
    return breaker["state"] == "open"


def can_attempt(breaker: dict, current_time: float) -> bool:
    """Check if attempt is allowed."""
    if breaker["state"] == "closed" or breaker["state"] == "half-open":
        return True
    return current_time - breaker["last_failure_time"] >= breaker["reset_timeout"]
