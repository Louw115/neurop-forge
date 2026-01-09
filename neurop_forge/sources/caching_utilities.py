"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Caching Utilities - Pure functions for cache key generation and TTL calculations.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import hashlib
import json


def generate_cache_key(*args) -> str:
    """Generate a cache key from multiple arguments."""
    parts = [str(arg) for arg in args]
    return ':'.join(parts)


def generate_cache_key_with_prefix(prefix: str, *args) -> str:
    """Generate a cache key with a prefix."""
    parts = [prefix] + [str(arg) for arg in args]
    return ':'.join(parts)


def hash_cache_key(key: str) -> str:
    """Hash a cache key using MD5 for fixed-length keys."""
    return hashlib.md5(key.encode()).hexdigest()


def hash_cache_key_sha256(key: str) -> str:
    """Hash a cache key using SHA256 for more uniqueness."""
    return hashlib.sha256(key.encode()).hexdigest()


def generate_versioned_key(key: str, version: int) -> str:
    """Generate a versioned cache key."""
    return f"{key}:v{version}"


def generate_namespaced_key(namespace: str, key: str) -> str:
    """Generate a namespaced cache key."""
    return f"{namespace}:{key}"


def generate_tagged_key(key: str, tags: list) -> str:
    """Generate a cache key with tags."""
    tag_str = ','.join(sorted(tags))
    return f"{key}[{tag_str}]"


def generate_dict_key(data: dict) -> str:
    """Generate a cache key from a dictionary."""
    sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.md5(sorted_data.encode()).hexdigest()


def generate_list_key(items: list) -> str:
    """Generate a cache key from a list."""
    serialized = json.dumps(items, sort_keys=True, separators=(',', ':'))
    return hashlib.md5(serialized.encode()).hexdigest()


def calculate_ttl_seconds(hours: float, minutes: float, seconds: float) -> int:
    """Calculate TTL in seconds from hours, minutes, and seconds."""
    return int(hours * 3600 + minutes * 60 + seconds)


def calculate_ttl_from_minutes(minutes: float) -> int:
    """Calculate TTL in seconds from minutes."""
    return int(minutes * 60)


def calculate_ttl_from_hours(hours: float) -> int:
    """Calculate TTL in seconds from hours."""
    return int(hours * 3600)


def calculate_ttl_from_days(days: float) -> int:
    """Calculate TTL in seconds from days."""
    return int(days * 86400)


def calculate_ttl_from_weeks(weeks: float) -> int:
    """Calculate TTL in seconds from weeks."""
    return int(weeks * 604800)


def ttl_to_minutes(seconds: int) -> float:
    """Convert TTL seconds to minutes."""
    return seconds / 60


def ttl_to_hours(seconds: int) -> float:
    """Convert TTL seconds to hours."""
    return seconds / 3600


def ttl_to_days(seconds: int) -> float:
    """Convert TTL seconds to days."""
    return seconds / 86400


def format_ttl_human_readable(seconds: int) -> str:
    """Format TTL in human-readable form."""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    if seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    return f"{days}d {hours}h"


def is_ttl_expired(created_at: int, ttl_seconds: int, current_time: int) -> bool:
    """Check if a TTL has expired."""
    return current_time >= created_at + ttl_seconds


def remaining_ttl(created_at: int, ttl_seconds: int, current_time: int) -> int:
    """Calculate remaining TTL in seconds."""
    remaining = (created_at + ttl_seconds) - current_time
    return max(0, remaining)


def extend_ttl(original_ttl: int, extension_seconds: int) -> int:
    """Extend a TTL by additional seconds."""
    return original_ttl + extension_seconds


def calculate_sliding_window_start(current_time: int, window_size: int) -> int:
    """Calculate the start of a sliding window."""
    return current_time - window_size


