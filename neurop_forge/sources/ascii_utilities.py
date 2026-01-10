"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
ASCII Utilities - Pure functions for ASCII text operations.
All functions are pure, deterministic, and atomic.
"""

def is_ascii(char: str) -> bool:
    """Check if character is ASCII."""
    return ord(char) < 128


def is_printable_ascii(char: str) -> bool:
    """Check if character is printable ASCII."""
    return 32 <= ord(char) < 127


def is_control_char(char: str) -> bool:
    """Check if character is control character."""
    return ord(char) < 32 or ord(char) == 127


def is_uppercase_letter(char: str) -> bool:
    """Check if character is uppercase letter."""
    return 65 <= ord(char) <= 90


def is_lowercase_letter(char: str) -> bool:
    """Check if character is lowercase letter."""
    return 97 <= ord(char) <= 122


def is_letter(char: str) -> bool:
    """Check if character is letter."""
    return is_uppercase_letter(char) or is_lowercase_letter(char)


def is_digit(char: str) -> bool:
    """Check if character is digit."""
    return 48 <= ord(char) <= 57


def is_alphanumeric(char: str) -> bool:
    """Check if character is alphanumeric."""
    return is_letter(char) or is_digit(char)


def is_whitespace(char: str) -> bool:
    """Check if character is whitespace."""
    return char in ' \t\n\r\f\v'


def is_punctuation(char: str) -> bool:
    """Check if character is punctuation."""
    return is_printable_ascii(char) and not is_alphanumeric(char) and not is_whitespace(char)


def to_uppercase_char(char: str) -> str:
    """Convert character to uppercase."""
    if is_lowercase_letter(char):
        return chr(ord(char) - 32)
    return char


def to_lowercase_char(char: str) -> str:
    """Convert character to lowercase."""
    if is_uppercase_letter(char):
        return chr(ord(char) + 32)
    return char


def char_to_digit(char: str) -> int:
    """Convert digit character to integer."""
    if is_digit(char):
        return ord(char) - 48
    return -1


def digit_to_char(digit: int) -> str:
    """Convert integer 0-9 to character."""
    if 0 <= digit <= 9:
        return chr(48 + digit)
    return ''


def get_char_name(char: str) -> str:
    """Get name of ASCII character."""
    code = ord(char)
    names = {
        0: "NUL", 7: "BEL", 8: "BS", 9: "TAB", 10: "LF",
        13: "CR", 27: "ESC", 32: "SPACE", 127: "DEL"
    }
    if code in names:
        return names[code]
    if is_printable_ascii(char):
        return char
    return f"0x{code:02X}"


def strip_non_ascii(text: str) -> str:
    """Remove non-ASCII characters."""
    return ''.join(c for c in text if is_ascii(c))


def replace_non_ascii(text: str, replacement: str) -> str:
    """Replace non-ASCII characters."""
    return ''.join(c if is_ascii(c) else replacement for c in text)


def count_ascii(text: str) -> int:
    """Count ASCII characters."""
    return sum(1 for c in text if is_ascii(c))


def count_non_ascii(text: str) -> int:
    """Count non-ASCII characters."""
    return sum(1 for c in text if not is_ascii(c))


def has_non_ascii(text: str) -> bool:
    """Check if text contains non-ASCII."""
    return any(not is_ascii(c) for c in text)


def ascii_only(text: str) -> bool:
    """Check if text is ASCII only."""
    return all(is_ascii(c) for c in text)


def char_frequency(text: str) -> dict:
    """Get frequency of each ASCII character."""
    freq = {}
    for c in text:
        if is_ascii(c):
            freq[c] = freq.get(c, 0) + 1
    return freq


def create_ascii_table(start: int, end: int) -> list:
    """Create ASCII table for range."""
    return [{"code": i, "char": chr(i), "hex": f"0x{i:02X}"} for i in range(start, end)]


def printable_ascii_chars() -> str:
    """Get all printable ASCII characters."""
    return ''.join(chr(i) for i in range(32, 127))


def uppercase_letters() -> str:
    """Get all uppercase letters."""
    return ''.join(chr(i) for i in range(65, 91))


def lowercase_letters() -> str:
    """Get all lowercase letters."""
    return ''.join(chr(i) for i in range(97, 123))


def digits() -> str:
    """Get all digit characters."""
    return ''.join(chr(i) for i in range(48, 58))


def escape_control_chars(text: str) -> str:
    """Escape control characters."""
    result = []
    for c in text:
        if is_control_char(c):
            result.append(f'\\x{ord(c):02X}')
        else:
            result.append(c)
    return ''.join(result)


def unescape_control_chars(text: str) -> str:
    """Unescape control characters."""
    import re
    def replace(match):
        return chr(int(match.group(1), 16))
    return re.sub(r'\\x([0-9A-Fa-f]{2})', replace, text)


def is_valid_identifier_char(char: str, first: bool) -> bool:
    """Check if valid identifier character."""
    if first:
        return is_letter(char) or char == '_'
    return is_alphanumeric(char) or char == '_'


def is_valid_identifier(text: str) -> bool:
    """Check if valid identifier."""
    if not text:
        return False
    if not is_valid_identifier_char(text[0], True):
        return False
    return all(is_valid_identifier_char(c, False) for c in text[1:])
