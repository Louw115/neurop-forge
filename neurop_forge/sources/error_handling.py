"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Error Handling Utilities - Pure functions for error handling patterns.
All functions are pure, deterministic, and atomic.
"""

def categorize_http_error(status_code: int) -> str:
    """Categorize an HTTP error by status code."""
    if status_code < 400:
        return "success"
    if status_code < 500:
        return "client_error"
    return "server_error"


def get_error_severity(status_code: int) -> str:
    """Get error severity level based on status code."""
    if status_code < 400:
        return "info"
    if status_code < 500:
        return "warning"
    if status_code < 503:
        return "error"
    return "critical"


def is_retriable_error(status_code: int) -> bool:
    """Check if an HTTP error is retriable."""
    retriable_codes = {408, 429, 500, 502, 503, 504}
    return status_code in retriable_codes


def is_client_error(status_code: int) -> bool:
    """Check if status code indicates client error."""
    return 400 <= status_code < 500


def is_server_error(status_code: int) -> bool:
    """Check if status code indicates server error."""
    return status_code >= 500


def get_standard_error_message(status_code: int) -> str:
    """Get standard error message for HTTP status code."""
    messages = {
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a teapot",
        422: "Unprocessable Entity",
        423: "Locked",
        429: "Too Many Requests",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout"
    }
    return messages.get(status_code, "Unknown Error")


def build_error_context(error_type: str, error_message: str, stack_trace: str, request_id: str, timestamp: str) -> dict:
    """Build error context for logging."""
    return {
        "type": error_type,
        "message": error_message,
        "stack_trace": stack_trace,
        "request_id": request_id,
        "timestamp": timestamp
    }


def sanitize_error_for_client(error_context: dict) -> dict:
    """Sanitize error context for client response (remove sensitive info)."""
    return {
        "type": error_context.get("type", "Error"),
        "message": error_context.get("message", "An error occurred"),
        "request_id": error_context.get("request_id", "")
    }


def extract_error_code(error_message: str) -> str:
    """Extract error code from error message."""
    import re
    match = re.search(r'\[([A-Z0-9_]+)\]', error_message)
    if match:
        return match.group(1)
    return ""


def format_error_code(category: str, subcategory: str, sequence: int) -> str:
    """Format a structured error code."""
    return f"{category.upper()}_{subcategory.upper()}_{sequence:03d}"


def parse_error_code(code: str) -> dict:
    """Parse a structured error code."""
    parts = code.split('_')
    if len(parts) >= 3:
        return {
            "category": parts[0],
            "subcategory": parts[1],
            "sequence": int(parts[2]) if parts[2].isdigit() else 0
        }
    return {"category": code, "subcategory": "", "sequence": 0}


def calculate_error_rate(error_count: int, total_count: int) -> float:
    """Calculate error rate as percentage."""
    if total_count <= 0:
        return 0.0
    return (error_count / total_count) * 100.0


def is_error_spike(current_rate: float, baseline_rate: float, threshold_multiplier: float) -> bool:
    """Check if current error rate indicates a spike."""
    if baseline_rate <= 0:
        return current_rate > 0
    return current_rate >= baseline_rate * threshold_multiplier


def should_alert_on_error(error_count: int, threshold: int, window_seconds: int, last_alert_time: int, current_time: int, cooldown_seconds: int) -> bool:
    """Determine if an error alert should be sent."""
    if error_count < threshold:
        return False
    if current_time - last_alert_time < cooldown_seconds:
        return False
    return True


def format_error_log(level: str, error_type: str, message: str, request_id: str, timestamp: str) -> str:
    """Format an error for logging."""
    return f"[{timestamp}] {level.upper()} [{request_id}] {error_type}: {message}"


def build_error_report(errors: list, start_time: str, end_time: str) -> dict:
    """Build an error report from a list of errors."""
    by_type = {}
    by_code = {}
    for error in errors:
        error_type = error.get("type", "unknown")
        error_code = error.get("code", 0)
        by_type[error_type] = by_type.get(error_type, 0) + 1
        by_code[error_code] = by_code.get(error_code, 0) + 1
    return {
        "period": {"start": start_time, "end": end_time},
        "total_errors": len(errors),
        "by_type": by_type,
        "by_status_code": by_code
    }


def classify_error_impact(status_code: int, affected_users: int, is_critical_path: bool) -> str:
    """Classify the impact level of an error."""
    if is_critical_path and status_code >= 500:
        return "critical"
    if affected_users > 100:
        return "high"
    if affected_users > 10:
        return "medium"
    return "low"


def suggest_error_action(error_type: str, status_code: int) -> str:
    """Suggest action to take for an error type."""
    if status_code == 429:
        return "implement_backoff"
    if status_code == 401 or status_code == 403:
        return "check_credentials"
    if status_code == 404:
        return "verify_resource_exists"
    if status_code == 400:
        return "validate_request"
    if status_code >= 500:
        return "investigate_server"
    return "log_and_monitor"


def build_retry_config(status_code: int) -> dict:
    """Build retry configuration based on error type."""
    if not is_retriable_error(status_code):
        return {"should_retry": False}
    configs = {
        408: {"should_retry": True, "max_attempts": 3, "base_delay_ms": 1000},
        429: {"should_retry": True, "max_attempts": 5, "base_delay_ms": 5000},
        500: {"should_retry": True, "max_attempts": 3, "base_delay_ms": 2000},
        502: {"should_retry": True, "max_attempts": 3, "base_delay_ms": 1000},
        503: {"should_retry": True, "max_attempts": 5, "base_delay_ms": 5000},
        504: {"should_retry": True, "max_attempts": 3, "base_delay_ms": 3000}
    }
    return configs.get(status_code, {"should_retry": True, "max_attempts": 3, "base_delay_ms": 1000})


def format_validation_error(field: str, constraint: str, value: str) -> dict:
    """Format a validation error detail."""
    return {
        "field": field,
        "constraint": constraint,
        "value": str(value)[:100],
        "message": f"Field '{field}' failed {constraint} validation"
    }


def group_validation_errors(errors: list) -> dict:
    """Group validation errors by field."""
    by_field = {}
    for error in errors:
        field = error.get("field", "unknown")
        if field not in by_field:
            by_field[field] = []
        by_field[field].append(error.get("message", ""))
    return by_field


def is_transient_error(error_message: str) -> bool:
    """Check if an error message indicates a transient error."""
    transient_patterns = [
        "timeout", "timed out", "connection refused", "connection reset",
        "temporarily unavailable", "service unavailable", "try again",
        "rate limit", "too many requests", "overloaded"
    ]
    message_lower = error_message.lower()
    return any(pattern in message_lower for pattern in transient_patterns)


def mask_sensitive_data_in_error(error_message: str) -> str:
    """Mask sensitive data in error messages."""
    import re
    masked = re.sub(r'password["\']?\s*[:=]\s*["\']?[^"\'&\s]+', 'password=***', error_message, flags=re.IGNORECASE)
    masked = re.sub(r'api[-_]?key["\']?\s*[:=]\s*["\']?[^"\'&\s]+', 'api_key=***', masked, flags=re.IGNORECASE)
    masked = re.sub(r'token["\']?\s*[:=]\s*["\']?[^"\'&\s]+', 'token=***', masked, flags=re.IGNORECASE)
    masked = re.sub(r'secret["\']?\s*[:=]\s*["\']?[^"\'&\s]+', 'secret=***', masked, flags=re.IGNORECASE)
    return masked


def truncate_stack_trace(stack_trace: str, max_lines: int) -> str:
    """Truncate stack trace to maximum lines."""
    lines = stack_trace.split('\n')
    if len(lines) <= max_lines:
        return stack_trace
    return '\n'.join(lines[:max_lines]) + f'\n... ({len(lines) - max_lines} more lines)'


def extract_error_location(stack_trace: str) -> dict:
    """Extract file and line from stack trace."""
    import re
    match = re.search(r'File "([^"]+)", line (\d+)', stack_trace)
    if match:
        return {"file": match.group(1), "line": int(match.group(2))}
    return {"file": "", "line": 0}


def build_circuit_breaker_state(failure_count: int, success_count: int, threshold: int, last_failure_time: int, timeout_seconds: int, current_time: int) -> dict:
    """Build circuit breaker state."""
    if failure_count >= threshold:
        if current_time - last_failure_time < timeout_seconds:
            return {"state": "open", "can_attempt": False}
        else:
            return {"state": "half_open", "can_attempt": True}
    return {"state": "closed", "can_attempt": True}


def should_open_circuit(failure_count: int, threshold: int, window_seconds: int, oldest_failure_time: int, current_time: int) -> bool:
    """Determine if circuit breaker should open."""
    if failure_count < threshold:
        return False
    return (current_time - oldest_failure_time) <= window_seconds


def calculate_backoff_delay(attempt: int, base_delay_ms: int, max_delay_ms: int, jitter_seed: int) -> int:
    """Calculate exponential backoff delay with jitter."""
    delay = base_delay_ms * (2 ** attempt)
    delay = min(delay, max_delay_ms)
    import hashlib
    jitter_hash = hashlib.sha256(f"{attempt}:{jitter_seed}".encode()).digest()
    jitter = int.from_bytes(jitter_hash[:4], 'big') % (delay // 4) if delay > 0 else 0
    return delay + jitter
