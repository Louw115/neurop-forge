"""
Rate Limiting - Pure functions for rate limiting calculations.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def token_bucket_can_consume(tokens_available: float, tokens_requested: int) -> bool:
    """Check if tokens can be consumed from bucket."""
    return tokens_available >= tokens_requested


def token_bucket_remaining(tokens_available: float, tokens_requested: int) -> float:
    """Calculate remaining tokens after consumption."""
    return max(0, tokens_available - tokens_requested)


def token_bucket_refill(current_tokens: float, max_tokens: int, refill_rate: float, elapsed_seconds: float) -> float:
    """Calculate new token count after refill."""
    new_tokens = current_tokens + (refill_rate * elapsed_seconds)
    return min(new_tokens, max_tokens)


def token_bucket_time_to_refill(current_tokens: float, target_tokens: int, refill_rate: float) -> float:
    """Calculate time in seconds until bucket has target tokens."""
    if current_tokens >= target_tokens:
        return 0.0
    tokens_needed = target_tokens - current_tokens
    return tokens_needed / refill_rate if refill_rate > 0 else float('inf')


def sliding_window_count(request_times: list, window_start: int, window_end: int) -> int:
    """Count requests within a sliding window."""
    return sum(1 for t in request_times if window_start <= t < window_end)


def sliding_window_can_proceed(request_count: int, max_requests: int) -> bool:
    """Check if request can proceed based on sliding window count."""
    return request_count < max_requests


def sliding_window_remaining(request_count: int, max_requests: int) -> int:
    """Calculate remaining requests in sliding window."""
    return max(0, max_requests - request_count)


def fixed_window_bucket(timestamp: int, window_size: int) -> int:
    """Get the fixed window bucket for a timestamp."""
    return timestamp // window_size


def fixed_window_can_proceed(current_count: int, max_count: int) -> bool:
    """Check if request can proceed in fixed window."""
    return current_count < max_count


def fixed_window_remaining(current_count: int, max_count: int) -> int:
    """Calculate remaining requests in fixed window."""
    return max(0, max_count - current_count)


def fixed_window_reset_time(current_time: int, window_size: int) -> int:
    """Calculate when current fixed window resets."""
    current_bucket = fixed_window_bucket(current_time, window_size)
    return (current_bucket + 1) * window_size


def leaky_bucket_water_level(current_level: float, leak_rate: float, elapsed_seconds: float) -> float:
    """Calculate water level after leaking."""
    return max(0, current_level - (leak_rate * elapsed_seconds))


def leaky_bucket_can_add(current_level: float, bucket_size: int, amount: float) -> bool:
    """Check if water can be added to leaky bucket."""
    return current_level + amount <= bucket_size


def leaky_bucket_after_add(current_level: float, amount: float, bucket_size: int) -> float:
    """Calculate water level after adding."""
    return min(current_level + amount, bucket_size)


def leaky_bucket_overflow(current_level: float, amount: float, bucket_size: int) -> float:
    """Calculate overflow amount if any."""
    return max(0, current_level + amount - bucket_size)


def calculate_rate_per_second(requests: int, time_window_seconds: int) -> float:
    """Calculate request rate per second."""
    return requests / time_window_seconds if time_window_seconds > 0 else 0.0


def calculate_rate_per_minute(requests: int, time_window_seconds: int) -> float:
    """Calculate request rate per minute."""
    return (requests / time_window_seconds) * 60 if time_window_seconds > 0 else 0.0


def calculate_rate_per_hour(requests: int, time_window_seconds: int) -> float:
    """Calculate request rate per hour."""
    return (requests / time_window_seconds) * 3600 if time_window_seconds > 0 else 0.0


def is_rate_exceeded(current_rate: float, max_rate: float) -> bool:
    """Check if current rate exceeds maximum."""
    return current_rate > max_rate


def calculate_retry_after(rate_limit_reset: int, current_time: int) -> int:
    """Calculate retry-after seconds."""
    return max(0, rate_limit_reset - current_time)


def exponential_backoff(base_delay: float, attempt: int, max_delay: float) -> float:
    """Calculate exponential backoff delay."""
    delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)


def exponential_backoff_with_jitter(base_delay: float, attempt: int, max_delay: float, jitter_factor: float, seed: int) -> float:
    """Calculate exponential backoff with deterministic jitter."""
    delay = exponential_backoff(base_delay, attempt, max_delay)
    jitter = ((seed % 1000) / 1000) * jitter_factor * delay
    return delay + jitter


def linear_backoff(base_delay: float, attempt: int, increment: float, max_delay: float) -> float:
    """Calculate linear backoff delay."""
    delay = base_delay + (attempt * increment)
    return min(delay, max_delay)


def constant_backoff(delay: float) -> float:
    """Return constant backoff delay."""
    return delay


def fibonacci_backoff(attempt: int, base_delay: float, max_delay: float) -> float:
    """Calculate Fibonacci-based backoff delay."""
    if attempt <= 0:
        return base_delay
    if attempt == 1:
        return base_delay
    a, b = 1, 1
    for _ in range(attempt - 1):
        a, b = b, a + b
    delay = base_delay * b
    return min(delay, max_delay)


def should_retry(attempt: int, max_attempts: int) -> bool:
    """Check if retry should be attempted."""
    return attempt < max_attempts


def remaining_attempts(current_attempt: int, max_attempts: int) -> int:
    """Calculate remaining retry attempts."""
    return max(0, max_attempts - current_attempt)


def calculate_quota_usage_percent(used: int, limit: int) -> float:
    """Calculate quota usage as percentage."""
    return (used / limit) * 100 if limit > 0 else 100.0


def quota_remaining(used: int, limit: int) -> int:
    """Calculate remaining quota."""
    return max(0, limit - used)


def is_quota_exhausted(used: int, limit: int) -> bool:
    """Check if quota is exhausted."""
    return used >= limit


def is_quota_warning(used: int, limit: int, warning_threshold: float) -> bool:
    """Check if quota usage exceeds warning threshold."""
    return calculate_quota_usage_percent(used, limit) >= warning_threshold


def weighted_rate_limit(base_limit: int, weight: float) -> int:
    """Calculate weighted rate limit."""
    return int(base_limit * weight)


def tier_rate_limit(tier: str, tier_limits: dict, default_limit: int) -> int:
    """Get rate limit for a tier."""
    return tier_limits.get(tier, default_limit)


def calculate_concurrent_limit(base_limit: int, active_connections: int) -> int:
    """Calculate remaining concurrent connection limit."""
    return max(0, base_limit - active_connections)


def is_concurrent_limit_reached(active_connections: int, max_connections: int) -> bool:
    """Check if concurrent connection limit is reached."""
    return active_connections >= max_connections


def calculate_burst_allowance(base_rate: float, burst_multiplier: float) -> float:
    """Calculate burst rate allowance."""
    return base_rate * burst_multiplier


def is_burst_allowed(current_burst: int, max_burst: int) -> bool:
    """Check if burst is allowed."""
    return current_burst < max_burst


def calculate_adaptive_limit(current_limit: int, success_rate: float, min_limit: int, max_limit: int) -> int:
    """Calculate adaptive rate limit based on success rate."""
    if success_rate >= 0.95:
        new_limit = int(current_limit * 1.1)
    elif success_rate < 0.8:
        new_limit = int(current_limit * 0.9)
    else:
        new_limit = current_limit
    return max(min_limit, min(new_limit, max_limit))


def format_rate_limit_header(limit: int, remaining: int, reset_time: int) -> dict:
    """Format rate limit headers as dictionary."""
    return {
        'X-RateLimit-Limit': str(limit),
        'X-RateLimit-Remaining': str(remaining),
        'X-RateLimit-Reset': str(reset_time)
    }


def parse_rate_limit_headers(headers: dict) -> dict:
    """Parse rate limit information from headers."""
    return {
        'limit': int(headers.get('X-RateLimit-Limit', 0)),
        'remaining': int(headers.get('X-RateLimit-Remaining', 0)),
        'reset': int(headers.get('X-RateLimit-Reset', 0))
    }


def calculate_request_cost(request_type: str, cost_map: dict, default_cost: int) -> int:
    """Calculate the cost of a request based on type."""
    return cost_map.get(request_type, default_cost)


def can_afford_request(quota_remaining: int, request_cost: int) -> bool:
    """Check if quota can afford request cost."""
    return quota_remaining >= request_cost


def calculate_wait_time_for_tokens(tokens_needed: float, refill_rate: float) -> float:
    """Calculate time to wait for sufficient tokens."""
    return tokens_needed / refill_rate if refill_rate > 0 else float('inf')


def distributed_rate_key(user_id: str, endpoint: str) -> str:
    """Generate a distributed rate limiting key."""
    return f"rate:{user_id}:{endpoint}"


def sliding_log_prune_count(timestamps: list, cutoff_time: int) -> int:
    """Count timestamps that should be pruned."""
    return sum(1 for t in timestamps if t < cutoff_time)


def is_circuit_open(failure_count: int, threshold: int) -> bool:
    """Check if circuit breaker should be open."""
    return failure_count >= threshold


def circuit_breaker_state(failure_count: int, threshold: int, last_failure_time: int, current_time: int, reset_timeout: int) -> str:
    """Determine circuit breaker state."""
    if failure_count < threshold:
        return "closed"
    if current_time - last_failure_time > reset_timeout:
        return "half-open"
    return "open"


def calculate_failure_rate(failures: int, total: int) -> float:
    """Calculate failure rate."""
    return failures / total if total > 0 else 0.0
