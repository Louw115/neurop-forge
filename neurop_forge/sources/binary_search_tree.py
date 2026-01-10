"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Binary Search Tree - Pure functions for BST operations.
All functions are pure, deterministic, and atomic.
"""

def create_bst_node(key, value, left, right) -> dict:
    """Create a BST node."""
    return {"key": key, "value": value, "left": left, "right": right}


def create_bst() -> dict:
    """Create an empty BST."""
    return {"root": None, "size": 0}


def bst_insert(tree: dict, key, value) -> dict:
    """Insert a key-value pair."""
    def insert_node(node, key, value):
        if node is None:
            return create_bst_node(key, value, None, None)
        if key < node["key"]:
            return create_bst_node(node["key"], node["value"], insert_node(node["left"], key, value), node["right"])
        elif key > node["key"]:
            return create_bst_node(node["key"], node["value"], node["left"], insert_node(node["right"], key, value))
        else:
            return create_bst_node(key, value, node["left"], node["right"])
    return {"root": insert_node(tree["root"], key, value), "size": tree["size"] + 1}


def bst_search(tree: dict, key):
    """Search for a key."""
    def search_node(node, key):
        if node is None:
            return None
        if key == node["key"]:
            return node["value"]
        elif key < node["key"]:
            return search_node(node["left"], key)
        else:
            return search_node(node["right"], key)
    return search_node(tree["root"], key)


def bst_contains(tree: dict, key) -> bool:
    """Check if key exists."""
    return bst_search(tree, key) is not None


def bst_min(tree: dict):
    """Get minimum key."""
    if tree["root"] is None:
        return None
    node = tree["root"]
    while node["left"]:
        node = node["left"]
    return node["key"]


def bst_max(tree: dict):
    """Get maximum key."""
    if tree["root"] is None:
        return None
    node = tree["root"]
    while node["right"]:
        node = node["right"]
    return node["key"]


def bst_inorder(tree: dict) -> list:
    """Get keys in sorted order."""
    def inorder_node(node):
        if node is None:
            return []
        return inorder_node(node["left"]) + [node["key"]] + inorder_node(node["right"])
    return inorder_node(tree["root"])


def bst_preorder(tree: dict) -> list:
    """Get keys in preorder."""
    def preorder_node(node):
        if node is None:
            return []
        return [node["key"]] + preorder_node(node["left"]) + preorder_node(node["right"])
    return preorder_node(tree["root"])


def bst_postorder(tree: dict) -> list:
    """Get keys in postorder."""
    def postorder_node(node):
        if node is None:
            return []
        return postorder_node(node["left"]) + postorder_node(node["right"]) + [node["key"]]
    return postorder_node(tree["root"])


def bst_height(tree: dict) -> int:
    """Get tree height."""
    def height_node(node):
        if node is None:
            return 0
        return 1 + max(height_node(node["left"]), height_node(node["right"]))
    return height_node(tree["root"])


def bst_size(tree: dict) -> int:
    """Get tree size."""
    return tree["size"]


def bst_is_empty(tree: dict) -> bool:
    """Check if tree is empty."""
    return tree["root"] is None


def bst_delete_min(tree: dict) -> dict:
    """Delete minimum key."""
    def delete_min_node(node):
        if node is None:
            return None
        if node["left"] is None:
            return node["right"]
        return create_bst_node(node["key"], node["value"], delete_min_node(node["left"]), node["right"])
    if tree["root"] is None:
        return tree
    return {"root": delete_min_node(tree["root"]), "size": max(0, tree["size"] - 1)}


def bst_delete(tree: dict, key) -> dict:
    """Delete a key."""
    def min_node(node):
        while node["left"]:
            node = node["left"]
        return node
    def delete_node(node, key):
        if node is None:
            return None
        if key < node["key"]:
            return create_bst_node(node["key"], node["value"], delete_node(node["left"], key), node["right"])
        elif key > node["key"]:
            return create_bst_node(node["key"], node["value"], node["left"], delete_node(node["right"], key))
        else:
            if node["left"] is None:
                return node["right"]
            if node["right"] is None:
                return node["left"]
            successor = min_node(node["right"])
            return create_bst_node(successor["key"], successor["value"], node["left"], delete_node(node["right"], successor["key"]))
    if not bst_contains(tree, key):
        return tree
    return {"root": delete_node(tree["root"], key), "size": tree["size"] - 1}


def bst_floor(tree: dict, key):
    """Find largest key <= given key."""
    def floor_node(node, key):
        if node is None:
            return None
        if key == node["key"]:
            return node["key"]
        if key < node["key"]:
            return floor_node(node["left"], key)
        t = floor_node(node["right"], key)
        return t if t is not None else node["key"]
    return floor_node(tree["root"], key)


def bst_ceiling(tree: dict, key):
    """Find smallest key >= given key."""
    def ceiling_node(node, key):
        if node is None:
            return None
        if key == node["key"]:
            return node["key"]
        if key > node["key"]:
            return ceiling_node(node["right"], key)
        t = ceiling_node(node["left"], key)
        return t if t is not None else node["key"]
    return ceiling_node(tree["root"], key)


def bst_range(tree: dict, lo, hi) -> list:
    """Get keys in range [lo, hi]."""
    def range_node(node, lo, hi):
        if node is None:
            return []
        result = []
        if lo < node["key"]:
            result.extend(range_node(node["left"], lo, hi))
        if lo <= node["key"] <= hi:
            result.append(node["key"])
        if hi > node["key"]:
            result.extend(range_node(node["right"], lo, hi))
        return result
    return range_node(tree["root"], lo, hi)


def bst_rank(tree: dict, key) -> int:
    """Get number of keys less than given key."""
    def size_node(node):
        if node is None:
            return 0
        return 1 + size_node(node["left"]) + size_node(node["right"])
    def rank_node(node, key):
        if node is None:
            return 0
        if key < node["key"]:
            return rank_node(node["left"], key)
        elif key > node["key"]:
            return 1 + size_node(node["left"]) + rank_node(node["right"], key)
        else:
            return size_node(node["left"])
    return rank_node(tree["root"], key)


def bst_from_sorted(keys: list, values: list) -> dict:
    """Build balanced BST from sorted keys."""
    def build(left, right):
        if left > right:
            return None
        mid = (left + right) // 2
        return create_bst_node(keys[mid], values[mid], build(left, mid - 1), build(mid + 1, right))
    return {"root": build(0, len(keys) - 1), "size": len(keys)}


def bst_to_dict(tree: dict) -> dict:
    """Convert BST to dictionary."""
    result = {}
    def collect(node):
        if node:
            collect(node["left"])
            result[node["key"]] = node["value"]
            collect(node["right"])
    collect(tree["root"])
    return result


def bst_is_valid(tree: dict) -> bool:
    """Check if tree satisfies BST property."""
    def is_valid_node(node, min_key, max_key):
        if node is None:
            return True
        if min_key is not None and node["key"] <= min_key:
            return False
        if max_key is not None and node["key"] >= max_key:
            return False
        return is_valid_node(node["left"], min_key, node["key"]) and is_valid_node(node["right"], node["key"], max_key)
    return is_valid_node(tree["root"], None, None)
