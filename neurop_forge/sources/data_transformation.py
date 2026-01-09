"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Data Transformation - Pure functions for transforming data structures.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def normalize_values(values: list, min_val: float, max_val: float) -> list:
    """Normalize values to a range between 0 and 1 using provided min/max bounds."""
    if not values:
        return []
    if min_val == max_val:
        return [0.5] * len(values)
    return [(v - min_val) / (max_val - min_val) for v in values]


def normalize_values_auto(values: list) -> list:
    """Normalize values to a range between 0 and 1 using actual min/max from data."""
    if not values:
        return []
    actual_min = min(values)
    actual_max = max(values)
    if actual_min == actual_max:
        return [0.5] * len(values)
    return [(v - actual_min) / (actual_max - actual_min) for v in values]


def scale_values(values: list, new_min: float, new_max: float) -> list:
    """Scale values from their current range to a new range."""
    if not values:
        return []
    normalized = normalize_values_auto(values)
    return [v * (new_max - new_min) + new_min for v in normalized]


def standardize_values(values: list) -> list:
    """Standardize values to have mean 0 and standard deviation 1."""
    if not values or len(values) < 2:
        return values
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    if variance == 0:
        return [0.0] * len(values)
    std_dev = variance ** 0.5
    return [(v - mean) / std_dev for v in values]


def clip_values(values: list, min_val: float, max_val: float) -> list:
    """Clip values to be within a specified range."""
    return [max(min_val, min(max_val, v)) for v in values]


def bin_values(values: list, num_bins: int) -> list:
    """Assign values to bins (returns bin indices)."""
    if not values or num_bins <= 0:
        return []
    min_val = min(values)
    max_val = max(values)
    if min_val == max_val:
        return [0] * len(values)
    bin_width = (max_val - min_val) / num_bins
    return [min(int((v - min_val) / bin_width), num_bins - 1) for v in values]


def rank_values(values: list) -> list:
    """Rank values (1 = smallest)."""
    if not values:
        return []
    sorted_with_idx = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0] * len(values)
    for rank, (idx, _) in enumerate(sorted_with_idx, 1):
        ranks[idx] = rank
    return ranks


def percentile_rank(values: list) -> list:
    """Convert values to percentile ranks (0-100)."""
    if not values:
        return []
    ranks = rank_values(values)
    n = len(values)
    return [(r - 1) / (n - 1) * 100 if n > 1 else 50.0 for r in ranks]


def pivot_dict_list(data: list, key_field: str, value_field: str) -> dict:
    """Pivot a list of dicts to a dict of key -> value."""
    if not data:
        return {}
    result = {}
    for item in data:
        if key_field in item and value_field in item:
            result[item[key_field]] = item[value_field]
    return result


def unpivot_dict(data: dict, key_name: str, value_name: str) -> list:
    """Unpivot a dict to a list of dicts with key/value fields."""
    return [{key_name: k, value_name: v} for k, v in data.items()]


def group_by_key(data: list, key: str) -> dict:
    """Group a list of dicts by a key field."""
    result = {}
    for item in data:
        if key in item:
            group_key = item[key]
            if group_key not in result:
                result[group_key] = []
            result[group_key].append(item)
    return result


def aggregate_by_key(data: list, key: str, value_field: str, operation: str) -> dict:
    """Aggregate values in groups by a key field."""
    groups = group_by_key(data, key)
    result = {}
    for group_key, items in groups.items():
        values = [item.get(value_field, 0) for item in items if value_field in item]
        if not values:
            result[group_key] = 0
        elif operation == "sum":
            result[group_key] = sum(values)
        elif operation == "avg":
            result[group_key] = sum(values) / len(values)
        elif operation == "min":
            result[group_key] = min(values)
        elif operation == "max":
            result[group_key] = max(values)
        elif operation == "count":
            result[group_key] = len(values)
        else:
            result[group_key] = values
    return result


def flatten_nested_dict(data: dict, separator: str) -> dict:
    """Flatten a nested dict to a flat dict with compound keys."""
    result = {}
    
    def _flatten(obj, prefix):
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{prefix}{separator}{k}" if prefix else k
                _flatten(v, new_key)
        else:
            result[prefix] = obj
    
    _flatten(data, "")
    return result


def unflatten_dict(data: dict, separator: str) -> dict:
    """Unflatten a flat dict with compound keys to nested dict."""
    result = {}
    for key, value in data.items():
        parts = key.split(separator)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def rename_keys(data: dict, mapping: dict) -> dict:
    """Rename keys in a dict according to a mapping."""
    return {mapping.get(k, k): v for k, v in data.items()}


def filter_keys(data: dict, keys: list) -> dict:
    """Filter a dict to only include specified keys."""
    return {k: v for k, v in data.items() if k in keys}


def exclude_keys(data: dict, keys: list) -> dict:
    """Filter a dict to exclude specified keys."""
    return {k: v for k, v in data.items() if k not in keys}


