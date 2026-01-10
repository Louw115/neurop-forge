"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Array Algorithms - Pure functions for array manipulation algorithms.
All functions are pure, deterministic, and atomic.
"""

def rotate_left(arr: list, k: int) -> list:
    """Rotate array left by k positions."""
    if not arr:
        return []
    k = k % len(arr)
    return arr[k:] + arr[:k]


def rotate_right(arr: list, k: int) -> list:
    """Rotate array right by k positions."""
    if not arr:
        return []
    k = k % len(arr)
    return arr[-k:] + arr[:-k]


def reverse(arr: list) -> list:
    """Reverse array."""
    return arr[::-1]


def reverse_range(arr: list, start: int, end: int) -> list:
    """Reverse portion of array."""
    result = list(arr)
    result[start:end+1] = result[start:end+1][::-1]
    return result


def shuffle_deterministic(arr: list, seed: int) -> list:
    """Deterministic shuffle using seed."""
    import hashlib
    result = list(arr)
    n = len(result)
    for i in range(n - 1, 0, -1):
        h = hashlib.sha256(f"{seed}-{i}".encode()).digest()
        j = h[0] % (i + 1)
        result[i], result[j] = result[j], result[i]
    return result


def partition(arr: list, predicate) -> dict:
    """Partition array by predicate."""
    true_arr = []
    false_arr = []
    for item in arr:
        if predicate(item):
            true_arr.append(item)
        else:
            false_arr.append(item)
    return {"true": true_arr, "false": false_arr}


def chunk(arr: list, size: int) -> list:
    """Split array into chunks."""
    return [arr[i:i+size] for i in range(0, len(arr), size)]


def flatten(arr: list) -> list:
    """Flatten nested array one level."""
    result = []
    for item in arr:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result


def deep_flatten(arr: list) -> list:
    """Recursively flatten nested array."""
    result = []
    for item in arr:
        if isinstance(item, list):
            result.extend(deep_flatten(item))
        else:
            result.append(item)
    return result


def unique(arr: list) -> list:
    """Get unique elements preserving order."""
    seen = set()
    result = []
    for item in arr:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def union(arr1: list, arr2: list) -> list:
    """Union of two arrays."""
    return unique(arr1 + arr2)


def intersection(arr1: list, arr2: list) -> list:
    """Intersection of two arrays."""
    set2 = set(arr2)
    return unique([x for x in arr1 if x in set2])


def difference(arr1: list, arr2: list) -> list:
    """Elements in arr1 not in arr2."""
    set2 = set(arr2)
    return [x for x in arr1 if x not in set2]


def symmetric_difference(arr1: list, arr2: list) -> list:
    """Elements in either but not both."""
    set1 = set(arr1)
    set2 = set(arr2)
    return list((set1 - set2) | (set2 - set1))


def zip_arrays(arr1: list, arr2: list) -> list:
    """Zip two arrays into pairs."""
    return list(zip(arr1, arr2))


def unzip_pairs(pairs: list) -> dict:
    """Unzip pairs into two arrays."""
    return {
        "first": [p[0] for p in pairs],
        "second": [p[1] for p in pairs]
    }


def interleave(arr1: list, arr2: list) -> list:
    """Interleave two arrays."""
    result = []
    for i in range(max(len(arr1), len(arr2))):
        if i < len(arr1):
            result.append(arr1[i])
        if i < len(arr2):
            result.append(arr2[i])
    return result


def compact(arr: list) -> list:
    """Remove None and empty values."""
    return [x for x in arr if x is not None and x != ""]


def take(arr: list, n: int) -> list:
    """Take first n elements."""
    return arr[:n]


def take_right(arr: list, n: int) -> list:
    """Take last n elements."""
    return arr[-n:] if n > 0 else []


def drop(arr: list, n: int) -> list:
    """Drop first n elements."""
    return arr[n:]


def drop_right(arr: list, n: int) -> list:
    """Drop last n elements."""
    return arr[:-n] if n > 0 else arr


def sample(arr: list, n: int, seed: int) -> list:
    """Sample n elements deterministically."""
    shuffled = shuffle_deterministic(arr, seed)
    return shuffled[:n]


def sliding_window(arr: list, size: int) -> list:
    """Generate sliding windows."""
    return [arr[i:i+size] for i in range(len(arr) - size + 1)]


def pairs(arr: list) -> list:
    """Generate consecutive pairs."""
    return [(arr[i], arr[i+1]) for i in range(len(arr) - 1)]


def group_consecutive(arr: list) -> list:
    """Group consecutive equal elements."""
    if not arr:
        return []
    groups = []
    current = [arr[0]]
    for item in arr[1:]:
        if item == current[-1]:
            current.append(item)
        else:
            groups.append(current)
            current = [item]
    groups.append(current)
    return groups


def run_length_encode(arr: list) -> list:
    """Run-length encode array."""
    if not arr:
        return []
    result = []
    current = arr[0]
    count = 1
    for item in arr[1:]:
        if item == current:
            count += 1
        else:
            result.append({"value": current, "count": count})
            current = item
            count = 1
    result.append({"value": current, "count": count})
    return result


def run_length_decode(encoded: list) -> list:
    """Decode run-length encoded array."""
    result = []
    for item in encoded:
        result.extend([item["value"]] * item["count"])
    return result


def max_subarray_sum(arr: list) -> dict:
    """Find maximum subarray sum (Kadane's algorithm)."""
    if not arr:
        return {"sum": 0, "start": -1, "end": -1}
    max_sum = arr[0]
    current_sum = arr[0]
    start = end = temp_start = 0
    for i in range(1, len(arr)):
        if current_sum + arr[i] < arr[i]:
            current_sum = arr[i]
            temp_start = i
        else:
            current_sum += arr[i]
        if current_sum > max_sum:
            max_sum = current_sum
            start = temp_start
            end = i
    return {"sum": max_sum, "start": start, "end": end}


def two_sum(arr: list, target: int) -> list:
    """Find two indices that sum to target."""
    seen = {}
    for i, num in enumerate(arr):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []


def find_duplicates(arr: list) -> list:
    """Find all duplicate elements."""
    seen = set()
    duplicates = set()
    for item in arr:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)


def remove_duplicates_sorted(arr: list) -> list:
    """Remove duplicates from sorted array."""
    if not arr:
        return []
    result = [arr[0]]
    for item in arr[1:]:
        if item != result[-1]:
            result.append(item)
    return result
