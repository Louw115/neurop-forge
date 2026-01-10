"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Query String - Pure functions for query string operations.
All functions are pure, deterministic, and atomic.
"""

from urllib.parse import quote, unquote


def parse_query_string(query: str) -> dict:
    """Parse query string to dictionary."""
    if not query:
        return {}
    if query.startswith("?"):
        query = query[1:]
    result = {}
    for pair in query.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            key = unquote(key)
            value = unquote(value)
            if key in result:
                if isinstance(result[key], list):
                    result[key].append(value)
                else:
                    result[key] = [result[key], value]
            else:
                result[key] = value
        elif pair:
            result[unquote(pair)] = ""
    return result


def build_query_string(params: dict) -> str:
    """Build query string from dictionary."""
    pairs = []
    for key, value in params.items():
        if isinstance(value, list):
            for v in value:
                pairs.append(f"{quote(str(key))}={quote(str(v))}")
        else:
            pairs.append(f"{quote(str(key))}={quote(str(value))}")
    return "&".join(pairs)


def add_param(query: str, key: str, value: str) -> str:
    """Add parameter to query string."""
    params = parse_query_string(query)
    params[key] = value
    return build_query_string(params)


def remove_param(query: str, key: str) -> str:
    """Remove parameter from query string."""
    params = parse_query_string(query)
    if key in params:
        del params[key]
    return build_query_string(params)


def get_param(query: str, key: str, default: str) -> str:
    """Get parameter value."""
    params = parse_query_string(query)
    return params.get(key, default)


def has_param(query: str, key: str) -> bool:
    """Check if parameter exists."""
    params = parse_query_string(query)
    return key in params


def merge_query_strings(query1: str, query2: str) -> str:
    """Merge two query strings."""
    params1 = parse_query_string(query1)
    params2 = parse_query_string(query2)
    merged = {**params1, **params2}
    return build_query_string(merged)


def filter_params(query: str, allowed_keys: list) -> str:
    """Filter query string to allowed keys."""
    params = parse_query_string(query)
    filtered = {k: v for k, v in params.items() if k in allowed_keys}
    return build_query_string(filtered)


def exclude_params(query: str, excluded_keys: list) -> str:
    """Exclude specific keys from query string."""
    params = parse_query_string(query)
    filtered = {k: v for k, v in params.items() if k not in excluded_keys}
    return build_query_string(filtered)


def sort_params(query: str) -> str:
    """Sort query string parameters alphabetically."""
    params = parse_query_string(query)
    sorted_params = dict(sorted(params.items()))
    return build_query_string(sorted_params)


def params_to_pairs(query: str) -> list:
    """Convert query string to list of pairs."""
    params = parse_query_string(query)
    pairs = []
    for key, value in params.items():
        if isinstance(value, list):
            for v in value:
                pairs.append([key, v])
        else:
            pairs.append([key, value])
    return pairs


def pairs_to_query(pairs: list) -> str:
    """Convert list of pairs to query string."""
    result = []
    for pair in pairs:
        if len(pair) >= 2:
            result.append(f"{quote(str(pair[0]))}={quote(str(pair[1]))}")
    return "&".join(result)


def append_to_url(url: str, query: str) -> str:
    """Append query string to URL."""
    if not query:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{query}"


def extract_query_from_url(url: str) -> str:
    """Extract query string from URL."""
    if "?" not in url:
        return ""
    return url.split("?", 1)[1].split("#")[0]


def update_url_param(url: str, key: str, value: str) -> str:
    """Update parameter in URL."""
    if "?" not in url:
        return f"{url}?{quote(key)}={quote(value)}"
    base, query = url.split("?", 1)
    fragment = ""
    if "#" in query:
        query, fragment = query.split("#", 1)
        fragment = "#" + fragment
    new_query = add_param(query, key, value)
    return f"{base}?{new_query}{fragment}"


def count_params(query: str) -> int:
    """Count number of parameters."""
    return len(parse_query_string(query))


def is_empty_query(query: str) -> bool:
    """Check if query string is empty."""
    return len(parse_query_string(query)) == 0


def encode_object_param(obj: dict) -> str:
    """Encode object as query parameter."""
    import json
    return quote(json.dumps(obj))


def decode_object_param(encoded: str) -> dict:
    """Decode object from query parameter."""
    import json
    try:
        return json.loads(unquote(encoded))
    except:
        return {}


def get_multi_param(query: str, key: str) -> list:
    """Get all values for a parameter."""
    params = parse_query_string(query)
    value = params.get(key, [])
    if isinstance(value, list):
        return value
    return [value] if value else []
