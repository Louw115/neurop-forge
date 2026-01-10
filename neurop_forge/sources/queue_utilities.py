"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Queue Utilities - Pure functions for queue data structures.
All functions are pure, deterministic, and atomic.
"""

def create_queue() -> dict:
    """Create an empty queue."""
    return {"items": [], "size": 0}


def queue_enqueue(queue: dict, item) -> dict:
    """Add item to back of queue."""
    return {
        "items": list(queue["items"]) + [item],
        "size": queue["size"] + 1
    }


def queue_dequeue(queue: dict) -> dict:
    """Remove and return front item."""
    if not queue["items"]:
        return {"queue": queue, "item": None}
    items = list(queue["items"])
    item = items.pop(0)
    return {
        "queue": {"items": items, "size": len(items)},
        "item": item
    }


def queue_peek(queue: dict):
    """Peek at front item without removing."""
    if queue["items"]:
        return queue["items"][0]
    return None


def queue_is_empty(queue: dict) -> bool:
    """Check if queue is empty."""
    return queue["size"] == 0


def queue_size(queue: dict) -> int:
    """Get queue size."""
    return queue["size"]


def queue_clear(queue: dict) -> dict:
    """Clear the queue."""
    return {"items": [], "size": 0}


def queue_to_list(queue: dict) -> list:
    """Convert queue to list."""
    return list(queue["items"])


def queue_from_list(items: list) -> dict:
    """Create queue from list."""
    return {"items": list(items), "size": len(items)}


def create_deque() -> dict:
    """Create an empty double-ended queue."""
    return {"items": [], "size": 0}


def deque_push_front(deque: dict, item) -> dict:
    """Add item to front of deque."""
    return {
        "items": [item] + list(deque["items"]),
        "size": deque["size"] + 1
    }


def deque_push_back(deque: dict, item) -> dict:
    """Add item to back of deque."""
    return {
        "items": list(deque["items"]) + [item],
        "size": deque["size"] + 1
    }


def deque_pop_front(deque: dict) -> dict:
    """Remove and return front item."""
    if not deque["items"]:
        return {"deque": deque, "item": None}
    items = list(deque["items"])
    item = items.pop(0)
    return {
        "deque": {"items": items, "size": len(items)},
        "item": item
    }


def deque_pop_back(deque: dict) -> dict:
    """Remove and return back item."""
    if not deque["items"]:
        return {"deque": deque, "item": None}
    items = list(deque["items"])
    item = items.pop()
    return {
        "deque": {"items": items, "size": len(items)},
        "item": item
    }


def deque_peek_front(deque: dict):
    """Peek at front item."""
    return deque["items"][0] if deque["items"] else None


def deque_peek_back(deque: dict):
    """Peek at back item."""
    return deque["items"][-1] if deque["items"] else None


def create_circular_buffer(capacity: int) -> dict:
    """Create a circular buffer."""
    return {
        "items": [None] * capacity,
        "capacity": capacity,
        "head": 0,
        "tail": 0,
        "size": 0
    }


def circular_buffer_push(buffer: dict, item) -> dict:
    """Push item to circular buffer."""
    items = list(buffer["items"])
    items[buffer["tail"]] = item
    new_tail = (buffer["tail"] + 1) % buffer["capacity"]
    new_head = buffer["head"]
    new_size = buffer["size"]
    if buffer["size"] < buffer["capacity"]:
        new_size += 1
    else:
        new_head = (buffer["head"] + 1) % buffer["capacity"]
    return {
        "items": items,
        "capacity": buffer["capacity"],
        "head": new_head,
        "tail": new_tail,
        "size": new_size
    }


def circular_buffer_pop(buffer: dict) -> dict:
    """Pop oldest item from circular buffer."""
    if buffer["size"] == 0:
        return {"buffer": buffer, "item": None}
    item = buffer["items"][buffer["head"]]
    new_head = (buffer["head"] + 1) % buffer["capacity"]
    return {
        "buffer": {
            "items": buffer["items"],
            "capacity": buffer["capacity"],
            "head": new_head,
            "tail": buffer["tail"],
            "size": buffer["size"] - 1
        },
        "item": item
    }


def circular_buffer_to_list(buffer: dict) -> list:
    """Convert circular buffer to list."""
    result = []
    idx = buffer["head"]
    for _ in range(buffer["size"]):
        result.append(buffer["items"][idx])
        idx = (idx + 1) % buffer["capacity"]
    return result


def create_bounded_queue(max_size: int) -> dict:
    """Create a bounded queue."""
    return {"items": [], "max_size": max_size}


def bounded_queue_enqueue(queue: dict, item) -> dict:
    """Enqueue to bounded queue, drop oldest if full."""
    items = list(queue["items"]) + [item]
    if len(items) > queue["max_size"]:
        items = items[-queue["max_size"]:]
    return {"items": items, "max_size": queue["max_size"]}


def bounded_queue_is_full(queue: dict) -> bool:
    """Check if bounded queue is full."""
    return len(queue["items"]) >= queue["max_size"]


def create_priority_queue() -> dict:
    """Create an empty priority queue."""
    return {"items": []}


def priority_queue_push(pq: dict, priority: int, value) -> dict:
    """Push item with priority."""
    items = list(pq["items"])
    items.append({"priority": priority, "value": value})
    items.sort(key=lambda x: x["priority"])
    return {"items": items}


def priority_queue_pop(pq: dict) -> dict:
    """Pop highest priority item."""
    if not pq["items"]:
        return {"pq": pq, "item": None}
    items = list(pq["items"])
    item = items.pop(0)
    return {"pq": {"items": items}, "item": item["value"]}


def priority_queue_peek(pq: dict):
    """Peek at highest priority item."""
    if pq["items"]:
        return pq["items"][0]["value"]
    return None


def batch_dequeue(queue: dict, count: int) -> dict:
    """Dequeue multiple items at once."""
    items = list(queue["items"])
    batch = items[:count]
    remaining = items[count:]
    return {
        "queue": {"items": remaining, "size": len(remaining)},
        "items": batch
    }


def queue_rotate(queue: dict, positions: int) -> dict:
    """Rotate queue by positions."""
    if not queue["items"]:
        return queue
    items = list(queue["items"])
    positions = positions % len(items)
    items = items[positions:] + items[:positions]
    return {"items": items, "size": len(items)}


def queue_reverse(queue: dict) -> dict:
    """Reverse a queue."""
    return {"items": list(reversed(queue["items"])), "size": queue["size"]}
