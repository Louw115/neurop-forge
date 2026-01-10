"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Skip List - Pure functions for skip list operations.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def _random_level(key, max_level: int) -> int:
    """Deterministic random level based on key hash."""
    h = hashlib.sha256(str(key).encode()).digest()
    level = 1
    for i in range(max_level - 1):
        if h[i % len(h)] < 128:
            level += 1
        else:
            break
    return level


def create_skip_list(max_level: int) -> dict:
    """Create an empty skip list."""
    return {
        "head": {"key": None, "value": None, "forward": [None] * max_level},
        "max_level": max_level,
        "level": 1,
        "size": 0
    }


def skip_list_search(sl: dict, key):
    """Search for a key."""
    node = sl["head"]
    for i in range(sl["level"] - 1, -1, -1):
        while node["forward"][i] and node["forward"][i]["key"] < key:
            node = node["forward"][i]
    node = node["forward"][0]
    if node and node["key"] == key:
        return node["value"]
    return None


def skip_list_contains(sl: dict, key) -> bool:
    """Check if key exists."""
    return skip_list_search(sl, key) is not None


def _clone_node(node: dict) -> dict:
    """Clone a skip list node."""
    if node is None:
        return None
    return {
        "key": node["key"],
        "value": node["value"],
        "forward": list(node["forward"])
    }


def skip_list_insert(sl: dict, key, value) -> dict:
    """Insert a key-value pair."""
    update = [None] * sl["max_level"]
    node = _clone_node(sl["head"])
    head = node
    for i in range(sl["level"] - 1, -1, -1):
        while node["forward"][i] and node["forward"][i]["key"] < key:
            next_node = _clone_node(node["forward"][i])
            node["forward"][i] = next_node
            node = next_node
        update[i] = node
    next_at_0 = node["forward"][0]
    if next_at_0 and next_at_0["key"] == key:
        new_node = _clone_node(next_at_0)
        new_node["value"] = value
        update[0]["forward"][0] = new_node
        return {**sl, "head": head}
    new_level = _random_level(key, sl["max_level"])
    level = sl["level"]
    if new_level > sl["level"]:
        for i in range(sl["level"], new_level):
            update[i] = head
        level = new_level
    new_node = {
        "key": key,
        "value": value,
        "forward": [None] * new_level
    }
    for i in range(new_level):
        new_node["forward"][i] = update[i]["forward"][i] if i < len(update[i]["forward"]) else None
        update[i]["forward"][i] = new_node
    return {
        "head": head,
        "max_level": sl["max_level"],
        "level": level,
        "size": sl["size"] + 1
    }


def skip_list_delete(sl: dict, key) -> dict:
    """Delete a key."""
    update = [None] * sl["max_level"]
    node = _clone_node(sl["head"])
    head = node
    for i in range(sl["level"] - 1, -1, -1):
        while node["forward"][i] and node["forward"][i]["key"] < key:
            next_node = _clone_node(node["forward"][i])
            node["forward"][i] = next_node
            node = next_node
        update[i] = node
    target = node["forward"][0]
    if not target or target["key"] != key:
        return sl
    for i in range(sl["level"]):
        if update[i]["forward"][i] != target:
            break
        update[i]["forward"][i] = target["forward"][i] if i < len(target["forward"]) else None
    level = sl["level"]
    while level > 1 and head["forward"][level - 1] is None:
        level -= 1
    return {
        "head": head,
        "max_level": sl["max_level"],
        "level": level,
        "size": sl["size"] - 1
    }


def skip_list_min(sl: dict):
    """Get minimum key."""
    first = sl["head"]["forward"][0]
    return first["key"] if first else None


def skip_list_max(sl: dict):
    """Get maximum key."""
    node = sl["head"]
    for i in range(sl["level"] - 1, -1, -1):
        while node["forward"][i]:
            node = node["forward"][i]
    return node["key"] if node["key"] is not None else None


def skip_list_size(sl: dict) -> int:
    """Get number of elements."""
    return sl["size"]


def skip_list_is_empty(sl: dict) -> bool:
    """Check if empty."""
    return sl["size"] == 0


def skip_list_to_list(sl: dict) -> list:
    """Convert to sorted list of key-value pairs."""
    result = []
    node = sl["head"]["forward"][0]
    while node:
        result.append((node["key"], node["value"]))
        node = node["forward"][0]
    return result


def skip_list_keys(sl: dict) -> list:
    """Get all keys in sorted order."""
    return [k for k, v in skip_list_to_list(sl)]


def skip_list_values(sl: dict) -> list:
    """Get all values in key order."""
    return [v for k, v in skip_list_to_list(sl)]


def skip_list_range(sl: dict, lo, hi) -> list:
    """Get key-value pairs in range [lo, hi]."""
    result = []
    node = sl["head"]
    for i in range(sl["level"] - 1, -1, -1):
        while node["forward"][i] and node["forward"][i]["key"] < lo:
            node = node["forward"][i]
    node = node["forward"][0]
    while node and node["key"] <= hi:
        result.append((node["key"], node["value"]))
        node = node["forward"][0]
    return result


def skip_list_floor(sl: dict, key):
    """Find largest key <= given key."""
    node = sl["head"]
    result = None
    for i in range(sl["level"] - 1, -1, -1):
        while node["forward"][i] and node["forward"][i]["key"] <= key:
            result = node["forward"][i]["key"]
            node = node["forward"][i]
    return result


def skip_list_ceiling(sl: dict, key):
    """Find smallest key >= given key."""
    node = sl["head"]
    for i in range(sl["level"] - 1, -1, -1):
        while node["forward"][i] and node["forward"][i]["key"] < key:
            node = node["forward"][i]
    node = node["forward"][0]
    return node["key"] if node else None


def skip_list_from_list(items: list, max_level: int) -> dict:
    """Create skip list from list of (key, value) pairs."""
    sl = create_skip_list(max_level)
    for key, value in sorted(items):
        sl = skip_list_insert(sl, key, value)
    return sl


def skip_list_level_stats(sl: dict) -> dict:
    """Get level statistics."""
    level_counts = [0] * sl["level"]
    node = sl["head"]["forward"][0]
    while node:
        for i in range(len(node["forward"])):
            if node["forward"][i]:
                level_counts[i] += 1
        node = node["forward"][0]
    return {
        "current_level": sl["level"],
        "max_level": sl["max_level"],
        "level_counts": level_counts
    }