def transpose_list_of_dicts(data: list) -> dict:
    """Transpose a list of dicts to a dict of lists."""
    if not data:
        return {}
    result = {}
    for item in data:
        for key, value in item.items():
            if key not in result:
                result[key] = []
            result[key].append(value)
    return result


def transpose_dict_of_lists(data: dict) -> list:
    """Transpose a dict of lists to a list of dicts."""
    if not data:
        return []
    keys = list(data.keys())
    if not keys:
        return []
    length = len(data[keys[0]])
    return [{k: data[k][i] for k in keys} for i in range(length)]


def merge_dicts(dicts: list) -> dict:
    """Merge multiple dicts into one (later values override)."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def deep_merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Deep merge two dicts (nested dicts are merged recursively)."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def diff_dicts(dict1: dict, dict2: dict) -> dict:
    """Find differences between two dicts."""
    result = {"added": {}, "removed": {}, "changed": {}}
    all_keys = set(dict1.keys()) | set(dict2.keys())
    for key in all_keys:
        if key not in dict1:
            result["added"][key] = dict2[key]
        elif key not in dict2:
            result["removed"][key] = dict1[key]
        elif dict1[key] != dict2[key]:
            result["changed"][key] = {"old": dict1[key], "new": dict2[key]}
    return result


def invert_dict(data: dict) -> dict:
    """Invert a dict (swap keys and values)."""
    return {v: k for k, v in data.items()}


def zip_to_dict(keys: list, values: list) -> dict:
    """Create a dict from parallel lists of keys and values."""
    return dict(zip(keys, values))


def unzip_dict(data: dict) -> tuple:
    """Split a dict into parallel lists of keys and values."""
    return (list(data.keys()), list(data.values()))


def sort_dict_by_key(data: dict, reverse: bool) -> dict:
    """Sort a dict by its keys."""
    return dict(sorted(data.items(), reverse=reverse))


def sort_dict_by_value(data: dict, reverse: bool) -> dict:
    """Sort a dict by its values."""
    return dict(sorted(data.items(), key=lambda x: x[1], reverse=reverse))


def fill_missing_values(data: list, default: any) -> list:
    """Replace None values with a default."""
    return [v if v is not None else default for v in data]


def interpolate_missing(values: list) -> list:
    """Linearly interpolate missing (None) values in a list."""
    if not values:
        return []
    result = values.copy()
    for i in range(len(result)):
        if result[i] is None:
            prev_idx = None
            next_idx = None
            for j in range(i - 1, -1, -1):
                if result[j] is not None:
                    prev_idx = j
                    break
            for j in range(i + 1, len(result)):
                if result[j] is not None:
                    next_idx = j
                    break
            if prev_idx is not None and next_idx is not None:
                ratio = (i - prev_idx) / (next_idx - prev_idx)
                result[i] = result[prev_idx] + (result[next_idx] - result[prev_idx]) * ratio
            elif prev_idx is not None:
                result[i] = result[prev_idx]
            elif next_idx is not None:
                result[i] = result[next_idx]
    return result


def remove_duplicates_by_key(data: list, key: str) -> list:
    """Remove duplicate dicts based on a key field (keeps first)."""
    seen = set()
    result = []
    for item in data:
        if key in item:
            if item[key] not in seen:
                seen.add(item[key])
                result.append(item)
        else:
            result.append(item)
    return result


def window_values(values: list, window_size: int) -> list:
    """Create sliding windows from a list."""
    if not values or window_size <= 0:
        return []
    return [values[i:i + window_size] for i in range(len(values) - window_size + 1)]


def running_average(values: list, window_size: int) -> list:
    """Calculate running average over a window."""
    if not values or window_size <= 0:
        return []
    windows = window_values(values, window_size)
    return [sum(w) / len(w) for w in windows]


def lag_values(values: list, lag: int, fill: any) -> list:
    """Shift values by a lag amount."""
    if not values:
        return []
    if lag > 0:
        return [fill] * lag + values[:-lag] if lag < len(values) else [fill] * len(values)
    elif lag < 0:
        return values[-lag:] + [fill] * (-lag) if -lag < len(values) else [fill] * len(values)
    return values.copy()


def difference_values(values: list, periods: int) -> list:
    """Calculate difference from N periods ago."""
    if not values or periods <= 0 or periods >= len(values):
        return []
    return [values[i] - values[i - periods] for i in range(periods, len(values))]


def cumulative_sum(values: list) -> list:
    """Calculate cumulative sum."""
    if not values:
        return []
    result = []
    total = 0
    for v in values:
        total += v
        result.append(total)
    return result


def pct_change(values: list) -> list:
    """Calculate percentage change from previous value."""
    if len(values) < 2:
        return []
    return [(values[i] - values[i-1]) / values[i-1] if values[i-1] != 0 else 0 
            for i in range(1, len(values))]
