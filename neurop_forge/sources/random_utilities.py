"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Random Utilities - Pure functions for deterministic random operations.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def hash_seed(seed: int, salt: str) -> int:
    """Generate hash-based seed."""
    h = hashlib.sha256(f"{seed}{salt}".encode()).digest()
    return int.from_bytes(h[:8], 'big')


def random_float(seed: int) -> float:
    """Generate deterministic float [0, 1)."""
    h = hashlib.sha256(str(seed).encode()).digest()
    return int.from_bytes(h[:8], 'big') / (2**64)


def random_int(seed: int, min_val: int, max_val: int) -> int:
    """Generate deterministic integer in range."""
    f = random_float(seed)
    return min_val + int(f * (max_val - min_val + 1))


def random_bool(seed: int, probability: float) -> bool:
    """Generate deterministic boolean with probability."""
    return random_float(seed) < probability


def random_choice(seed: int, items: list):
    """Choose deterministic random item from list."""
    if not items:
        return None
    idx = random_int(seed, 0, len(items) - 1)
    return items[idx]


def random_sample(seed: int, items: list, count: int) -> list:
    """Sample deterministic random items without replacement."""
    if count >= len(items):
        return list(items)
    result = []
    available = list(items)
    for i in range(count):
        idx = random_int(hash_seed(seed, f"sample_{i}"), 0, len(available) - 1)
        result.append(available[idx])
        available.pop(idx)
    return result


def shuffle(seed: int, items: list) -> list:
    """Deterministic shuffle."""
    result = list(items)
    for i in range(len(result) - 1, 0, -1):
        j = random_int(hash_seed(seed, f"shuffle_{i}"), 0, i)
        result[i], result[j] = result[j], result[i]
    return result


def random_string(seed: int, length: int, charset: str) -> str:
    """Generate deterministic random string."""
    result = []
    for i in range(length):
        idx = random_int(hash_seed(seed, f"char_{i}"), 0, len(charset) - 1)
        result.append(charset[idx])
    return ''.join(result)


def random_alphanumeric(seed: int, length: int) -> str:
    """Generate deterministic alphanumeric string."""
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return random_string(seed, length, charset)


def random_hex(seed: int, length: int) -> str:
    """Generate deterministic hex string."""
    return random_string(seed, length, "0123456789abcdef")


def random_uuid(seed: int) -> str:
    """Generate deterministic UUID v4 format."""
    hex_chars = random_hex(seed, 32)
    return f"{hex_chars[:8]}-{hex_chars[8:12]}-4{hex_chars[13:16]}-{hex_chars[16:20]}-{hex_chars[20:32]}"


def weighted_choice(seed: int, items: list, weights: list):
    """Choose item based on weights."""
    total = sum(weights)
    threshold = random_float(seed) * total
    cumulative = 0
    for item, weight in zip(items, weights):
        cumulative += weight
        if cumulative >= threshold:
            return item
    return items[-1]


def random_gaussian(seed: int, mean: float, std: float) -> float:
    """Generate deterministic Gaussian random number (Box-Muller)."""
    import math
    u1 = random_float(seed)
    u2 = random_float(hash_seed(seed, "gaussian"))
    z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return mean + std * z0


def random_exponential(seed: int, rate: float) -> float:
    """Generate deterministic exponential random number."""
    import math
    u = random_float(seed)
    return -math.log(1 - u) / rate


def random_poisson(seed: int, lam: float) -> int:
    """Generate deterministic Poisson random number."""
    import math
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random_float(hash_seed(seed, f"poisson_{k}"))
    return k - 1


def random_binomial(seed: int, n: int, p: float) -> int:
    """Generate deterministic binomial random number."""
    count = 0
    for i in range(n):
        if random_bool(hash_seed(seed, f"binom_{i}"), p):
            count += 1
    return count


def random_date(seed: int, start_year: int, end_year: int) -> dict:
    """Generate deterministic random date."""
    year = random_int(seed, start_year, end_year)
    month = random_int(hash_seed(seed, "month"), 1, 12)
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    max_day = days_in_month[month - 1]
    if month == 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        max_day = 29
    day = random_int(hash_seed(seed, "day"), 1, max_day)
    return {"year": year, "month": month, "day": day}


def random_color_hex(seed: int) -> str:
    """Generate deterministic random hex color."""
    return "#" + random_hex(seed, 6)


def random_ip(seed: int) -> str:
    """Generate deterministic random IPv4 address."""
    parts = [random_int(hash_seed(seed, f"ip_{i}"), 0, 255) for i in range(4)]
    return '.'.join(str(p) for p in parts)


def random_email(seed: int, domain: str) -> str:
    """Generate deterministic random email."""
    username = random_alphanumeric(seed, 10).lower()
    return f"{username}@{domain}"


def random_phone(seed: int) -> str:
    """Generate deterministic random phone number."""
    area = random_int(seed, 200, 999)
    exchange = random_int(hash_seed(seed, "ex"), 200, 999)
    line = random_int(hash_seed(seed, "line"), 1000, 9999)
    return f"{area}-{exchange}-{line}"
