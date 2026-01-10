"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Iterator Utilities - Pure functions for iterator operations.
All functions are pure, deterministic, and atomic.
"""

def take(items: list, n: int) -> list:
    """Take first n items."""
    return items[:n]


def take_while(items: list, predicate) -> list:
    """Take items while predicate is true."""
    result = []
    for item in items:
        if predicate(item):
            result.append(item)
        else:
            break
    return result


def drop(items: list, n: int) -> list:
    """Drop first n items."""
    return items[n:]


def drop_while(items: list, predicate) -> list:
    """Drop items while predicate is true."""
    for i, item in enumerate(items):
        if not predicate(item):
            return items[i:]
    return []


def filter_items(items: list, predicate) -> list:
    """Filter items by predicate."""
    return [item for item in items if predicate(item)]


def reject_items(items: list, predicate) -> list:
    """Reject items matching predicate."""
    return [item for item in items if not predicate(item)]


def map_items(items: list, mapper) -> list:
    """Map function over items."""
    return [mapper(item) for item in items]


def flat_map(items: list, mapper) -> list:
    """Map and flatten results."""
    result = []
    for item in items:
        result.extend(mapper(item))
    return result


def reduce_items(items: list, reducer, initial):
    """Reduce items to single value."""
    result = initial
    for item in items:
        result = reducer(result, item)
    return result


def scan(items: list, reducer, initial) -> list:
    """Like reduce but returns all intermediate values."""
    result = [initial]
    current = initial
    for item in items:
        current = reducer(current, item)
        result.append(current)
    return result


def zip_with(items1: list, items2: list, combiner) -> list:
    """Zip with custom combiner function."""
    return [combiner(a, b) for a, b in zip(items1, items2)]


def enumerate_items(items: list, start: int) -> list:
    """Enumerate items with index."""
    return [(start + i, item) for i, item in enumerate(items)]


def cycle(items: list, times: int) -> list:
    """Cycle through items n times."""
    return items * times


def repeat_item(item, times: int) -> list:
    """Repeat single item n times."""
    return [item] * times


def range_list(start: int, end: int, step: int) -> list:
    """Generate range as list."""
    return list(range(start, end, step))


def chunk(items: list, size: int) -> list:
    """Split into chunks of size."""
    return [items[i:i+size] for i in range(0, len(items), size)]


def window(items: list, size: int) -> list:
    """Sliding window over items."""
    return [items[i:i+size] for i in range(len(items) - size + 1)]


def pairwise(items: list) -> list:
    """Get consecutive pairs."""
    return [(items[i], items[i+1]) for i in range(len(items) - 1)]


def group_by(items: list, key_fn) -> dict:
    """Group items by key function."""
    groups = {}
    for item in items:
        key = key_fn(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups


def partition(items: list, predicate) -> dict:
    """Partition items by predicate."""
    true_items = []
    false_items = []
    for item in items:
        if predicate(item):
            true_items.append(item)
        else:
            false_items.append(item)
    return {"true": true_items, "false": false_items}


def interleave(items1: list, items2: list) -> list:
    """Interleave two lists."""
    result = []
    for a, b in zip(items1, items2):
        result.extend([a, b])
    longer = items1 if len(items1) > len(items2) else items2
    result.extend(longer[min(len(items1), len(items2)):])
    return result


def deduplicate(items: list) -> list:
    """Remove duplicates preserving order."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def deduplicate_by(items: list, key_fn) -> list:
    """Remove duplicates by key function."""
    seen = set()
    result = []
    for item in items:
        key = key_fn(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def sort_by(items: list, key_fn, reverse: bool) -> list:
    """Sort items by key function."""
    return sorted(items, key=key_fn, reverse=reverse)


def find_first(items: list, predicate):
    """Find first matching item."""
    for item in items:
        if predicate(item):
            return item
    return None


def find_last(items: list, predicate):
    """Find last matching item."""
    for item in reversed(items):
        if predicate(item):
            return item
    return None


def find_index(items: list, predicate) -> int:
    """Find index of first matching item."""
    for i, item in enumerate(items):
        if predicate(item):
            return i
    return -1


def count_by(items: list, key_fn) -> dict:
    """Count items by key function."""
    counts = {}
    for item in items:
        key = key_fn(item)
        counts[key] = counts.get(key, 0) + 1
    return counts


def max_by(items: list, key_fn):
    """Find max item by key function."""
    if not items:
        return None
    return max(items, key=key_fn)


def min_by(items: list, key_fn):
    """Find min item by key function."""
    if not items:
        return None
    return min(items, key=key_fn)


def frequencies(items: list) -> dict:
    """Get frequency of each item."""
    freq = {}
    for item in items:
        freq[item] = freq.get(item, 0) + 1
    return freq
