"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Disjoint Set (Union-Find) - Pure functions for disjoint set operations.
All functions are pure, deterministic, and atomic.
"""

def create_disjoint_set(elements: list) -> dict:
    """Create disjoint set from elements."""
    return {
        "parent": {e: e for e in elements},
        "rank": {e: 0 for e in elements},
        "size": {e: 1 for e in elements},
        "count": len(elements)
    }


def find_root(ds: dict, element) -> tuple:
    """Find root of element with path compression."""
    parent = dict(ds["parent"])
    root = element
    path = []
    while parent[root] != root:
        path.append(root)
        root = parent[root]
    for node in path:
        parent[node] = root
    return (root, {**ds, "parent": parent})


def union(ds: dict, a, b) -> dict:
    """Union two sets by rank."""
    root_a, ds = find_root(ds, a)
    root_b, ds = find_root(ds, b)
    if root_a == root_b:
        return ds
    rank = dict(ds["rank"])
    parent = dict(ds["parent"])
    size = dict(ds["size"])
    if rank[root_a] < rank[root_b]:
        parent[root_a] = root_b
        size[root_b] += size[root_a]
    elif rank[root_a] > rank[root_b]:
        parent[root_b] = root_a
        size[root_a] += size[root_b]
    else:
        parent[root_b] = root_a
        rank[root_a] += 1
        size[root_a] += size[root_b]
    return {
        "parent": parent,
        "rank": rank,
        "size": size,
        "count": ds["count"] - 1
    }


def connected(ds: dict, a, b) -> tuple:
    """Check if two elements are connected."""
    root_a, ds = find_root(ds, a)
    root_b, ds = find_root(ds, b)
    return (root_a == root_b, ds)


def set_count(ds: dict) -> int:
    """Get number of disjoint sets."""
    return ds["count"]


def set_size_of(ds: dict, element) -> int:
    """Get size of set containing element."""
    root, ds = find_root(ds, element)
    return ds["size"].get(root, 0)


def get_components(ds: dict) -> dict:
    """Get all components as lists."""
    components = {}
    for element in ds["parent"]:
        root, ds = find_root(ds, element)
        if root not in components:
            components[root] = []
        components[root].append(element)
    return components


def get_component(ds: dict, element) -> list:
    """Get all elements in same component."""
    root, ds = find_root(ds, element)
    return [e for e in ds["parent"] if find_root(ds, e)[0] == root]


def is_singleton(ds: dict, element) -> bool:
    """Check if element is in singleton set."""
    return set_size_of(ds, element) == 1


def add_element(ds: dict, element) -> dict:
    """Add new element as singleton."""
    if element in ds["parent"]:
        return ds
    return {
        "parent": {**ds["parent"], element: element},
        "rank": {**ds["rank"], element: 0},
        "size": {**ds["size"], element: 1},
        "count": ds["count"] + 1
    }


def remove_element(ds: dict, element) -> dict:
    """Remove element from its set."""
    if element not in ds["parent"]:
        return ds
    root, ds = find_root(ds, element)
    if root == element:
        return ds
    parent = dict(ds["parent"])
    del parent[element]
    size = dict(ds["size"])
    size[root] -= 1
    rank = dict(ds["rank"])
    if element in rank:
        del rank[element]
    if element in size:
        del size[element]
    return {
        "parent": parent,
        "rank": rank,
        "size": size,
        "count": ds["count"]
    }


def get_roots(ds: dict) -> list:
    """Get all root elements."""
    return [e for e, p in ds["parent"].items() if e == p]


def largest_component_size(ds: dict) -> int:
    """Get size of largest component."""
    roots = get_roots(ds)
    if not roots:
        return 0
    return max(ds["size"].get(r, 0) for r in roots)


def smallest_component_size(ds: dict) -> int:
    """Get size of smallest component."""
    roots = get_roots(ds)
    if not roots:
        return 0
    return min(ds["size"].get(r, 0) for r in roots)


def component_sizes(ds: dict) -> list:
    """Get sorted list of component sizes."""
    return sorted([ds["size"].get(r, 0) for r in get_roots(ds)], reverse=True)


def are_all_connected(ds: dict) -> bool:
    """Check if all elements are in one component."""
    return ds["count"] == 1


def merge_sets(ds1: dict, ds2: dict) -> dict:
    """Merge two disjoint set structures."""
    result = ds1
    for element in ds2["parent"]:
        result = add_element(result, element)
    components = get_components(ds2)
    for root, members in components.items():
        for i in range(1, len(members)):
            result = union(result, members[0], members[i])
    return result


def reset_element(ds: dict, element) -> dict:
    """Reset element to be its own singleton."""
    if element not in ds["parent"]:
        return add_element(ds, element)
    parent = dict(ds["parent"])
    parent[element] = element
    rank = dict(ds["rank"])
    rank[element] = 0
    size = dict(ds["size"])
    size[element] = 1
    return {
        "parent": parent,
        "rank": rank,
        "size": size,
        "count": ds["count"] + 1
    }


def element_count(ds: dict) -> int:
    """Get total number of elements."""
    return len(ds["parent"])


def has_element(ds: dict, element) -> bool:
    """Check if element exists in set."""
    return element in ds["parent"]


def to_adjacency(ds: dict) -> dict:
    """Convert to adjacency representation."""
    components = get_components(ds)
    adjacency = {e: [] for e in ds["parent"]}
    for members in components.values():
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                adjacency[a].append(b)
                adjacency[b].append(a)
    return adjacency
