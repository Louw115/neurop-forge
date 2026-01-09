"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Math and Statistics Functions - Pure functions for mathematical operations.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import math


def square_root(value: float) -> float:
    """Calculate the square root of a non-negative number."""
    if value < 0:
        return 0.0
    return math.sqrt(value)


def cube_root(value: float) -> float:
    """Calculate the cube root of a number."""
    if value < 0:
        return -(abs(value) ** (1/3))
    return value ** (1/3)


def power_of(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    return base ** exponent


def natural_log(value: float) -> float:
    """Calculate the natural logarithm of a positive number."""
    if value <= 0:
        return 0.0
    return math.log(value)


def log_base_10(value: float) -> float:
    """Calculate the base-10 logarithm of a positive number."""
    if value <= 0:
        return 0.0
    return math.log10(value)


def log_base_2(value: float) -> float:
    """Calculate the base-2 logarithm of a positive number."""
    if value <= 0:
        return 0.0
    return math.log2(value)


def exponential(value: float) -> float:
    """Calculate e raised to the power of value."""
    return math.exp(value)


def floor_division(a: float, b: float) -> int:
    """Perform floor division of a by b."""
    if b == 0:
        return 0
    return int(a // b)


def modulo(a: float, b: float) -> float:
    """Calculate the remainder of a divided by b."""
    if b == 0:
        return 0.0
    return a % b


def absolute_value(value: float) -> float:
    """Return the absolute value of a number."""
    return abs(value)


def sign(value: float) -> int:
    """Return the sign of a number: -1, 0, or 1."""
    if value < 0:
        return -1
    if value > 0:
        return 1
    return 0


def floor(value: float) -> int:
    """Round a number down to the nearest integer."""
    return math.floor(value)


def ceiling(value: float) -> int:
    """Round a number up to the nearest integer."""
    return math.ceil(value)


def round_half_up(value: float, decimals: int) -> float:
    """Round a number to specified decimal places using half-up rounding."""
    multiplier = 10 ** decimals
    return math.floor(value * multiplier + 0.5) / multiplier


def truncate(value: float) -> int:
    """Truncate a number to its integer part."""
    return int(value)


def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer."""
    if n < 0:
        return 0
    if n <= 1:
        return 1
    return math.factorial(n)


def gcd(a: int, b: int) -> int:
    """Calculate the greatest common divisor of two integers."""
    return math.gcd(abs(a), abs(b))


def lcm(a: int, b: int) -> int:
    """Calculate the least common multiple of two integers."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def is_prime(n: int) -> bool:
    """Check if a number is a prime number."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n < 0:
        return 0
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def mean(values: list) -> float:
    """Calculate the arithmetic mean of a list of numbers."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def median(values: list) -> float:
    """Calculate the median of a list of numbers."""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    n = len(sorted_values)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_values[mid - 1] + sorted_values[mid]) / 2
    return sorted_values[mid]


def mode(values: list):
    """Find the most common value in a list."""
    if not values:
        return None
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    max_count = max(counts.values())
    for v in values:
        if counts[v] == max_count:
            return v
    return None


def variance(values: list) -> float:
    """Calculate the population variance of a list of numbers."""
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return sum((x - avg) ** 2 for x in values) / len(values)


def standard_deviation(values: list) -> float:
    """Calculate the population standard deviation of a list of numbers."""
    return math.sqrt(variance(values))


def range_of_values(values: list) -> float:
    """Calculate the range (max - min) of a list of numbers."""
    if not values:
        return 0.0
    return max(values) - min(values)


def percentile(values: list, p: float) -> float:
    """Calculate the pth percentile of a list of numbers."""
    if not values or p < 0 or p > 100:
        return 0.0
    sorted_values = sorted(values)
    k = (len(sorted_values) - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    return sorted_values[int(f)] * (c - k) + sorted_values[int(c)] * (k - f)


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value to be within a specified range."""
    return max(minimum, min(maximum, value))


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values."""
    return start + (end - start) * t


def map_range(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """Map a value from one range to another."""
    if in_max == in_min:
        return out_min
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def normalize(value: float, minimum: float, maximum: float) -> float:
    """Normalize a value to a 0-1 range based on min and max."""
    if maximum == minimum:
        return 0.0
    return (value - minimum) / (maximum - minimum)


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180 / math.pi


def sine(radians: float) -> float:
    """Calculate the sine of an angle in radians."""
    return math.sin(radians)


def cosine(radians: float) -> float:
    """Calculate the cosine of an angle in radians."""
    return math.cos(radians)


def tangent(radians: float) -> float:
    """Calculate the tangent of an angle in radians."""
    return math.tan(radians)


def hypotenuse(a: float, b: float) -> float:
    """Calculate the hypotenuse of a right triangle."""
    return math.hypot(a, b)


def distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate the Euclidean distance between two 2D points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_3d(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    """Calculate the Euclidean distance between two 3D points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
