"""
Data Parsing Functions - Pure functions for parsing structured data.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import json


def parse_json(text: str):
    """Parse a JSON string into a Python object."""
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def to_json(obj) -> str:
    """Convert a Python object to a JSON string."""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return ""


def to_json_pretty(obj) -> str:
    """Convert a Python object to a formatted JSON string."""
    try:
        return json.dumps(obj, indent=2)
    except (TypeError, ValueError):
        return ""


def parse_csv_line(line: str, delimiter: str) -> list:
    """Parse a single CSV line into a list of values."""
    if not line:
        return []
    if not delimiter:
        delimiter = ','
    return line.split(delimiter)


def to_csv_line(values: list, delimiter: str) -> str:
    """Convert a list of values to a CSV line."""
    if not values:
        return ""
    if not delimiter:
        delimiter = ','
    return delimiter.join(str(v) for v in values)


def parse_key_value(text: str, separator: str) -> tuple:
    """Parse a key-value pair from a string."""
    if not text:
        return ("", "")
    if not separator:
        separator = '='
    if separator not in text:
        return (text.strip(), "")
    parts = text.split(separator, 1)
    return (parts[0].strip(), parts[1].strip())


def parse_key_value_pairs(text: str, pair_separator: str, kv_separator: str) -> dict:
    """Parse multiple key-value pairs from a string."""
    if not text:
        return {}
    if not pair_separator:
        pair_separator = '&'
    if not kv_separator:
        kv_separator = '='
    result = {}
    pairs = text.split(pair_separator)
    for pair in pairs:
        key, value = parse_key_value(pair, kv_separator)
        if key:
            result[key] = value
    return result


def dict_to_key_value_string(data: dict, pair_separator: str, kv_separator: str) -> str:
    """Convert a dictionary to a key-value string."""
    if not data:
        return ""
    if not pair_separator:
        pair_separator = '&'
    if not kv_separator:
        kv_separator = '='
    pairs = [f"{k}{kv_separator}{v}" for k, v in data.items()]
    return pair_separator.join(pairs)


def parse_boolean(text: str) -> bool:
    """Parse a string into a boolean value."""
    if not text:
        return False
    return text.lower().strip() in ('true', 'yes', '1', 'on', 'y')


def parse_integer(text: str, default: int) -> int:
    """Parse a string into an integer with a default value."""
    if not text:
        return default
    try:
        return int(text.strip())
    except ValueError:
        return default


def parse_float(text: str, default: float) -> float:
    """Parse a string into a float with a default value."""
    if not text:
        return default
    try:
        return float(text.strip())
    except ValueError:
        return default


def parse_list(text: str, separator: str) -> list:
    """Parse a string into a list using a separator."""
    if not text:
        return []
    if not separator:
        separator = ','
    return [item.strip() for item in text.split(separator)]


def list_to_string(items: list, separator: str) -> str:
    """Convert a list to a string using a separator."""
    if not items:
        return ""
    if not separator:
        separator = ','
    return separator.join(str(item) for item in items)


def extract_numbers(text: str) -> list:
    """Extract all numbers from a string."""
    if not text:
        return []
    result = []
    current = ""
    for char in text:
        if char.isdigit() or (char == '.' and '.' not in current) or (char == '-' and not current):
            current += char
        elif current:
            try:
                if '.' in current:
                    result.append(float(current))
                else:
                    result.append(int(current))
            except ValueError:
                pass
            current = ""
    if current:
        try:
            if '.' in current:
                result.append(float(current))
            else:
                result.append(int(current))
        except ValueError:
            pass
    return result


def extract_words(text: str) -> list:
    """Extract all words from a string."""
    if not text:
        return []
    result = []
    current = ""
    for char in text:
        if char.isalpha():
            current += char
        elif current:
            result.append(current)
            current = ""
    if current:
        result.append(current)
    return result


def parse_ini_line(line: str) -> tuple:
    """Parse a single INI-style line. Returns (type, key, value)."""
    line = line.strip()
    if not line or line.startswith('#') or line.startswith(';'):
        return ('comment', '', line)
    if line.startswith('[') and line.endswith(']'):
        return ('section', line[1:-1], '')
    if '=' in line:
        key, value = parse_key_value(line, '=')
        return ('property', key, value)
    return ('unknown', '', line)


def get_nested_value(data: dict, path: str, separator: str):
    """Get a nested value from a dictionary using a path string."""
    if not data or not path:
        return None
    if not separator:
        separator = '.'
    keys = path.split(separator)
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list):
            try:
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            except ValueError:
                return None
        else:
            return None
    return current


def set_nested_value(data: dict, path: str, value, separator: str) -> dict:
    """Set a nested value in a dictionary using a path string."""
    if not path:
        return data
    if not separator:
        separator = '.'
    result = dict(data) if data else {}
    keys = path.split(separator)
    current = result
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    return result


def flatten_dict(data: dict, separator: str, prefix: str) -> dict:
    """Flatten a nested dictionary into a single-level dictionary."""
    if not data:
        return {}
    if not separator:
        separator = '.'
    result = {}
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_dict(value, separator, new_key))
        else:
            result[new_key] = value
    return result


def unflatten_dict(data: dict, separator: str) -> dict:
    """Unflatten a flat dictionary into a nested dictionary."""
    if not data:
        return {}
    if not separator:
        separator = '.'
    result = {}
    for flat_key, value in data.items():
        result = set_nested_value(result, flat_key, value, separator)
    return result


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Merge two dictionaries, with dict2 values taking precedence."""
    if not dict1:
        return dict2 or {}
    if not dict2:
        return dict1 or {}
    result = dict(dict1)
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def filter_dict_keys(data: dict, keys: list) -> dict:
    """Filter a dictionary to only include specified keys."""
    if not data or not keys:
        return {}
    return {k: v for k, v in data.items() if k in keys}


def exclude_dict_keys(data: dict, keys: list) -> dict:
    """Filter a dictionary to exclude specified keys."""
    if not data:
        return {}
    if not keys:
        return dict(data)
    return {k: v for k, v in data.items() if k not in keys}
