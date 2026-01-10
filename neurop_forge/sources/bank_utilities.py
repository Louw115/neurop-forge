"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Bank Utilities - Pure functions for banking operations.
All functions are pure, deterministic, and atomic.
"""

import re


def is_valid_iban(iban: str) -> bool:
    """Validate IBAN format and checksum."""
    iban = iban.replace(" ", "").upper()
    if len(iban) < 15 or len(iban) > 34:
        return False
    if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]+$', iban):
        return False
    rearranged = iban[4:] + iban[:4]
    converted = ""
    for c in rearranged:
        if c.isalpha():
            converted += str(ord(c) - ord('A') + 10)
        else:
            converted += c
    return int(converted) % 97 == 1


def format_iban(iban: str) -> str:
    """Format IBAN with spaces every 4 characters."""
    iban = iban.replace(" ", "").upper()
    return " ".join(iban[i:i+4] for i in range(0, len(iban), 4))


def get_iban_country(iban: str) -> str:
    """Get country code from IBAN."""
    return iban.replace(" ", "").upper()[:2]


def get_iban_bban(iban: str) -> str:
    """Get BBAN (Basic Bank Account Number) from IBAN."""
    return iban.replace(" ", "").upper()[4:]


def is_valid_swift(swift: str) -> bool:
    """Validate SWIFT/BIC code format."""
    swift = swift.upper()
    if len(swift) not in [8, 11]:
        return False
    return bool(re.match(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$', swift))


def format_swift(swift: str) -> str:
    """Format SWIFT code."""
    return swift.upper()


def get_swift_bank_code(swift: str) -> str:
    """Get bank code from SWIFT."""
    return swift.upper()[:4]


def get_swift_country(swift: str) -> str:
    """Get country code from SWIFT."""
    return swift.upper()[4:6]


def get_swift_location(swift: str) -> str:
    """Get location code from SWIFT."""
    return swift.upper()[6:8]


def get_swift_branch(swift: str) -> str:
    """Get branch code from SWIFT."""
    swift = swift.upper()
    return swift[8:] if len(swift) == 11 else "XXX"


def is_valid_routing_number(routing: str) -> bool:
    """Validate US ABA routing number."""
    if len(routing) != 9 or not routing.isdigit():
        return False
    digits = [int(d) for d in routing]
    checksum = (3 * (digits[0] + digits[3] + digits[6]) +
                7 * (digits[1] + digits[4] + digits[7]) +
                1 * (digits[2] + digits[5] + digits[8]))
    return checksum % 10 == 0


def mask_account_number(account: str, visible: int) -> str:
    """Mask account number showing only last n digits."""
    if len(account) <= visible:
        return account
    return "*" * (len(account) - visible) + account[-visible:]


def mask_card_number(card: str, visible_start: int, visible_end: int) -> str:
    """Mask card number showing start and end digits."""
    digits = card.replace(" ", "").replace("-", "")
    masked = digits[:visible_start] + "*" * (len(digits) - visible_start - visible_end) + digits[-visible_end:]
    return " ".join(masked[i:i+4] for i in range(0, len(masked), 4))


def is_valid_credit_card(card: str) -> bool:
    """Validate credit card number using Luhn algorithm."""
    digits = card.replace(" ", "").replace("-", "")
    if not digits.isdigit() or len(digits) < 13 or len(digits) > 19:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def get_card_type(card: str) -> str:
    """Detect credit card type from number."""
    digits = card.replace(" ", "").replace("-", "")
    if digits.startswith("4"):
        return "visa"
    if digits[:2] in ["51", "52", "53", "54", "55"]:
        return "mastercard"
    if int(digits[:6]) >= 222100 and int(digits[:6]) <= 272099:
        return "mastercard"
    if digits[:2] in ["34", "37"]:
        return "amex"
    if digits[:4] == "6011" or digits[:2] == "65":
        return "discover"
    return "unknown"


def format_card_number(card: str) -> str:
    """Format card number with spaces."""
    digits = card.replace(" ", "").replace("-", "")
    return " ".join(digits[i:i+4] for i in range(0, len(digits), 4))


def calculate_simple_interest(principal: float, rate: float, years: float) -> float:
    """Calculate simple interest."""
    return principal * rate * years


def calculate_compound_interest(principal: float, rate: float, periods: int, time: float) -> float:
    """Calculate compound interest."""
    return principal * ((1 + rate / periods) ** (periods * time)) - principal


def calculate_monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """Calculate monthly loan payment."""
    if annual_rate == 0:
        return principal / months
    monthly_rate = annual_rate / 12
    return principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)


def calculate_apr(rate: float, fees: float, principal: float, periods: int) -> float:
    """Calculate APR including fees."""
    total_interest = principal * rate * periods
    total_cost = total_interest + fees
    return total_cost / principal / periods


def amortization_schedule(principal: float, annual_rate: float, months: int) -> list:
    """Generate amortization schedule."""
    monthly_payment = calculate_monthly_payment(principal, annual_rate, months)
    balance = principal
    schedule = []
    monthly_rate = annual_rate / 12
    for i in range(1, months + 1):
        interest = balance * monthly_rate
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        schedule.append({
            "payment": i,
            "principal": round(principal_payment, 2),
            "interest": round(interest, 2),
            "balance": round(max(0, balance), 2)
        })
    return schedule


def calculate_loan_balance(principal: float, annual_rate: float, months_total: int, months_paid: int) -> float:
    """Calculate remaining loan balance."""
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return principal * (1 - months_paid / months_total)
    monthly_payment = calculate_monthly_payment(principal, annual_rate, months_total)
    return principal * (1 + monthly_rate) ** months_paid - monthly_payment * ((1 + monthly_rate) ** months_paid - 1) / monthly_rate


def is_valid_cvv(cvv: str, card_type: str) -> bool:
    """Validate CVV based on card type."""
    if not cvv.isdigit():
        return False
    if card_type == "amex":
        return len(cvv) == 4
    return len(cvv) == 3


def is_expired_card(exp_month: int, exp_year: int, current_month: int, current_year: int) -> bool:
    """Check if card is expired."""
    if exp_year < current_year:
        return True
    if exp_year == current_year and exp_month < current_month:
        return True
    return False
