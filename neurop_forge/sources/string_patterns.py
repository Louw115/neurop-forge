"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
String Patterns - Pure functions for pattern matching and manipulation.
All functions are pure, deterministic, and atomic.
"""

def starts_with(text: str, prefix: str) -> bool:
    """Check if text starts with prefix."""
    return text.startswith(prefix)


def ends_with(text: str, suffix: str) -> bool:
    """Check if text ends with suffix."""
    return text.endswith(suffix)


def contains(text: str, substring: str) -> bool:
    """Check if text contains substring."""
    return substring in text


def contains_any(text: str, substrings: list) -> bool:
    """Check if text contains any of the substrings."""
    return any(s in text for s in substrings)


def contains_all(text: str, substrings: list) -> bool:
    """Check if text contains all substrings."""
    return all(s in text for s in substrings)


def count_occurrences(text: str, substring: str) -> int:
    """Count occurrences of substring."""
    return text.count(substring)


def find_all(text: str, substring: str) -> list:
    """Find all occurrences of substring."""
    positions = []
    start = 0
    while True:
        pos = text.find(substring, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


def replace_first(text: str, old: str, new: str) -> str:
    """Replace first occurrence."""
    return text.replace(old, new, 1)


def replace_last(text: str, old: str, new: str) -> str:
    """Replace last occurrence."""
    pos = text.rfind(old)
    if pos == -1:
        return text
    return text[:pos] + new + text[pos + len(old):]


def remove_prefix(text: str, prefix: str) -> str:
    """Remove prefix if present."""
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def remove_suffix(text: str, suffix: str) -> str:
    """Remove suffix if present."""
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text


def ensure_prefix(text: str, prefix: str) -> str:
    """Ensure text starts with prefix."""
    if text.startswith(prefix):
        return text
    return prefix + text


def ensure_suffix(text: str, suffix: str) -> str:
    """Ensure text ends with suffix."""
    if text.endswith(suffix):
        return text
    return text + suffix


def pad_left(text: str, length: int, char: str) -> str:
    """Pad text on the left."""
    return text.rjust(length, char)


def pad_right(text: str, length: int, char: str) -> str:
    """Pad text on the right."""
    return text.ljust(length, char)


def pad_center(text: str, length: int, char: str) -> str:
    """Pad text in the center."""
    return text.center(length, char)


def truncate(text: str, max_length: int, suffix: str) -> str:
    """Truncate text with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def truncate_words(text: str, max_words: int, suffix: str) -> str:
    """Truncate to max words."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + suffix


def wrap_text(text: str, width: int) -> list:
    """Wrap text to specified width."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    for word in words:
        if current_length + len(word) + len(current_line) <= width:
            current_line.append(word)
            current_length += len(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def indent_text(text: str, spaces: int) -> str:
    """Indent each line."""
    indent = " " * spaces
    return "\n".join(indent + line for line in text.split("\n"))


def dedent_text(text: str, spaces: int) -> str:
    """Remove indentation from each line."""
    lines = []
    for line in text.split("\n"):
        if line.startswith(" " * spaces):
            lines.append(line[spaces:])
        else:
            lines.append(line.lstrip())
    return "\n".join(lines)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace to single spaces."""
    return " ".join(text.split())


def collapse_whitespace(text: str) -> str:
    """Collapse multiple whitespace to single."""
    import re
    return re.sub(r'\s+', ' ', text)


def remove_whitespace(text: str) -> str:
    """Remove all whitespace."""
    return "".join(text.split())


def extract_between(text: str, start_marker: str, end_marker: str) -> str:
    """Extract text between markers."""
    start_pos = text.find(start_marker)
    if start_pos == -1:
        return ""
    start_pos += len(start_marker)
    end_pos = text.find(end_marker, start_pos)
    if end_pos == -1:
        return ""
    return text[start_pos:end_pos]


def extract_all_between(text: str, start_marker: str, end_marker: str) -> list:
    """Extract all texts between markers."""
    results = []
    start = 0
    while True:
        start_pos = text.find(start_marker, start)
        if start_pos == -1:
            break
        start_pos += len(start_marker)
        end_pos = text.find(end_marker, start_pos)
        if end_pos == -1:
            break
        results.append(text[start_pos:end_pos])
        start = end_pos + len(end_marker)
    return results


def split_at(text: str, position: int) -> tuple:
    """Split text at position."""
    return (text[:position], text[position:])


def split_lines(text: str) -> list:
    """Split text into lines."""
    return text.splitlines()


def join_lines(lines: list, separator: str) -> str:
    """Join lines with separator."""
    return separator.join(lines)


def reverse_string(text: str) -> str:
    """Reverse a string."""
    return text[::-1]


def is_palindrome(text: str) -> bool:
    """Check if text is a palindrome."""
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


def common_prefix(strings: list) -> str:
    """Find common prefix of strings."""
    if not strings:
        return ""
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


def common_suffix(strings: list) -> str:
    """Find common suffix of strings."""
    if not strings:
        return ""
    suffix = strings[0]
    for s in strings[1:]:
        while not s.endswith(suffix):
            suffix = suffix[1:]
            if not suffix:
                return ""
    return suffix


def mask_string(text: str, start: int, end: int, mask_char: str) -> str:
    """Mask portion of string."""
    if start >= len(text):
        return text
    end = min(end, len(text))
    return text[:start] + mask_char * (end - start) + text[end:]


def repeat_string(text: str, count: int) -> str:
    """Repeat string count times."""
    return text * count


def interleave_strings(s1: str, s2: str) -> str:
    """Interleave two strings."""
    result = []
    for i in range(max(len(s1), len(s2))):
        if i < len(s1):
            result.append(s1[i])
        if i < len(s2):
            result.append(s2[i])
    return "".join(result)
