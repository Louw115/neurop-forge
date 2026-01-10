"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
JSON Utilities - Pure functions for JSON manipulation.
All functions are pure, deterministic, and atomic.
"""

import json


def parse_json(text: str) -> dict:
    """Parse JSON string."""
    try:
        return {"success": True, "data": json.loads(text), "error": None}
    except json.JSONDecodeError as e:
        return {"success": False, "data": None, "error": str(e)}


def stringify_json(data, indent: int) -> str:
    """Convert to JSON string."""
    return json.dumps(data, indent=indent if indent > 0 else None)


def minify_json(text: str) -> str:
    """Minify JSON string."""
    result = parse_json(text)
    if result["success"]:
        return json.dumps(result["data"], separators=(",", ":"))
    return text


def prettify_json(text: str, indent: int) -> str:
    """Prettify JSON string."""
    result = parse_json(text)
    if result["success"]:
        return json.dumps(result["data"], indent=indent)
    return text


def get_path(data, path: str, default):
    """Get value at path (dot notation)."""
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list):
            try:
                current = current[int(key)]
            except (ValueError, IndexError):
                return default
        else:
            return default
    return current


def set_path(data: dict, path: str, value) -> dict:
    """Set value at path (returns new dict)."""
    keys = path.split(".")
    if not keys:
        return data
    result = dict(data) if isinstance(data, dict) else {}
    current = result
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current[key] = dict(current[key])
        current = current[key]
    current[keys[-1]] = value
    return result


def delete_path(data: dict, path: str) -> dict:
    """Delete value at path (returns new dict)."""
    keys = path.split(".")
    if not keys:
        return data
    result = dict(data)
    current = result
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            return result
        current[key] = dict(current[key])
        current = current[key]
    if keys[-1] in current:
        del current[keys[-1]]
    return result


def has_path(data, path: str) -> bool:
    """Check if path exists."""
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list):
            try:
                current = current[int(key)]
            except (ValueError, IndexError):
                return False
        else:
            return False
    return True


def flatten_json(data: dict, separator: str) -> dict:
    """Flatten nested JSON to single level."""
    result = {}
    def flatten(obj, prefix):
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{prefix}{separator}{k}" if prefix else k
                flatten(v, new_key)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                new_key = f"{prefix}{separator}{i}" if prefix else str(i)
                flatten(v, new_key)
        else:
            result[prefix] = obj
    flatten(data, "")
    return result


def unflatten_json(data: dict, separator: str) -> dict:
    """Unflatten JSON back to nested structure."""
    result = {}
    for key, value in data.items():
        keys = key.split(separator)
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    return result


def merge_json(obj1: dict, obj2: dict) -> dict:
    """Deep merge two JSON objects."""
    result = dict(obj1)
    for key, value in obj2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json(result[key], value)
        else:
            result[key] = value
    return result


def diff_json(obj1: dict, obj2: dict) -> dict:
    """Get differences between two JSON objects."""
    added = {}
    removed = {}
    modified = {}
    for key in obj2:
        if key not in obj1:
            added[key] = obj2[key]
        elif obj1[key] != obj2[key]:
            modified[key] = {"old": obj1[key], "new": obj2[key]}
    for key in obj1:
        if key not in obj2:
            removed[key] = obj1[key]
    return {"added": added, "removed": removed, "modified": modified}


def pick_keys(data: dict, keys: list) -> dict:
    """Pick specific keys from object."""
    return {k: data[k] for k in keys if k in data}


def omit_keys(data: dict, keys: list) -> dict:
    """Omit specific keys from object."""
    return {k: v for k, v in data.items() if k not in keys}


def rename_keys(data: dict, mapping: dict) -> dict:
    """Rename keys according to mapping."""
    result = {}
    for k, v in data.items():
        new_key = mapping.get(k, k)
        result[new_key] = v
    return result


def filter_null(data: dict) -> dict:
    """Remove null values from object."""
    return {k: v for k, v in data.items() if v is not None}


def filter_empty(data: dict) -> dict:
    """Remove empty values from object."""
    return {k: v for k, v in data.items() if v not in [None, "", [], {}]}


def get_keys(data: dict) -> list:
    """Get all keys at top level."""
    return list(data.keys())


def get_values(data: dict) -> list:
    """Get all values at top level."""
    return list(data.values())


def count_keys(data: dict) -> int:
    """Count keys at top level."""
    return len(data)


def is_valid_json(text: str) -> bool:
    """Check if text is valid JSON."""
    return parse_json(text)["success"]


def json_type(value) -> str:
    """Get JSON type of value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) or isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unknown"


def traverse_json(data, visitor) -> None:
    """Traverse JSON and apply visitor to each node."""
    def traverse(obj, path):
        visitor(path, obj)
        if isinstance(obj, dict):
            for k, v in obj.items():
                traverse(v, path + [k])
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                traverse(v, path + [i])
    traverse(data, [])


def clone_json(data) -> dict:
    """Deep clone JSON object."""
    return json.loads(json.dumps(data))
