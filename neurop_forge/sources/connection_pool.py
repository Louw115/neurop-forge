"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Connection Pool Utilities - Pure functions for connection pool management patterns.
All functions are pure, deterministic, and atomic.
No actual database connections - just pool logic helpers.
"""

def calculate_pool_size(max_connections: int, workers: int, connections_per_worker: int) -> int:
    """Calculate optimal pool size based on workers and connections per worker."""
    calculated = workers * connections_per_worker
    return min(calculated, max_connections)


def calculate_min_pool_size(max_size: int, ratio: float) -> int:
    """Calculate minimum pool size as a ratio of max size."""
    return max(1, int(max_size * ratio))


def should_grow_pool(current_size: int, max_size: int, waiting_requests: int, threshold: int) -> bool:
    """Determine if pool should grow based on demand."""
    return current_size < max_size and waiting_requests > threshold


def should_shrink_pool(current_size: int, min_size: int, idle_connections: int, idle_threshold: int) -> bool:
    """Determine if pool should shrink based on idle connections."""
    return current_size > min_size and idle_connections > idle_threshold


def calculate_connection_age_seconds(created_at_timestamp: int, current_timestamp: int) -> int:
    """Calculate age of a connection in seconds."""
    return current_timestamp - created_at_timestamp


def is_connection_stale(created_at_timestamp: int, current_timestamp: int, max_age_seconds: int) -> bool:
    """Check if a connection has exceeded maximum age."""
    return calculate_connection_age_seconds(created_at_timestamp, current_timestamp) > max_age_seconds


def is_connection_idle_too_long(last_used_timestamp: int, current_timestamp: int, max_idle_seconds: int) -> bool:
    """Check if a connection has been idle too long."""
    return (current_timestamp - last_used_timestamp) > max_idle_seconds


def calculate_pool_utilization(active_connections: int, pool_size: int) -> float:
    """Calculate pool utilization percentage."""
    if pool_size <= 0:
        return 0.0
    return (active_connections / pool_size) * 100.0


def is_pool_exhausted(active_connections: int, pool_size: int) -> bool:
    """Check if pool has no available connections."""
    return active_connections >= pool_size


def calculate_wait_queue_position(queue_size: int) -> int:
    """Calculate position in wait queue for new request."""
    return queue_size + 1


def should_reject_request(queue_size: int, max_queue_size: int) -> bool:
    """Determine if request should be rejected due to queue overflow."""
    return queue_size >= max_queue_size


def calculate_estimated_wait_time(queue_position: int, avg_request_duration_ms: int) -> int:
    """Estimate wait time in milliseconds based on queue position."""
    return queue_position * avg_request_duration_ms


def format_pool_stats(pool_name: str, size: int, active: int, idle: int, waiting: int) -> str:
    """Format pool statistics as a string."""
    utilization = calculate_pool_utilization(active, size)
    return f"Pool '{pool_name}': size={size}, active={active}, idle={idle}, waiting={waiting}, utilization={utilization:.1f}%"


def parse_connection_string(conn_str: str) -> dict:
    """Parse a database connection string into components."""
    import re
    result = {
        "host": "",
        "port": 5432,
        "database": "",
        "user": "",
        "password": "",
        "options": {}
    }
    pattern = r'^(?:(\w+)://)?(?:([^:@]+)(?::([^@]*))?@)?([^:/]+)?(?::(\d+))?(?:/([^?]+))?(?:\?(.+))?$'
    match = re.match(pattern, conn_str)
    if match:
        if match.group(2):
            result["user"] = match.group(2)
        if match.group(3):
            result["password"] = match.group(3)
        if match.group(4):
            result["host"] = match.group(4)
        if match.group(5):
            result["port"] = int(match.group(5))
        if match.group(6):
            result["database"] = match.group(6)
        if match.group(7):
            for param in match.group(7).split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    result["options"][key] = value
    return result


def build_connection_string(host: str, port: int, database: str, user: str, password: str, options: dict) -> str:
    """Build a connection string from components."""
    auth = ""
    if user:
        auth = user
        if password:
            auth += f":{password}"
        auth += "@"
    host_part = host
    if port and port != 5432:
        host_part += f":{port}"
    options_str = ""
    if options:
        options_str = "?" + "&".join(f"{k}={v}" for k, v in options.items())
    return f"postgresql://{auth}{host_part}/{database}{options_str}"


def mask_connection_password(conn_str: str) -> str:
    """Mask the password in a connection string for logging."""
    import re
    return re.sub(r'(://[^:]+:)[^@]+(@)', r'\1***\2', conn_str)


def is_valid_connection_string(conn_str: str) -> bool:
    """Validate a connection string format."""
    import re
    pattern = r'^(postgresql|postgres|mysql|sqlite)://'
    return bool(re.match(pattern, conn_str))


def get_connection_driver(conn_str: str) -> str:
    """Extract the database driver from connection string."""
    if conn_str.startswith('postgresql://') or conn_str.startswith('postgres://'):
        return 'postgresql'
    if conn_str.startswith('mysql://'):
        return 'mysql'
    if conn_str.startswith('sqlite://'):
        return 'sqlite'
    return 'unknown'


def calculate_retry_connection_delay(attempt: int, base_delay_ms: int, max_delay_ms: int) -> int:
    """Calculate delay before retry connection attempt."""
    delay = base_delay_ms * (2 ** attempt)
    return min(delay, max_delay_ms)


def should_retry_connection(error_code: str, attempt: int, max_attempts: int) -> bool:
    """Determine if connection should be retried based on error."""
    retriable_codes = {"08001", "08003", "08004", "08006", "08007", "57P01", "57P02", "57P03"}
    return error_code in retriable_codes and attempt < max_attempts


def format_connection_error(error_code: str, error_message: str, host: str, port: int) -> str:
    """Format a connection error for logging."""
    return f"Connection failed to {host}:{port} - [{error_code}] {error_message}"


def calculate_health_check_interval(pool_size: int, base_interval_seconds: int) -> int:
    """Calculate health check interval based on pool size."""
    return max(base_interval_seconds, pool_size * 2)


def is_connection_healthy(last_check_timestamp: int, current_timestamp: int, health_check_interval: int) -> bool:
    """Check if connection health is up to date."""
    return (current_timestamp - last_check_timestamp) <= health_check_interval


def generate_health_check_query(driver: str) -> str:
    """Generate appropriate health check query for database driver."""
    queries = {
        "postgresql": "SELECT 1",
        "mysql": "SELECT 1",
        "sqlite": "SELECT 1"
    }
    return queries.get(driver, "SELECT 1")


def calculate_connection_score(age_seconds: int, max_age: int, error_count: int, max_errors: int) -> float:
    """Calculate a health score for a connection (0.0 to 1.0)."""
    age_score = 1.0 - min(age_seconds / max_age, 1.0)
    error_score = 1.0 - min(error_count / max_errors, 1.0)
    return (age_score + error_score) / 2.0


def select_connection_fifo(connection_ages: list) -> int:
    """Select connection using FIFO (oldest first) strategy."""
    if not connection_ages:
        return -1
    return connection_ages.index(min(connection_ages))


def select_connection_lifo(connection_ages: list) -> int:
    """Select connection using LIFO (newest first) strategy."""
    if not connection_ages:
        return -1
    return connection_ages.index(max(connection_ages))


def select_connection_round_robin(current_index: int, pool_size: int) -> int:
    """Select connection using round-robin strategy."""
    if pool_size <= 0:
        return -1
    return (current_index + 1) % pool_size


def get_pool_metrics(active: int, idle: int, waiting: int, total_acquired: int, total_released: int, total_timeouts: int) -> dict:
    """Compile pool metrics into a dictionary."""
    return {
        "active_connections": active,
        "idle_connections": idle,
        "waiting_requests": waiting,
        "total_acquired": total_acquired,
        "total_released": total_released,
        "total_timeouts": total_timeouts,
        "acquisition_rate": total_acquired / max(total_released, 1)
    }


def should_log_pool_warning(utilization: float, warning_threshold: float) -> bool:
    """Check if pool utilization warrants a warning."""
    return utilization >= warning_threshold


def should_log_pool_critical(utilization: float, waiting: int, critical_threshold: float) -> bool:
    """Check if pool status is critical."""
    return utilization >= critical_threshold or waiting > 0


def calculate_optimal_pool_config(expected_concurrent_users: int, queries_per_request: int, avg_query_duration_ms: int, max_wait_ms: int) -> dict:
    """Calculate optimal pool configuration based on expected load."""
    connections_needed = int((expected_concurrent_users * queries_per_request * avg_query_duration_ms) / 1000)
    min_connections = max(2, connections_needed // 4)
    max_connections = max(connections_needed * 2, 10)
    return {
        "min_size": min_connections,
        "max_size": max_connections,
        "connection_timeout_ms": max_wait_ms,
        "idle_timeout_seconds": 300,
        "max_lifetime_seconds": 3600
    }


def validate_pool_config(config: dict) -> dict:
    """Validate pool configuration parameters."""
    errors = []
    if config.get("min_size", 0) < 0:
        errors.append("min_size must be non-negative")
    if config.get("max_size", 0) < config.get("min_size", 0):
        errors.append("max_size must be >= min_size")
    if config.get("connection_timeout_ms", 0) < 0:
        errors.append("connection_timeout_ms must be non-negative")
    if config.get("idle_timeout_seconds", 0) < 0:
        errors.append("idle_timeout_seconds must be non-negative")
    return {"valid": len(errors) == 0, "errors": errors}


def build_pool_name(database: str, purpose: str) -> str:
    """Generate a descriptive pool name."""
    return f"{database}_{purpose}_pool"


def calculate_connection_reuse_ratio(total_queries: int, total_connections_created: int) -> float:
    """Calculate how effectively connections are being reused."""
    if total_connections_created <= 0:
        return 0.0
    return total_queries / total_connections_created
