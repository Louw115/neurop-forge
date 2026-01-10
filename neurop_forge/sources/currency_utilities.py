"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Currency Utilities - Pure functions for currency operations.
All functions are pure, deterministic, and atomic.
"""

def create_money(amount: float, currency: str) -> dict:
    """Create a money object."""
    return {"amount": round(amount, 2), "currency": currency.upper()}


def add_money(m1: dict, m2: dict) -> dict:
    """Add two money objects (same currency)."""
    if m1["currency"] != m2["currency"]:
        return {"error": "Currency mismatch"}
    return create_money(m1["amount"] + m2["amount"], m1["currency"])


def subtract_money(m1: dict, m2: dict) -> dict:
    """Subtract money objects (same currency)."""
    if m1["currency"] != m2["currency"]:
        return {"error": "Currency mismatch"}
    return create_money(m1["amount"] - m2["amount"], m1["currency"])


def multiply_money(money: dict, factor: float) -> dict:
    """Multiply money by factor."""
    return create_money(money["amount"] * factor, money["currency"])


def divide_money(money: dict, divisor: float) -> dict:
    """Divide money by divisor."""
    if divisor == 0:
        return {"error": "Division by zero"}
    return create_money(money["amount"] / divisor, money["currency"])


def convert_currency(money: dict, rate: float, target_currency: str) -> dict:
    """Convert money to another currency."""
    return create_money(money["amount"] * rate, target_currency)


def is_positive(money: dict) -> bool:
    """Check if amount is positive."""
    return money["amount"] > 0


def is_negative(money: dict) -> bool:
    """Check if amount is negative."""
    return money["amount"] < 0


def is_zero(money: dict) -> bool:
    """Check if amount is zero."""
    return money["amount"] == 0


def compare_money(m1: dict, m2: dict) -> int:
    """Compare two money objects. Returns -1, 0, or 1."""
    if m1["currency"] != m2["currency"]:
        return 0
    if m1["amount"] < m2["amount"]:
        return -1
    if m1["amount"] > m2["amount"]:
        return 1
    return 0


def min_money(moneys: list) -> dict:
    """Get minimum amount from list."""
    if not moneys:
        return None
    result = moneys[0]
    for m in moneys[1:]:
        if m["currency"] == result["currency"] and m["amount"] < result["amount"]:
            result = m
    return result


def max_money(moneys: list) -> dict:
    """Get maximum amount from list."""
    if not moneys:
        return None
    result = moneys[0]
    for m in moneys[1:]:
        if m["currency"] == result["currency"] and m["amount"] > result["amount"]:
            result = m
    return result


def sum_money(moneys: list) -> dict:
    """Sum list of money objects."""
    if not moneys:
        return None
    result = moneys[0]
    for m in moneys[1:]:
        result = add_money(result, m)
    return result


def average_money(moneys: list) -> dict:
    """Calculate average of money objects."""
    if not moneys:
        return None
    total = sum_money(moneys)
    return divide_money(total, len(moneys))


def allocate(money: dict, ratios: list) -> list:
    """Allocate money according to ratios."""
    total_ratio = sum(ratios)
    if total_ratio == 0:
        return [create_money(0, money["currency"]) for _ in ratios]
    allocations = []
    remaining = money["amount"]
    for i, ratio in enumerate(ratios):
        if i == len(ratios) - 1:
            allocations.append(create_money(remaining, money["currency"]))
        else:
            share = round(money["amount"] * ratio / total_ratio, 2)
            allocations.append(create_money(share, money["currency"]))
            remaining -= share
    return allocations


def split_evenly(money: dict, parts: int) -> list:
    """Split money evenly into parts."""
    if parts <= 0:
        return []
    base = round(money["amount"] / parts, 2)
    remainder = round(money["amount"] - base * parts, 2)
    allocations = [create_money(base, money["currency"]) for _ in range(parts)]
    allocations[0] = create_money(allocations[0]["amount"] + remainder, money["currency"])
    return allocations


def format_currency(money: dict, symbol: str, decimal_places: int) -> str:
    """Format money with symbol."""
    return f"{symbol}{money['amount']:,.{decimal_places}f}"


def parse_currency(text: str, currency: str) -> dict:
    """Parse currency string."""
    cleaned = "".join(c for c in text if c.isdigit() or c == "." or c == "-")
    try:
        return create_money(float(cleaned), currency)
    except ValueError:
        return None


def apply_discount(money: dict, discount_percent: float) -> dict:
    """Apply percentage discount."""
    discount_amount = money["amount"] * (discount_percent / 100)
    return create_money(money["amount"] - discount_amount, money["currency"])


def apply_tax(money: dict, tax_percent: float) -> dict:
    """Apply tax to amount."""
    tax_amount = money["amount"] * (tax_percent / 100)
    return create_money(money["amount"] + tax_amount, money["currency"])


def calculate_tax(money: dict, tax_percent: float) -> dict:
    """Calculate tax amount."""
    tax_amount = money["amount"] * (tax_percent / 100)
    return create_money(tax_amount, money["currency"])


def extract_tax(money: dict, tax_percent: float) -> dict:
    """Extract tax from tax-inclusive amount."""
    base = money["amount"] / (1 + tax_percent / 100)
    return {
        "base": create_money(base, money["currency"]),
        "tax": create_money(money["amount"] - base, money["currency"])
    }


def round_to_cents(money: dict) -> dict:
    """Round to nearest cent."""
    return create_money(round(money["amount"], 2), money["currency"])


def round_up_to_cents(money: dict) -> dict:
    """Round up to nearest cent."""
    import math
    return create_money(math.ceil(money["amount"] * 100) / 100, money["currency"])


def round_down_to_cents(money: dict) -> dict:
    """Round down to nearest cent."""
    import math
    return create_money(math.floor(money["amount"] * 100) / 100, money["currency"])


def get_currency_symbol(currency_code: str) -> str:
    """Get currency symbol."""
    symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥",
        "CAD": "C$", "AUD": "A$", "CHF": "Fr", "CNY": "¥",
        "INR": "₹", "MXN": "$", "BRL": "R$", "KRW": "₩"
    }
    return symbols.get(currency_code.upper(), currency_code)


def get_currency_decimals(currency_code: str) -> int:
    """Get decimal places for currency."""
    no_decimals = ["JPY", "KRW", "VND", "IDR"]
    return 0 if currency_code.upper() in no_decimals else 2


def cents_to_dollars(cents: int, currency: str) -> dict:
    """Convert cents to dollars."""
    return create_money(cents / 100, currency)


def dollars_to_cents(money: dict) -> int:
    """Convert dollars to cents."""
    return round(money["amount"] * 100)
