"""
Phone Utilities - Pure functions for phone number parsing and formatting.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import re


def normalize_phone(phone: str) -> str:
    """Remove all non-digit characters from phone number."""
    return re.sub(r'\D', '', phone)


def is_valid_phone_length(phone: str, min_length: int, max_length: int) -> bool:
    """Check if phone number has valid length."""
    digits = normalize_phone(phone)
    return min_length <= len(digits) <= max_length


def is_valid_us_phone(phone: str) -> bool:
    """Check if a phone number is a valid US format."""
    digits = normalize_phone(phone)
    if len(digits) == 10:
        return digits[0] not in '01'
    if len(digits) == 11 and digits[0] == '1':
        return digits[1] not in '01'
    return False


def is_valid_e164(phone: str) -> bool:
    """Check if a phone number is in E.164 format."""
    pattern = r'^\+[1-9]\d{6,14}$'
    return bool(re.match(pattern, phone))


def format_us_phone(phone: str) -> str:
    """Format a phone number in US format: (XXX) XXX-XXXX."""
    digits = normalize_phone(phone)
    if len(digits) == 11 and digits[0] == '1':
        digits = digits[1:]
    if len(digits) != 10:
        return phone
    return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"


def format_us_phone_dashes(phone: str) -> str:
    """Format a phone number with dashes: XXX-XXX-XXXX."""
    digits = normalize_phone(phone)
    if len(digits) == 11 and digits[0] == '1':
        digits = digits[1:]
    if len(digits) != 10:
        return phone
    return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"


def format_us_phone_dots(phone: str) -> str:
    """Format a phone number with dots: XXX.XXX.XXXX."""
    digits = normalize_phone(phone)
    if len(digits) == 11 and digits[0] == '1':
        digits = digits[1:]
    if len(digits) != 10:
        return phone
    return f"{digits[0:3]}.{digits[3:6]}.{digits[6:10]}"


def format_e164(phone: str, country_code: str) -> str:
    """Format a phone number in E.164 format."""
    digits = normalize_phone(phone)
    country = country_code.lstrip('+')
    if digits.startswith(country):
        return f"+{digits}"
    return f"+{country}{digits}"


def format_international(phone: str, country_code: str) -> str:
    """Format a phone number with international prefix."""
    digits = normalize_phone(phone)
    return f"+{country_code} {digits}"


def extract_country_code(phone: str) -> str:
    """Extract country code from E.164 formatted number."""
    if not phone.startswith('+'):
        return ""
    digits = phone[1:]
    one_digit = ['1', '7']
    two_digit = ['20', '27', '30', '31', '32', '33', '34', '36', '39', '40', '41', '43', '44', '45', '46', '47', '48', '49', '51', '52', '53', '54', '55', '56', '57', '58', '60', '61', '62', '63', '64', '65', '66', '81', '82', '84', '86', '90', '91', '92', '93', '94', '95', '98']
    if digits[0] in one_digit:
        return digits[0]
    if digits[:2] in two_digit:
        return digits[:2]
    return digits[:3]


def extract_national_number(phone: str, country_code: str) -> str:
    """Extract national number without country code."""
    digits = normalize_phone(phone)
    code = country_code.lstrip('+')
    if digits.startswith(code):
        return digits[len(code):]
    return digits


def mask_phone(phone: str, visible_digits: int) -> str:
    """Mask a phone number showing only last N digits."""
    digits = normalize_phone(phone)
    if len(digits) <= visible_digits:
        return '*' * len(digits)
    masked = '*' * (len(digits) - visible_digits)
    return masked + digits[-visible_digits:]


def mask_phone_middle(phone: str) -> str:
    """Mask the middle portion of a phone number."""
    digits = normalize_phone(phone)
    if len(digits) < 6:
        return '*' * len(digits)
    return digits[:3] + '*' * (len(digits) - 6) + digits[-3:]


def get_area_code(phone: str) -> str:
    """Extract area code from US phone number."""
    digits = normalize_phone(phone)
    if len(digits) == 11 and digits[0] == '1':
        return digits[1:4]
    if len(digits) >= 10:
        return digits[0:3]
    return ""


def get_exchange_code(phone: str) -> str:
    """Extract exchange code from US phone number."""
    digits = normalize_phone(phone)
    if len(digits) == 11 and digits[0] == '1':
        return digits[4:7]
    if len(digits) >= 10:
        return digits[3:6]
    return ""


def get_subscriber_number(phone: str) -> str:
    """Extract subscriber number from US phone number."""
    digits = normalize_phone(phone)
    if len(digits) == 11 and digits[0] == '1':
        return digits[7:11]
    if len(digits) >= 10:
        return digits[6:10]
    return ""


def is_toll_free(phone: str) -> bool:
    """Check if a US phone number is toll-free."""
    digits = normalize_phone(phone)
    if len(digits) == 11 and digits[0] == '1':
        area = digits[1:4]
    elif len(digits) == 10:
        area = digits[0:3]
    else:
        return False
    toll_free_areas = ['800', '833', '844', '855', '866', '877', '888']
    return area in toll_free_areas


def is_premium_rate(phone: str) -> bool:
    """Check if a US phone number is premium rate (900)."""
    area = get_area_code(phone)
    return area == '900'


def phones_match(phone1: str, phone2: str) -> bool:
    """Check if two phone numbers match (comparing digits only)."""
    d1 = normalize_phone(phone1)
    d2 = normalize_phone(phone2)
    if len(d1) == 11 and d1[0] == '1':
        d1 = d1[1:]
    if len(d2) == 11 and d2[0] == '1':
        d2 = d2[1:]
    return d1 == d2 and len(d1) >= 10


def extract_phones_from_text(text: str) -> list:
    """Extract phone numbers from text."""
    patterns = [
        r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{10,11}'
    ]
    results = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        results.extend(matches)
    return list(set(results))


def count_phones_in_text(text: str) -> int:
    """Count phone numbers in text."""
    return len(extract_phones_from_text(text))


def format_phone_link(phone: str, country_code: str) -> str:
    """Format a phone number as a tel: link."""
    formatted = format_e164(phone, country_code)
    return f"tel:{formatted}"


def format_sms_link(phone: str, country_code: str, body: str) -> str:
    """Format a phone number as an SMS link."""
    from urllib.parse import quote
    formatted = format_e164(phone, country_code)
    if body:
        return f"sms:{formatted}?body={quote(body)}"
    return f"sms:{formatted}"


def format_whatsapp_link(phone: str) -> str:
    """Format a phone number as a WhatsApp link."""
    digits = normalize_phone(phone)
    return f"https://wa.me/{digits}"


def split_phone_parts(phone: str) -> dict:
    """Split a US phone number into parts."""
    return {
        'area_code': get_area_code(phone),
        'exchange': get_exchange_code(phone),
        'subscriber': get_subscriber_number(phone)
    }


def is_valid_extension(extension: str) -> bool:
    """Check if a phone extension is valid."""
    digits = re.sub(r'\D', '', extension)
    return 1 <= len(digits) <= 6


def format_with_extension(phone: str, extension: str) -> str:
    """Format a phone number with extension."""
    formatted = format_us_phone(phone)
    return f"{formatted} ext. {extension}" if extension else formatted


def parse_phone_with_extension(phone_str: str) -> dict:
    """Parse a phone string that may contain an extension."""
    ext_patterns = [r'ext\.?\s*(\d+)', r'x\s*(\d+)', r'#\s*(\d+)']
    extension = ""
    clean_phone = phone_str
    for pattern in ext_patterns:
        match = re.search(pattern, phone_str, re.IGNORECASE)
        if match:
            extension = match.group(1)
            clean_phone = phone_str[:match.start()].strip()
            break
    return {'phone': normalize_phone(clean_phone), 'extension': extension}


def is_mobile_prefix(phone: str, mobile_prefixes: list) -> bool:
    """Check if phone starts with a mobile prefix."""
    digits = normalize_phone(phone)
    for prefix in mobile_prefixes:
        if digits.startswith(prefix):
            return True
    return False


def get_country_for_code(country_code: str) -> str:
    """Get country name for a country code."""
    codes = {
        '1': 'United States/Canada',
        '44': 'United Kingdom',
        '33': 'France',
        '49': 'Germany',
        '39': 'Italy',
        '34': 'Spain',
        '81': 'Japan',
        '86': 'China',
        '91': 'India',
        '61': 'Australia',
        '55': 'Brazil',
        '52': 'Mexico',
        '7': 'Russia'
    }
    return codes.get(country_code.lstrip('+'), 'Unknown')


def validate_phone_format(phone: str, expected_format: str) -> bool:
    """Validate phone matches expected format pattern."""
    format_patterns = {
        'us_parens': r'^\(\d{3}\) \d{3}-\d{4}$',
        'us_dashes': r'^\d{3}-\d{3}-\d{4}$',
        'us_dots': r'^\d{3}\.\d{3}\.\d{4}$',
        'e164': r'^\+\d{11,15}$',
        'digits_only': r'^\d{10,15}$'
    }
    pattern = format_patterns.get(expected_format)
    if not pattern:
        return False
    return bool(re.match(pattern, phone))


def sanitize_phone_input(phone: str) -> str:
    """Sanitize phone input by removing invalid characters."""
    allowed = set('0123456789+()-. ')
    return ''.join(c for c in phone if c in allowed)
