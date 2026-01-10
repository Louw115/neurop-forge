"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Bloom Filter - Pure functions for probabilistic set membership.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def create_bloom_filter(size: int, num_hashes: int) -> dict:
    """Create a bloom filter."""
    return {
        "bits": [0] * size,
        "size": size,
        "num_hashes": num_hashes,
        "count": 0
    }


def _hash_item(item: str, seed: int, size: int) -> int:
    """Generate hash for item with seed."""
    h = hashlib.sha256(f"{seed}:{item}".encode()).digest()
    return int.from_bytes(h[:4], 'big') % size


def bloom_add(bloom: dict, item: str) -> dict:
    """Add item to bloom filter."""
    bits = list(bloom["bits"])
    for i in range(bloom["num_hashes"]):
        idx = _hash_item(item, i, bloom["size"])
        bits[idx] = 1
    return {
        "bits": bits,
        "size": bloom["size"],
        "num_hashes": bloom["num_hashes"],
        "count": bloom["count"] + 1
    }


def bloom_might_contain(bloom: dict, item: str) -> bool:
    """Check if item might be in bloom filter (may have false positives)."""
    for i in range(bloom["num_hashes"]):
        idx = _hash_item(item, i, bloom["size"])
        if bloom["bits"][idx] == 0:
            return False
    return True


def bloom_definitely_not_contains(bloom: dict, item: str) -> bool:
    """Check if item is definitely not in bloom filter."""
    return not bloom_might_contain(bloom, item)


def calculate_optimal_size(expected_items: int, false_positive_rate: float) -> int:
    """Calculate optimal bloom filter size."""
    import math
    if expected_items <= 0 or false_positive_rate <= 0:
        return 1
    m = -expected_items * math.log(false_positive_rate) / (math.log(2) ** 2)
    return max(1, int(m))


def calculate_optimal_hashes(filter_size: int, expected_items: int) -> int:
    """Calculate optimal number of hash functions."""
    import math
    if expected_items <= 0:
        return 1
    k = (filter_size / expected_items) * math.log(2)
    return max(1, int(k))


def estimate_false_positive_rate(filter_size: int, num_hashes: int, items_added: int) -> float:
    """Estimate current false positive rate."""
    import math
    if filter_size <= 0:
        return 1.0
    prob = (1 - math.exp(-num_hashes * items_added / filter_size)) ** num_hashes
    return prob


def bloom_fill_ratio(bloom: dict) -> float:
    """Calculate what fraction of bits are set."""
    return sum(bloom["bits"]) / bloom["size"] if bloom["size"] > 0 else 0


def bloom_union(bloom1: dict, bloom2: dict) -> dict:
    """Union of two bloom filters (same size and hash count)."""
    if bloom1["size"] != bloom2["size"] or bloom1["num_hashes"] != bloom2["num_hashes"]:
        return bloom1
    bits = [b1 | b2 for b1, b2 in zip(bloom1["bits"], bloom2["bits"])]
    return {
        "bits": bits,
        "size": bloom1["size"],
        "num_hashes": bloom1["num_hashes"],
        "count": bloom1["count"] + bloom2["count"]
    }


def bloom_intersection(bloom1: dict, bloom2: dict) -> dict:
    """Intersection of two bloom filters (same size and hash count)."""
    if bloom1["size"] != bloom2["size"] or bloom1["num_hashes"] != bloom2["num_hashes"]:
        return bloom1
    bits = [b1 & b2 for b1, b2 in zip(bloom1["bits"], bloom2["bits"])]
    return {
        "bits": bits,
        "size": bloom1["size"],
        "num_hashes": bloom1["num_hashes"],
        "count": 0
    }


def create_counting_bloom_filter(size: int, num_hashes: int) -> dict:
    """Create a counting bloom filter."""
    return {
        "counters": [0] * size,
        "size": size,
        "num_hashes": num_hashes,
        "count": 0
    }


def counting_bloom_add(bloom: dict, item: str) -> dict:
    """Add item to counting bloom filter."""
    counters = list(bloom["counters"])
    for i in range(bloom["num_hashes"]):
        idx = _hash_item(item, i, bloom["size"])
        counters[idx] += 1
    return {
        "counters": counters,
        "size": bloom["size"],
        "num_hashes": bloom["num_hashes"],
        "count": bloom["count"] + 1
    }


def counting_bloom_remove(bloom: dict, item: str) -> dict:
    """Remove item from counting bloom filter."""
    counters = list(bloom["counters"])
    for i in range(bloom["num_hashes"]):
        idx = _hash_item(item, i, bloom["size"])
        if counters[idx] > 0:
            counters[idx] -= 1
    return {
        "counters": counters,
        "size": bloom["size"],
        "num_hashes": bloom["num_hashes"],
        "count": max(0, bloom["count"] - 1)
    }


def counting_bloom_might_contain(bloom: dict, item: str) -> bool:
    """Check if item might be in counting bloom filter."""
    for i in range(bloom["num_hashes"]):
        idx = _hash_item(item, i, bloom["size"])
        if bloom["counters"][idx] == 0:
            return False
    return True


def create_scalable_bloom_filter(initial_size: int, false_positive_rate: float) -> dict:
    """Create a scalable bloom filter that grows as needed."""
    num_hashes = calculate_optimal_hashes(initial_size, initial_size)
    return {
        "filters": [create_bloom_filter(initial_size, num_hashes)],
        "growth_factor": 2,
        "false_positive_rate": false_positive_rate,
        "total_count": 0
    }


def scalable_bloom_add(bloom: dict, item: str) -> dict:
    """Add item to scalable bloom filter."""
    current_filter = bloom["filters"][-1]
    if bloom_fill_ratio(current_filter) > 0.5:
        new_size = current_filter["size"] * bloom["growth_factor"]
        num_hashes = calculate_optimal_hashes(new_size, new_size)
        new_filter = create_bloom_filter(new_size, num_hashes)
        new_filter = bloom_add(new_filter, item)
        return {
            "filters": bloom["filters"] + [new_filter],
            "growth_factor": bloom["growth_factor"],
            "false_positive_rate": bloom["false_positive_rate"],
            "total_count": bloom["total_count"] + 1
        }
    updated_filter = bloom_add(current_filter, item)
    return {
        "filters": bloom["filters"][:-1] + [updated_filter],
        "growth_factor": bloom["growth_factor"],
        "false_positive_rate": bloom["false_positive_rate"],
        "total_count": bloom["total_count"] + 1
    }


def scalable_bloom_might_contain(bloom: dict, item: str) -> bool:
    """Check if item might be in scalable bloom filter."""
    return any(bloom_might_contain(f, item) for f in bloom["filters"])


def bloom_to_bytes(bloom: dict) -> bytes:
    """Serialize bloom filter to bytes."""
    byte_count = (bloom["size"] + 7) // 8
    result = bytearray(byte_count)
    for i, bit in enumerate(bloom["bits"]):
        if bit:
            result[i // 8] |= (1 << (i % 8))
    return bytes(result)


def bloom_from_bytes(data: bytes, size: int, num_hashes: int) -> dict:
    """Deserialize bloom filter from bytes."""
    bits = [0] * size
    for i in range(min(size, len(data) * 8)):
        if data[i // 8] & (1 << (i % 8)):
            bits[i] = 1
    return {
        "bits": bits,
        "size": size,
        "num_hashes": num_hashes,
        "count": 0
    }
