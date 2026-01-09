"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Slug Utilities - Pure functions for URL slugs and ID generation.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import re
import hashlib


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def slugify_with_separator(text: str, separator: str) -> str:
    """Convert text to slug with custom separator."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', separator, text)
    return text.strip(separator)


def slugify_preserve_case(text: str) -> str:
    """Convert text to slug preserving case."""
    text = text.strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def slugify_unicode(text: str) -> str:
    """Convert text to slug preserving unicode letters."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def deslugify(slug: str) -> str:
    """Convert slug back to title case text."""
    return slug.replace('-', ' ').replace('_', ' ').title()


def is_valid_slug(slug: str) -> bool:
    """Check if a string is a valid slug."""
    if not slug:
        return False
    return bool(re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug))


def is_valid_slug_extended(slug: str) -> bool:
    """Check if a string is a valid slug (allowing underscores)."""
    if not slug:
        return False
    return bool(re.match(r'^[a-z0-9]+(?:[-_][a-z0-9]+)*$', slug))


def truncate_slug(slug: str, max_length: int) -> str:
    """Truncate a slug to maximum length without breaking words."""
    if len(slug) <= max_length:
        return slug
    truncated = slug[:max_length]
    last_sep = max(truncated.rfind('-'), truncated.rfind('_'))
    if last_sep > 0:
        return truncated[:last_sep]
    return truncated.rstrip('-_')


def unique_slug(base_slug: str, existing_slugs: list) -> str:
    """Generate a unique slug by appending numbers if needed."""
    if base_slug not in existing_slugs:
        return base_slug
    counter = 1
    while f"{base_slug}-{counter}" in existing_slugs:
        counter += 1
    return f"{base_slug}-{counter}"


def hash_based_slug(text: str, length: int) -> str:
    """Generate a hash-based slug of specified length."""
    hash_hex = hashlib.sha256(text.encode()).hexdigest()
    return hash_hex[:length]


def generate_short_id(data: str, length: int) -> str:
    """Generate a short ID from data using hash."""
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    hash_bytes = hashlib.sha256(data.encode()).digest()
    result = []
    for i in range(length):
        index = hash_bytes[i % len(hash_bytes)] % len(alphabet)
        result.append(alphabet[index])
    return ''.join(result)


def generate_base62_id(number: int) -> str:
    """Convert a number to base62 ID."""
    if number == 0:
        return '0'
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    result = []
    while number > 0:
        result.append(alphabet[number % 62])
        number //= 62
    return ''.join(reversed(result))


def parse_base62_id(id_str: str) -> int:
    """Parse a base62 ID back to number."""
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    result = 0
    for char in id_str:
        result = result * 62 + alphabet.index(char)
    return result


def generate_base36_id(number: int) -> str:
    """Convert a number to base36 ID (lowercase alphanumeric)."""
    if number == 0:
        return '0'
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = []
    while number > 0:
        result.append(alphabet[number % 36])
        number //= 36
    return ''.join(reversed(result))


def parse_base36_id(id_str: str) -> int:
    """Parse a base36 ID back to number."""
    return int(id_str, 36)


def slug_to_path(slug: str) -> str:
    """Convert a slug to a file path format."""
    return slug.replace('-', '/').replace('_', '/')


def path_to_slug(path: str) -> str:
    """Convert a path to a slug format."""
    return path.replace('/', '-').replace('\\', '-').strip('-')


def combine_slugs(slugs: list, separator: str) -> str:
    """Combine multiple slugs into one."""
    return separator.join(s for s in slugs if s)


def split_slug(slug: str, separator: str) -> list:
    """Split a slug into parts."""
    return [part for part in slug.split(separator) if part]


def add_slug_suffix(slug: str, suffix: str) -> str:
    """Add a suffix to a slug."""
    return f"{slug}-{suffix}" if slug else suffix


def add_slug_prefix(slug: str, prefix: str) -> str:
    """Add a prefix to a slug."""
    return f"{prefix}-{slug}" if slug else prefix


def remove_slug_suffix(slug: str, suffix: str) -> str:
    """Remove a suffix from a slug."""
    if slug.endswith(f"-{suffix}"):
        return slug[:-len(suffix)-1]
    return slug


def remove_slug_prefix(slug: str, prefix: str) -> str:
    """Remove a prefix from a slug."""
    if slug.startswith(f"{prefix}-"):
        return slug[len(prefix)+1:]
    return slug


def extract_slug_number(slug: str) -> int:
    """Extract trailing number from a slug."""
    match = re.search(r'-(\d+)$', slug)
    return int(match.group(1)) if match else 0


def increment_slug_number(slug: str) -> str:
    """Increment the trailing number in a slug."""
    match = re.search(r'-(\d+)$', slug)
    if match:
        num = int(match.group(1)) + 1
        return slug[:match.start()] + f"-{num}"
    return f"{slug}-1"


def normalize_slug(slug: str) -> str:
    """Normalize a slug by removing duplicate separators."""
    slug = re.sub(r'-+', '-', slug)
    slug = re.sub(r'_+', '_', slug)
    return slug.strip('-_')


def compare_slugs(slug1: str, slug2: str) -> bool:
    """Compare two slugs for equality (case-insensitive)."""
    return normalize_slug(slug1.lower()) == normalize_slug(slug2.lower())


def slug_contains(slug: str, substring: str) -> bool:
    """Check if a slug contains a substring."""
    return substring.lower() in slug.lower()


def generate_readable_id(words: list, separator: str) -> str:
    """Generate a readable ID from word list."""
    return separator.join(word.lower() for word in words)


def obfuscate_id(id_value: int, key: int) -> int:
    """Obfuscate an integer ID with XOR."""
    return id_value ^ key


def deobfuscate_id(obfuscated: int, key: int) -> int:
    """Deobfuscate an XOR obfuscated ID."""
    return obfuscated ^ key


def is_numeric_id(id_str: str) -> bool:
    """Check if an ID string is purely numeric."""
    return id_str.isdigit()


def is_alphanumeric_id(id_str: str) -> bool:
    """Check if an ID string is alphanumeric."""
    return id_str.isalnum()


def pad_numeric_id(id_value: int, width: int) -> str:
    """Pad a numeric ID with leading zeros."""
    return str(id_value).zfill(width)


def format_prefixed_id(prefix: str, id_value: int, width: int) -> str:
    """Format an ID with prefix and zero padding."""
    return f"{prefix}{str(id_value).zfill(width)}"


def parse_prefixed_id(prefixed_id: str, prefix: str) -> int:
    """Parse an ID with prefix to extract the number."""
    if prefixed_id.startswith(prefix):
        try:
            return int(prefixed_id[len(prefix):])
        except ValueError:
            return 0
    return 0


def generate_checksum_digit(number: int) -> int:
    """Generate a simple checksum digit for a number."""
    digits = [int(d) for d in str(number)]
    total = sum((i + 1) * d for i, d in enumerate(digits))
    return total % 10


def validate_checksum_digit(number: int, checksum: int) -> bool:
    """Validate a checksum digit."""
    return generate_checksum_digit(number) == checksum


def encode_timestamp_id(timestamp: int, sequence: int) -> str:
    """Encode a timestamp-based ID."""
    combined = (timestamp << 16) | (sequence & 0xFFFF)
    return generate_base62_id(combined)


def decode_timestamp_id(id_str: str) -> dict:
    """Decode a timestamp-based ID."""
    combined = parse_base62_id(id_str)
    timestamp = combined >> 16
    sequence = combined & 0xFFFF
    return {'timestamp': timestamp, 'sequence': sequence}
