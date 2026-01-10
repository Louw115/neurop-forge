"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Interval Utilities - Pure functions for interval/range operations.
All functions are pure, deterministic, and atomic.
"""

def create_interval(start, end) -> dict:
    """Create an interval."""
    return {"start": start, "end": end}


def interval_contains(interval: dict, value) -> bool:
    """Check if interval contains value."""
    return interval["start"] <= value <= interval["end"]


def interval_contains_exclusive(interval: dict, value) -> bool:
    """Check if interval contains value (exclusive ends)."""
    return interval["start"] < value < interval["end"]


def intervals_overlap(a: dict, b: dict) -> bool:
    """Check if two intervals overlap."""
    return a["start"] <= b["end"] and b["start"] <= a["end"]


def intervals_touch(a: dict, b: dict) -> bool:
    """Check if two intervals touch (adjacent)."""
    return a["end"] == b["start"] or b["end"] == a["start"]


def interval_intersection(a: dict, b: dict) -> dict:
    """Get intersection of two intervals."""
    if not intervals_overlap(a, b):
        return None
    return create_interval(max(a["start"], b["start"]), min(a["end"], b["end"]))


def interval_union(a: dict, b: dict) -> dict:
    """Get union of two overlapping intervals."""
    if not intervals_overlap(a, b) and not intervals_touch(a, b):
        return None
    return create_interval(min(a["start"], b["start"]), max(a["end"], b["end"]))


def interval_difference(a: dict, b: dict) -> list:
    """Get difference a - b (parts of a not in b)."""
    if not intervals_overlap(a, b):
        return [a]
    result = []
    if a["start"] < b["start"]:
        result.append(create_interval(a["start"], b["start"]))
    if a["end"] > b["end"]:
        result.append(create_interval(b["end"], a["end"]))
    return result


def interval_length(interval: dict) -> float:
    """Calculate interval length."""
    return interval["end"] - interval["start"]


def interval_midpoint(interval: dict):
    """Calculate interval midpoint."""
    return (interval["start"] + interval["end"]) / 2


def interval_is_empty(interval: dict) -> bool:
    """Check if interval is empty."""
    return interval["start"] > interval["end"]


def interval_is_point(interval: dict) -> bool:
    """Check if interval is a single point."""
    return interval["start"] == interval["end"]


def interval_split(interval: dict, point) -> list:
    """Split interval at point."""
    if point <= interval["start"] or point >= interval["end"]:
        return [interval]
    return [
        create_interval(interval["start"], point),
        create_interval(point, interval["end"])
    ]


def interval_expand(interval: dict, amount) -> dict:
    """Expand interval by amount on both sides."""
    return create_interval(interval["start"] - amount, interval["end"] + amount)


def interval_shrink(interval: dict, amount) -> dict:
    """Shrink interval by amount on both sides."""
    new_start = interval["start"] + amount
    new_end = interval["end"] - amount
    if new_start > new_end:
        mid = interval_midpoint(interval)
        return create_interval(mid, mid)
    return create_interval(new_start, new_end)


def interval_shift(interval: dict, amount) -> dict:
    """Shift interval by amount."""
    return create_interval(interval["start"] + amount, interval["end"] + amount)


def interval_scale(interval: dict, factor) -> dict:
    """Scale interval around midpoint."""
    mid = interval_midpoint(interval)
    half_length = interval_length(interval) / 2 * factor
    return create_interval(mid - half_length, mid + half_length)


def merge_intervals(intervals: list) -> list:
    """Merge overlapping intervals."""
    if not intervals:
        return []
    sorted_intervals = sorted(intervals, key=lambda x: x["start"])
    merged = [sorted_intervals[0]]
    for interval in sorted_intervals[1:]:
        last = merged[-1]
        if intervals_overlap(last, interval) or intervals_touch(last, interval):
            merged[-1] = interval_union(last, interval)
        else:
            merged.append(interval)
    return merged


def find_gaps(intervals: list, bounds: dict) -> list:
    """Find gaps between intervals within bounds."""
    if not intervals:
        return [bounds]
    merged = merge_intervals(intervals)
    gaps = []
    if merged[0]["start"] > bounds["start"]:
        gaps.append(create_interval(bounds["start"], merged[0]["start"]))
    for i in range(len(merged) - 1):
        gaps.append(create_interval(merged[i]["end"], merged[i + 1]["start"]))
    if merged[-1]["end"] < bounds["end"]:
        gaps.append(create_interval(merged[-1]["end"], bounds["end"]))
    return gaps


def intervals_coverage(intervals: list, bounds: dict) -> float:
    """Calculate total coverage as fraction of bounds."""
    merged = merge_intervals(intervals)
    total = sum(interval_length(i) for i in merged if intervals_overlap(i, bounds))
    bound_length = interval_length(bounds)
    return total / bound_length if bound_length > 0 else 0


def find_interval_containing(intervals: list, value) -> dict:
    """Find first interval containing value."""
    for interval in intervals:
        if interval_contains(interval, value):
            return interval
    return None


def find_all_intervals_containing(intervals: list, value) -> list:
    """Find all intervals containing value."""
    return [i for i in intervals if interval_contains(i, value)]


def interval_to_range(interval: dict, step: float) -> list:
    """Generate range of values in interval."""
    result = []
    current = interval["start"]
    while current <= interval["end"]:
        result.append(current)
        current += step
    return result


def clamp_to_interval(value, interval: dict):
    """Clamp value to interval."""
    return max(interval["start"], min(interval["end"], value))


def is_within_interval(value, interval: dict, tolerance: float) -> bool:
    """Check if value is within interval with tolerance."""
    return (interval["start"] - tolerance) <= value <= (interval["end"] + tolerance)


def build_interval_tree_node(interval: dict, left, right) -> dict:
    """Build an interval tree node."""
    return {
        "interval": interval,
        "max_end": interval["end"],
        "left": left,
        "right": right
    }


def interval_compare(a: dict, b: dict) -> int:
    """Compare two intervals by start then end."""
    if a["start"] != b["start"]:
        return -1 if a["start"] < b["start"] else 1
    if a["end"] != b["end"]:
        return -1 if a["end"] < b["end"] else 1
    return 0


def partition_intervals(intervals: list, point) -> dict:
    """Partition intervals by point."""
    before = []
    containing = []
    after = []
    for interval in intervals:
        if interval["end"] < point:
            before.append(interval)
        elif interval["start"] > point:
            after.append(interval)
        else:
            containing.append(interval)
    return {"before": before, "containing": containing, "after": after}
