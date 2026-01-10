"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Tree Utilities - Pure functions for tree data structures.
All functions are pure, deterministic, and atomic.
"""

def create_tree_node(node_id: str, value, children: list) -> dict:
    """Create a tree node."""
    return {
        "id": node_id,
        "value": value,
        "children": list(children)
    }


def create_leaf_node(node_id: str, value) -> dict:
    """Create a leaf node."""
    return create_tree_node(node_id, value, [])


def is_leaf(node: dict) -> bool:
    """Check if node is a leaf."""
    return len(node.get("children", [])) == 0


def add_child(parent: dict, child: dict) -> dict:
    """Add a child to a parent node."""
    result = dict(parent)
    result["children"] = list(parent.get("children", []))
    result["children"].append(child)
    return result


def remove_child(parent: dict, child_id: str) -> dict:
    """Remove a child by ID."""
    result = dict(parent)
    result["children"] = [c for c in parent.get("children", []) if c.get("id") != child_id]
    return result


def find_node(root: dict, node_id: str) -> dict:
    """Find a node by ID in tree."""
    if root.get("id") == node_id:
        return root
    for child in root.get("children", []):
        found = find_node(child, node_id)
        if found:
            return found
    return None


def get_node_path(root: dict, node_id: str) -> list:
    """Get path from root to node."""
    if root.get("id") == node_id:
        return [node_id]
    for child in root.get("children", []):
        path = get_node_path(child, node_id)
        if path:
            return [root["id"]] + path
    return []


def get_depth(root: dict, node_id: str) -> int:
    """Get depth of a node in tree."""
    path = get_node_path(root, node_id)
    return len(path) - 1 if path else -1


def tree_height(node: dict) -> int:
    """Calculate height of tree."""
    if is_leaf(node):
        return 0
    return 1 + max(tree_height(c) for c in node.get("children", []))


def count_nodes(node: dict) -> int:
    """Count total nodes in tree."""
    return 1 + sum(count_nodes(c) for c in node.get("children", []))


def count_leaves(node: dict) -> int:
    """Count leaf nodes in tree."""
    if is_leaf(node):
        return 1
    return sum(count_leaves(c) for c in node.get("children", []))


def get_leaves(node: dict) -> list:
    """Get all leaf nodes."""
    if is_leaf(node):
        return [node]
    leaves = []
    for child in node.get("children", []):
        leaves.extend(get_leaves(child))
    return leaves


def traverse_preorder(node: dict) -> list:
    """Traverse tree in pre-order."""
    result = [node]
    for child in node.get("children", []):
        result.extend(traverse_preorder(child))
    return result


def traverse_postorder(node: dict) -> list:
    """Traverse tree in post-order."""
    result = []
    for child in node.get("children", []):
        result.extend(traverse_postorder(child))
    result.append(node)
    return result


def traverse_level_order(root: dict) -> list:
    """Traverse tree in level-order (BFS)."""
    result = []
    queue = [root]
    while queue:
        node = queue.pop(0)
        result.append(node)
        queue.extend(node.get("children", []))
    return result


def get_level_nodes(root: dict, level: int) -> list:
    """Get all nodes at a specific level."""
    if level == 0:
        return [root]
    nodes = []
    for child in root.get("children", []):
        nodes.extend(get_level_nodes(child, level - 1))
    return nodes


def map_tree(node: dict, transform) -> dict:
    """Apply transformation to all node values."""
    result = dict(node)
    result["value"] = transform(node["value"])
    result["children"] = [map_tree(c, transform) for c in node.get("children", [])]
    return result


def filter_tree(node: dict, predicate) -> dict:
    """Filter tree nodes by predicate."""
    if not predicate(node):
        return None
    result = dict(node)
    result["children"] = []
    for child in node.get("children", []):
        filtered = filter_tree(child, predicate)
        if filtered:
            result["children"].append(filtered)
    return result


def fold_tree(node: dict, combine, initial):
    """Fold tree to single value."""
    value = combine(initial, node["value"])
    for child in node.get("children", []):
        value = fold_tree(child, combine, value)
    return value


def collect_values(node: dict) -> list:
    """Collect all values in tree."""
    return [n["value"] for n in traverse_preorder(node)]


def tree_to_flat_list(node: dict, parent_id: str) -> list:
    """Convert tree to flat list with parent references."""
    result = [{"id": node["id"], "value": node["value"], "parent_id": parent_id}]
    for child in node.get("children", []):
        result.extend(tree_to_flat_list(child, node["id"]))
    return result


def flat_list_to_tree(items: list, id_field: str, parent_field: str) -> list:
    """Convert flat list to tree structure."""
    by_id = {item[id_field]: dict(item) for item in items}
    for item in by_id.values():
        item["children"] = []
    roots = []
    for item in by_id.values():
        parent_id = item.get(parent_field)
        if parent_id and parent_id in by_id:
            by_id[parent_id]["children"].append(item)
        else:
            roots.append(item)
    return roots


def get_ancestors(root: dict, node_id: str) -> list:
    """Get all ancestor nodes."""
    path = get_node_path(root, node_id)
    if len(path) <= 1:
        return []
    ancestors = []
    current = root
    for p in path[:-1]:
        if current["id"] == p:
            ancestors.append(current)
        for child in current.get("children", []):
            if child["id"] in path:
                current = child
                break
    return ancestors


def get_siblings(root: dict, node_id: str) -> list:
    """Get sibling nodes."""
    path = get_node_path(root, node_id)
    if len(path) <= 1:
        return []
    parent_id = path[-2]
    parent = find_node(root, parent_id)
    return [c for c in parent.get("children", []) if c["id"] != node_id]


def get_descendants(node: dict) -> list:
    """Get all descendant nodes."""
    result = []
    for child in node.get("children", []):
        result.append(child)
        result.extend(get_descendants(child))
    return result


def prune_at_depth(node: dict, max_depth: int) -> dict:
    """Prune tree at maximum depth."""
    if max_depth <= 0:
        result = dict(node)
        result["children"] = []
        return result
    result = dict(node)
    result["children"] = [prune_at_depth(c, max_depth - 1) for c in node.get("children", [])]
    return result
