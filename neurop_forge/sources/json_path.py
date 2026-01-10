"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
JSON Path - Pure functions for JSON path operations.
All functions are pure, deterministic, and atomic.
"""


def get_by_path(obj, path: str):
    """Get value at JSON path."""
    if not path:
        return obj
    parts = parse_path(path)
    current = obj
    for part in parts:
        if isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                return None
        elif isinstance(current, list):
            try:
                idx = int(part)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            except ValueError:
                return None
        else:
            return None
    return current


def parse_path(path: str) -> list:
    """Parse JSON path into parts."""
    if path.startswith("$."):
        path = path[2:]
    elif path.startswith("$"):
        path = path[1:]
    parts = []
    current = ""
    in_bracket = False
    for char in path:
        if char == "[":
            if current:
                parts.append(current)
                current = ""
            in_bracket = True
        elif char == "]":
            if current:
                parts.append(current.strip("'\""))
                current = ""
            in_bracket = False
        elif char == "." and not in_bracket:
            if current:
                parts.append(current)
                current = ""
        else:
            current += char
    if current:
        parts.append(current)
    return parts


def build_path(parts: list) -> str:
    """Build JSON path from parts."""
    result = "$"
    for part in parts:
        if isinstance(part, int) or part.isdigit():
            result += f"[{part}]"
        elif " " in part or "." in part:
            result += f"['{part}']"
        else:
            result += f".{part}"
    return result


def set_by_path(obj: dict, path: str, value) -> dict:
    """Set value at JSON path, returning new object."""
    import json
    result = json.loads(json.dumps(obj))
    parts = parse_path(path)
    if not parts:
        return value if isinstance(value, dict) else result
    current = result
    for part in parts[:-1]:
        if isinstance(current, dict):
            if part not in current:
                current[part] = {}
            current = current[part]
        elif isinstance(current, list):
            idx = int(part)
            current = current[idx]
    last = parts[-1]
    if isinstance(current, dict):
        current[last] = value
    elif isinstance(current, list):
        current[int(last)] = value
    return result


def delete_by_path(obj: dict, path: str) -> dict:
    """Delete value at JSON path, returning new object."""
    import json
    result = json.loads(json.dumps(obj))
    parts = parse_path(path)
    if not parts:
        return result
    current = result
    for part in parts[:-1]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list):
            idx = int(part)
            current = current[idx]
        else:
            return result
    last = parts[-1]
    if isinstance(current, dict) and last in current:
        del current[last]
    elif isinstance(current, list):
        idx = int(last)
        if 0 <= idx < len(current):
            current.pop(idx)
    return result


def exists(obj, path: str) -> bool:
    """Check if path exists."""
    parts = parse_path(path)
    current = obj
    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                return False
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return False
            except ValueError:
                return False
        else:
            return False
    return True


def find_all_paths(obj, value) -> list:
    """Find all paths to a value."""
    paths = []
    def search(current, path):
        if current == value:
            paths.append(build_path(path))
        elif isinstance(current, dict):
            for k, v in current.items():
                search(v, path + [k])
        elif isinstance(current, list):
            for i, v in enumerate(current):
                search(v, path + [str(i)])
    search(obj, [])
    return paths


def get_all_paths(obj) -> list:
    """Get all leaf paths in object."""
    paths = []
    def traverse(current, path):
        if isinstance(current, dict):
            for k, v in current.items():
                traverse(v, path + [k])
        elif isinstance(current, list):
            for i, v in enumerate(current):
                traverse(v, path + [str(i)])
        else:
            paths.append(build_path(path))
    traverse(obj, [])
    return paths


def flatten_json(obj: dict, separator: str) -> dict:
    """Flatten nested JSON to flat dict."""
    result = {}
    def flatten(current, prefix):
        if isinstance(current, dict):
            for k, v in current.items():
                new_key = f"{prefix}{separator}{k}" if prefix else k
                flatten(v, new_key)
        elif isinstance(current, list):
            for i, v in enumerate(current):
                new_key = f"{prefix}{separator}{i}" if prefix else str(i)
                flatten(v, new_key)
        else:
            result[prefix] = current
    flatten(obj, "")
    return result


def unflatten_json(flat: dict, separator: str) -> dict:
    """Unflatten flat dict to nested JSON."""
    result = {}
    for key, value in flat.items():
        parts = key.split(separator)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def merge_at_path(obj: dict, path: str, new_values: dict) -> dict:
    """Merge values at path."""
    existing = get_by_path(obj, path)
    if isinstance(existing, dict):
        merged = {**existing, **new_values}
    else:
        merged = new_values
    return set_by_path(obj, path, merged)


def append_to_array(obj: dict, path: str, value) -> dict:
    """Append value to array at path."""
    existing = get_by_path(obj, path)
    if isinstance(existing, list):
        new_array = existing + [value]
    else:
        new_array = [value]
    return set_by_path(obj, path, new_array)
