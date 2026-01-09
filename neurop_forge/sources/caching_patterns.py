"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Caching Patterns - Pure functions for caching strategies.
All functions are pure, deterministic, and atomic.
"""

def build_cache_key(prefix: str, parts: list) -> str:
    """Build a cache key from parts."""
    return f"{prefix}:" + ":".join(str(p) for p in parts)


def parse_cache_key(key: str) -> list:
    """Parse a cache key into parts."""
    return key.split(":")


def build_cache_entry(value, ttl_seconds: int, created_at: str) -> dict:
    """Build a cache entry."""
    return {
        "value": value,
        "ttl": ttl_seconds,
        "created_at": created_at,
        "hits": 0
    }


def is_cache_expired(entry: dict, current_timestamp: str) -> bool:
    """Check if cache entry is expired."""
    from datetime import datetime
    created = datetime.fromisoformat(entry["created_at"].replace('Z', '+00:00'))
    current = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
    elapsed = (current - created).total_seconds()
    return elapsed >= entry["ttl"]


def calculate_cache_ttl_remaining(entry: dict, current_timestamp: str) -> int:
    """Calculate remaining TTL in seconds."""
    from datetime import datetime
    created = datetime.fromisoformat(entry["created_at"].replace('Z', '+00:00'))
    current = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
    elapsed = (current - created).total_seconds()
    return max(0, int(entry["ttl"] - elapsed))


def increment_cache_hits(entry: dict) -> dict:
    """Increment cache hit counter."""
    result = dict(entry)
    result["hits"] = entry.get("hits", 0) + 1
    return result


def calculate_cache_hit_rate(hits: int, misses: int) -> float:
    """Calculate cache hit rate percentage."""
    total = hits + misses
    if total <= 0:
        return 0.0
    return (hits / total) * 100


def build_lru_entry(key: str, value, access_time: str) -> dict:
    """Build an LRU cache entry."""
    return {
        "key": key,
        "value": value,
        "access_time": access_time
    }


def find_lru_eviction_candidate(entries: list) -> str:
    """Find least recently used entry key."""
    if not entries:
        return ""
    oldest = min(entries, key=lambda e: e["access_time"])
    return oldest["key"]


def update_lru_access_time(entry: dict, new_access_time: str) -> dict:
    """Update LRU entry access time."""
    result = dict(entry)
    result["access_time"] = new_access_time
    return result


def build_lfu_entry(key: str, value, frequency: int) -> dict:
    """Build an LFU cache entry."""
    return {
        "key": key,
        "value": value,
        "frequency": frequency
    }


def find_lfu_eviction_candidate(entries: list) -> str:
    """Find least frequently used entry key."""
    if not entries:
        return ""
    least_freq = min(entries, key=lambda e: e["frequency"])
    return least_freq["key"]


def increment_lfu_frequency(entry: dict) -> dict:
    """Increment LFU entry frequency."""
    result = dict(entry)
    result["frequency"] = entry.get("frequency", 0) + 1
    return result


def should_cache(response_status: int, cacheable_statuses: list) -> bool:
    """Check if response should be cached."""
    return response_status in cacheable_statuses


def parse_cache_control_header(header: str) -> dict:
    """Parse Cache-Control header."""
    directives = {}
    for part in header.split(","):
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            directives[key.strip()] = value.strip()
        else:
            directives[part] = True
    return directives


def build_cache_control_header(max_age: int, public: bool, no_cache: bool, no_store: bool) -> str:
    """Build Cache-Control header value."""
    parts = []
    if no_store:
        parts.append("no-store")
    elif no_cache:
        parts.append("no-cache")
    else:
        parts.append("public" if public else "private")
        parts.append(f"max-age={max_age}")
    return ", ".join(parts)


def calculate_stale_time(max_age: int, stale_while_revalidate: int, elapsed: int) -> dict:
    """Calculate if content is stale and within stale window."""
    is_fresh = elapsed < max_age
    is_stale_but_usable = max_age <= elapsed < (max_age + stale_while_revalidate)
    return {
        "fresh": is_fresh,
        "stale_usable": is_stale_but_usable,
        "expired": elapsed >= (max_age + stale_while_revalidate)
    }


def generate_etag(content_hash: str, weak: bool) -> str:
    """Generate an ETag header value."""
    if weak:
        return f'W/"{content_hash}"'
    return f'"{content_hash}"'


def parse_etag(etag: str) -> dict:
    """Parse an ETag header value."""
    weak = etag.startswith("W/")
    value = etag.replace("W/", "").strip('"')
    return {"weak": weak, "value": value}


def etags_match(etag1: str, etag2: str, weak_comparison: bool) -> bool:
    """Compare two ETags."""
    parsed1 = parse_etag(etag1)
    parsed2 = parse_etag(etag2)
    if weak_comparison:
        return parsed1["value"] == parsed2["value"]
    if parsed1["weak"] or parsed2["weak"]:
        return False
    return parsed1["value"] == parsed2["value"]


def build_cache_stats(entries_count: int, total_size_bytes: int, hit_count: int, miss_count: int, eviction_count: int) -> dict:
    """Build cache statistics."""
    return {
        "entries": entries_count,
        "size_bytes": total_size_bytes,
        "hits": hit_count,
        "misses": miss_count,
        "evictions": eviction_count,
        "hit_rate": calculate_cache_hit_rate(hit_count, miss_count)
    }


def should_evict(current_size: int, max_size: int, current_entries: int, max_entries: int) -> bool:
    """Check if cache should evict entries."""
    return current_size >= max_size or current_entries >= max_entries


def calculate_cache_memory_pressure(used_bytes: int, max_bytes: int) -> float:
    """Calculate cache memory pressure percentage."""
    if max_bytes <= 0:
        return 0.0
    return (used_bytes / max_bytes) * 100


def estimate_entry_size(key: str, value_size: int, overhead_bytes: int) -> int:
    """Estimate cache entry size in bytes."""
    return len(key.encode()) + value_size + overhead_bytes


def build_warm_up_keys(patterns: list, params: list) -> list:
    """Build keys for cache warm-up."""
    keys = []
    for pattern in patterns:
        for param in params:
            keys.append(pattern.replace("{}", str(param)))
    return keys


def calculate_ttl_jitter(base_ttl: int, jitter_percent: float, seed: int) -> int:
    """Calculate TTL with jitter to prevent stampede."""
    import hashlib
    hash_val = hashlib.sha256(str(seed).encode()).digest()
    jitter_ratio = (hash_val[0] / 255.0 - 0.5) * 2
    jitter = int(base_ttl * (jitter_percent / 100) * jitter_ratio)
    return base_ttl + jitter
