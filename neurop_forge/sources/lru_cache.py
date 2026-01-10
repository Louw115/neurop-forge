"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
LRU Cache - Pure functions for LRU cache implementation.
All functions are pure, deterministic, and atomic.
"""

def create_lru_cache(capacity: int) -> dict:
    """Create an LRU cache."""
    return {
        "capacity": capacity,
        "items": {},
        "order": [],
        "size": 0
    }


def lru_get(cache: dict, key: str) -> dict:
    """Get value from cache (updates access order)."""
    if key not in cache["items"]:
        return {"cache": cache, "value": None, "hit": False}
    order = [k for k in cache["order"] if k != key]
    order.append(key)
    return {
        "cache": {
            "capacity": cache["capacity"],
            "items": dict(cache["items"]),
            "order": order,
            "size": cache["size"]
        },
        "value": cache["items"][key],
        "hit": True
    }


def lru_put(cache: dict, key: str, value) -> dict:
    """Put value in cache (evicts LRU if full)."""
    items = dict(cache["items"])
    order = list(cache["order"])
    if key in items:
        order = [k for k in order if k != key]
        items[key] = value
        order.append(key)
        return {
            "capacity": cache["capacity"],
            "items": items,
            "order": order,
            "size": cache["size"]
        }
    if len(items) >= cache["capacity"]:
        evicted = order.pop(0)
        del items[evicted]
    items[key] = value
    order.append(key)
    return {
        "capacity": cache["capacity"],
        "items": items,
        "order": order,
        "size": len(items)
    }


def lru_remove(cache: dict, key: str) -> dict:
    """Remove key from cache."""
    if key not in cache["items"]:
        return cache
    items = dict(cache["items"])
    del items[key]
    order = [k for k in cache["order"] if k != key]
    return {
        "capacity": cache["capacity"],
        "items": items,
        "order": order,
        "size": len(items)
    }


def lru_contains(cache: dict, key: str) -> bool:
    """Check if key is in cache."""
    return key in cache["items"]


def lru_size(cache: dict) -> int:
    """Get current cache size."""
    return cache["size"]


def lru_is_full(cache: dict) -> bool:
    """Check if cache is full."""
    return cache["size"] >= cache["capacity"]


def lru_clear(cache: dict) -> dict:
    """Clear the cache."""
    return create_lru_cache(cache["capacity"])


def lru_keys(cache: dict) -> list:
    """Get all keys (MRU first)."""
    return list(reversed(cache["order"]))


def lru_values(cache: dict) -> list:
    """Get all values (MRU first)."""
    return [cache["items"][k] for k in reversed(cache["order"])]


def lru_peek(cache: dict, key: str):
    """Get value without updating access order."""
    return cache["items"].get(key)


def lru_mru_key(cache: dict):
    """Get most recently used key."""
    return cache["order"][-1] if cache["order"] else None


def lru_lru_key(cache: dict):
    """Get least recently used key."""
    return cache["order"][0] if cache["order"] else None


def lru_resize(cache: dict, new_capacity: int) -> dict:
    """Resize cache (evicts LRU entries if shrinking)."""
    if new_capacity >= cache["size"]:
        return {
            "capacity": new_capacity,
            "items": dict(cache["items"]),
            "order": list(cache["order"]),
            "size": cache["size"]
        }
    evict_count = cache["size"] - new_capacity
    order = cache["order"][evict_count:]
    items = {k: cache["items"][k] for k in order}
    return {
        "capacity": new_capacity,
        "items": items,
        "order": order,
        "size": len(items)
    }


def lru_update_capacity(cache: dict, new_capacity: int) -> dict:
    """Update capacity (alias for resize)."""
    return lru_resize(cache, new_capacity)


def lru_touch(cache: dict, key: str) -> dict:
    """Touch key to update access time."""
    if key not in cache["items"]:
        return cache
    order = [k for k in cache["order"] if k != key]
    order.append(key)
    return {
        "capacity": cache["capacity"],
        "items": dict(cache["items"]),
        "order": order,
        "size": cache["size"]
    }


def lru_get_stats(cache: dict) -> dict:
    """Get cache statistics."""
    return {
        "size": cache["size"],
        "capacity": cache["capacity"],
        "utilization": cache["size"] / cache["capacity"] if cache["capacity"] > 0 else 0,
        "lru_key": lru_lru_key(cache),
        "mru_key": lru_mru_key(cache)
    }


def create_ttl_lru_cache(capacity: int) -> dict:
    """Create LRU cache with TTL support."""
    return {
        "capacity": capacity,
        "items": {},
        "ttls": {},
        "order": [],
        "size": 0
    }


def ttl_lru_put(cache: dict, key: str, value, ttl_seconds: int, current_time: int) -> dict:
    """Put value with TTL."""
    base = lru_put({
        "capacity": cache["capacity"],
        "items": cache["items"],
        "order": cache["order"],
        "size": cache["size"]
    }, key, value)
    ttls = dict(cache.get("ttls", {}))
    ttls[key] = current_time + ttl_seconds
    return {**base, "ttls": ttls}


def ttl_lru_get(cache: dict, key: str, current_time: int) -> dict:
    """Get value if not expired."""
    if key not in cache["items"]:
        return {"cache": cache, "value": None, "hit": False}
    ttl = cache.get("ttls", {}).get(key, float("inf"))
    if current_time > ttl:
        new_cache = lru_remove(cache, key)
        new_ttls = dict(cache.get("ttls", {}))
        if key in new_ttls:
            del new_ttls[key]
        new_cache["ttls"] = new_ttls
        return {"cache": new_cache, "value": None, "hit": False}
    result = lru_get({
        "capacity": cache["capacity"],
        "items": cache["items"],
        "order": cache["order"],
        "size": cache["size"]
    }, key)
    result["cache"]["ttls"] = cache.get("ttls", {})
    return result


def ttl_lru_cleanup_expired(cache: dict, current_time: int) -> dict:
    """Remove all expired entries."""
    result = cache
    for key, ttl in list(cache.get("ttls", {}).items()):
        if current_time > ttl:
            result = lru_remove(result, key)
            ttls = dict(result.get("ttls", {}))
            if key in ttls:
                del ttls[key]
            result["ttls"] = ttls
    return result


def lru_to_dict(cache: dict) -> dict:
    """Convert cache to dictionary."""
    return dict(cache["items"])


def lru_from_dict(d: dict, capacity: int) -> dict:
    """Create cache from dictionary."""
    cache = create_lru_cache(capacity)
    for k, v in d.items():
        cache = lru_put(cache, str(k), v)
    return cache
