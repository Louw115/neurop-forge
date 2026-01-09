"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Regex Utilities - Pure functions for regex pattern building and validation.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import re


def is_valid_regex(pattern: str) -> bool:
    """Check if a string is a valid regex pattern."""
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def escape_regex(text: str) -> str:
    """Escape special regex characters in a string."""
    return re.escape(text)


def extract_matches(text: str, pattern: str) -> list:
    """Extract all matches of a pattern from text."""
    try:
        return re.findall(pattern, text)
    except re.error:
        return []


def extract_first_match(text: str, pattern: str) -> str:
    """Extract the first match of a pattern from text."""
    try:
        match = re.search(pattern, text)
        return match.group(0) if match else ""
    except re.error:
        return ""


def extract_groups(text: str, pattern: str) -> tuple:
    """Extract capture groups from the first match."""
    try:
        match = re.search(pattern, text)
        return match.groups() if match else ()
    except re.error:
        return ()


def extract_named_groups(text: str, pattern: str) -> dict:
    """Extract named capture groups from the first match."""
    try:
        match = re.search(pattern, text)
        return match.groupdict() if match else {}
    except re.error:
        return {}


def count_matches(text: str, pattern: str) -> int:
    """Count the number of pattern matches in text."""
    try:
        return len(re.findall(pattern, text))
    except re.error:
        return 0


def replace_pattern(text: str, pattern: str, replacement: str) -> str:
    """Replace all occurrences of a pattern with a replacement."""
    try:
        return re.sub(pattern, replacement, text)
    except re.error:
        return text


def replace_first(text: str, pattern: str, replacement: str) -> str:
    """Replace only the first occurrence of a pattern."""
    try:
        return re.sub(pattern, replacement, text, count=1)
    except re.error:
        return text


def split_by_pattern(text: str, pattern: str) -> list:
    """Split text by a regex pattern."""
    try:
        return re.split(pattern, text)
    except re.error:
        return [text]


def split_by_pattern_limit(text: str, pattern: str, max_splits: int) -> list:
    """Split text by a regex pattern with a maximum number of splits."""
    try:
        return re.split(pattern, text, maxsplit=max_splits)
    except re.error:
        return [text]


def matches_pattern(text: str, pattern: str) -> bool:
    """Check if text contains a match for the pattern."""
    try:
        return bool(re.search(pattern, text))
    except re.error:
        return False


def matches_fully(text: str, pattern: str) -> bool:
    """Check if the entire text matches the pattern."""
    try:
        return bool(re.fullmatch(pattern, text))
    except re.error:
        return False


def starts_with_pattern(text: str, pattern: str) -> bool:
    """Check if text starts with a match for the pattern."""
    try:
        return bool(re.match(pattern, text))
    except re.error:
        return False


def build_word_boundary_pattern(word: str) -> str:
    """Build a pattern that matches a word with word boundaries."""
    escaped = re.escape(word)
    return r'\b' + escaped + r'\b'


def build_case_insensitive_pattern(pattern: str) -> str:
    """Build a case-insensitive version of a pattern."""
    return '(?i)' + pattern


def build_multiline_pattern(pattern: str) -> str:
    """Build a multiline version of a pattern."""
    return '(?m)' + pattern


def build_dotall_pattern(pattern: str) -> str:
    """Build a pattern where dot matches newlines."""
    return '(?s)' + pattern


def build_alternation(patterns: list) -> str:
    """Build an alternation pattern from a list of patterns."""
    if not patterns:
        return ""
    return '(' + '|'.join(patterns) + ')'


def build_optional(pattern: str) -> str:
    """Build an optional version of a pattern."""
    return '(' + pattern + ')?'


def build_one_or_more(pattern: str) -> str:
    """Build a one-or-more repetition of a pattern."""
    return '(' + pattern + ')+'


def build_zero_or_more(pattern: str) -> str:
    """Build a zero-or-more repetition of a pattern."""
    return '(' + pattern + ')*'


def build_exactly_n(pattern: str, n: int) -> str:
    """Build a pattern that matches exactly n times."""
    return '(' + pattern + '){' + str(n) + '}'


def build_n_to_m(pattern: str, n: int, m: int) -> str:
    """Build a pattern that matches between n and m times."""
    return '(' + pattern + '){' + str(n) + ',' + str(m) + '}'


def build_at_least_n(pattern: str, n: int) -> str:
    """Build a pattern that matches at least n times."""
    return '(' + pattern + '){' + str(n) + ',}'


def build_non_capturing_group(pattern: str) -> str:
    """Build a non-capturing group."""
    return '(?:' + pattern + ')'


def build_named_group(name: str, pattern: str) -> str:
    """Build a named capture group."""
    return '(?P<' + name + '>' + pattern + ')'


def build_lookahead(pattern: str) -> str:
    """Build a positive lookahead assertion."""
    return '(?=' + pattern + ')'


def build_negative_lookahead(pattern: str) -> str:
    """Build a negative lookahead assertion."""
    return '(?!' + pattern + ')'


def build_lookbehind(pattern: str) -> str:
    """Build a positive lookbehind assertion."""
    return '(?<=' + pattern + ')'


def build_negative_lookbehind(pattern: str) -> str:
    """Build a negative lookbehind assertion."""
    return '(?<!' + pattern + ')'


def build_start_anchor() -> str:
    """Return the start-of-string anchor."""
    return '^'


