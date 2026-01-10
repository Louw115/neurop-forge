"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Error Codes - Pure functions for error code handling.
All functions are pure, deterministic, and atomic.
"""


def create_error_code(category: str, code: int) -> str:
    """Create error code string."""
    return f"{category.upper()}-{code:04d}"


def parse_error_code(error_code: str) -> dict:
    """Parse error code into components."""
    parts = error_code.split("-")
    if len(parts) != 2:
        return {"valid": False, "category": "", "code": 0}
    try:
        return {
            "valid": True,
            "category": parts[0],
            "code": int(parts[1])
        }
    except ValueError:
        return {"valid": False, "category": "", "code": 0}


def is_valid_error_code(error_code: str) -> bool:
    """Check if error code is valid."""
    return parse_error_code(error_code)["valid"]


def get_error_category(error_code: str) -> str:
    """Get category from error code."""
    return parse_error_code(error_code)["category"]


def is_category(error_code: str, category: str) -> bool:
    """Check if error code is in category."""
    return get_error_category(error_code).upper() == category.upper()


def create_error_response(code: str, message: str, details: dict) -> dict:
    """Create standardized error response."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }


def get_http_status_for_code(error_code: str) -> int:
    """Get HTTP status for error code category."""
    category = get_error_category(error_code)
    status_map = {
        "AUTH": 401,
        "PERM": 403,
        "NOTFOUND": 404,
        "VAL": 400,
        "CONFLICT": 409,
        "RATE": 429,
        "SERVER": 500,
        "TIMEOUT": 504
    }
    return status_map.get(category, 500)


def is_client_error(error_code: str) -> bool:
    """Check if error is client error."""
    status = get_http_status_for_code(error_code)
    return 400 <= status < 500


def is_server_error(error_code: str) -> bool:
    """Check if error is server error."""
    status = get_http_status_for_code(error_code)
    return status >= 500


def is_retryable_error(error_code: str) -> bool:
    """Check if error is retryable."""
    category = get_error_category(error_code)
    return category in ["TIMEOUT", "RATE", "SERVER"]


def format_user_message(error_code: str, messages: dict) -> str:
    """Format user-friendly message for error code."""
    return messages.get(error_code, "An error occurred")


def create_validation_error(field: str, rule: str, message: str) -> dict:
    """Create validation error object."""
    return {
        "code": create_error_code("VAL", hash(field + rule) % 1000),
        "field": field,
        "rule": rule,
        "message": message
    }


def aggregate_validation_errors(errors: list) -> dict:
    """Aggregate validation errors by field."""
    by_field = {}
    for error in errors:
        field = error.get("field", "_general")
        if field not in by_field:
            by_field[field] = []
        by_field[field].append({
            "code": error.get("code"),
            "rule": error.get("rule"),
            "message": error.get("message")
        })
    return by_field


def create_error_chain(errors: list) -> dict:
    """Create error chain from multiple errors."""
    return {
        "primary": errors[0] if errors else None,
        "chain": errors,
        "count": len(errors)
    }


def has_error_type(errors: list, category: str) -> bool:
    """Check if any error is of category."""
    return any(is_category(e.get("code", ""), category) for e in errors)


def filter_errors_by_category(errors: list, category: str) -> list:
    """Filter errors by category."""
    return [e for e in errors if is_category(e.get("code", ""), category)]


def map_error_code(source_code: str, mapping: dict) -> str:
    """Map error code to different code."""
    return mapping.get(source_code, source_code)


def create_error_log_entry(error_code: str, message: str, context: dict, timestamp: int) -> dict:
    """Create error log entry."""
    return {
        "timestamp": timestamp,
        "code": error_code,
        "message": message,
        "context": context,
        "severity": get_severity(error_code)
    }


def get_severity(error_code: str) -> str:
    """Get severity level for error code."""
    category = get_error_category(error_code)
    if category in ["SERVER", "TIMEOUT"]:
        return "error"
    if category in ["AUTH", "PERM"]:
        return "warning"
    return "info"


def should_alert(error_code: str) -> bool:
    """Check if error should trigger alert."""
    return get_severity(error_code) == "error"


def increment_error_counter(counters: dict, error_code: str) -> dict:
    """Increment counter for error code."""
    result = dict(counters)
    result[error_code] = result.get(error_code, 0) + 1
    return result


def get_top_errors(counters: dict, n: int) -> list:
    """Get top N most frequent errors."""
    sorted_errors = sorted(counters.items(), key=lambda x: -x[1])
    return sorted_errors[:n]
