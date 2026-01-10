"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Ring Buffer - Pure functions for circular buffer operations.
All functions are pure, deterministic, and atomic.
"""

def create_ring_buffer(capacity: int) -> dict:
    """Create a ring buffer."""
    return {
        "items": [None] * capacity,
        "capacity": capacity,
        "head": 0,
        "tail": 0,
        "size": 0,
        "full": False
    }


def ring_push(buffer: dict, item) -> dict:
    """Push item to ring buffer."""
    items = list(buffer["items"])
    items[buffer["tail"]] = item
    new_tail = (buffer["tail"] + 1) % buffer["capacity"]
    if buffer["full"]:
        new_head = (buffer["head"] + 1) % buffer["capacity"]
        new_size = buffer["capacity"]
    else:
        new_head = buffer["head"]
        new_size = buffer["size"] + 1
    return {
        "items": items,
        "capacity": buffer["capacity"],
        "head": new_head,
        "tail": new_tail,
        "size": new_size,
        "full": new_size == buffer["capacity"]
    }


def ring_pop(buffer: dict) -> dict:
    """Pop oldest item from ring buffer."""
    if buffer["size"] == 0:
        return {"buffer": buffer, "item": None}
    item = buffer["items"][buffer["head"]]
    items = list(buffer["items"])
    items[buffer["head"]] = None
    new_head = (buffer["head"] + 1) % buffer["capacity"]
    return {
        "buffer": {
            "items": items,
            "capacity": buffer["capacity"],
            "head": new_head,
            "tail": buffer["tail"],
            "size": buffer["size"] - 1,
            "full": False
        },
        "item": item
    }


def ring_peek(buffer: dict):
    """Peek at oldest item."""
    if buffer["size"] == 0:
        return None
    return buffer["items"][buffer["head"]]


def ring_peek_newest(buffer: dict):
    """Peek at newest item."""
    if buffer["size"] == 0:
        return None
    idx = (buffer["tail"] - 1) % buffer["capacity"]
    return buffer["items"][idx]


def ring_size(buffer: dict) -> int:
    """Get current size."""
    return buffer["size"]


def ring_capacity(buffer: dict) -> int:
    """Get capacity."""
    return buffer["capacity"]


def ring_is_empty(buffer: dict) -> bool:
    """Check if empty."""
    return buffer["size"] == 0


def ring_is_full(buffer: dict) -> bool:
    """Check if full."""
    return buffer["full"]


def ring_clear(buffer: dict) -> dict:
    """Clear the buffer."""
    return create_ring_buffer(buffer["capacity"])


def ring_to_list(buffer: dict) -> list:
    """Convert to list (oldest to newest)."""
    result = []
    for i in range(buffer["size"]):
        idx = (buffer["head"] + i) % buffer["capacity"]
        result.append(buffer["items"][idx])
    return result


def ring_from_list(items: list, capacity: int) -> dict:
    """Create ring buffer from list."""
    buffer = create_ring_buffer(capacity)
    for item in items:
        buffer = ring_push(buffer, item)
    return buffer


def ring_get(buffer: dict, index: int):
    """Get item at index (0 = oldest)."""
    if index < 0 or index >= buffer["size"]:
        return None
    idx = (buffer["head"] + index) % buffer["capacity"]
    return buffer["items"][idx]


def ring_get_from_end(buffer: dict, index: int):
    """Get item at index from end (0 = newest)."""
    if index < 0 or index >= buffer["size"]:
        return None
    idx = (buffer["tail"] - 1 - index) % buffer["capacity"]
    return buffer["items"][idx]


def ring_take(buffer: dict, n: int) -> list:
    """Take n oldest items."""
    return ring_to_list(buffer)[:n]


def ring_take_latest(buffer: dict, n: int) -> list:
    """Take n newest items."""
    items = ring_to_list(buffer)
    return items[-n:] if n < len(items) else items


def ring_drop(buffer: dict, n: int) -> dict:
    """Drop n oldest items."""
    result = buffer
    for _ in range(min(n, buffer["size"])):
        pop_result = ring_pop(result)
        result = pop_result["buffer"]
    return result


def ring_map(buffer: dict, transform) -> dict:
    """Apply transformation to all items."""
    items = [transform(i) if i is not None else None for i in buffer["items"]]
    return {**buffer, "items": items}


def ring_filter(buffer: dict, predicate) -> list:
    """Filter items by predicate."""
    return [item for item in ring_to_list(buffer) if predicate(item)]


def ring_reduce(buffer: dict, combine, initial):
    """Reduce buffer to single value."""
    result = initial
    for item in ring_to_list(buffer):
        result = combine(result, item)
    return result


def ring_sum(buffer: dict) -> float:
    """Sum all numeric items."""
    return sum(x for x in ring_to_list(buffer) if x is not None)


def ring_average(buffer: dict) -> float:
    """Calculate average of items."""
    items = [x for x in ring_to_list(buffer) if x is not None]
    return sum(items) / len(items) if items else 0


def ring_min(buffer: dict):
    """Get minimum item."""
    items = [x for x in ring_to_list(buffer) if x is not None]
    return min(items) if items else None


def ring_max(buffer: dict):
    """Get maximum item."""
    items = [x for x in ring_to_list(buffer) if x is not None]
    return max(items) if items else None


def ring_contains(buffer: dict, item) -> bool:
    """Check if buffer contains item."""
    return item in ring_to_list(buffer)


def ring_count(buffer: dict, item) -> int:
    """Count occurrences of item."""
    return ring_to_list(buffer).count(item)


def ring_fill_ratio(buffer: dict) -> float:
    """Calculate fill ratio."""
    return buffer["size"] / buffer["capacity"] if buffer["capacity"] > 0 else 0


def ring_available_space(buffer: dict) -> int:
    """Get available space."""
    return buffer["capacity"] - buffer["size"]


def ring_resize(buffer: dict, new_capacity: int) -> dict:
    """Resize buffer (may truncate oldest items)."""
    items = ring_to_list(buffer)
    if new_capacity < len(items):
        items = items[-new_capacity:]
    return ring_from_list(items, new_capacity)
