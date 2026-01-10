"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Exception Utilities - Pure functions for exception handling patterns.
All functions are pure, deterministic, and atomic.
"""

def create_error_result(success: bool, value, error: str) -> dict:
    """Create standardized result object."""
    return {
        "success": success,
        "value": value,
        "error": error
    }


def ok(value) -> dict:
    """Create success result."""
    return create_error_result(True, value, None)


def err(error: str) -> dict:
    """Create error result."""
    return create_error_result(False, None, error)


def is_ok(result: dict) -> bool:
    """Check if result is success."""
    return result.get("success", False)


def is_err(result: dict) -> bool:
    """Check if result is error."""
    return not result.get("success", True)


def unwrap(result: dict, default=None):
    """Unwrap result value or return default."""
    if is_ok(result):
        return result.get("value")
    return default


def unwrap_or_raise(result: dict):
    """Unwrap result or raise exception."""
    if is_ok(result):
        return result.get("value")
    raise ValueError(result.get("error", "Unknown error"))


def map_result(result: dict, mapper) -> dict:
    """Map function over result value."""
    if is_ok(result):
        return ok(mapper(result["value"]))
    return result


def flat_map_result(result: dict, mapper) -> dict:
    """Flat map function over result."""
    if is_ok(result):
        return mapper(result["value"])
    return result


def combine_results(results: list) -> dict:
    """Combine multiple results."""
    errors = []
    values = []
    for r in results:
        if is_err(r):
            errors.append(r.get("error"))
        else:
            values.append(r.get("value"))
    if errors:
        return err("; ".join(errors))
    return ok(values)


def first_ok(results: list) -> dict:
    """Return first successful result."""
    for r in results:
        if is_ok(r):
            return r
    return err("No successful results")


def categorize_error(error: str) -> str:
    """Categorize error type from message."""
    error_lower = error.lower()
    if "timeout" in error_lower:
        return "timeout"
    if "connection" in error_lower or "network" in error_lower:
        return "network"
    if "permission" in error_lower or "denied" in error_lower:
        return "permission"
    if "not found" in error_lower or "missing" in error_lower:
        return "not_found"
    if "invalid" in error_lower or "validation" in error_lower:
        return "validation"
    if "authentication" in error_lower or "unauthorized" in error_lower:
        return "auth"
    return "unknown"


def is_retryable(error_category: str) -> bool:
    """Check if error category is retryable."""
    return error_category in ["timeout", "network"]


def create_error_chain(errors: list) -> dict:
    """Create error chain for tracking."""
    return {
        "errors": errors,
        "count": len(errors),
        "first": errors[0] if errors else None,
        "last": errors[-1] if errors else None
    }


def add_to_chain(chain: dict, error: str) -> dict:
    """Add error to chain."""
    new_errors = chain.get("errors", []) + [error]
    return create_error_chain(new_errors)


def format_error_message(error: str, context: dict) -> str:
    """Format error message with context."""
    parts = [error]
    for key, value in context.items():
        parts.append(f"{key}={value}")
    return " | ".join(parts)


def parse_error_message(formatted: str) -> dict:
    """Parse formatted error message."""
    parts = formatted.split(" | ")
    result = {"message": parts[0]}
    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            result[key] = value
    return result


def create_validation_error(field: str, message: str) -> dict:
    """Create validation error."""
    return {
        "type": "validation",
        "field": field,
        "message": message
    }


def aggregate_validation_errors(errors: list) -> dict:
    """Aggregate validation errors by field."""
    by_field = {}
    for error in errors:
        field = error.get("field", "general")
        if field not in by_field:
            by_field[field] = []
        by_field[field].append(error.get("message"))
    return by_field


def has_field_error(errors: dict, field: str) -> bool:
    """Check if field has errors."""
    return field in errors and len(errors[field]) > 0


def get_field_errors(errors: dict, field: str) -> list:
    """Get errors for specific field."""
    return errors.get(field, [])


def create_http_error(status: int, message: str) -> dict:
    """Create HTTP error object."""
    return {
        "status": status,
        "message": message,
        "category": categorize_http_status(status)
    }


def categorize_http_status(status: int) -> str:
    """Categorize HTTP status code."""
    if status < 400:
        return "success"
    if status < 500:
        return "client_error"
    return "server_error"


def is_client_error(status: int) -> bool:
    """Check if status is client error."""
    return 400 <= status < 500


def is_server_error(status: int) -> bool:
    """Check if status is server error."""
    return status >= 500


def get_http_message(status: int) -> str:
    """Get standard HTTP message for status."""
    messages = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        408: "Request Timeout",
        409: "Conflict",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout"
    }
    return messages.get(status, "Unknown Error")
