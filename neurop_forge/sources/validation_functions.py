"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Validation Functions - Pure functions for data validation.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import re


def is_empty(value) -> bool:
    """Check if a value is empty (None, empty string, empty list, etc.)."""
    if value is None:
        return True
    if isinstance(value, str) and len(value) == 0:
        return True
    if isinstance(value, (list, dict, tuple, set)) and len(value) == 0:
        return True
    return False


def is_not_empty(value) -> bool:
    """Check if a value is not empty."""
    return not is_empty(value)


def is_none(value) -> bool:
    """Check if a value is None."""
    return value is None


def is_not_none(value) -> bool:
    """Check if a value is not None."""
    return value is not None


def is_numeric_string(text: str) -> bool:
    """Check if a string represents a valid number."""
    if not text:
        return False
    try:
        float(text)
        return True
    except ValueError:
        return False


def is_integer_string(text: str) -> bool:
    """Check if a string represents a valid integer."""
    if not text:
        return False
    try:
        int(text)
        return True
    except ValueError:
        return False


def is_positive_number(value: float) -> bool:
    """Check if a number is positive (greater than zero)."""
    return value > 0


def is_negative_number(value: float) -> bool:
    """Check if a number is negative (less than zero)."""
    return value < 0


def is_zero(value: float) -> bool:
    """Check if a number is zero."""
    return value == 0


def is_non_negative(value: float) -> bool:
    """Check if a number is non-negative (zero or positive)."""
    return value >= 0


def is_non_positive(value: float) -> bool:
    """Check if a number is non-positive (zero or negative)."""
    return value <= 0


def is_in_range(value: float, min_val: float, max_val: float) -> bool:
    """Check if a number is within a range (inclusive)."""
    return min_val <= value <= max_val


def is_in_range_exclusive(value: float, min_val: float, max_val: float) -> bool:
    """Check if a number is within a range (exclusive)."""
    return min_val < value < max_val


def is_even(value: int) -> bool:
    """Check if an integer is even."""
    return value % 2 == 0


def is_odd(value: int) -> bool:
    """Check if an integer is odd."""
    return value % 2 != 0


def is_valid_email(email: str) -> bool:
    """Check if a string is a valid email address format."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL format."""
    if not url:
        return False
    pattern = r'^https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})+(?:/[^\s]*)?$'
    return bool(re.match(pattern, url))


def is_valid_phone(phone: str) -> bool:
    """Check if a string is a valid phone number format."""
    if not phone:
        return False
    cleaned = re.sub(r'[\s\-\.\(\)]', '', phone)
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, cleaned))


def is_valid_uuid(uuid_string: str) -> bool:
    """Check if a string is a valid UUID format."""
    if not uuid_string:
        return False
    pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    return bool(re.match(pattern, uuid_string))


def is_valid_hex_color(color: str) -> bool:
    """Check if a string is a valid hex color code."""
    if not color:
        return False
    pattern = r'^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$'
    return bool(re.match(pattern, color))


def is_valid_ipv4(ip: str) -> bool:
    """Check if a string is a valid IPv4 address."""
    if not ip:
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    return True


def has_minimum_length(text: str, min_length: int) -> bool:
    """Check if a string has at least the minimum length."""
    return len(text) >= min_length


def has_maximum_length(text: str, max_length: int) -> bool:
    """Check if a string does not exceed the maximum length."""
    return len(text) <= max_length


def is_length_between(text: str, min_length: int, max_length: int) -> bool:
    """Check if a string length is between min and max (inclusive)."""
    length = len(text)
    return min_length <= length <= max_length


def contains_uppercase(text: str) -> bool:
    """Check if a string contains at least one uppercase letter."""
    return any(c.isupper() for c in text)


def contains_lowercase(text: str) -> bool:
    """Check if a string contains at least one lowercase letter."""
    return any(c.islower() for c in text)


def contains_digit(text: str) -> bool:
    """Check if a string contains at least one digit."""
    return any(c.isdigit() for c in text)


def contains_special_char(text: str) -> bool:
    """Check if a string contains at least one special character."""
    special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    return any(c in special_chars for c in text)


def matches_pattern(text: str, pattern: str) -> bool:
    """Check if a string matches a regex pattern."""
    if not text or not pattern:
        return False
    try:
        return bool(re.match(pattern, text))
    except re.error:
        return False
