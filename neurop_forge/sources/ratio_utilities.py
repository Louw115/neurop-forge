"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Ratio Utilities - Pure functions for ratio calculations.
All functions are pure, deterministic, and atomic.
"""

import math


def create_ratio(numerator: int, denominator: int) -> tuple:
    """Create simplified ratio tuple."""
    if denominator == 0:
        return (0, 0)
    gcd = math.gcd(numerator, denominator)
    return (numerator // gcd, denominator // gcd)


def ratio_to_decimal(numerator: int, denominator: int) -> float:
    """Convert ratio to decimal."""
    if denominator == 0:
        return 0
    return numerator / denominator


def decimal_to_ratio(decimal: float, max_denominator: int) -> tuple:
    """Convert decimal to closest ratio."""
    best = (0, 1)
    best_error = abs(decimal)
    for d in range(1, max_denominator + 1):
        n = round(decimal * d)
        error = abs(decimal - n / d)
        if error < best_error:
            best_error = error
            best = (n, d)
    return create_ratio(best[0], best[1])


def ratio_to_percent(numerator: int, denominator: int) -> float:
    """Convert ratio to percentage."""
    return ratio_to_decimal(numerator, denominator) * 100


def percent_to_ratio(percent: float) -> tuple:
    """Convert percentage to ratio."""
    return create_ratio(int(percent), 100)


def add_ratios(r1: tuple, r2: tuple) -> tuple:
    """Add two ratios."""
    n1, d1 = r1
    n2, d2 = r2
    if d1 == 0 or d2 == 0:
        return (0, 0)
    return create_ratio(n1 * d2 + n2 * d1, d1 * d2)


def subtract_ratios(r1: tuple, r2: tuple) -> tuple:
    """Subtract two ratios."""
    n1, d1 = r1
    n2, d2 = r2
    if d1 == 0 or d2 == 0:
        return (0, 0)
    return create_ratio(n1 * d2 - n2 * d1, d1 * d2)


def multiply_ratios(r1: tuple, r2: tuple) -> tuple:
    """Multiply two ratios."""
    n1, d1 = r1
    n2, d2 = r2
    return create_ratio(n1 * n2, d1 * d2)


def divide_ratios(r1: tuple, r2: tuple) -> tuple:
    """Divide two ratios."""
    n1, d1 = r1
    n2, d2 = r2
    if n2 == 0:
        return (0, 0)
    return create_ratio(n1 * d2, d1 * n2)


def compare_ratios(r1: tuple, r2: tuple) -> int:
    """Compare ratios (-1, 0, 1)."""
    d1 = ratio_to_decimal(r1[0], r1[1])
    d2 = ratio_to_decimal(r2[0], r2[1])
    if d1 < d2:
        return -1
    if d1 > d2:
        return 1
    return 0


def format_ratio(ratio: tuple, separator: str) -> str:
    """Format ratio as string."""
    return f"{ratio[0]}{separator}{ratio[1]}"


def parse_ratio(ratio_str: str) -> tuple:
    """Parse ratio from string."""
    for sep in [":", "/", "-"]:
        if sep in ratio_str:
            parts = ratio_str.split(sep)
            if len(parts) == 2:
                try:
                    return create_ratio(int(parts[0]), int(parts[1]))
                except ValueError:
                    pass
    return (0, 0)


def is_valid_ratio(ratio: tuple) -> bool:
    """Check if ratio is valid."""
    return len(ratio) == 2 and ratio[1] != 0


def invert_ratio(ratio: tuple) -> tuple:
    """Invert ratio (swap numerator/denominator)."""
    if ratio[0] == 0:
        return (0, 0)
    return create_ratio(ratio[1], ratio[0])


def scale_ratio(ratio: tuple, factor: int) -> tuple:
    """Scale ratio by factor."""
    return (ratio[0] * factor, ratio[1] * factor)


def get_aspect_ratio(width: int, height: int) -> tuple:
    """Get aspect ratio from dimensions."""
    return create_ratio(width, height)


def format_aspect_ratio(width: int, height: int) -> str:
    """Format aspect ratio (e.g., 16:9)."""
    ratio = get_aspect_ratio(width, height)
    return f"{ratio[0]}:{ratio[1]}"


def calculate_dimension(known: int, ratio: tuple, is_width: bool) -> int:
    """Calculate dimension from ratio."""
    if is_width:
        return int(known * ratio[0] / ratio[1]) if ratio[1] != 0 else 0
    return int(known * ratio[1] / ratio[0]) if ratio[0] != 0 else 0


def is_golden_ratio(ratio: tuple, tolerance: float) -> bool:
    """Check if ratio is close to golden ratio."""
    golden = 1.618033988749895
    value = ratio_to_decimal(ratio[0], ratio[1])
    return abs(value - golden) <= tolerance


def blend_ratios(r1: tuple, r2: tuple, weight: float) -> tuple:
    """Blend two ratios by weight."""
    d1 = ratio_to_decimal(r1[0], r1[1])
    d2 = ratio_to_decimal(r2[0], r2[1])
    blended = d1 * (1 - weight) + d2 * weight
    return decimal_to_ratio(blended, 100)