def build_end_anchor() -> str:
    """Return the end-of-string anchor."""
    return '$'


def build_character_class(chars: str) -> str:
    """Build a character class from a string of characters."""
    escaped = chars.replace('\\', '\\\\').replace(']', '\\]').replace('^', '\\^').replace('-', '\\-')
    return '[' + escaped + ']'


def build_negated_character_class(chars: str) -> str:
    """Build a negated character class from a string of characters."""
    escaped = chars.replace('\\', '\\\\').replace(']', '\\]').replace('^', '\\^').replace('-', '\\-')
    return '[^' + escaped + ']'


def get_pattern_digit() -> str:
    """Return the pattern for a single digit."""
    return r'\d'


def get_pattern_non_digit() -> str:
    """Return the pattern for a non-digit."""
    return r'\D'


def get_pattern_word_char() -> str:
    """Return the pattern for a word character."""
    return r'\w'


def get_pattern_non_word_char() -> str:
    """Return the pattern for a non-word character."""
    return r'\W'


def get_pattern_whitespace() -> str:
    """Return the pattern for whitespace."""
    return r'\s'


def get_pattern_non_whitespace() -> str:
    """Return the pattern for non-whitespace."""
    return r'\S'


def get_pattern_any_char() -> str:
    """Return the pattern for any character (except newline)."""
    return '.'


def get_pattern_email() -> str:
    """Return a pattern for matching email addresses."""
    return r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'


def get_pattern_url() -> str:
    """Return a pattern for matching URLs."""
    return r'https?://[^\s<>"\']+|www\.[^\s<>"\']+'


def get_pattern_ipv4() -> str:
    """Return a pattern for matching IPv4 addresses."""
    return r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'


def get_pattern_phone_us() -> str:
    """Return a pattern for matching US phone numbers."""
    return r'(?:\+1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?)?[0-9]{3}[-.\s]?[0-9]{4}'


def get_pattern_date_iso() -> str:
    """Return a pattern for matching ISO date format (YYYY-MM-DD)."""
    return r'\d{4}-\d{2}-\d{2}'


def get_pattern_time_24h() -> str:
    """Return a pattern for matching 24-hour time format."""
    return r'(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?'


def get_pattern_hex_color() -> str:
    """Return a pattern for matching hex color codes."""
    return r'#(?:[0-9a-fA-F]{3}){1,2}\b'


def get_pattern_credit_card() -> str:
    """Return a pattern for matching credit card numbers."""
    return r'\b(?:\d{4}[-\s]?){3}\d{4}\b'


def find_all_positions(text: str, pattern: str) -> list:
    """Find all match positions as (start, end) tuples."""
    try:
        return [(m.start(), m.end()) for m in re.finditer(pattern, text)]
    except re.error:
        return []


def find_first_position(text: str, pattern: str) -> tuple:
    """Find the first match position as (start, end) tuple."""
    try:
        match = re.search(pattern, text)
        return (match.start(), match.end()) if match else (-1, -1)
    except re.error:
        return (-1, -1)


def remove_pattern(text: str, pattern: str) -> str:
    """Remove all occurrences of a pattern from text."""
    try:
        return re.sub(pattern, '', text)
    except re.error:
        return text


def keep_only_pattern(text: str, pattern: str) -> str:
    """Keep only the parts of text that match the pattern."""
    try:
        return ''.join(re.findall(pattern, text))
    except re.error:
        return ""


def is_only_digits(text: str) -> bool:
    """Check if text contains only digits."""
    return bool(re.fullmatch(r'\d+', text))


def is_only_letters(text: str) -> bool:
    """Check if text contains only letters."""
    return bool(re.fullmatch(r'[a-zA-Z]+', text))


def is_only_alphanumeric(text: str) -> bool:
    """Check if text contains only alphanumeric characters."""
    return bool(re.fullmatch(r'[a-zA-Z0-9]+', text))


def is_only_whitespace(text: str) -> bool:
    """Check if text contains only whitespace."""
    return bool(re.fullmatch(r'\s+', text))


def extract_numbers(text: str) -> list:
    """Extract all numbers (integers and floats) from text."""
    return re.findall(r'-?\d+\.?\d*', text)


def extract_words(text: str) -> list:
    """Extract all words from text."""
    return re.findall(r'\b\w+\b', text)


def extract_sentences(text: str) -> list:
    """Extract sentences from text."""
    return re.findall(r'[^.!?]+[.!?]+', text)


def normalize_whitespace(text: str) -> str:
    """Replace multiple whitespace with single space."""
    return re.sub(r'\s+', ' ', text).strip()


def remove_extra_spaces(text: str) -> str:
    """Remove extra spaces (more than one consecutive space)."""
    return re.sub(r' +', ' ', text)


def camel_to_snake(text: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(text: str) -> str:
    """Convert snake_case to camelCase."""
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def extract_hashtags(text: str) -> list:
    """Extract hashtags from text."""
    return re.findall(r'#\w+', text)


def extract_mentions(text: str) -> list:
    """Extract @mentions from text."""
    return re.findall(r'@\w+', text)


def mask_pattern(text: str, pattern: str, mask_char: str) -> str:
    """Mask all matches of a pattern with a character."""
    def replacer(match):
        return mask_char * len(match.group(0))
    try:
        return re.sub(pattern, replacer, text)
    except re.error:
        return text
