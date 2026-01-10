"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Linked List - Pure functions for linked list operations.
All functions are pure, deterministic, and atomic.
"""

def create_node(value, next_node: dict) -> dict:
    """Create a linked list node."""
    return {"value": value, "next": next_node}


def create_list() -> dict:
    """Create an empty linked list."""
    return {"head": None, "size": 0}


def list_prepend(ll: dict, value) -> dict:
    """Prepend value to list."""
    new_node = create_node(value, ll["head"])
    return {"head": new_node, "size": ll["size"] + 1}


def list_append(ll: dict, value) -> dict:
    """Append value to end of list."""
    new_node = create_node(value, None)
    if ll["head"] is None:
        return {"head": new_node, "size": 1}
    def append_to_end(node):
        if node["next"] is None:
            return create_node(node["value"], new_node)
        return create_node(node["value"], append_to_end(node["next"]))
    return {"head": append_to_end(ll["head"]), "size": ll["size"] + 1}


def list_head(ll: dict):
    """Get head value."""
    if ll["head"]:
        return ll["head"]["value"]
    return None


def list_tail(ll: dict) -> dict:
    """Get list without head."""
    if ll["head"] is None:
        return ll
    return {"head": ll["head"]["next"], "size": ll["size"] - 1}


def list_get(ll: dict, index: int):
    """Get value at index."""
    node = ll["head"]
    for _ in range(index):
        if node is None:
            return None
        node = node["next"]
    return node["value"] if node else None


def list_length(ll: dict) -> int:
    """Get list length."""
    return ll["size"]


def list_is_empty(ll: dict) -> bool:
    """Check if list is empty."""
    return ll["head"] is None


def list_to_array(ll: dict) -> list:
    """Convert linked list to array."""
    result = []
    node = ll["head"]
    while node:
        result.append(node["value"])
        node = node["next"]
    return result


def list_from_array(arr: list) -> dict:
    """Create linked list from array."""
    ll = create_list()
    for value in reversed(arr):
        ll = list_prepend(ll, value)
    return ll


def list_reverse(ll: dict) -> dict:
    """Reverse linked list."""
    result = create_list()
    node = ll["head"]
    while node:
        result = list_prepend(result, node["value"])
        node = node["next"]
    return result


def list_map(ll: dict, transform) -> dict:
    """Apply transformation to all values."""
    def map_node(node):
        if node is None:
            return None
        return create_node(transform(node["value"]), map_node(node["next"]))
    return {"head": map_node(ll["head"]), "size": ll["size"]}


def list_filter(ll: dict, predicate) -> dict:
    """Filter list by predicate."""
    def filter_node(node):
        if node is None:
            return None
        rest = filter_node(node["next"])
        if predicate(node["value"]):
            return create_node(node["value"], rest)
        return rest
    new_head = filter_node(ll["head"])
    size = 0
    node = new_head
    while node:
        size += 1
        node = node["next"]
    return {"head": new_head, "size": size}


def list_find(ll: dict, predicate):
    """Find first value matching predicate."""
    node = ll["head"]
    while node:
        if predicate(node["value"]):
            return node["value"]
        node = node["next"]
    return None


def list_contains(ll: dict, value) -> bool:
    """Check if list contains value."""
    node = ll["head"]
    while node:
        if node["value"] == value:
            return True
        node = node["next"]
    return False


def list_index_of(ll: dict, value) -> int:
    """Get index of value or -1."""
    node = ll["head"]
    index = 0
    while node:
        if node["value"] == value:
            return index
        node = node["next"]
        index += 1
    return -1


def list_insert_at(ll: dict, index: int, value) -> dict:
    """Insert value at index."""
    if index == 0:
        return list_prepend(ll, value)
    def insert_helper(node, i):
        if node is None or i <= 0:
            return create_node(value, node)
        return create_node(node["value"], insert_helper(node["next"], i - 1))
    return {"head": insert_helper(ll["head"], index), "size": ll["size"] + 1}


def list_remove_at(ll: dict, index: int) -> dict:
    """Remove value at index."""
    if index == 0 and ll["head"]:
        return list_tail(ll)
    def remove_helper(node, i):
        if node is None:
            return None
        if i == 0:
            return node["next"]
        return create_node(node["value"], remove_helper(node["next"], i - 1))
    return {"head": remove_helper(ll["head"], index), "size": max(0, ll["size"] - 1)}


def list_concat(ll1: dict, ll2: dict) -> dict:
    """Concatenate two lists."""
    if ll1["head"] is None:
        return ll2
    def concat_helper(node):
        if node["next"] is None:
            return create_node(node["value"], ll2["head"])
        return create_node(node["value"], concat_helper(node["next"]))
    return {"head": concat_helper(ll1["head"]), "size": ll1["size"] + ll2["size"]}


def list_take(ll: dict, n: int) -> dict:
    """Take first n elements."""
    def take_helper(node, count):
        if node is None or count <= 0:
            return None
        return create_node(node["value"], take_helper(node["next"], count - 1))
    return {"head": take_helper(ll["head"], n), "size": min(n, ll["size"])}


def list_drop(ll: dict, n: int) -> dict:
    """Drop first n elements."""
    node = ll["head"]
    count = n
    while node and count > 0:
        node = node["next"]
        count -= 1
    return {"head": node, "size": max(0, ll["size"] - n)}


def list_last(ll: dict):
    """Get last value."""
    if ll["head"] is None:
        return None
    node = ll["head"]
    while node["next"]:
        node = node["next"]
    return node["value"]


def list_fold(ll: dict, combine, initial):
    """Fold list to single value."""
    result = initial
    node = ll["head"]
    while node:
        result = combine(result, node["value"])
        node = node["next"]
    return result


def list_sum(ll: dict) -> float:
    """Sum all numeric values."""
    return list_fold(ll, lambda a, b: a + b, 0)


def list_any(ll: dict, predicate) -> bool:
    """Check if any value matches predicate."""
    return list_find(ll, predicate) is not None


def list_all(ll: dict, predicate) -> bool:
    """Check if all values match predicate."""
    node = ll["head"]
    while node:
        if not predicate(node["value"]):
            return False
        node = node["next"]
    return True
