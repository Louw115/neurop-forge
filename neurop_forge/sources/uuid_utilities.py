"""
UUID Utilities - Pure functions for UUID validation, parsing, and analysis.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import re


def is_valid_uuid(text: str) -> bool:
    """Check if a string is a valid UUID (any version)."""
    pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    return bool(re.match(pattern, text))


def is_valid_uuid_v4(text: str) -> bool:
    """Check if a string is a valid UUID version 4."""
    pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
    return bool(re.match(pattern, text))


def is_valid_uuid_v1(text: str) -> bool:
    """Check if a string is a valid UUID version 1."""
    pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-1[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
    return bool(re.match(pattern, text))


def is_valid_uuid_v3(text: str) -> bool:
    """Check if a string is a valid UUID version 3."""
    pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-3[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
    return bool(re.match(pattern, text))


def is_valid_uuid_v5(text: str) -> bool:
    """Check if a string is a valid UUID version 5."""
    pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-5[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
    return bool(re.match(pattern, text))


def get_uuid_version(uuid_str: str) -> int:
    """Get the version number of a UUID. Returns 0 if invalid."""
    if not is_valid_uuid(uuid_str):
        return 0
    version_char = uuid_str[14]
    if version_char in '12345':
        return int(version_char)
    return 0


def get_uuid_variant(uuid_str: str) -> str:
    """Get the variant of a UUID."""
    if not is_valid_uuid(uuid_str):
        return "invalid"
    variant_char = uuid_str[19].lower()
    if variant_char in '89ab':
        return "RFC4122"
    elif variant_char in '0123456789':
        return "NCS"
    elif variant_char in 'cd':
        return "Microsoft"
    else:
        return "Reserved"


def normalize_uuid(uuid_str: str) -> str:
    """Normalize a UUID to lowercase with hyphens."""
    cleaned = uuid_str.replace('-', '').replace('{', '').replace('}', '').lower()
    if len(cleaned) != 32:
        return ""
    return f"{cleaned[:8]}-{cleaned[8:12]}-{cleaned[12:16]}-{cleaned[16:20]}-{cleaned[20:]}"


def uuid_to_uppercase(uuid_str: str) -> str:
    """Convert a UUID to uppercase format."""
    normalized = normalize_uuid(uuid_str)
    return normalized.upper() if normalized else ""


def uuid_to_lowercase(uuid_str: str) -> str:
    """Convert a UUID to lowercase format."""
    return normalize_uuid(uuid_str)


def uuid_to_urn(uuid_str: str) -> str:
    """Convert a UUID to URN format."""
    normalized = normalize_uuid(uuid_str)
    return f"urn:uuid:{normalized}" if normalized else ""


def urn_to_uuid(urn: str) -> str:
    """Extract UUID from URN format."""
    if urn.lower().startswith('urn:uuid:'):
        return normalize_uuid(urn[9:])
    return ""


def uuid_to_hex(uuid_str: str) -> str:
    """Convert a UUID to hex string without hyphens."""
    return normalize_uuid(uuid_str).replace('-', '')


def hex_to_uuid(hex_str: str) -> str:
    """Convert a 32-character hex string to UUID format."""
    cleaned = hex_str.lower()
    if len(cleaned) != 32 or not all(c in '0123456789abcdef' for c in cleaned):
        return ""
    return f"{cleaned[:8]}-{cleaned[8:12]}-{cleaned[12:16]}-{cleaned[16:20]}-{cleaned[20:]}"


def uuid_to_bytes_hex(uuid_str: str) -> str:
    """Convert UUID to bytes representation as hex string."""
    hex_str = uuid_to_hex(uuid_str)
    return hex_str if hex_str else ""


def uuid_to_int(uuid_str: str) -> int:
    """Convert UUID to its integer representation."""
    hex_str = uuid_to_hex(uuid_str)
    return int(hex_str, 16) if hex_str else 0


def int_to_uuid(value: int) -> str:
    """Convert an integer to UUID format."""
    if value < 0:
        return ""
    hex_str = format(value, '032x')
    return hex_to_uuid(hex_str)


def compare_uuids(uuid1: str, uuid2: str) -> int:
    """Compare two UUIDs. Returns -1, 0, or 1."""
    n1 = normalize_uuid(uuid1)
    n2 = normalize_uuid(uuid2)
    if not n1 or not n2:
        return 0
    if n1 < n2:
        return -1
    elif n1 > n2:
        return 1
    return 0


def uuids_equal(uuid1: str, uuid2: str) -> bool:
    """Check if two UUIDs are equal (case-insensitive)."""
    return normalize_uuid(uuid1) == normalize_uuid(uuid2)


def is_nil_uuid(uuid_str: str) -> bool:
    """Check if a UUID is the nil UUID (all zeros)."""
    return normalize_uuid(uuid_str) == "00000000-0000-0000-0000-000000000000"


def get_nil_uuid() -> str:
    """Return the nil UUID."""
    return "00000000-0000-0000-0000-000000000000"


def is_max_uuid(uuid_str: str) -> bool:
    """Check if a UUID is the max UUID (all ones)."""
    return normalize_uuid(uuid_str) == "ffffffff-ffff-ffff-ffff-ffffffffffff"


def get_max_uuid() -> str:
    """Return the max UUID."""
    return "ffffffff-ffff-ffff-ffff-ffffffffffff"


def extract_timestamp_v1(uuid_str: str) -> int:
    """Extract timestamp from UUID v1 (returns 0 if not v1)."""
    if not is_valid_uuid_v1(uuid_str):
        return 0
    hex_str = uuid_to_hex(uuid_str)
    time_low = hex_str[0:8]
    time_mid = hex_str[8:12]
    time_hi = hex_str[12:16]
    time_hi_version = int(time_hi, 16) & 0x0FFF
    timestamp = int(time_low, 16) + (int(time_mid, 16) << 32) + (time_hi_version << 48)
    return timestamp


def extract_clock_seq_v1(uuid_str: str) -> int:
    """Extract clock sequence from UUID v1 (returns 0 if not v1)."""
    if not is_valid_uuid_v1(uuid_str):
        return 0
    hex_str = uuid_to_hex(uuid_str)
    clock_seq_hi = int(hex_str[16:18], 16) & 0x3F
    clock_seq_low = int(hex_str[18:20], 16)
    return (clock_seq_hi << 8) | clock_seq_low


def extract_node_v1(uuid_str: str) -> str:
    """Extract node (MAC address) from UUID v1."""
    if not is_valid_uuid_v1(uuid_str):
        return ""
    hex_str = uuid_to_hex(uuid_str)
    node = hex_str[20:32]
    return ':'.join(node[i:i+2] for i in range(0, 12, 2))


def format_uuid_with_braces(uuid_str: str) -> str:
    """Format UUID with curly braces (Windows/GUID style)."""
    normalized = normalize_uuid(uuid_str)
    return f"{{{normalized.upper()}}}" if normalized else ""


def parse_braced_uuid(braced: str) -> str:
    """Parse a UUID from braced format."""
    if braced.startswith('{') and braced.endswith('}'):
        return normalize_uuid(braced[1:-1])
    return ""


def is_valid_ulid(text: str) -> bool:
    """Check if a string is a valid ULID format."""
    pattern = r'^[0-9A-HJKMNP-TV-Z]{26}$'
    return bool(re.match(pattern, text, re.IGNORECASE))


def is_valid_ksuid(text: str) -> bool:
    """Check if a string is a valid KSUID format (27 characters, base62)."""
    pattern = r'^[0-9A-Za-z]{27}$'
    return bool(re.match(pattern, text))


def is_valid_nanoid(text: str, expected_length: int) -> bool:
    """Check if a string could be a valid NanoID of expected length."""
    if len(text) != expected_length:
        return False
    pattern = r'^[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, text))


def get_uuid_time_part(uuid_str: str) -> str:
    """Get the time-related portion of the UUID."""
    normalized = normalize_uuid(uuid_str)
    if not normalized:
        return ""
    return normalized[:18]


def get_uuid_random_part(uuid_str: str) -> str:
    """Get the random/node portion of the UUID."""
    normalized = normalize_uuid(uuid_str)
    if not normalized:
        return ""
    return normalized[19:]


def mask_uuid(uuid_str: str, visible_chars: int) -> str:
    """Mask a UUID showing only first N characters."""
    normalized = normalize_uuid(uuid_str)
    if not normalized:
        return ""
    if visible_chars <= 0:
        return "********-****-****-****-************"
    visible = normalized[:visible_chars]
    masked_part = normalized[visible_chars:].replace('-', '*').replace('a', '*').replace('b', '*').replace('c', '*').replace('d', '*').replace('e', '*').replace('f', '*')
    for i in '0123456789':
        masked_part = masked_part.replace(i, '*')
    result = visible + masked_part
    return result[:8] + '-' + result[8:12].replace('-', '') + '-' + result[12:16].replace('-', '') + '-' + result[16:20].replace('-', '') + '-' + result[20:].replace('-', '')


def extract_uuids_from_text(text: str) -> list:
    """Extract all UUIDs from a text string."""
    pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    return re.findall(pattern, text)


def count_uuids_in_text(text: str) -> int:
    """Count the number of UUIDs in a text string."""
    return len(extract_uuids_from_text(text))


def sort_uuids(uuids: list) -> list:
    """Sort a list of UUIDs lexicographically."""
    normalized = [(normalize_uuid(u), u) for u in uuids if normalize_uuid(u)]
    normalized.sort(key=lambda x: x[0])
    return [orig for _, orig in normalized]


def deduplicate_uuids(uuids: list) -> list:
    """Remove duplicate UUIDs (case-insensitive comparison)."""
    seen = set()
    result = []
    for uuid in uuids:
        normalized = normalize_uuid(uuid)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(uuid)
    return result