def calculate_fixed_window_start(current_time: int, window_size: int) -> int:
    """Calculate the start of a fixed window."""
    return (current_time // window_size) * window_size


def calculate_window_bucket(timestamp: int, window_size: int) -> int:
    """Calculate which bucket a timestamp belongs to."""
    return timestamp // window_size


def should_refresh_cache(created_at: int, ttl_seconds: int, current_time: int, refresh_threshold: float) -> bool:
    """Check if cache should be proactively refreshed (before expiry)."""
    remaining = remaining_ttl(created_at, ttl_seconds, current_time)
    threshold = ttl_seconds * refresh_threshold
    return remaining < threshold


def calculate_exponential_backoff_ttl(base_ttl: int, attempt: int, max_ttl: int) -> int:
    """Calculate TTL with exponential backoff."""
    ttl = base_ttl * (2 ** attempt)
    return min(ttl, max_ttl)


def calculate_jittered_ttl(base_ttl: int, jitter_factor: float, seed_value: int) -> int:
    """Calculate TTL with deterministic jitter."""
    jitter = (seed_value % 1000) / 1000 * jitter_factor
    return int(base_ttl * (1 + jitter - jitter_factor / 2))


def lru_should_evict(cache_size: int, max_size: int) -> bool:
    """Check if LRU eviction should occur."""
    return cache_size >= max_size


def calculate_eviction_count(cache_size: int, max_size: int, target_ratio: float) -> int:
    """Calculate how many items to evict."""
    if cache_size <= max_size:
        return 0
    target_size = int(max_size * target_ratio)
    return cache_size - target_size


def calculate_memory_size_estimate(item_count: int, avg_key_size: int, avg_value_size: int) -> int:
    """Estimate memory usage of cache in bytes."""
    return item_count * (avg_key_size + avg_value_size)


def should_compress_value(value_size: int, compression_threshold: int) -> bool:
    """Check if a value should be compressed."""
    return value_size >= compression_threshold


def calculate_hit_rate(hits: int, misses: int) -> float:
    """Calculate cache hit rate."""
    total = hits + misses
    return hits / total if total > 0 else 0.0


def calculate_miss_rate(hits: int, misses: int) -> float:
    """Calculate cache miss rate."""
    total = hits + misses
    return misses / total if total > 0 else 0.0


def calculate_cache_efficiency(hits: int, misses: int, evictions: int) -> float:
    """Calculate cache efficiency score."""
    total = hits + misses
    if total == 0:
        return 0.0
    hit_rate = hits / total
    eviction_penalty = evictions / total if total > 0 else 0
    return max(0, hit_rate - eviction_penalty * 0.5)


def generate_etag(content: str) -> str:
    """Generate an ETag for content."""
    return f'"{hashlib.md5(content.encode()).hexdigest()}"'


def generate_weak_etag(content: str) -> str:
    """Generate a weak ETag for content."""
    return f'W/"{hashlib.md5(content.encode()).hexdigest()}"'


def is_etag_match(etag1: str, etag2: str) -> bool:
    """Check if two ETags match."""
    e1 = etag1.strip('"').lstrip('W/')
    e2 = etag2.strip('"').lstrip('W/')
    return e1 == e2


def parse_etag(etag: str) -> dict:
    """Parse an ETag into its components."""
    is_weak = etag.startswith('W/')
    value = etag.lstrip('W/').strip('"')
    return {'weak': is_weak, 'value': value}


def generate_cache_control_header(max_age: int, directives: list) -> str:
    """Generate a Cache-Control header value."""
    parts = [f"max-age={max_age}"] + directives
    return ', '.join(parts)


def parse_max_age(cache_control: str) -> int:
    """Parse max-age from Cache-Control header."""
    import re
    match = re.search(r'max-age=(\d+)', cache_control)
    return int(match.group(1)) if match else 0


def is_cache_control_no_cache(cache_control: str) -> bool:
    """Check if Cache-Control contains no-cache."""
    return 'no-cache' in cache_control.lower()


def is_cache_control_no_store(cache_control: str) -> bool:
    """Check if Cache-Control contains no-store."""
    return 'no-store' in cache_control.lower()


def is_cache_control_private(cache_control: str) -> bool:
    """Check if Cache-Control contains private."""
    return 'private' in cache_control.lower()


def is_cache_control_public(cache_control: str) -> bool:
    """Check if Cache-Control contains public."""
    return 'public' in cache_control.lower()


def calculate_stale_while_revalidate_ttl(max_age: int, stale_seconds: int) -> int:
    """Calculate total TTL including stale-while-revalidate period."""
    return max_age + stale_seconds


def is_stale(created_at: int, max_age: int, current_time: int) -> bool:
    """Check if cache entry is stale but may still be usable."""
    return current_time > created_at + max_age


def is_stale_within_tolerance(created_at: int, max_age: int, tolerance: int, current_time: int) -> bool:
    """Check if cache is stale but within tolerance for stale-while-revalidate."""
    if current_time <= created_at + max_age:
        return False
    return current_time <= created_at + max_age + tolerance


def partition_key(key: str, num_partitions: int) -> int:
    """Calculate which partition a key belongs to."""
    hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return hash_value % num_partitions


def generate_shard_key(key: str, num_shards: int) -> str:
    """Generate a shard-prefixed key."""
    shard = partition_key(key, num_shards)
    return f"shard{shard}:{key}"


def calculate_ttl_with_variance(base_ttl: int, variance_percent: float, key_hash: int) -> int:
    """Calculate TTL with variance to prevent thundering herd."""
    variance = int(base_ttl * variance_percent)
    offset = (key_hash % (2 * variance + 1)) - variance
    return max(1, base_ttl + offset)
