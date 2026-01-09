"""
Type Conversion Functions - Pure functions for type conversion.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def to_integer(value) -> int:
    """Convert a value to an integer."""
    if value is None:
        return 0
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return 0
    return 0


def to_float(value) -> float:
    """Convert a value to a float."""
    if value is None:
        return 0.0
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def to_string(value) -> str:
    """Convert a value to a string."""
    if value is None:
        return ""
    return str(value)


def to_boolean(value) -> bool:
    """Convert a value to a boolean."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on')
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return bool(value)


def to_list(value) -> list:
    """Convert a value to a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value[:]
    if isinstance(value, (tuple, set)):
        return list(value)
    if isinstance(value, str):
        return list(value)
    if isinstance(value, dict):
        return list(value.items())
    return [value]


def parse_integer(text: str, default: int) -> int:
    """Parse a string to an integer with a default value on failure."""
    if not text:
        return default
    try:
        return int(text)
    except ValueError:
        return default


def parse_float(text: str, default: float) -> float:
    """Parse a string to a float with a default value on failure."""
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def parse_boolean(text: str) -> bool:
    """Parse a string to a boolean."""
    if not text:
        return False
    return text.lower() in ('true', 'yes', '1', 'on', 'y')


def integer_to_binary(value: int) -> str:
    """Convert an integer to its binary string representation."""
    if value < 0:
        return "-" + bin(abs(value))[2:]
    return bin(value)[2:]


def integer_to_hex(value: int) -> str:
    """Convert an integer to its hexadecimal string representation."""
    if value < 0:
        return "-" + hex(abs(value))[2:]
    return hex(value)[2:]


def integer_to_octal(value: int) -> str:
    """Convert an integer to its octal string representation."""
    if value < 0:
        return "-" + oct(abs(value))[2:]
    return oct(value)[2:]


def binary_to_integer(binary_str: str) -> int:
    """Convert a binary string to an integer."""
    if not binary_str:
        return 0
    try:
        return int(binary_str, 2)
    except ValueError:
        return 0


def hex_to_integer(hex_str: str) -> int:
    """Convert a hexadecimal string to an integer."""
    if not hex_str:
        return 0
    try:
        return int(hex_str, 16)
    except ValueError:
        return 0


def float_to_percentage(value: float) -> str:
    """Convert a float to a percentage string."""
    return f"{value * 100:.2f}%"


def percentage_to_float(percentage: str) -> float:
    """Convert a percentage string to a float."""
    if not percentage:
        return 0.0
    cleaned = percentage.strip().rstrip('%')
    try:
        return float(cleaned) / 100
    except ValueError:
        return 0.0


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9


def meters_to_feet(meters: float) -> float:
    """Convert meters to feet."""
    return meters * 3.28084


def feet_to_meters(feet: float) -> float:
    """Convert feet to meters."""
    return feet / 3.28084


def kilograms_to_pounds(kilograms: float) -> float:
    """Convert kilograms to pounds."""
    return kilograms * 2.20462


def pounds_to_kilograms(pounds: float) -> float:
    """Convert pounds to kilograms."""
    return pounds / 2.20462


def round_to_decimal_places(value: float, places: int) -> float:
    """Round a float to a specified number of decimal places."""
    return round(value, places)


def floor_value(value: float) -> int:
    """Round a float down to the nearest integer."""
    import math
    return math.floor(value)


def ceiling_value(value: float) -> int:
    """Round a float up to the nearest integer."""
    import math
    return math.ceil(value)
