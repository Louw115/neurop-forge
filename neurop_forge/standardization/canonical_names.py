"""
Canonical Parameter Names for Neurop Block Forge V2.

Defines the standard parameter names for each data type, along with
common aliases that map to each canonical name.
"""

from typing import Dict, List, Set, Optional


CANONICAL_BY_TYPE: Dict[str, Dict[str, List[str]]] = {
    "string": {
        "text": ["s", "str", "string", "input", "value", "txt", "content", "message"],
        "pattern": ["regex", "regexp", "re", "pat"],
        "separator": ["sep", "delimiter", "delim", "split_char"],
        "prefix": ["pre", "start"],
        "suffix": ["suf", "end", "post"],
        "char": ["character", "c", "fill_char", "pad_char"],
        "replacement": ["repl", "replace_with", "new_value"],
        "encoding": ["enc", "charset"],
    },
    "integer": {
        "n": ["num", "number", "count", "amount", "qty"],
        "index": ["idx", "i", "pos", "position"],
        "start": ["begin", "from_idx", "start_idx", "offset"],
        "end": ["stop", "to_idx", "end_idx", "limit"],
        "width": ["length", "size", "len", "pad_length"],
        "precision": ["decimals", "decimal_places", "digits"],
        "base": ["radix"],
        "attempt": ["retry", "try_count", "attempt_num"],
    },
    "float": {
        "value": ["num", "number", "x", "amount"],
        "rate": ["ratio", "factor", "multiplier", "percent"],
        "min_value": ["minimum", "lower", "floor"],
        "max_value": ["maximum", "upper", "ceiling"],
        "threshold": ["limit", "cutoff"],
    },
    "boolean": {
        "flag": ["enabled", "active", "on", "value"],
        "strict": ["exact", "precise"],
        "case_sensitive": ["case_insensitive", "ignore_case"],
        "reverse": ["invert", "descending", "desc"],
        "include_empty": ["allow_empty", "keep_empty"],
    },
    "list": {
        "items": ["lst", "list", "values", "array", "elements", "data"],
        "keys": ["key_list", "names"],
        "indices": ["indexes", "positions"],
    },
    "dict": {
        "data": ["obj", "dict", "mapping", "object", "record"],
        "schema": ["structure", "spec", "definition"],
        "defaults": ["default_values", "fallbacks"],
    },
    "any": {
        "value": ["val", "v", "input", "x"],
        "default": ["fallback", "default_value"],
    },
}

CANONICAL_NAMES: Dict[str, str] = {}
_ALIAS_TO_CANONICAL: Dict[str, Dict[str, str]] = {}

for data_type, canonical_map in CANONICAL_BY_TYPE.items():
    _ALIAS_TO_CANONICAL[data_type] = {}
    for canonical, aliases in canonical_map.items():
        CANONICAL_NAMES[canonical] = data_type
        _ALIAS_TO_CANONICAL[data_type][canonical] = canonical
        for alias in aliases:
            _ALIAS_TO_CANONICAL[data_type][alias] = canonical


def get_canonical_name(param_name: str, data_type: str = "any") -> Optional[str]:
    """
    Get the canonical name for a parameter.
    
    Args:
        param_name: The parameter name to look up
        data_type: The data type of the parameter
        
    Returns:
        The canonical name if found, None otherwise
    """
    type_map = _ALIAS_TO_CANONICAL.get(data_type.lower(), {})
    if param_name in type_map:
        return type_map[param_name]
    
    any_map = _ALIAS_TO_CANONICAL.get("any", {})
    if param_name in any_map:
        return any_map[param_name]
    
    for type_key, alias_map in _ALIAS_TO_CANONICAL.items():
        if param_name in alias_map:
            return alias_map[param_name]
    
    return None


def is_canonical(param_name: str) -> bool:
    """Check if a parameter name is already canonical."""
    return param_name in CANONICAL_NAMES


def get_aliases(canonical_name: str, data_type: str = None) -> List[str]:
    """Get all aliases for a canonical name."""
    if data_type:
        canonical_map = CANONICAL_BY_TYPE.get(data_type.lower(), {})
        return canonical_map.get(canonical_name, [])
    
    for type_key, canonical_map in CANONICAL_BY_TYPE.items():
        if canonical_name in canonical_map:
            return canonical_map[canonical_name]
    
    return []


def get_all_valid_names(data_type: str) -> Set[str]:
    """Get all valid parameter names (canonical + aliases) for a data type."""
    valid = set()
    canonical_map = CANONICAL_BY_TYPE.get(data_type.lower(), {})
    for canonical, aliases in canonical_map.items():
        valid.add(canonical)
        valid.update(aliases)
    return valid
