"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Regex Helpers - Pure functions for regex pattern building.
All functions are pure, deterministic, and atomic.
"""

import re


def escape_pattern(text: str) -> str:
    """Escape special regex characters."""
    return re.escape(text)


def create_literal_pattern(text: str) -> str:
    """Create pattern that matches literal text."""
    return re.escape(text)


def create_word_boundary_pattern(word: str) -> str:
    """Create pattern with word boundaries."""
    return r'\b' + re.escape(word) + r'\b'


def create_case_insensitive_pattern(pattern: str) -> str:
    """Add case-insensitive flag to pattern."""
    return f"(?i){pattern}"


def create_multiline_pattern(pattern: str) -> str:
    """Add multiline flag to pattern."""
    return f"(?m){pattern}"


def create_dotall_pattern(pattern: str) -> str:
    """Add dotall flag (dot matches newline)."""
    return f"(?s){pattern}"


def create_optional(pattern: str) -> str:
    """Make pattern optional."""
    return f"(?:{pattern})?"


def create_group(pattern: str) -> str:
    """Create non-capturing group."""
    return f"(?:{pattern})"


def create_named_group(name: str, pattern: str) -> str:
    """Create named capturing group."""
    return f"(?P<{name}>{pattern})"


def create_alternatives(*patterns) -> str:
    """Create alternation pattern."""
    return "|".join(f"(?:{p})" for p in patterns)


def create_sequence(*patterns) -> str:
    """Create sequence pattern."""
    return "".join(patterns)


def create_repeat(pattern: str, min_count: int, max_count: int) -> str:
    """Create repeat pattern."""
    if max_count == -1:
        if min_count == 0:
            return f"(?:{pattern})*"
        elif min_count == 1:
            return f"(?:{pattern})+"
        else:
            return f"(?:{pattern}){{{min_count},}}"
    return f"(?:{pattern}){{{min_count},{max_count}}}"


def create_exactly(pattern: str, count: int) -> str:
    """Create exact repeat pattern."""
    return f"(?:{pattern}){{{count}}}"


def create_at_least(pattern: str, count: int) -> str:
    """Create minimum repeat pattern."""
    return f"(?:{pattern}){{{count},}}"


def create_at_most(pattern: str, count: int) -> str:
    """Create maximum repeat pattern."""
    return f"(?:{pattern}){{0,{count}}}"


def create_lookahead(pattern: str) -> str:
    """Create positive lookahead."""
    return f"(?={pattern})"


def create_negative_lookahead(pattern: str) -> str:
    """Create negative lookahead."""
    return f"(?!{pattern})"


def create_lookbehind(pattern: str) -> str:
    """Create positive lookbehind."""
    return f"(?<={pattern})"


def create_negative_lookbehind(pattern: str) -> str:
    """Create negative lookbehind."""
    return f"(?<!{pattern})"


def create_character_class(chars: str) -> str:
    """Create character class."""
    escaped = chars.replace("\\", "\\\\").replace("]", "\\]").replace("^", "\\^").replace("-", "\\-")
    return f"[{escaped}]"


def create_negated_class(chars: str) -> str:
    """Create negated character class."""
    escaped = chars.replace("\\", "\\\\").replace("]", "\\]").replace("-", "\\-")
    return f"[^{escaped}]"


def create_range(start: str, end: str) -> str:
    """Create character range."""
    return f"[{start}-{end}]"


def match_all(text: str, pattern: str) -> list:
    """Find all matches."""
    return re.findall(pattern, text)


def match_first(text: str, pattern: str) -> str:
    """Find first match."""
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def match_groups(text: str, pattern: str) -> list:
    """Get all groups from first match."""
    match = re.search(pattern, text)
    return list(match.groups()) if match else []


def match_named_groups(text: str, pattern: str) -> dict:
    """Get named groups from first match."""
    match = re.search(pattern, text)
    return match.groupdict() if match else {}


def replace_all(text: str, pattern: str, replacement: str) -> str:
    """Replace all matches."""
    return re.sub(pattern, replacement, text)


def replace_first(text: str, pattern: str, replacement: str) -> str:
    """Replace first match."""
    return re.sub(pattern, replacement, text, count=1)


def split_by_pattern(text: str, pattern: str) -> list:
    """Split text by pattern."""
    return re.split(pattern, text)


def count_matches(text: str, pattern: str) -> int:
    """Count pattern matches."""
    return len(re.findall(pattern, text))


def is_full_match(text: str, pattern: str) -> bool:
    """Check if pattern matches entire text."""
    return bool(re.fullmatch(pattern, text))


def get_match_positions(text: str, pattern: str) -> list:
    """Get start and end positions of all matches."""
    return [(m.start(), m.end()) for m in re.finditer(pattern, text)]


def validate_regex(pattern: str) -> dict:
    """Validate if regex pattern is valid."""
    try:
        re.compile(pattern)
        return {"valid": True, "error": None}
    except re.error as e:
        return {"valid": False, "error": str(e)}


DIGIT = r"\d"
NON_DIGIT = r"\D"
WORD_CHAR = r"\w"
NON_WORD_CHAR = r"\W"
WHITESPACE = r"\s"
NON_WHITESPACE = r"\S"
ANY_CHAR = r"."
START = r"^"
END = r"$"
WORD_BOUNDARY = r"\b"
