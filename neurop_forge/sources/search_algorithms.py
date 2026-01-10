"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Search Algorithms - Pure functions for searching.
All functions are pure, deterministic, and atomic.
"""

def linear_search(items: list, target) -> int:
    """Linear search - returns index or -1."""
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1


def binary_search(items: list, target) -> int:
    """Binary search on sorted list - returns index or -1."""
    left, right = 0, len(items) - 1
    while left <= right:
        mid = (left + right) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def binary_search_leftmost(items: list, target) -> int:
    """Find leftmost occurrence of target."""
    left, right = 0, len(items)
    while left < right:
        mid = (left + right) // 2
        if items[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left if left < len(items) and items[left] == target else -1


def binary_search_rightmost(items: list, target) -> int:
    """Find rightmost occurrence of target."""
    left, right = 0, len(items)
    while left < right:
        mid = (left + right) // 2
        if items[mid] <= target:
            left = mid + 1
        else:
            right = mid
    return left - 1 if left > 0 and items[left - 1] == target else -1


def lower_bound(items: list, target) -> int:
    """Find first position where target could be inserted."""
    left, right = 0, len(items)
    while left < right:
        mid = (left + right) // 2
        if items[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


def upper_bound(items: list, target) -> int:
    """Find last position where target could be inserted."""
    left, right = 0, len(items)
    while left < right:
        mid = (left + right) // 2
        if items[mid] <= target:
            left = mid + 1
        else:
            right = mid
    return left


def interpolation_search(items: list, target) -> int:
    """Interpolation search for uniformly distributed sorted list."""
    low, high = 0, len(items) - 1
    while low <= high and items[low] <= target <= items[high]:
        if items[low] == items[high]:
            return low if items[low] == target else -1
        pos = low + int(((target - items[low]) * (high - low)) / (items[high] - items[low]))
        if items[pos] == target:
            return pos
        elif items[pos] < target:
            low = pos + 1
        else:
            high = pos - 1
    return -1


def exponential_search(items: list, target) -> int:
    """Exponential search - good for unbounded lists."""
    if not items:
        return -1
    if items[0] == target:
        return 0
    bound = 1
    while bound < len(items) and items[bound] <= target:
        bound *= 2
    left = bound // 2
    right = min(bound, len(items) - 1)
    while left <= right:
        mid = (left + right) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def jump_search(items: list, target) -> int:
    """Jump search on sorted list."""
    import math
    n = len(items)
    step = int(math.sqrt(n))
    prev = 0
    while items[min(step, n) - 1] < target:
        prev = step
        step += int(math.sqrt(n))
        if prev >= n:
            return -1
    for i in range(prev, min(step, n)):
        if items[i] == target:
            return i
    return -1


def ternary_search(items: list, target) -> int:
    """Ternary search on sorted list."""
    left, right = 0, len(items) - 1
    while left <= right:
        mid1 = left + (right - left) // 3
        mid2 = right - (right - left) // 3
        if items[mid1] == target:
            return mid1
        if items[mid2] == target:
            return mid2
        if target < items[mid1]:
            right = mid1 - 1
        elif target > items[mid2]:
            left = mid2 + 1
        else:
            left = mid1 + 1
            right = mid2 - 1
    return -1


def find_first(items: list, predicate) -> int:
    """Find first item matching predicate."""
    for i, item in enumerate(items):
        if predicate(item):
            return i
    return -1


def find_last(items: list, predicate) -> int:
    """Find last item matching predicate."""
    result = -1
    for i, item in enumerate(items):
        if predicate(item):
            result = i
    return result


def find_all_indices(items: list, target) -> list:
    """Find all indices of target."""
    return [i for i, item in enumerate(items) if item == target]


def count_occurrences(items: list, target) -> int:
    """Count occurrences of target."""
    return sum(1 for item in items if item == target)


def find_peak(items: list) -> int:
    """Find a peak element index."""
    if not items:
        return -1
    left, right = 0, len(items) - 1
    while left < right:
        mid = (left + right) // 2
        if items[mid] < items[mid + 1]:
            left = mid + 1
        else:
            right = mid
    return left


def find_minimum_rotated(items: list) -> int:
    """Find minimum in rotated sorted array."""
    left, right = 0, len(items) - 1
    while left < right:
        mid = (left + right) // 2
        if items[mid] > items[right]:
            left = mid + 1
        else:
            right = mid
    return left


def search_rotated(items: list, target) -> int:
    """Search in rotated sorted array."""
    left, right = 0, len(items) - 1
    while left <= right:
        mid = (left + right) // 2
        if items[mid] == target:
            return mid
        if items[left] <= items[mid]:
            if items[left] <= target < items[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if items[mid] < target <= items[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1


def find_closest(items: list, target) -> int:
    """Find index of element closest to target in sorted list."""
    if not items:
        return -1
    if target <= items[0]:
        return 0
    if target >= items[-1]:
        return len(items) - 1
    left, right = 0, len(items) - 1
    while left < right - 1:
        mid = (left + right) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            left = mid
        else:
            right = mid
    return left if abs(items[left] - target) <= abs(items[right] - target) else right


def find_range(items: list, target) -> tuple:
    """Find range of indices where target occurs."""
    left = binary_search_leftmost(items, target)
    if left == -1:
        return (-1, -1)
    right = binary_search_rightmost(items, target)
    return (left, right)


def search_matrix(matrix: list, target) -> tuple:
    """Search in row-wise and column-wise sorted matrix."""
    if not matrix or not matrix[0]:
        return (-1, -1)
    rows, cols = len(matrix), len(matrix[0])
    row, col = 0, cols - 1
    while row < rows and col >= 0:
        if matrix[row][col] == target:
            return (row, col)
        elif matrix[row][col] < target:
            row += 1
        else:
            col -= 1
    return (-1, -1)
