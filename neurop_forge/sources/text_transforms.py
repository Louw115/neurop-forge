"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Text Transforms - Pure functions for text case and format transformations.
All functions are pure, deterministic, and atomic.
"""

import re


def to_uppercase(text: str) -> str:
    """Convert to uppercase."""
    return text.upper()


def to_lowercase(text: str) -> str:
    """Convert to lowercase."""
    return text.lower()


def to_titlecase(text: str) -> str:
    """Convert to title case."""
    return text.title()


def capitalize_first(text: str) -> str:
    """Capitalize first letter only."""
    if not text:
        return text
    return text[0].upper() + text[1:]


def capitalize_sentences(text: str) -> str:
    """Capitalize first letter of each sentence."""
    sentences = re.split(r'([.!?]\s+)', text)
    result = []
    for i, part in enumerate(sentences):
        if i == 0 or (i > 0 and sentences[i-1].strip() in '.!?'):
            result.append(capitalize_first(part))
        else:
            result.append(part)
    return ''.join(result)


def to_camelcase(text: str) -> str:
    """Convert to camelCase."""
    words = re.split(r'[\s_\-]+', text)
    if not words:
        return ""
    return words[0].lower() + ''.join(w.capitalize() for w in words[1:])


def to_pascalcase(text: str) -> str:
    """Convert to PascalCase."""
    words = re.split(r'[\s_\-]+', text)
    return ''.join(w.capitalize() for w in words)


def to_snakecase(text: str) -> str:
    """Convert to snake_case."""
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
    text = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', text)
    text = re.sub(r'[\s\-]+', '_', text)
    return text.lower()


def to_kebabcase(text: str) -> str:
    """Convert to kebab-case."""
    return to_snakecase(text).replace('_', '-')


def to_constantcase(text: str) -> str:
    """Convert to CONSTANT_CASE."""
    return to_snakecase(text).upper()


def to_dotcase(text: str) -> str:
    """Convert to dot.case."""
    return to_snakecase(text).replace('_', '.')


def to_pathcase(text: str) -> str:
    """Convert to path/case."""
    return to_snakecase(text).replace('_', '/')


def swap_case(text: str) -> str:
    """Swap character cases."""
    return text.swapcase()


def strip_whitespace(text: str) -> str:
    """Remove leading and trailing whitespace."""
    return text.strip()


def strip_left(text: str) -> str:
    """Remove leading whitespace."""
    return text.lstrip()


def strip_right(text: str) -> str:
    """Remove trailing whitespace."""
    return text.rstrip()


def collapse_whitespace(text: str) -> str:
    """Collapse multiple whitespace to single space."""
    return re.sub(r'\s+', ' ', text)


def remove_whitespace(text: str) -> str:
    """Remove all whitespace."""
    return re.sub(r'\s', '', text)


def slugify(text: str) -> str:
    """Convert to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def strip_html(text: str) -> str:
    """Remove HTML tags."""
    return re.sub(r'<[^>]+>', '', text)


def strip_non_ascii(text: str) -> str:
    """Remove non-ASCII characters."""
    return ''.join(c for c in text if ord(c) < 128)


def strip_numbers(text: str) -> str:
    """Remove all numbers."""
    return re.sub(r'\d', '', text)


def strip_punctuation(text: str) -> str:
    """Remove punctuation."""
    return re.sub(r'[^\w\s]', '', text)


def normalize_unicode(text: str) -> str:
    """Normalize Unicode to NFC form."""
    import unicodedata
    return unicodedata.normalize('NFC', text)


def remove_accents(text: str) -> str:
    """Remove accents from characters."""
    import unicodedata
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def truncate(text: str, max_length: int, suffix: str) -> str:
    """Truncate text with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def truncate_words(text: str, max_words: int, suffix: str) -> str:
    """Truncate to word count."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + suffix


def repeat(text: str, count: int) -> str:
    """Repeat text n times."""
    return text * count


def reverse(text: str) -> str:
    """Reverse text."""
    return text[::-1]


def reverse_words(text: str) -> str:
    """Reverse word order."""
    return ' '.join(text.split()[::-1])


def center(text: str, width: int, char: str) -> str:
    """Center text with padding."""
    return text.center(width, char)


def pad_left(text: str, width: int, char: str) -> str:
    """Pad text on left."""
    return text.rjust(width, char)


def pad_right(text: str, width: int, char: str) -> str:
    """Pad text on right."""
    return text.ljust(width, char)


def wrap_text(text: str, width: int) -> list:
    """Wrap text to width."""
    words = text.split()
    lines = []
    current = []
    length = 0
    for word in words:
        if length + len(word) + len(current) <= width:
            current.append(word)
            length += len(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
            length = len(word)
    if current:
        lines.append(' '.join(current))
    return lines


def dedent(text: str) -> str:
    """Remove common leading whitespace."""
    lines = text.split('\n')
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return text
    min_indent = min(len(l) - len(l.lstrip()) for l in non_empty)
    return '\n'.join(l[min_indent:] if len(l) >= min_indent else l for l in lines)


def indent(text: str, spaces: int) -> str:
    """Add indentation to each line."""
    prefix = ' ' * spaces
    return '\n'.join(prefix + l for l in text.split('\n'))
