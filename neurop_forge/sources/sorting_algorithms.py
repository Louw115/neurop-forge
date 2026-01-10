"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Sorting Algorithms - Pure functions for sorting.
All functions are pure, deterministic, and atomic.
"""

def bubble_sort(items: list) -> list:
    """Bubble sort algorithm."""
    result = list(items)
    n = len(result)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break
    return result


def insertion_sort(items: list) -> list:
    """Insertion sort algorithm."""
    result = list(items)
    for i in range(1, len(result)):
        key = result[i]
        j = i - 1
        while j >= 0 and result[j] > key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = key
    return result


def selection_sort(items: list) -> list:
    """Selection sort algorithm."""
    result = list(items)
    n = len(result)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if result[j] < result[min_idx]:
                min_idx = j
        result[i], result[min_idx] = result[min_idx], result[i]
    return result


def merge_sorted(left: list, right: list) -> list:
    """Merge two sorted lists."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(items: list) -> list:
    """Merge sort algorithm."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid])
    right = merge_sort(items[mid:])
    return merge_sorted(left, right)


def quick_sort(items: list) -> list:
    """Quick sort algorithm."""
    if len(items) <= 1:
        return list(items)
    pivot = items[len(items) // 2]
    left = [x for x in items if x < pivot]
    middle = [x for x in items if x == pivot]
    right = [x for x in items if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def heap_sort(items: list) -> list:
    """Heap sort algorithm."""
    def heapify(arr, n, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and arr[left] > arr[largest]:
            largest = left
        if right < n and arr[right] > arr[largest]:
            largest = right
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)
    result = list(items)
    n = len(result)
    for i in range(n // 2 - 1, -1, -1):
        heapify(result, n, i)
    for i in range(n - 1, 0, -1):
        result[0], result[i] = result[i], result[0]
        heapify(result, i, 0)
    return result


def counting_sort(items: list, max_value: int) -> list:
    """Counting sort for integers."""
    count = [0] * (max_value + 1)
    for item in items:
        count[item] += 1
    result = []
    for i in range(max_value + 1):
        result.extend([i] * count[i])
    return result


def radix_sort(items: list) -> list:
    """Radix sort for non-negative integers."""
    if not items:
        return []
    max_val = max(items)
    exp = 1
    result = list(items)
    while max_val // exp > 0:
        buckets = [[] for _ in range(10)]
        for item in result:
            buckets[(item // exp) % 10].append(item)
        result = []
        for bucket in buckets:
            result.extend(bucket)
        exp *= 10
    return result


def bucket_sort(items: list, num_buckets: int) -> list:
    """Bucket sort for floats in [0, 1)."""
    if not items:
        return []
    buckets = [[] for _ in range(num_buckets)]
    for item in items:
        idx = int(item * num_buckets)
        idx = min(idx, num_buckets - 1)
        buckets[idx].append(item)
    for bucket in buckets:
        bucket.sort()
    result = []
    for bucket in buckets:
        result.extend(bucket)
    return result


def is_sorted(items: list) -> bool:
    """Check if list is sorted."""
    return all(items[i] <= items[i + 1] for i in range(len(items) - 1))


def is_sorted_descending(items: list) -> bool:
    """Check if list is sorted in descending order."""
    return all(items[i] >= items[i + 1] for i in range(len(items) - 1))


def sort_descending(items: list) -> list:
    """Sort in descending order."""
    return sorted(items, reverse=True)


def partial_sort(items: list, k: int) -> list:
    """Get k smallest elements in sorted order."""
    return sorted(items)[:k]


def nth_element(items: list, n: int):
    """Find nth smallest element."""
    if n < 0 or n >= len(items):
        return None
    return sorted(items)[n]


def sort_by_key(items: list, key_fn) -> list:
    """Sort by key function."""
    return sorted(items, key=key_fn)


def stable_sort(items: list) -> list:
    """Stable sort (maintains relative order of equal elements)."""
    return sorted(items)


def sort_indices(items: list) -> list:
    """Get indices that would sort the list."""
    return sorted(range(len(items)), key=lambda i: items[i])


def argsort(items: list) -> list:
    """Return indices that would sort the array."""
    return sort_indices(items)


def rank_items(items: list) -> list:
    """Assign ranks to items (1-based)."""
    sorted_items = sorted(enumerate(items), key=lambda x: x[1])
    ranks = [0] * len(items)
    for rank, (idx, _) in enumerate(sorted_items, 1):
        ranks[idx] = rank
    return ranks


def inversion_count(items: list) -> int:
    """Count number of inversions."""
    count = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] > items[j]:
                count += 1
    return count


def three_way_partition(items: list, pivot) -> dict:
    """Three-way partition around pivot."""
    less = [x for x in items if x < pivot]
    equal = [x for x in items if x == pivot]
    greater = [x for x in items if x > pivot]
    return {"less": less, "equal": equal, "greater": greater}


def sort_nearly_sorted(items: list, k: int) -> list:
    """Sort nearly sorted array (elements at most k positions away)."""
    return sorted(items)
