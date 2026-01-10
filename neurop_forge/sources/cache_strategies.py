"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Cache Strategies - Pure functions for caching strategies.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def create_cache_key(prefix: str, *args) -> str:
    """Create cache key from prefix and arguments."""
    parts = [prefix] + [str(a) for a in args]
    return ":".join(parts)


def hash_cache_key(key: str) -> str:
    """Hash cache key for fixed length."""
    return hashlib.md5(key.encode()).hexdigest()


def create_ttl_entry(value, ttl_seconds: int, created_at: int) -> dict:
    """Create cache entry with TTL."""
    return {
        "value": value,
        "ttl": ttl_seconds,
        "created_at": created_at,
        "expires_at": created_at + ttl_seconds
    }


def is_expired(entry: dict, current_time: int) -> bool:
    """Check if cache entry is expired."""
    return current_time >= entry.get("expires_at", 0)


def calculate_remaining_ttl(entry: dict, current_time: int) -> int:
    """Calculate remaining TTL in seconds."""
    remaining = entry.get("expires_at", 0) - current_time
    return max(0, remaining)


def should_refresh_ahead(entry: dict, current_time: int, threshold: float) -> bool:
    """Check if entry should be refreshed ahead of expiration."""
    total_ttl = entry["ttl"]
    remaining = calculate_remaining_ttl(entry, current_time)
    return remaining < total_ttl * threshold


def get_cache_stats(hits: int, misses: int) -> dict:
    """Calculate cache statistics."""
    total = hits + misses
    return {
        "hits": hits,
        "misses": misses,
        "total": total,
        "hit_rate": hits / total if total > 0 else 0,
        "miss_rate": misses / total if total > 0 else 0
    }


def lru_access(order: list, key: str, max_size: int) -> dict:
    """Update LRU access order, return evicted key if any."""
    new_order = [k for k in order if k != key]
    new_order.append(key)
    evicted = None
    if len(new_order) > max_size:
        evicted = new_order.pop(0)
    return {"order": new_order, "evicted": evicted}


def lfu_access(frequencies: dict, key: str) -> dict:
    """Update LFU frequencies."""
    new_freq = dict(frequencies)
    new_freq[key] = new_freq.get(key, 0) + 1
    return new_freq


def lfu_evict_candidate(frequencies: dict) -> str:
    """Find LFU eviction candidate."""
    if not frequencies:
        return None
    return min(frequencies.keys(), key=lambda k: frequencies[k])


def fifo_evict(order: list) -> dict:
    """FIFO eviction - get first item."""
    if not order:
        return {"order": order, "evicted": None}
    return {"order": order[1:], "evicted": order[0]}


def random_evict(keys: list, seed: int) -> str:
    """Random eviction using deterministic seed."""
    if not keys:
        return None
    h = hashlib.sha256(str(seed).encode()).digest()
    idx = h[0] % len(keys)
    return keys[idx]


def ttl_evict_candidates(entries: dict, current_time: int) -> list:
    """Find all expired entries."""
    return [k for k, v in entries.items() if is_expired(v, current_time)]


def calculate_etag(content: bytes) -> str:
    """Calculate ETag from content."""
    return f'"{hashlib.md5(content).hexdigest()}"'


def is_weak_etag(etag: str) -> bool:
    """Check if ETag is weak."""
    return etag.startswith("W/")


def compare_etags(etag1: str, etag2: str, weak: bool) -> bool:
    """Compare ETags (weak or strong comparison)."""
    if weak:
        e1 = etag1.replace("W/", "").strip('"')
        e2 = etag2.replace("W/", "").strip('"')
        return e1 == e2
    return etag1 == etag2


def parse_cache_control(header: str) -> dict:
    """Parse Cache-Control header."""
    result = {}
    for directive in header.split(","):
        directive = directive.strip()
        if "=" in directive:
            key, value = directive.split("=", 1)
            result[key.strip()] = value.strip()
        else:
            result[directive] = True
    return result


def build_cache_control(directives: dict) -> str:
    """Build Cache-Control header value."""
    parts = []
    for key, value in directives.items():
        if value is True:
            parts.append(key)
        else:
            parts.append(f"{key}={value}")
    return ", ".join(parts)


def is_cacheable(cache_control: dict, status_code: int) -> bool:
    """Check if response is cacheable."""
    if "no-store" in cache_control:
        return False
    if "private" in cache_control:
        return False
    return status_code in [200, 203, 204, 206, 300, 301, 404, 405, 410, 414, 501]


def get_max_age(cache_control: dict) -> int:
    """Get max-age from cache control."""
    if "max-age" in cache_control:
        return int(cache_control["max-age"])
    return 0


def is_stale_while_revalidate(cache_control: dict) -> bool:
    """Check if stale-while-revalidate is set."""
    return "stale-while-revalidate" in cache_control


def get_stale_while_revalidate(cache_control: dict) -> int:
    """Get stale-while-revalidate value."""
    value = cache_control.get("stale-while-revalidate")
    return int(value) if value and value is not True else 0


def calculate_freshness(entry: dict, current_time: int) -> str:
    """Calculate entry freshness status."""
    if is_expired(entry, current_time):
        return "stale"
    remaining = calculate_remaining_ttl(entry, current_time)
    if remaining < entry["ttl"] * 0.1:
        return "nearly_stale"
    return "fresh"


def namespace_key(namespace: str, key: str) -> str:
    """Add namespace to cache key."""
    return f"{namespace}:{key}"


def parse_namespaced_key(full_key: str) -> dict:
    """Parse namespaced key."""
    if ":" in full_key:
        namespace, key = full_key.split(":", 1)
        return {"namespace": namespace, "key": key}
    return {"namespace": "", "key": full_key}


def versioned_key(key: str, version: int) -> str:
    """Add version to cache key."""
    return f"{key}:v{version}"
