"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Formatting Utilities - Pure functions for formatting data for display.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def format_number(value: float, decimals: int) -> str:
    """Format a number with specified decimal places."""
    return f"{value:.{decimals}f}"


def format_number_with_commas(value: float) -> str:
    """Format a number with thousands separators."""
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.2f}"


def format_percentage(value: float, decimals: int) -> str:
    """Format a decimal as a percentage."""
    return f"{value * 100:.{decimals}f}%"


def format_currency_usd(value: float) -> str:
    """Format a number as USD currency."""
    if value < 0:
        return f"-${abs(value):,.2f}"
    return f"${value:,.2f}"


def format_currency_eur(value: float) -> str:
    """Format a number as EUR currency."""
    if value < 0:
        return f"-{abs(value):,.2f}"
    return f"{value:,.2f}"


def format_bytes(bytes_value: int) -> str:
    """Format bytes as human-readable string."""
    if bytes_value < 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    value = float(bytes_value)
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"
    return f"{value:.2f} {units[unit_index]}"


def format_bytes_binary(bytes_value: int) -> str:
    """Format bytes using binary units (KiB, MiB, etc.)."""
    if bytes_value < 0:
        return "0 B"
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    unit_index = 0
    value = float(bytes_value)
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"
    return f"{value:.2f} {units[unit_index]}"


def format_duration_seconds(seconds: int) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 0:
        return "0s"
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    secs = seconds % 60
    if minutes < 60:
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    if hours < 24:
        parts = [f"{hours}h"]
        if mins:
            parts.append(f"{mins}m")
        if secs:
            parts.append(f"{secs}s")
        return ' '.join(parts)
    days = hours // 24
    hrs = hours % 24
    parts = [f"{days}d"]
    if hrs:
        parts.append(f"{hrs}h")
    if mins:
        parts.append(f"{mins}m")
    return ' '.join(parts)


def format_duration_milliseconds(ms: int) -> str:
    """Format milliseconds as human-readable duration."""
    if ms < 0:
        return "0ms"
    if ms < 1000:
        return f"{ms}ms"
    return format_duration_seconds(ms // 1000)


def format_ordinal(n: int) -> str:
    """Format a number as ordinal (1st, 2nd, 3rd, etc.)."""
    if n < 0:
        return str(n)
    suffix = 'th'
    if n % 100 not in (11, 12, 13):
        if n % 10 == 1:
            suffix = 'st'
        elif n % 10 == 2:
            suffix = 'nd'
        elif n % 10 == 3:
            suffix = 'rd'
    return f"{n}{suffix}"


def format_phone_us(phone: str) -> str:
    """Format a phone number as US format."""
    digits = ''.join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    if len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return phone


def format_credit_card(number: str) -> str:
    """Format a credit card number with spaces."""
    digits = ''.join(c for c in number if c.isdigit())
    if len(digits) == 16:
        return f"{digits[:4]} {digits[4:8]} {digits[8:12]} {digits[12:]}"
    if len(digits) == 15:
        return f"{digits[:4]} {digits[4:10]} {digits[10:]}"
    return number


def mask_credit_card(number: str) -> str:
    """Mask a credit card number showing only last 4 digits."""
    digits = ''.join(c for c in number if c.isdigit())
    if len(digits) >= 4:
        return '*' * (len(digits) - 4) + digits[-4:]
    return '*' * len(digits)


def format_ssn(ssn: str) -> str:
    """Format a Social Security Number with dashes."""
    digits = ''.join(c for c in ssn if c.isdigit())
    if len(digits) == 9:
        return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
    return ssn


def mask_ssn(ssn: str) -> str:
    """Mask a Social Security Number showing only last 4 digits."""
    digits = ''.join(c for c in ssn if c.isdigit())
    if len(digits) >= 4:
        return f"***-**-{digits[-4:]}"
    return '***-**-****'


def format_list_english(items: list, conjunction: str) -> str:
    """Format a list as English text (e.g., 'a, b, and c')."""
    if not items:
        return ""
    if len(items) == 1:
        return str(items[0])
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return ', '.join(str(i) for i in items[:-1]) + f", {conjunction} {items[-1]}"


def pluralize(word: str, count: int) -> str:
    """Return singular or plural form based on count."""
    if count == 1:
        return word
    if word.endswith('y') and not word.endswith(('ay', 'ey', 'iy', 'oy', 'uy')):
        return word[:-1] + 'ies'
    if word.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return word + 'es'
    return word + 's'


def format_count(count: int, singular: str, plural: str) -> str:
    """Format a count with singular/plural word."""
    word = singular if count == 1 else plural
    return f"{count:,} {word}"


def pad_left_zeros(value: int, width: int) -> str:
    """Pad an integer with leading zeros to a specified width."""
    return str(value).zfill(width)


def format_scientific(value: float, decimals: int) -> str:
    """Format a number in scientific notation."""
    return f"{value:.{decimals}e}"


def format_fraction(numerator: int, denominator: int) -> str:
    """Format two integers as a fraction."""
    if denominator == 0:
        return "undefined"
    return f"{numerator}/{denominator}"


def format_ratio(a: float, b: float, precision: int) -> str:
    """Format a ratio as 'a:b'."""
    if b == 0:
        return "undefined"
    ratio = a / b
    return f"{round(ratio, precision)}:1"


def format_range(start: float, end: float, decimals: int) -> str:
    """Format a numeric range."""
    if decimals == 0:
        return f"{int(start)}-{int(end)}"
    return f"{start:.{decimals}f}-{end:.{decimals}f}"


def title_case(text: str) -> str:
    """Convert text to title case."""
    return text.title()


def sentence_case(text: str) -> str:
    """Convert text to sentence case."""
    if not text:
        return ""
    return text[0].upper() + text[1:].lower()


def snake_to_title(text: str) -> str:
    """Convert snake_case to Title Case."""
    return ' '.join(word.capitalize() for word in text.split('_'))


def camel_to_title(text: str) -> str:
    """Convert camelCase to Title Case."""
    result = []
    for i, char in enumerate(text):
        if char.isupper() and i > 0:
            result.append(' ')
        result.append(char)
    return ''.join(result).title()


def format_boolean(value: bool, true_text: str, false_text: str) -> str:
    """Format a boolean as custom text."""
    return true_text if value else false_text
