"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Functional Utilities - Pure functions for functional programming patterns.
All functions are pure, deterministic, and atomic.
"""

def identity(x):
    """Identity function."""
    return x


def constant(value):
    """Create a function that always returns the same value."""
    def fn(*args):
        return value
    return fn


def compose(*functions):
    """Compose functions (right to left)."""
    def composed(x):
        result = x
        for fn in reversed(functions):
            result = fn(result)
        return result
    return composed


def pipe(*functions):
    """Pipe functions (left to right)."""
    def piped(x):
        result = x
        for fn in functions:
            result = fn(result)
        return result
    return piped


def curry2(fn):
    """Curry a 2-argument function."""
    def curried(a):
        def inner(b):
            return fn(a, b)
        return inner
    return curried


def partial(fn, *args):
    """Partially apply a function."""
    def applied(*more_args):
        return fn(*args, *more_args)
    return applied


def flip(fn):
    """Flip first two arguments of a function."""
    def flipped(a, b, *args):
        return fn(b, a, *args)
    return flipped


def memoize_result(fn, args_tuple, cache: dict) -> dict:
    """Memoize function result (returns updated cache)."""
    if args_tuple in cache:
        return {"result": cache[args_tuple], "cache": cache}
    result = fn(*args_tuple)
    new_cache = dict(cache)
    new_cache[args_tuple] = result
    return {"result": result, "cache": new_cache}


def map_fn(fn, items: list) -> list:
    """Map function over list."""
    return [fn(item) for item in items]


def filter_fn(predicate, items: list) -> list:
    """Filter list by predicate."""
    return [item for item in items if predicate(item)]


def reduce_fn(fn, items: list, initial):
    """Reduce list to single value."""
    result = initial
    for item in items:
        result = fn(result, item)
    return result


def flatmap(fn, items: list) -> list:
    """Map and flatten."""
    result = []
    for item in items:
        result.extend(fn(item))
    return result


def zip_with(fn, list1: list, list2: list) -> list:
    """Zip lists with function."""
    return [fn(a, b) for a, b in zip(list1, list2)]


def unzip(pairs: list) -> tuple:
    """Unzip list of pairs."""
    if not pairs:
        return ([], [])
    return (
        [p[0] for p in pairs],
        [p[1] for p in pairs]
    )


def take_while(predicate, items: list) -> list:
    """Take items while predicate is true."""
    result = []
    for item in items:
        if not predicate(item):
            break
        result.append(item)
    return result


def drop_while(predicate, items: list) -> list:
    """Drop items while predicate is true."""
    i = 0
    for item in items:
        if not predicate(item):
            break
        i += 1
    return items[i:]


def partition_by(predicate, items: list) -> dict:
    """Partition items by predicate."""
    true_items = []
    false_items = []
    for item in items:
        if predicate(item):
            true_items.append(item)
        else:
            false_items.append(item)
    return {"true": true_items, "false": false_items}


def group_by(key_fn, items: list) -> dict:
    """Group items by key function."""
    groups = {}
    for item in items:
        key = key_fn(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups


def unique_by(key_fn, items: list) -> list:
    """Get unique items by key function."""
    seen = set()
    result = []
    for item in items:
        key = key_fn(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def count_by(key_fn, items: list) -> dict:
    """Count items by key function."""
    counts = {}
    for item in items:
        key = key_fn(item)
        counts[key] = counts.get(key, 0) + 1
    return counts


def find_first(predicate, items: list):
    """Find first item matching predicate."""
    for item in items:
        if predicate(item):
            return item
    return None


def find_last(predicate, items: list):
    """Find last item matching predicate."""
    result = None
    for item in items:
        if predicate(item):
            result = item
    return result


def all_match(predicate, items: list) -> bool:
    """Check if all items match predicate."""
    return all(predicate(item) for item in items)


def any_match(predicate, items: list) -> bool:
    """Check if any item matches predicate."""
    return any(predicate(item) for item in items)


def none_match(predicate, items: list) -> bool:
    """Check if no items match predicate."""
    return not any(predicate(item) for item in items)


def max_by(key_fn, items: list):
    """Find item with maximum key."""
    if not items:
        return None
    return max(items, key=key_fn)


def min_by(key_fn, items: list):
    """Find item with minimum key."""
    if not items:
        return None
    return min(items, key=key_fn)


def sort_by(key_fn, items: list, reverse: bool) -> list:
    """Sort items by key function."""
    return sorted(items, key=key_fn, reverse=reverse)


def index_of(predicate, items: list) -> int:
    """Find index of first matching item."""
    for i, item in enumerate(items):
        if predicate(item):
            return i
    return -1


def scan(fn, items: list, initial) -> list:
    """Cumulative reduce (like reduce but returns all intermediate values)."""
    result = [initial]
    current = initial
    for item in items:
        current = fn(current, item)
        result.append(current)
    return result
