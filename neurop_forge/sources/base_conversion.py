"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Base Conversion - Pure functions for number base conversions.
All functions are pure, deterministic, and atomic.
"""

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def to_base(number: int, base: int) -> str:
    """Convert integer to string in given base."""
    if number == 0:
        return "0"
    if base < 2 or base > 62:
        return ""
    is_negative = number < 0
    number = abs(number)
    result = []
    while number > 0:
        result.append(DIGITS[number % base])
        number //= base
    if is_negative:
        result.append("-")
    return "".join(reversed(result))


def from_base(string: str, base: int) -> int:
    """Convert string from given base to integer."""
    if not string:
        return 0
    is_negative = string[0] == "-"
    if is_negative:
        string = string[1:]
    result = 0
    for char in string.upper():
        value = DIGITS.index(char.upper() if char.isupper() else char)
        if value >= base:
            return 0
        result = result * base + value
    return -result if is_negative else result


def to_binary(number: int) -> str:
    """Convert integer to binary string."""
    return to_base(number, 2)


def from_binary(binary: str) -> int:
    """Convert binary string to integer."""
    return from_base(binary, 2)


def to_octal(number: int) -> str:
    """Convert integer to octal string."""
    return to_base(number, 8)


def from_octal(octal: str) -> int:
    """Convert octal string to integer."""
    return from_base(octal, 8)


def to_hexadecimal(number: int) -> str:
    """Convert integer to hexadecimal string."""
    return to_base(number, 16)


def from_hexadecimal(hex_str: str) -> int:
    """Convert hexadecimal string to integer."""
    return from_base(hex_str, 16)


def to_base62(number: int) -> str:
    """Convert integer to base62 string."""
    return to_base(number, 62)


def from_base62(string: str) -> int:
    """Convert base62 string to integer."""
    return from_base(string, 62)


def to_base36(number: int) -> str:
    """Convert integer to base36 string."""
    return to_base(number, 36)


def from_base36(string: str) -> int:
    """Convert base36 string to integer."""
    return from_base(string, 36)


def convert_base(string: str, from_base_num: int, to_base_num: int) -> str:
    """Convert string from one base to another."""
    decimal = from_base(string, from_base_num)
    return to_base(decimal, to_base_num)


def is_valid_base_string(string: str, base: int) -> bool:
    """Check if string is valid for given base."""
    if not string:
        return False
    start = 1 if string[0] == "-" else 0
    for char in string[start:]:
        idx = DIGITS.find(char.upper() if char.isupper() else char)
        if idx == -1 or idx >= base:
            return False
    return True


def to_roman(number: int) -> str:
    """Convert integer to Roman numerals."""
    if number <= 0 or number > 3999:
        return ""
    values = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
              (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
              (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    result = []
    for value, numeral in values:
        while number >= value:
            result.append(numeral)
            number -= value
    return "".join(result)


def from_roman(roman: str) -> int:
    """Convert Roman numerals to integer."""
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    result = 0
    prev = 0
    for char in reversed(roman.upper()):
        value = values.get(char, 0)
        if value < prev:
            result -= value
        else:
            result += value
        prev = value
    return result


def int_to_words(number: int) -> str:
    """Convert integer to English words."""
    if number == 0:
        return "zero"
    ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
            "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
            "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    scales = ["", "thousand", "million", "billion", "trillion"]
    if number < 0:
        return "negative " + int_to_words(-number)
    def under_thousand(n):
        if n < 20:
            return ones[n]
        if n < 100:
            return tens[n // 10] + ("-" + ones[n % 10] if n % 10 else "")
        return ones[n // 100] + " hundred" + (" " + under_thousand(n % 100) if n % 100 else "")
    result = []
    scale_idx = 0
    while number > 0:
        chunk = number % 1000
        if chunk:
            part = under_thousand(chunk)
            if scales[scale_idx]:
                part += " " + scales[scale_idx]
            result.insert(0, part)
        number //= 1000
        scale_idx += 1
    return " ".join(result)


def float_to_fraction(value: float, max_denom: int) -> dict:
    """Convert float to approximate fraction."""
    if value == 0:
        return {"numerator": 0, "denominator": 1}
    sign = 1 if value >= 0 else -1
    value = abs(value)
    best_num, best_denom = 0, 1
    best_error = abs(value)
    for denom in range(1, max_denom + 1):
        num = round(value * denom)
        error = abs(value - num / denom)
        if error < best_error:
            best_error = error
            best_num = num
            best_denom = denom
    return {"numerator": sign * best_num, "denominator": best_denom}


def fraction_to_decimal(numerator: int, denominator: int, precision: int) -> str:
    """Convert fraction to decimal string."""
    if denominator == 0:
        return "undefined"
    is_negative = (numerator < 0) != (denominator < 0)
    numerator = abs(numerator)
    denominator = abs(denominator)
    integer_part = numerator // denominator
    remainder = numerator % denominator
    decimal_part = []
    for _ in range(precision):
        remainder *= 10
        decimal_part.append(str(remainder // denominator))
        remainder %= denominator
    result = str(integer_part)
    if decimal_part:
        result += "." + "".join(decimal_part)
    return ("-" if is_negative else "") + result


def bytes_to_int(byte_data: bytes, endian: str) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(byte_data, endian)


def int_to_bytes(number: int, length: int, endian: str) -> bytes:
    """Convert integer to bytes."""
    return number.to_bytes(length, endian)


def to_scientific_notation(number: float, precision: int) -> str:
    """Convert to scientific notation."""
    if number == 0:
        return "0e+0"
    import math
    exp = math.floor(math.log10(abs(number)))
    mantissa = number / (10 ** exp)
    return f"{mantissa:.{precision}f}e{exp:+d}"


def from_scientific_notation(notation: str) -> float:
    """Parse scientific notation."""
    return float(notation)
