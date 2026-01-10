"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Set Utilities - Pure functions for set operations.
All functions are pure, deterministic, and atomic.
"""

def set_union(set1: list, set2: list) -> list:
    """Union of two sets."""
    return list(set(set1) | set(set2))


def set_intersection(set1: list, set2: list) -> list:
    """Intersection of two sets."""
    return list(set(set1) & set(set2))


def set_difference(set1: list, set2: list) -> list:
    """Difference of two sets (set1 - set2)."""
    return list(set(set1) - set(set2))


def set_symmetric_difference(set1: list, set2: list) -> list:
    """Symmetric difference of two sets."""
    return list(set(set1) ^ set(set2))


def set_is_subset(subset: list, superset: list) -> bool:
    """Check if first set is subset of second."""
    return set(subset) <= set(superset)


def set_is_superset(superset: list, subset: list) -> bool:
    """Check if first set is superset of second."""
    return set(superset) >= set(subset)


def set_is_disjoint(set1: list, set2: list) -> bool:
    """Check if two sets are disjoint."""
    return set(set1).isdisjoint(set(set2))


def set_contains(items: list, element) -> bool:
    """Check if set contains element."""
    return element in items


def set_add(items: list, element) -> list:
    """Add element to set."""
    s = set(items)
    s.add(element)
    return list(s)


def set_remove(items: list, element) -> list:
    """Remove element from set."""
    s = set(items)
    s.discard(element)
    return list(s)


def set_toggle(items: list, element) -> list:
    """Toggle element in set."""
    s = set(items)
    if element in s:
        s.discard(element)
    else:
        s.add(element)
    return list(s)


def set_from_list(items: list) -> list:
    """Create set from list (deduplicate)."""
    return list(set(items))


def set_size(items: list) -> int:
    """Get number of unique elements."""
    return len(set(items))


def set_is_empty(items: list) -> bool:
    """Check if set is empty."""
    return len(items) == 0


def set_equals(set1: list, set2: list) -> bool:
    """Check if two sets are equal."""
    return set(set1) == set(set2)


def set_power_set(items: list) -> list:
    """Generate power set."""
    items = list(set(items))
    result = [[]]
    for item in items:
        result.extend([subset + [item] for subset in result])
    return result


def set_cartesian_product(set1: list, set2: list) -> list:
    """Cartesian product of two sets."""
    return [(a, b) for a in set1 for b in set2]


def set_union_all(sets: list) -> list:
    """Union of multiple sets."""
    result = set()
    for s in sets:
        result |= set(s)
    return list(result)


def set_intersection_all(sets: list) -> list:
    """Intersection of multiple sets."""
    if not sets:
        return []
    result = set(sets[0])
    for s in sets[1:]:
        result &= set(s)
    return list(result)


def set_jaccard_similarity(set1: list, set2: list) -> float:
    """Calculate Jaccard similarity coefficient."""
    s1, s2 = set(set1), set(set2)
    intersection = len(s1 & s2)
    union = len(s1 | s2)
    return intersection / union if union > 0 else 0.0


def set_jaccard_distance(set1: list, set2: list) -> float:
    """Calculate Jaccard distance."""
    return 1.0 - set_jaccard_similarity(set1, set2)


def set_overlap_coefficient(set1: list, set2: list) -> float:
    """Calculate overlap coefficient."""
    s1, s2 = set(set1), set(set2)
    intersection = len(s1 & s2)
    min_size = min(len(s1), len(s2))
    return intersection / min_size if min_size > 0 else 0.0


def set_dice_coefficient(set1: list, set2: list) -> float:
    """Calculate Dice coefficient."""
    s1, s2 = set(set1), set(set2)
    intersection = len(s1 & s2)
    total = len(s1) + len(s2)
    return 2 * intersection / total if total > 0 else 0.0


def set_min(items: list):
    """Get minimum element."""
    return min(items) if items else None


def set_max(items: list):
    """Get maximum element."""
    return max(items) if items else None


def set_pop(items: list) -> dict:
    """Remove and return arbitrary element."""
    if not items:
        return {"element": None, "remaining": []}
    s = list(items)
    element = s.pop()
    return {"element": element, "remaining": s}


def set_random_sample(items: list, n: int, seed: int) -> list:
    """Get random sample from set."""
    import hashlib
    items = list(set(items))
    if n >= len(items):
        return items
    result = []
    remaining = list(items)
    for i in range(n):
        h = hashlib.sha256(f"{seed}:{i}".encode()).digest()
        idx = int.from_bytes(h[:4], 'big') % len(remaining)
        result.append(remaining.pop(idx))
    return result


def set_partition(items: list, predicate) -> dict:
    """Partition set based on predicate."""
    items = list(set(items))
    true_set = []
    false_set = []
    for item in items:
        if predicate(item):
            true_set.append(item)
        else:
            false_set.append(item)
    return {"matches": true_set, "non_matches": false_set}


def set_map(items: list, transform) -> list:
    """Apply transformation to all elements."""
    return list(set(transform(item) for item in items))


def set_filter(items: list, predicate) -> list:
    """Filter set by predicate."""
    return list(set(item for item in items if predicate(item)))


def set_reduce(items: list, combine, initial):
    """Reduce set to single value."""
    result = initial
    for item in set(items):
        result = combine(result, item)
    return result


def set_to_sorted_list(items: list, reverse: bool) -> list:
    """Convert set to sorted list."""
    return sorted(set(items), reverse=reverse)


def multiset_count(items: list) -> dict:
    """Count occurrences in multiset."""
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def multiset_union(set1: list, set2: list) -> list:
    """Multiset union (max of counts)."""
    counts1 = multiset_count(set1)
    counts2 = multiset_count(set2)
    all_keys = set(counts1.keys()) | set(counts2.keys())
    result = []
    for key in all_keys:
        count = max(counts1.get(key, 0), counts2.get(key, 0))
        result.extend([key] * count)
    return result


def multiset_intersection(set1: list, set2: list) -> list:
    """Multiset intersection (min of counts)."""
    counts1 = multiset_count(set1)
    counts2 = multiset_count(set2)
    result = []
    for key in counts1:
        if key in counts2:
            count = min(counts1[key], counts2[key])
            result.extend([key] * count)
    return result
