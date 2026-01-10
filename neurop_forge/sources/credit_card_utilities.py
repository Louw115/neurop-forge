"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Credit Card Utilities - Pure functions for credit card operations.
All functions are pure, deterministic, and atomic.
"""

import re


def extract_digits(card: str) -> str:
    """Extract only digits from card number."""
    return re.sub(r'\D', '', card)


def luhn_check(card: str) -> bool:
    """Validate card using Luhn algorithm."""
    digits = extract_digits(card)
    if not digits:
        return False
    total = 0
    for i, digit in enumerate(reversed(digits)):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def get_card_type(card: str) -> str:
    """Detect card type from number."""
    digits = extract_digits(card)
    if not digits:
        return "unknown"
    if re.match(r'^4', digits):
        return "visa"
    if re.match(r'^5[1-5]', digits) or re.match(r'^2(2[2-9]|[3-6]|7[01]|720)', digits):
        return "mastercard"
    if re.match(r'^3[47]', digits):
        return "amex"
    if re.match(r'^6(?:011|5)', digits):
        return "discover"
    if re.match(r'^35', digits):
        return "jcb"
    if re.match(r'^3(?:0[0-5]|[68])', digits):
        return "diners"
    return "unknown"


def is_valid_length(card: str) -> bool:
    """Check if card has valid length for type."""
    digits = extract_digits(card)
    card_type = get_card_type(card)
    lengths = {
        "visa": [13, 16, 19],
        "mastercard": [16],
        "amex": [15],
        "discover": [16, 19],
        "jcb": [16, 19],
        "diners": [14, 16]
    }
    valid_lengths = lengths.get(card_type, [16])
    return len(digits) in valid_lengths


def validate_card(card: str) -> dict:
    """Full card validation."""
    digits = extract_digits(card)
    return {
        "valid": luhn_check(card) and is_valid_length(card),
        "type": get_card_type(card),
        "length": len(digits),
        "luhn_valid": luhn_check(card),
        "length_valid": is_valid_length(card)
    }


def format_card(card: str) -> str:
    """Format card number with spaces."""
    digits = extract_digits(card)
    card_type = get_card_type(card)
    if card_type == "amex":
        return f"{digits[:4]} {digits[4:10]} {digits[10:]}"
    return " ".join(digits[i:i+4] for i in range(0, len(digits), 4))


def mask_card(card: str) -> str:
    """Mask card showing only last 4 digits."""
    digits = extract_digits(card)
    if len(digits) < 4:
        return "*" * len(digits)
    masked = "*" * (len(digits) - 4) + digits[-4:]
    return format_card(masked)


def get_last_four(card: str) -> str:
    """Get last 4 digits."""
    digits = extract_digits(card)
    return digits[-4:] if len(digits) >= 4 else digits


def get_bin(card: str) -> str:
    """Get Bank Identification Number (first 6 digits)."""
    digits = extract_digits(card)
    return digits[:6] if len(digits) >= 6 else digits


def is_test_card(card: str) -> bool:
    """Check if card is a known test card."""
    test_cards = [
        "4111111111111111",
        "5555555555554444",
        "378282246310005",
        "6011111111111117",
        "4242424242424242"
    ]
    return extract_digits(card) in test_cards


def validate_expiry(month: int, year: int, current_month: int, current_year: int) -> bool:
    """Validate expiry date."""
    if month < 1 or month > 12:
        return False
    if year < current_year:
        return False
    if year == current_year and month < current_month:
        return False
    return True


def format_expiry(month: int, year: int) -> str:
    """Format expiry as MM/YY."""
    return f"{month:02d}/{year % 100:02d}"


def parse_expiry(expiry: str) -> dict:
    """Parse expiry string MM/YY or MM/YYYY."""
    match = re.match(r'^(\d{2})[/\-](\d{2,4})$', expiry)
    if not match:
        return {"valid": False, "month": 0, "year": 0}
    month = int(match.group(1))
    year = int(match.group(2))
    if year < 100:
        year += 2000
    return {"valid": True, "month": month, "year": year}


def validate_cvv(cvv: str, card_type: str) -> bool:
    """Validate CVV."""
    digits = extract_digits(cvv)
    if card_type == "amex":
        return len(digits) == 4
    return len(digits) == 3


def get_cvv_name(card_type: str) -> str:
    """Get CVV field name for card type."""
    if card_type == "amex":
        return "CID"
    if card_type == "discover":
        return "CID"
    return "CVV"


def compare_cards(card1: str, card2: str) -> bool:
    """Compare two card numbers."""
    return extract_digits(card1) == extract_digits(card2)


def generate_check_digit(partial: str) -> str:
    """Generate Luhn check digit for partial number."""
    digits = extract_digits(partial)
    total = 0
    for i, digit in enumerate(reversed(digits)):
        n = int(digit)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    check = (10 - (total % 10)) % 10
    return str(check)
