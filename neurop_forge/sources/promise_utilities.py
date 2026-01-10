"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Promise/Future Utilities - Pure functions for async patterns.
All functions are pure, deterministic, and atomic.
"""

def create_pending_promise(promise_id: str) -> dict:
    """Create a pending promise."""
    return {
        "id": promise_id,
        "status": "pending",
        "value": None,
        "error": None,
        "timestamp": None
    }


def resolve_promise(promise: dict, value, timestamp: str) -> dict:
    """Resolve a promise with a value."""
    if promise["status"] != "pending":
        return promise
    return {
        "id": promise["id"],
        "status": "resolved",
        "value": value,
        "error": None,
        "timestamp": timestamp
    }


def reject_promise(promise: dict, error: str, timestamp: str) -> dict:
    """Reject a promise with an error."""
    if promise["status"] != "pending":
        return promise
    return {
        "id": promise["id"],
        "status": "rejected",
        "value": None,
        "error": error,
        "timestamp": timestamp
    }


def is_pending(promise: dict) -> bool:
    """Check if promise is pending."""
    return promise["status"] == "pending"


def is_resolved(promise: dict) -> bool:
    """Check if promise is resolved."""
    return promise["status"] == "resolved"


def is_rejected(promise: dict) -> bool:
    """Check if promise is rejected."""
    return promise["status"] == "rejected"


def is_settled(promise: dict) -> bool:
    """Check if promise is settled (resolved or rejected)."""
    return promise["status"] in ["resolved", "rejected"]


def get_value(promise: dict):
    """Get promise value if resolved."""
    return promise["value"] if is_resolved(promise) else None


def get_error(promise: dict):
    """Get promise error if rejected."""
    return promise["error"] if is_rejected(promise) else None


def map_promise(promise: dict, transform) -> dict:
    """Map transformation over resolved value."""
    if not is_resolved(promise):
        return promise
    return {**promise, "value": transform(promise["value"])}


def flat_map_promise(promise: dict, transform) -> dict:
    """Flat map transformation over resolved value."""
    if not is_resolved(promise):
        return promise
    new_promise = transform(promise["value"])
    return new_promise if isinstance(new_promise, dict) else promise


def recover_promise(promise: dict, recovery_fn) -> dict:
    """Recover from rejected promise."""
    if not is_rejected(promise):
        return promise
    return {
        "id": promise["id"],
        "status": "resolved",
        "value": recovery_fn(promise["error"]),
        "error": None,
        "timestamp": promise["timestamp"]
    }


def all_settled(promises: list) -> bool:
    """Check if all promises are settled."""
    return all(is_settled(p) for p in promises)


def any_resolved(promises: list) -> bool:
    """Check if any promise is resolved."""
    return any(is_resolved(p) for p in promises)


def all_resolved(promises: list) -> bool:
    """Check if all promises are resolved."""
    return all(is_resolved(p) for p in promises)


def any_rejected(promises: list) -> bool:
    """Check if any promise is rejected."""
    return any(is_rejected(p) for p in promises)


def collect_values(promises: list) -> list:
    """Collect values from resolved promises."""
    return [p["value"] for p in promises if is_resolved(p)]


def collect_errors(promises: list) -> list:
    """Collect errors from rejected promises."""
    return [p["error"] for p in promises if is_rejected(p)]


def first_resolved(promises: list) -> dict:
    """Get first resolved promise."""
    for p in promises:
        if is_resolved(p):
            return p
    return None


def first_settled(promises: list) -> dict:
    """Get first settled promise."""
    for p in promises:
        if is_settled(p):
            return p
    return None


def create_deferred() -> dict:
    """Create a deferred (promise with external resolution)."""
    return {
        "promise": create_pending_promise("deferred"),
        "resolved": False,
        "rejected": False
    }


def build_promise_result(success: bool, value, error: str) -> dict:
    """Build a promise-like result object."""
    return {
        "success": success,
        "value": value if success else None,
        "error": error if not success else None
    }


def retry_result(attempts: int, max_attempts: int, last_error: str, success: bool) -> dict:
    """Build retry result."""
    return {
        "success": success,
        "attempts": attempts,
        "max_attempts": max_attempts,
        "should_retry": not success and attempts < max_attempts,
        "last_error": last_error
    }


def calculate_retry_delay(attempt: int, base_delay: int, max_delay: int, strategy: str) -> int:
    """Calculate delay for retry attempt."""
    if strategy == "constant":
        return base_delay
    elif strategy == "linear":
        return min(base_delay * attempt, max_delay)
    elif strategy == "exponential":
        return min(base_delay * (2 ** (attempt - 1)), max_delay)
    return base_delay


def build_timeout_result(timed_out: bool, duration_ms: int, timeout_ms: int) -> dict:
    """Build timeout result."""
    return {
        "timed_out": timed_out,
        "duration_ms": duration_ms,
        "timeout_ms": timeout_ms
    }


def partition_promises(promises: list) -> dict:
    """Partition promises by status."""
    return {
        "pending": [p for p in promises if is_pending(p)],
        "resolved": [p for p in promises if is_resolved(p)],
        "rejected": [p for p in promises if is_rejected(p)]
    }


def summarize_promises(promises: list) -> dict:
    """Summarize promise states."""
    partition = partition_promises(promises)
    return {
        "total": len(promises),
        "pending": len(partition["pending"]),
        "resolved": len(partition["resolved"]),
        "rejected": len(partition["rejected"]),
        "completion_rate": len(partition["resolved"]) / len(promises) if promises else 0
    }


def chain_results(results: list) -> dict:
    """Chain multiple results, stopping at first failure."""
    for result in results:
        if not result.get("success", False):
            return result
    if results:
        return results[-1]
    return build_promise_result(True, None, None)


def merge_results(results: list) -> dict:
    """Merge multiple results."""
    values = []
    errors = []
    for result in results:
        if result.get("success", False):
            values.append(result.get("value"))
        else:
            errors.append(result.get("error"))
    return {
        "success": len(errors) == 0,
        "values": values,
        "errors": errors
    }
