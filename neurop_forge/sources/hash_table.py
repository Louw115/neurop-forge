"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Hash Table - Pure functions for hash table/map operations.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def _hash_key(key: str, size: int) -> int:
    """Hash a key to bucket index."""
    h = hashlib.sha256(str(key).encode()).digest()
    return int.from_bytes(h[:4], 'big') % size


def create_hash_table(size: int) -> dict:
    """Create a hash table."""
    return {
        "buckets": [[] for _ in range(size)],
        "size": size,
        "count": 0
    }


def hash_table_put(ht: dict, key: str, value) -> dict:
    """Put a key-value pair."""
    idx = _hash_key(key, ht["size"])
    buckets = [list(b) for b in ht["buckets"]]
    for i, (k, v) in enumerate(buckets[idx]):
        if k == key:
            buckets[idx][i] = (key, value)
            return {"buckets": buckets, "size": ht["size"], "count": ht["count"]}
    buckets[idx].append((key, value))
    return {"buckets": buckets, "size": ht["size"], "count": ht["count"] + 1}


def hash_table_get(ht: dict, key: str):
    """Get value by key."""
    idx = _hash_key(key, ht["size"])
    for k, v in ht["buckets"][idx]:
        if k == key:
            return v
    return None


def hash_table_contains(ht: dict, key: str) -> bool:
    """Check if key exists."""
    idx = _hash_key(key, ht["size"])
    return any(k == key for k, v in ht["buckets"][idx])


def hash_table_remove(ht: dict, key: str) -> dict:
    """Remove a key."""
    idx = _hash_key(key, ht["size"])
    buckets = [list(b) for b in ht["buckets"]]
    original_len = len(buckets[idx])
    buckets[idx] = [(k, v) for k, v in buckets[idx] if k != key]
    new_count = ht["count"] - (original_len - len(buckets[idx]))
    return {"buckets": buckets, "size": ht["size"], "count": new_count}


def hash_table_keys(ht: dict) -> list:
    """Get all keys."""
    keys = []
    for bucket in ht["buckets"]:
        for k, v in bucket:
            keys.append(k)
    return keys


def hash_table_values(ht: dict) -> list:
    """Get all values."""
    values = []
    for bucket in ht["buckets"]:
        for k, v in bucket:
            values.append(v)
    return values


def hash_table_items(ht: dict) -> list:
    """Get all key-value pairs."""
    items = []
    for bucket in ht["buckets"]:
        for k, v in bucket:
            items.append((k, v))
    return items


def hash_table_count(ht: dict) -> int:
    """Get number of entries."""
    return ht["count"]


def hash_table_is_empty(ht: dict) -> bool:
    """Check if empty."""
    return ht["count"] == 0


def hash_table_load_factor(ht: dict) -> float:
    """Calculate load factor."""
    return ht["count"] / ht["size"] if ht["size"] > 0 else 0


def hash_table_get_or_default(ht: dict, key: str, default):
    """Get value or default if not found."""
    value = hash_table_get(ht, key)
    return value if value is not None else default


def hash_table_update(ht: dict, updates: dict) -> dict:
    """Update multiple key-value pairs."""
    result = ht
    for k, v in updates.items():
        result = hash_table_put(result, k, v)
    return result


def hash_table_merge(ht1: dict, ht2: dict) -> dict:
    """Merge two hash tables."""
    result = ht1
    for k, v in hash_table_items(ht2):
        result = hash_table_put(result, k, v)
    return result


def hash_table_from_dict(d: dict, size: int) -> dict:
    """Create hash table from dictionary."""
    ht = create_hash_table(size)
    for k, v in d.items():
        ht = hash_table_put(ht, str(k), v)
    return ht


def hash_table_to_dict(ht: dict) -> dict:
    """Convert hash table to dictionary."""
    return dict(hash_table_items(ht))


def hash_table_map_values(ht: dict, transform) -> dict:
    """Apply transformation to all values."""
    result = create_hash_table(ht["size"])
    for k, v in hash_table_items(ht):
        result = hash_table_put(result, k, transform(v))
    return result


def hash_table_filter(ht: dict, predicate) -> dict:
    """Filter entries by predicate."""
    result = create_hash_table(ht["size"])
    for k, v in hash_table_items(ht):
        if predicate(k, v):
            result = hash_table_put(result, k, v)
    return result


def hash_table_bucket_sizes(ht: dict) -> list:
    """Get size of each bucket."""
    return [len(b) for b in ht["buckets"]]


def hash_table_max_bucket_size(ht: dict) -> int:
    """Get maximum bucket size (collision indicator)."""
    return max(len(b) for b in ht["buckets"])


def hash_table_collision_count(ht: dict) -> int:
    """Count entries that have collisions."""
    return sum(max(0, len(b) - 1) for b in ht["buckets"])


def hash_table_should_resize(ht: dict, threshold: float) -> bool:
    """Check if hash table should be resized."""
    return hash_table_load_factor(ht) > threshold


def hash_table_resize(ht: dict, new_size: int) -> dict:
    """Resize hash table."""
    new_ht = create_hash_table(new_size)
    for k, v in hash_table_items(ht):
        new_ht = hash_table_put(new_ht, k, v)
    return new_ht


def hash_table_increment(ht: dict, key: str, amount: int) -> dict:
    """Increment a numeric value."""
    current = hash_table_get_or_default(ht, key, 0)
    return hash_table_put(ht, key, current + amount)


def hash_table_append_to_list(ht: dict, key: str, value) -> dict:
    """Append value to list stored at key."""
    current = hash_table_get_or_default(ht, key, [])
    return hash_table_put(ht, key, list(current) + [value])


def hash_table_set_nested(ht: dict, keys: list, value) -> dict:
    """Set a nested value."""
    if not keys:
        return ht
    if len(keys) == 1:
        return hash_table_put(ht, keys[0], value)
    current = hash_table_get_or_default(ht, keys[0], {})
    if isinstance(current, dict):
        nested_ht = hash_table_from_dict(current, 16)
    else:
        nested_ht = create_hash_table(16)
    nested_ht = hash_table_set_nested(nested_ht, keys[1:], value)
    return hash_table_put(ht, keys[0], hash_table_to_dict(nested_ht))


def compute_if_absent(ht: dict, key: str, compute_fn) -> dict:
    """Compute and store value if key is absent."""
    if hash_table_contains(ht, key):
        return ht
    return hash_table_put(ht, key, compute_fn(key))
