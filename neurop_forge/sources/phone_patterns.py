"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Phone Patterns - Pure functions for phone number operations.
All functions are pure, deterministic, and atomic.
"""

import re


def extract_digits(phone: str) -> str:
    """Extract only digits from phone."""
    return re.sub(r'\D', '', phone)


def format_us_phone(digits: str) -> str:
    """Format as US phone (XXX) XXX-XXXX."""
    digits = extract_digits(digits)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    if len(digits) == 11 and digits[0] == "1":
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return digits


def format_international(digits: str, country_code: str) -> str:
    """Format international phone."""
    digits = extract_digits(digits)
    return f"+{country_code} {digits}"


def format_e164(digits: str, country_code: str) -> str:
    """Format as E.164 international."""
    digits = extract_digits(digits)
    return f"+{country_code}{digits}"


def is_valid_us_phone(phone: str) -> bool:
    """Validate US phone number."""
    digits = extract_digits(phone)
    if len(digits) == 10:
        return digits[0] not in "01"
    if len(digits) == 11:
        return digits[0] == "1" and digits[1] not in "01"
    return False


def is_valid_phone_length(phone: str, min_len: int, max_len: int) -> bool:
    """Validate phone length."""
    digits = extract_digits(phone)
    return min_len <= len(digits) <= max_len


def get_area_code(phone: str) -> str:
    """Extract area code from US phone."""
    digits = extract_digits(phone)
    if len(digits) == 10:
        return digits[:3]
    if len(digits) == 11 and digits[0] == "1":
        return digits[1:4]
    return ""


def get_exchange(phone: str) -> str:
    """Extract exchange from US phone."""
    digits = extract_digits(phone)
    if len(digits) == 10:
        return digits[3:6]
    if len(digits) == 11 and digits[0] == "1":
        return digits[4:7]
    return ""


def get_subscriber(phone: str) -> str:
    """Extract subscriber number from US phone."""
    digits = extract_digits(phone)
    if len(digits) == 10:
        return digits[6:]
    if len(digits) == 11 and digits[0] == "1":
        return digits[7:]
    return ""


def normalize_phone(phone: str) -> str:
    """Normalize phone to digits only."""
    return extract_digits(phone)


def add_country_code(phone: str, country_code: str) -> str:
    """Add country code if missing."""
    digits = extract_digits(phone)
    if not digits.startswith(country_code):
        return country_code + digits
    return digits


def remove_country_code(phone: str, country_code: str) -> str:
    """Remove country code."""
    digits = extract_digits(phone)
    if digits.startswith(country_code):
        return digits[len(country_code):]
    return digits


def mask_phone(phone: str) -> str:
    """Mask phone showing last 4 digits."""
    digits = extract_digits(phone)
    if len(digits) < 4:
        return "*" * len(digits)
    return "*" * (len(digits) - 4) + digits[-4:]


def compare_phones(phone1: str, phone2: str) -> bool:
    """Compare two phone numbers."""
    return extract_digits(phone1) == extract_digits(phone2)


def is_toll_free(phone: str) -> bool:
    """Check if phone is toll-free."""
    toll_free = ["800", "888", "877", "866", "855", "844", "833"]
    area_code = get_area_code(phone)
    return area_code in toll_free


def is_premium_rate(phone: str) -> bool:
    """Check if phone is premium rate."""
    area_code = get_area_code(phone)
    return area_code in ["900"]


def format_tel_link(phone: str) -> str:
    """Format as tel: link."""
    digits = extract_digits(phone)
    return f"tel:+{digits}"


def parse_phone_parts(phone: str) -> dict:
    """Parse phone into parts."""
    digits = extract_digits(phone)
    return {
        "country_code": "1" if len(digits) == 11 and digits[0] == "1" else "",
        "area_code": get_area_code(phone),
        "exchange": get_exchange(phone),
        "subscriber": get_subscriber(phone),
        "full": digits
    }


def is_mobile_us(phone: str) -> bool:
    """Check if likely mobile (US heuristic)."""
    return is_valid_us_phone(phone)


def format_sms_link(phone: str, message: str) -> str:
    """Format as SMS link."""
    digits = extract_digits(phone)
    from urllib.parse import quote
    return f"sms:+{digits}?body={quote(message)}"


def validate_extension(ext: str) -> bool:
    """Validate phone extension."""
    digits = extract_digits(ext)
    return 1 <= len(digits) <= 6


def format_with_extension(phone: str, ext: str) -> str:
    """Format phone with extension."""
    formatted = format_us_phone(phone)
    if ext:
        return f"{formatted} ext. {ext}"
    return formatted
