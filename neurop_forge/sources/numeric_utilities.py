"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Numeric Utilities - Pure functions for numeric operations.
All functions are pure, deterministic, and atomic.
"""

import math


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to range."""
    return max(min_val, min(max_val, value))


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation."""
    return start + (end - start) * t


def inverse_lerp(start: float, end: float, value: float) -> float:
    """Inverse linear interpolation."""
    if start == end:
        return 0
    return (value - start) / (end - start)


def remap(value: float, from_min: float, from_max: float, to_min: float, to_max: float) -> float:
    """Remap value from one range to another."""
    t = inverse_lerp(from_min, from_max, value)
    return lerp(to_min, to_max, t)


def sign(value: float) -> int:
    """Get sign of value (-1, 0, or 1)."""
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def is_between(value: float, min_val: float, max_val: float, inclusive: bool) -> bool:
    """Check if value is in range."""
    if inclusive:
        return min_val <= value <= max_val
    return min_val < value < max_val


def is_approximately_equal(a: float, b: float, epsilon: float) -> bool:
    """Check if values are approximately equal."""
    return abs(a - b) < epsilon


def round_to_decimals(value: float, decimals: int) -> float:
    """Round to specific decimal places."""
    return round(value, decimals)


def round_to_nearest(value: float, nearest: float) -> float:
    """Round to nearest multiple."""
    return round(value / nearest) * nearest


def floor_to_nearest(value: float, nearest: float) -> float:
    """Floor to nearest multiple."""
    return math.floor(value / nearest) * nearest


def ceil_to_nearest(value: float, nearest: float) -> float:
    """Ceiling to nearest multiple."""
    return math.ceil(value / nearest) * nearest


def truncate(value: float, decimals: int) -> float:
    """Truncate to decimal places."""
    factor = 10 ** decimals
    return int(value * factor) / factor


def wrap(value: float, min_val: float, max_val: float) -> float:
    """Wrap value to range."""
    range_size = max_val - min_val
    return min_val + (value - min_val) % range_size


def step(value: float, threshold: float) -> int:
    """Step function (0 or 1)."""
    return 1 if value >= threshold else 0


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Smooth step interpolation."""
    t = clamp((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * (3 - 2 * t)


def smootherstep(edge0: float, edge1: float, x: float) -> float:
    """Smoother step interpolation."""
    t = clamp((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * t * (t * (t * 6 - 15) + 10)


def factorial(n: int) -> int:
    """Calculate factorial."""
    if n < 0:
        return 0
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def fibonacci(n: int) -> int:
    """Get nth Fibonacci number."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def gcd(a: int, b: int) -> int:
    """Greatest common divisor."""
    while b:
        a, b = b, a % b
    return abs(a)


def lcm(a: int, b: int) -> int:
    """Least common multiple."""
    return abs(a * b) // gcd(a, b)


def is_prime(n: int) -> bool:
    """Check if number is prime."""
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


def prime_factors(n: int) -> list:
    """Get prime factors."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def is_perfect_square(n: int) -> bool:
    """Check if perfect square."""
    if n < 0:
        return False
    root = int(math.sqrt(n))
    return root * root == n


def is_power_of_two(n: int) -> bool:
    """Check if power of two."""
    return n > 0 and (n & (n - 1)) == 0


def next_power_of_two(n: int) -> int:
    """Get next power of two."""
    if n <= 0:
        return 1
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    return n + 1


def digital_root(n: int) -> int:
    """Calculate digital root."""
    if n == 0:
        return 0
    return 1 + (n - 1) % 9


def sum_digits(n: int) -> int:
    """Sum of digits."""
    n = abs(n)
    total = 0
    while n:
        total += n % 10
        n //= 10
    return total


def count_digits(n: int) -> int:
    """Count number of digits."""
    if n == 0:
        return 1
    return len(str(abs(n)))


def is_palindrome_number(n: int) -> bool:
    """Check if number is palindrome."""
    if n < 0:
        return False
    s = str(n)
    return s == s[::-1]


def reverse_number(n: int) -> int:
    """Reverse digits of number."""
    negative = n < 0
    n = abs(n)
    result = int(str(n)[::-1])
    return -result if negative else result
