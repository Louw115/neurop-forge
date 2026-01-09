"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Comparison and Logic Functions - Pure functions for comparisons and logical operations.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def equals(a, b) -> bool:
    """Check if two values are equal."""
    return a == b


def not_equals(a, b) -> bool:
    """Check if two values are not equal."""
    return a != b


def is_greater_than(a: float, b: float) -> bool:
    """Check if a is greater than b."""
    return a > b


def is_greater_or_equal(a: float, b: float) -> bool:
    """Check if a is greater than or equal to b."""
    return a >= b


def is_less_than(a: float, b: float) -> bool:
    """Check if a is less than b."""
    return a < b


def is_less_or_equal(a: float, b: float) -> bool:
    """Check if a is less than or equal to b."""
    return a <= b


def is_between(value: float, lower: float, upper: float) -> bool:
    """Check if a value is between lower and upper (inclusive)."""
    return lower <= value <= upper


def is_between_exclusive(value: float, lower: float, upper: float) -> bool:
    """Check if a value is between lower and upper (exclusive)."""
    return lower < value < upper


def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value to be within a range."""
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value


def compare_values(a: float, b: float) -> int:
    """Compare two values. Returns -1 if a < b, 0 if equal, 1 if a > b."""
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def logical_and(a: bool, b: bool) -> bool:
    """Logical AND operation."""
    return a and b


def logical_or(a: bool, b: bool) -> bool:
    """Logical OR operation."""
    return a or b


def logical_not(value: bool) -> bool:
    """Logical NOT operation."""
    return not value


def logical_xor(a: bool, b: bool) -> bool:
    """Logical XOR operation."""
    return (a and not b) or (not a and b)


def logical_nand(a: bool, b: bool) -> bool:
    """Logical NAND operation."""
    return not (a and b)


def logical_nor(a: bool, b: bool) -> bool:
    """Logical NOR operation."""
    return not (a or b)


def all_true(values: list) -> bool:
    """Check if all values in a list are truthy."""
    return all(values)


def any_true(values: list) -> bool:
    """Check if any value in a list is truthy."""
    return any(values)


def none_true(values: list) -> bool:
    """Check if no values in a list are truthy."""
    return not any(values)


def count_true(values: list) -> int:
    """Count the number of truthy values in a list."""
    return sum(1 for v in values if v)


def count_false(values: list) -> int:
    """Count the number of falsy values in a list."""
    return sum(1 for v in values if not v)


def if_then_else(condition: bool, true_value, false_value):
    """Return true_value if condition is true, otherwise false_value."""
    return true_value if condition else false_value


def coalesce(values: list):
    """Return the first non-None value from a list."""
    for value in values:
        if value is not None:
            return value
    return None


def coalesce_empty(values: list):
    """Return the first non-empty value from a list."""
    for value in values:
        if value is not None and value != "" and value != [] and value != {}:
            return value
    return None


def default_if_none(value, default):
    """Return value if not None, otherwise return default."""
    return value if value is not None else default


def default_if_empty(value, default):
    """Return value if not empty, otherwise return default."""
    if value is None or value == "" or value == [] or value == {}:
        return default
    return value


def safe_divide(numerator: float, denominator: float, default: float) -> float:
    """Divide numerator by denominator, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def sign_of(value: float) -> int:
    """Return the sign of a number: -1, 0, or 1."""
    if value < 0:
        return -1
    if value > 0:
        return 1
    return 0


def is_same_sign(a: float, b: float) -> bool:
    """Check if two numbers have the same sign."""
    return (a >= 0) == (b >= 0)


def is_opposite_sign(a: float, b: float) -> bool:
    """Check if two numbers have opposite signs."""
    return (a > 0 and b < 0) or (a < 0 and b > 0)
