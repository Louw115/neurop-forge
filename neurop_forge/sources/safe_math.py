"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Safe Math - Pure functions for safe mathematical operations.
All functions are pure, deterministic, and atomic.
"""

import math


def safe_divide(a: float, b: float, default: float) -> float:
    """Safely divide with default on zero."""
    if b == 0:
        return default
    return a / b


def safe_int_divide(a: int, b: int, default: int) -> int:
    """Safely integer divide with default on zero."""
    if b == 0:
        return default
    return a // b


def safe_modulo(a: int, b: int, default: int) -> int:
    """Safely compute modulo with default on zero."""
    if b == 0:
        return default
    return a % b


def safe_sqrt(x: float, default: float) -> float:
    """Safely compute square root with default on negative."""
    if x < 0:
        return default
    return math.sqrt(x)


def safe_log(x: float, base: float, default: float) -> float:
    """Safely compute logarithm with default on invalid input."""
    if x <= 0 or base <= 0 or base == 1:
        return default
    return math.log(x, base)


def safe_log10(x: float, default: float) -> float:
    """Safely compute log base 10."""
    if x <= 0:
        return default
    return math.log10(x)


def safe_log2(x: float, default: float) -> float:
    """Safely compute log base 2."""
    if x <= 0:
        return default
    return math.log2(x)


def safe_power(base: float, exp: float, default: float) -> float:
    """Safely compute power with default on invalid."""
    try:
        result = math.pow(base, exp)
        if math.isnan(result) or math.isinf(result):
            return default
        return result
    except (ValueError, OverflowError):
        return default


def safe_asin(x: float, default: float) -> float:
    """Safely compute arc sine."""
    if x < -1 or x > 1:
        return default
    return math.asin(x)


def safe_acos(x: float, default: float) -> float:
    """Safely compute arc cosine."""
    if x < -1 or x > 1:
        return default
    return math.acos(x)


def checked_add(a: int, b: int, max_val: int) -> dict:
    """Add with overflow check."""
    result = a + b
    if result > max_val:
        return {"success": False, "value": max_val, "overflow": True}
    return {"success": True, "value": result, "overflow": False}


def checked_multiply(a: int, b: int, max_val: int) -> dict:
    """Multiply with overflow check."""
    result = a * b
    if result > max_val:
        return {"success": False, "value": max_val, "overflow": True}
    return {"success": True, "value": result, "overflow": False}


def checked_subtract(a: int, b: int, min_val: int) -> dict:
    """Subtract with underflow check."""
    result = a - b
    if result < min_val:
        return {"success": False, "value": min_val, "underflow": True}
    return {"success": True, "value": result, "underflow": False}


def saturating_add(a: int, b: int, max_val: int) -> int:
    """Add with saturation at max."""
    result = a + b
    return min(result, max_val)


def saturating_subtract(a: int, b: int, min_val: int) -> int:
    """Subtract with saturation at min."""
    result = a - b
    return max(result, min_val)


def saturating_multiply(a: int, b: int, max_val: int) -> int:
    """Multiply with saturation at max."""
    result = a * b
    return min(result, max_val)


def is_finite(x: float) -> bool:
    """Check if value is finite."""
    return math.isfinite(x)


def is_nan(x: float) -> bool:
    """Check if value is NaN."""
    return math.isnan(x)


def is_inf(x: float) -> bool:
    """Check if value is infinity."""
    return math.isinf(x)


def clamp_to_finite(x: float, default: float) -> float:
    """Clamp to finite value."""
    if math.isnan(x) or math.isinf(x):
        return default
    return x


def safe_reciprocal(x: float, default: float) -> float:
    """Safely compute reciprocal."""
    if x == 0:
        return default
    return 1 / x


def safe_percentage(part: float, whole: float, default: float) -> float:
    """Safely compute percentage."""
    if whole == 0:
        return default
    return (part / whole) * 100


def safe_average(values: list, default: float) -> float:
    """Safely compute average."""
    if not values:
        return default
    return sum(values) / len(values)


def safe_weighted_average(values: list, weights: list, default: float) -> float:
    """Safely compute weighted average."""
    if not values or not weights or len(values) != len(weights):
        return default
    total_weight = sum(weights)
    if total_weight == 0:
        return default
    return sum(v * w for v, w in zip(values, weights)) / total_weight


def safe_geometric_mean(values: list, default: float) -> float:
    """Safely compute geometric mean."""
    if not values:
        return default
    if any(v <= 0 for v in values):
        return default
    product = 1
    for v in values:
        product *= v
    return product ** (1 / len(values))


def safe_harmonic_mean(values: list, default: float) -> float:
    """Safely compute harmonic mean."""
    if not values:
        return default
    if any(v == 0 for v in values):
        return default
    return len(values) / sum(1/v for v in values)


def bound_check(value: float, min_val: float, max_val: float) -> dict:
    """Check if value is within bounds."""
    return {
        "in_bounds": min_val <= value <= max_val,
        "value": value,
        "min": min_val,
        "max": max_val,
        "below": value < min_val,
        "above": value > max_val
    }


def normalize_to_range(value: float, min_val: float, max_val: float) -> float:
    """Normalize value to [0, 1] range."""
    if max_val == min_val:
        return 0
    return (value - min_val) / (max_val - min_val)


def denormalize_from_range(normalized: float, min_val: float, max_val: float) -> float:
    """Denormalize from [0, 1] to original range."""
    return min_val + normalized * (max_val - min_val)
