"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Object Utilities - Pure functions for object manipulation.
All functions are pure, deterministic, and atomic.
"""

def get_nested(obj: dict, path: str, default):
    """Get nested value by dot notation path."""
    keys = path.split(".")
    current = obj
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def set_nested(obj: dict, path: str, value) -> dict:
    """Set nested value by path, returning new object."""
    keys = path.split(".")
    result = dict(obj)
    current = result
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current[key] = dict(current[key])
        current = current[key]
    current[keys[-1]] = value
    return result


def has_key(obj: dict, key: str) -> bool:
    """Check if object has key."""
    return key in obj


def has_nested_key(obj: dict, path: str) -> bool:
    """Check if nested key exists."""
    keys = path.split(".")
    current = obj
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False
    return True


def delete_key(obj: dict, key: str) -> dict:
    """Delete key from object, returning new object."""
    result = dict(obj)
    if key in result:
        del result[key]
    return result


def delete_nested(obj: dict, path: str) -> dict:
    """Delete nested key, returning new object."""
    keys = path.split(".")
    if len(keys) == 1:
        return delete_key(obj, keys[0])
    result = dict(obj)
    current = result
    for key in keys[:-1]:
        if key not in current:
            return result
        current[key] = dict(current[key])
        current = current[key]
    if keys[-1] in current:
        del current[keys[-1]]
    return result


def merge(obj1: dict, obj2: dict) -> dict:
    """Shallow merge two objects."""
    return {**obj1, **obj2}


def deep_merge(obj1: dict, obj2: dict) -> dict:
    """Deep merge two objects."""
    result = dict(obj1)
    for key, value in obj2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def pick(obj: dict, keys: list) -> dict:
    """Pick specific keys from object."""
    return {k: obj[k] for k in keys if k in obj}


def omit(obj: dict, keys: list) -> dict:
    """Omit specific keys from object."""
    return {k: v for k, v in obj.items() if k not in keys}


def invert(obj: dict) -> dict:
    """Invert keys and values."""
    return {v: k for k, v in obj.items()}


def map_keys(obj: dict, fn) -> dict:
    """Map function over keys."""
    return {fn(k): v for k, v in obj.items()}


def map_values(obj: dict, fn) -> dict:
    """Map function over values."""
    return {k: fn(v) for k, v in obj.items()}


def filter_keys(obj: dict, predicate) -> dict:
    """Filter object by key predicate."""
    return {k: v for k, v in obj.items() if predicate(k)}


def filter_values(obj: dict, predicate) -> dict:
    """Filter object by value predicate."""
    return {k: v for k, v in obj.items() if predicate(v)}


def entries(obj: dict) -> list:
    """Get list of [key, value] pairs."""
    return list(obj.items())


def from_entries(pairs: list) -> dict:
    """Create object from [key, value] pairs."""
    return dict(pairs)


def keys(obj: dict) -> list:
    """Get list of keys."""
    return list(obj.keys())


def values(obj: dict) -> list:
    """Get list of values."""
    return list(obj.values())


def is_empty(obj: dict) -> bool:
    """Check if object is empty."""
    return len(obj) == 0


def size(obj: dict) -> int:
    """Get number of keys."""
    return len(obj)


def equals(obj1: dict, obj2: dict) -> bool:
    """Check if objects are equal."""
    return obj1 == obj2


def deep_equals(obj1: dict, obj2: dict) -> bool:
    """Deep equality check."""
    if type(obj1) != type(obj2):
        return False
    if isinstance(obj1, dict):
        if obj1.keys() != obj2.keys():
            return False
        return all(deep_equals(obj1[k], obj2[k]) for k in obj1)
    if isinstance(obj1, list):
        if len(obj1) != len(obj2):
            return False
        return all(deep_equals(a, b) for a, b in zip(obj1, obj2))
    return obj1 == obj2


def clone(obj: dict) -> dict:
    """Shallow clone object."""
    return dict(obj)


def deep_clone(obj: dict) -> dict:
    """Deep clone object."""
    import json
    return json.loads(json.dumps(obj))


def find_key(obj: dict, predicate) -> str:
    """Find key by value predicate."""
    for k, v in obj.items():
        if predicate(v):
            return k
    return None


def transform(obj: dict, transforms: dict) -> dict:
    """Apply transforms to specific keys."""
    result = dict(obj)
    for key, fn in transforms.items():
        if key in result:
            result[key] = fn(result[key])
    return result


def defaults(obj: dict, default_values: dict) -> dict:
    """Apply default values for missing keys."""
    result = dict(default_values)
    result.update(obj)
    return result


def compact(obj: dict) -> dict:
    """Remove None values."""
    return {k: v for k, v in obj.items() if v is not None}


def compact_deep(obj: dict) -> dict:
    """Recursively remove None values."""
    result = {}
    for k, v in obj.items():
        if v is None:
            continue
        if isinstance(v, dict):
            v = compact_deep(v)
        result[k] = v
    return result


def rename_key(obj: dict, old_key: str, new_key: str) -> dict:
    """Rename a key."""
    result = dict(obj)
    if old_key in result:
        result[new_key] = result.pop(old_key)
    return result


def flatten(obj: dict, separator: str) -> dict:
    """Flatten nested object."""
    result = {}
    def _flatten(item, prefix):
        if isinstance(item, dict):
            for k, v in item.items():
                new_key = f"{prefix}{separator}{k}" if prefix else k
                _flatten(v, new_key)
        else:
            result[prefix] = item
    _flatten(obj, "")
    return result


def unflatten(obj: dict, separator: str) -> dict:
    """Unflatten object."""
    result = {}
    for key, value in obj.items():
        keys = key.split(separator)
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    return result
