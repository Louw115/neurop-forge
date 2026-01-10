"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Assertion Utilities - Pure functions for assertion and testing patterns.
All functions are pure, deterministic, and atomic.
"""


def assert_equals(actual, expected) -> dict:
    """Assert two values are equal."""
    passed = actual == expected
    return {
        "passed": passed,
        "actual": actual,
        "expected": expected,
        "message": "" if passed else f"Expected {expected}, got {actual}"
    }


def assert_not_equals(actual, not_expected) -> dict:
    """Assert two values are not equal."""
    passed = actual != not_expected
    return {
        "passed": passed,
        "actual": actual,
        "not_expected": not_expected,
        "message": "" if passed else f"Expected not to equal {not_expected}"
    }


def assert_true(value: bool) -> dict:
    """Assert value is true."""
    passed = value is True
    return {
        "passed": passed,
        "actual": value,
        "message": "" if passed else "Expected True"
    }


def assert_false(value: bool) -> dict:
    """Assert value is false."""
    passed = value is False
    return {
        "passed": passed,
        "actual": value,
        "message": "" if passed else "Expected False"
    }


def assert_none(value) -> dict:
    """Assert value is None."""
    passed = value is None
    return {
        "passed": passed,
        "actual": value,
        "message": "" if passed else f"Expected None, got {value}"
    }


def assert_not_none(value) -> dict:
    """Assert value is not None."""
    passed = value is not None
    return {
        "passed": passed,
        "actual": value,
        "message": "" if passed else "Expected not None"
    }


def assert_greater(value, threshold) -> dict:
    """Assert value is greater than threshold."""
    passed = value > threshold
    return {
        "passed": passed,
        "actual": value,
        "threshold": threshold,
        "message": "" if passed else f"Expected {value} > {threshold}"
    }


def assert_greater_or_equal(value, threshold) -> dict:
    """Assert value is greater or equal."""
    passed = value >= threshold
    return {
        "passed": passed,
        "actual": value,
        "threshold": threshold,
        "message": "" if passed else f"Expected {value} >= {threshold}"
    }


def assert_less(value, threshold) -> dict:
    """Assert value is less than threshold."""
    passed = value < threshold
    return {
        "passed": passed,
        "actual": value,
        "threshold": threshold,
        "message": "" if passed else f"Expected {value} < {threshold}"
    }


def assert_less_or_equal(value, threshold) -> dict:
    """Assert value is less or equal."""
    passed = value <= threshold
    return {
        "passed": passed,
        "actual": value,
        "threshold": threshold,
        "message": "" if passed else f"Expected {value} <= {threshold}"
    }


def assert_in_range(value, min_val, max_val) -> dict:
    """Assert value is in range."""
    passed = min_val <= value <= max_val
    return {
        "passed": passed,
        "actual": value,
        "min": min_val,
        "max": max_val,
        "message": "" if passed else f"Expected {value} in [{min_val}, {max_val}]"
    }


def assert_contains(collection, item) -> dict:
    """Assert collection contains item."""
    passed = item in collection
    return {
        "passed": passed,
        "item": item,
        "message": "" if passed else f"Expected collection to contain {item}"
    }


def assert_not_contains(collection, item) -> dict:
    """Assert collection does not contain item."""
    passed = item not in collection
    return {
        "passed": passed,
        "item": item,
        "message": "" if passed else f"Expected collection to not contain {item}"
    }


def assert_length(collection, expected_length: int) -> dict:
    """Assert collection has expected length."""
    actual = len(collection)
    passed = actual == expected_length
    return {
        "passed": passed,
        "actual_length": actual,
        "expected_length": expected_length,
        "message": "" if passed else f"Expected length {expected_length}, got {actual}"
    }


def assert_empty(collection) -> dict:
    """Assert collection is empty."""
    passed = len(collection) == 0
    return {
        "passed": passed,
        "actual_length": len(collection),
        "message": "" if passed else f"Expected empty, got {len(collection)} items"
    }


def assert_not_empty(collection) -> dict:
    """Assert collection is not empty."""
    passed = len(collection) > 0
    return {
        "passed": passed,
        "actual_length": len(collection),
        "message": "" if passed else "Expected not empty"
    }


def assert_type(value, expected_type: str) -> dict:
    """Assert value is of expected type."""
    actual = type(value).__name__
    passed = actual == expected_type
    return {
        "passed": passed,
        "actual_type": actual,
        "expected_type": expected_type,
        "message": "" if passed else f"Expected type {expected_type}, got {actual}"
    }


def assert_match(text: str, pattern: str) -> dict:
    """Assert text matches pattern."""
    import re
    passed = bool(re.match(pattern, text))
    return {
        "passed": passed,
        "text": text,
        "pattern": pattern,
        "message": "" if passed else f"Expected to match {pattern}"
    }


def assert_starts_with(text: str, prefix: str) -> dict:
    """Assert text starts with prefix."""
    passed = text.startswith(prefix)
    return {
        "passed": passed,
        "text": text,
        "prefix": prefix,
        "message": "" if passed else f"Expected to start with {prefix}"
    }


def assert_ends_with(text: str, suffix: str) -> dict:
    """Assert text ends with suffix."""
    passed = text.endswith(suffix)
    return {
        "passed": passed,
        "text": text,
        "suffix": suffix,
        "message": "" if passed else f"Expected to end with {suffix}"
    }


def assert_deep_equals(actual: dict, expected: dict) -> dict:
    """Assert deep equality of objects."""
    import json
    passed = json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)
    return {
        "passed": passed,
        "message": "" if passed else "Objects are not deeply equal"
    }


def summarize_assertions(results: list) -> dict:
    """Summarize assertion results."""
    total = len(results)
    passed = sum(1 for r in results if r.get("passed"))
    failed = total - passed
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / total if total > 0 else 0,
        "all_passed": failed == 0
    }
