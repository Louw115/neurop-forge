"""
List/Collection Operations - Pure functions for list manipulation.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def get_first(items: list):
    """Get the first element of a list. Returns None if empty."""
    if not items:
        return None
    return items[0]


def get_last(items: list):
    """Get the last element of a list. Returns None if empty."""
    if not items:
        return None
    return items[-1]


def get_at_index(items: list, index: int):
    """Get the element at a specific index. Returns None if out of bounds."""
    if index < 0 or index >= len(items):
        return None
    return items[index]


def take_first_n(items: list, n: int) -> list:
    """Take the first n elements from a list."""
    if n < 0:
        return []
    return items[:n]


def take_last_n(items: list, n: int) -> list:
    """Take the last n elements from a list."""
    if n < 0:
        return []
    return items[-n:] if n > 0 else []


def drop_first_n(items: list, n: int) -> list:
    """Drop the first n elements from a list."""
    if n < 0:
        return items[:]
    return items[n:]


def drop_last_n(items: list, n: int) -> list:
    """Drop the last n elements from a list."""
    if n <= 0:
        return items[:]
    return items[:-n]


def list_length(items: list) -> int:
    """Return the length of a list."""
    return len(items)


def is_empty_list(items: list) -> bool:
    """Check if a list is empty."""
    return len(items) == 0


def reverse_list(items: list) -> list:
    """Reverse the order of elements in a list."""
    return items[::-1]


def flatten_list(nested: list) -> list:
    """Flatten a nested list by one level."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result


def flatten_deep(nested: list) -> list:
    """Recursively flatten a deeply nested list."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten_deep(item))
        else:
            result.append(item)
    return result


def unique_elements(items: list) -> list:
    """Return a list with duplicate elements removed, preserving order."""
    seen = set()
    result = []
    for item in items:
        key = item if not isinstance(item, list) else tuple(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def concatenate_lists(list_a: list, list_b: list) -> list:
    """Concatenate two lists into a new list."""
    return list_a + list_b


def chunk_list(items: list, chunk_size: int) -> list:
    """Split a list into chunks of specified size."""
    if chunk_size <= 0:
        return []
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def zip_lists(list_a: list, list_b: list) -> list:
    """Zip two lists into a list of pairs."""
    return list(zip(list_a, list_b))


def unzip_pairs(pairs: list) -> tuple:
    """Unzip a list of pairs into two separate lists."""
    if not pairs:
        return ([], [])
    list_a = [pair[0] for pair in pairs if len(pair) >= 1]
    list_b = [pair[1] for pair in pairs if len(pair) >= 2]
    return (list_a, list_b)


def contains_element(items: list, element) -> bool:
    """Check if a list contains a specific element."""
    return element in items


def index_of_element(items: list, element) -> int:
    """Find the index of the first occurrence of an element. Returns -1 if not found."""
    try:
        return items.index(element)
    except ValueError:
        return -1


def count_element(items: list, element) -> int:
    """Count occurrences of an element in a list."""
    return items.count(element)


def filter_none_values(items: list) -> list:
    """Remove None values from a list."""
    return [item for item in items if item is not None]


def filter_empty_strings(items: list) -> list:
    """Remove empty strings from a list."""
    return [item for item in items if item != ""]


def sort_ascending(items: list) -> list:
    """Sort a list in ascending order."""
    return sorted(items)


def sort_descending(items: list) -> list:
    """Sort a list in descending order."""
    return sorted(items, reverse=True)


def sum_numbers(items: list) -> float:
    """Sum all numeric values in a list."""
    return sum(item for item in items if isinstance(item, (int, float)))


def product_numbers(items: list) -> float:
    """Calculate the product of all numeric values in a list."""
    result = 1
    for item in items:
        if isinstance(item, (int, float)):
            result *= item
    return result


def min_value(items: list):
    """Find the minimum value in a list. Returns None if empty."""
    if not items:
        return None
    return min(items)


def max_value(items: list):
    """Find the maximum value in a list. Returns None if empty."""
    if not items:
        return None
    return max(items)


def average_value(items: list) -> float:
    """Calculate the average of numeric values in a list."""
    numbers = [item for item in items if isinstance(item, (int, float))]
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def partition_list(items: list, pivot_index: int) -> tuple:
    """Partition a list into two parts at the given index."""
    return (items[:pivot_index], items[pivot_index:])


def interleave_lists(list_a: list, list_b: list) -> list:
    """Interleave elements from two lists."""
    result = []
    max_len = max(len(list_a), len(list_b))
    for i in range(max_len):
        if i < len(list_a):
            result.append(list_a[i])
        if i < len(list_b):
            result.append(list_b[i])
    return result
