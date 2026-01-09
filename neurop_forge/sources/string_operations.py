"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
String Operations - Pure functions for string manipulation.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def trim_whitespace(text: str) -> str:
    """Remove leading and trailing whitespace from a string."""
    return text.strip()


def trim_left(text: str) -> str:
    """Remove leading whitespace from a string."""
    return text.lstrip()


def trim_right(text: str) -> str:
    """Remove trailing whitespace from a string."""
    return text.rstrip()


def to_uppercase(text: str) -> str:
    """Convert a string to uppercase."""
    return text.upper()


def to_lowercase(text: str) -> str:
    """Convert a string to lowercase."""
    return text.lower()


def capitalize_first(text: str) -> str:
    """Capitalize the first character of a string."""
    return text.capitalize()


def capitalize_words(text: str) -> str:
    """Capitalize the first character of each word in a string."""
    return text.title()


def reverse_string(text: str) -> str:
    """Reverse the characters in a string."""
    return text[::-1]


def string_length(text: str) -> int:
    """Return the length of a string."""
    return len(text)


def contains_substring(text: str, substring: str) -> bool:
    """Check if a string contains a substring."""
    return substring in text


def starts_with_prefix(text: str, prefix: str) -> bool:
    """Check if a string starts with a prefix."""
    return text.startswith(prefix)


def ends_with_suffix(text: str, suffix: str) -> bool:
    """Check if a string ends with a suffix."""
    return text.endswith(suffix)


def replace_substring(text: str, old: str, new: str) -> str:
    """Replace all occurrences of old substring with new substring."""
    return text.replace(old, new)


def replace_first(text: str, old: str, new: str) -> str:
    """Replace only the first occurrence of old substring with new substring."""
    return text.replace(old, new, 1)


def split_by_delimiter(text: str, delimiter: str) -> list:
    """Split a string by a delimiter into a list of substrings."""
    return text.split(delimiter)


def split_lines(text: str) -> list:
    """Split a string into lines."""
    return text.splitlines()


def join_with_delimiter(items: list, delimiter: str) -> str:
    """Join a list of strings with a delimiter."""
    return delimiter.join(str(item) for item in items)


def pad_left(text: str, width: int, fill_char: str) -> str:
    """Pad a string on the left to reach the specified width."""
    if len(fill_char) != 1:
        fill_char = ' '
    return text.rjust(width, fill_char)


def pad_right(text: str, width: int, fill_char: str) -> str:
    """Pad a string on the right to reach the specified width."""
    if len(fill_char) != 1:
        fill_char = ' '
    return text.ljust(width, fill_char)


def pad_center(text: str, width: int, fill_char: str) -> str:
    """Pad a string on both sides to center it within the specified width."""
    if len(fill_char) != 1:
        fill_char = ' '
    return text.center(width, fill_char)


def truncate_string(text: str, max_length: int) -> str:
    """Truncate a string to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length]


def truncate_with_ellipsis(text: str, max_length: int) -> str:
    """Truncate a string and add ellipsis if it exceeds max length."""
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        return text[:max_length]
    return text[:max_length - 3] + "..."


def repeat_string(text: str, count: int) -> str:
    """Repeat a string a specified number of times."""
    if count < 0:
        return ""
    return text * count


def count_occurrences(text: str, substring: str) -> int:
    """Count the number of occurrences of a substring in a string."""
    return text.count(substring)


def find_position(text: str, substring: str) -> int:
    """Find the position of the first occurrence of substring. Returns -1 if not found."""
    return text.find(substring)


def extract_substring(text: str, start: int, end: int) -> str:
    """Extract a substring from start to end position."""
    return text[start:end]


def remove_prefix(text: str, prefix: str) -> str:
    """Remove a prefix from a string if present."""
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def remove_suffix(text: str, suffix: str) -> str:
    """Remove a suffix from a string if present."""
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text


def is_empty_string(text: str) -> bool:
    """Check if a string is empty."""
    return len(text) == 0


def is_blank_string(text: str) -> bool:
    """Check if a string is empty or contains only whitespace."""
    return len(text.strip()) == 0


def is_alphabetic(text: str) -> bool:
    """Check if a string contains only alphabetic characters."""
    return text.isalpha() if text else False


def is_alphanumeric(text: str) -> bool:
    """Check if a string contains only alphanumeric characters."""
    return text.isalnum() if text else False


def is_digits_only(text: str) -> bool:
    """Check if a string contains only digit characters."""
    return text.isdigit() if text else False
