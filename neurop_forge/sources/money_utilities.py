"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Money Utilities - Pure functions for currency formatting and calculations.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def cents_to_dollars(cents: int) -> float:
    """Convert cents to dollars."""
    return cents / 100


def dollars_to_cents(dollars: float) -> int:
    """Convert dollars to cents (rounds to nearest cent)."""
    return round(dollars * 100)


def format_currency(amount: float, symbol: str, decimal_places: int) -> str:
    """Format a currency amount with symbol."""
    formatted = f"{amount:,.{decimal_places}f}"
    return f"{symbol}{formatted}"


def format_currency_no_symbol(amount: float, decimal_places: int) -> str:
    """Format a currency amount without symbol."""
    return f"{amount:,.{decimal_places}f}"


def parse_currency(amount_str: str) -> float:
    """Parse a currency string to float."""
    cleaned = amount_str.replace(',', '').replace('$', '').replace('€', '').replace('£', '').replace('¥', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def round_to_cents(amount: float) -> float:
    """Round amount to nearest cent."""
    return round(amount, 2)


def round_up_to_cents(amount: float) -> float:
    """Round amount up to nearest cent."""
    import math
    return math.ceil(amount * 100) / 100


def round_down_to_cents(amount: float) -> float:
    """Round amount down to nearest cent."""
    import math
    return math.floor(amount * 100) / 100


def bankers_round(amount: float, decimal_places: int) -> float:
    """Round using banker's rounding (round half to even)."""
    from decimal import Decimal, ROUND_HALF_EVEN
    d = Decimal(str(amount))
    rounded = d.quantize(Decimal(10) ** -decimal_places, rounding=ROUND_HALF_EVEN)
    return float(rounded)


def calculate_percentage(amount: float, percentage: float) -> float:
    """Calculate percentage of an amount."""
    return round_to_cents(amount * percentage / 100)


def add_percentage(amount: float, percentage: float) -> float:
    """Add a percentage to an amount."""
    return round_to_cents(amount * (1 + percentage / 100))


def subtract_percentage(amount: float, percentage: float) -> float:
    """Subtract a percentage from an amount."""
    return round_to_cents(amount * (1 - percentage / 100))


def calculate_tax(amount: float, tax_rate: float) -> float:
    """Calculate tax amount."""
    return round_to_cents(amount * tax_rate / 100)


def add_tax(amount: float, tax_rate: float) -> float:
    """Add tax to an amount."""
    return round_to_cents(amount * (1 + tax_rate / 100))


def extract_tax(amount_with_tax: float, tax_rate: float) -> float:
    """Extract tax from a tax-inclusive amount."""
    return round_to_cents(amount_with_tax - (amount_with_tax / (1 + tax_rate / 100)))


def calculate_discount(original: float, discount_percent: float) -> float:
    """Calculate discount amount."""
    return round_to_cents(original * discount_percent / 100)


def apply_discount(original: float, discount_percent: float) -> float:
    """Apply discount to get final price."""
    return round_to_cents(original * (1 - discount_percent / 100))


def calculate_discount_percent(original: float, discounted: float) -> float:
    """Calculate the discount percentage."""
    if original <= 0:
        return 0.0
    return round((original - discounted) / original * 100, 2)


def split_amount(amount: float, parts: int) -> list:
    """Split an amount into equal parts (handles rounding)."""
    if parts <= 0:
        return []
    base = round_down_to_cents(amount / parts)
    remainder_cents = round(amount * 100) - round(base * 100 * parts)
    result = [base] * parts
    for i in range(int(remainder_cents)):
        result[i] = round_to_cents(result[i] + 0.01)
    return result


def calculate_tip(amount: float, tip_percent: float) -> float:
    """Calculate tip amount."""
    return round_to_cents(amount * tip_percent / 100)


def calculate_total_with_tip(amount: float, tip_percent: float) -> float:
    """Calculate total including tip."""
    return round_to_cents(amount * (1 + tip_percent / 100))


def is_valid_currency_amount(amount: float) -> bool:
    """Check if amount is a valid currency value."""
    return amount >= 0 and round(amount * 100) == amount * 100


def format_accounting(amount: float, symbol: str) -> str:
    """Format in accounting style (negatives in parentheses)."""
    if amount < 0:
        return f"({symbol}{abs(amount):,.2f})"
    return f"{symbol}{amount:,.2f}"


def format_compact_currency(amount: float, symbol: str) -> str:
    """Format currency in compact form (K, M, B)."""
    if abs(amount) >= 1_000_000_000:
        return f"{symbol}{amount / 1_000_000_000:.1f}B"
    if abs(amount) >= 1_000_000:
        return f"{symbol}{amount / 1_000_000:.1f}M"
    if abs(amount) >= 1_000:
        return f"{symbol}{amount / 1_000:.1f}K"
    return f"{symbol}{amount:.2f}"


def get_currency_symbol(currency_code: str) -> str:
    """Get currency symbol from ISO code."""
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥',
        'CAD': 'CA$', 'AUD': 'A$', 'CHF': 'CHF', 'INR': '₹', 'KRW': '₩',
        'BRL': 'R$', 'MXN': 'MX$', 'RUB': '₽', 'SGD': 'S$', 'HKD': 'HK$'
    }
    return symbols.get(currency_code.upper(), currency_code)


def get_currency_decimal_places(currency_code: str) -> int:
    """Get number of decimal places for a currency."""
    zero_decimal = ['JPY', 'KRW', 'VND', 'CLP', 'ISK', 'HUF']
    three_decimal = ['BHD', 'JOD', 'KWD', 'OMR']
    code = currency_code.upper()
    if code in zero_decimal:
        return 0
    if code in three_decimal:
        return 3
    return 2


def convert_currency(amount: float, rate: float) -> float:
    """Convert amount using exchange rate."""
    return round_to_cents(amount * rate)


def calculate_exchange_fee(amount: float, fee_percent: float) -> float:
    """Calculate exchange fee."""
    return round_to_cents(amount * fee_percent / 100)


def amount_after_exchange(amount: float, rate: float, fee_percent: float) -> float:
    """Calculate amount after exchange with fee."""
    converted = amount * rate
    fee = converted * fee_percent / 100
    return round_to_cents(converted - fee)


def calculate_compound_interest(principal: float, rate: float, periods: int, compounds_per_period: int) -> float:
    """Calculate compound interest."""
    r = rate / 100 / compounds_per_period
    n = periods * compounds_per_period
    return round_to_cents(principal * ((1 + r) ** n))


def calculate_simple_interest(principal: float, rate: float, periods: int) -> float:
    """Calculate simple interest amount."""
    return round_to_cents(principal * rate * periods / 100)


def calculate_loan_payment(principal: float, annual_rate: float, months: int) -> float:
    """Calculate monthly loan payment."""
    if annual_rate == 0:
        return round_to_cents(principal / months)
    monthly_rate = annual_rate / 100 / 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return round_to_cents(payment)


def calculate_total_loan_cost(monthly_payment: float, months: int) -> float:
    """Calculate total cost of a loan."""
    return round_to_cents(monthly_payment * months)


def calculate_loan_interest(principal: float, monthly_payment: float, months: int) -> float:
    """Calculate total interest on a loan."""
    return round_to_cents(monthly_payment * months - principal)


def compare_amounts(amount1: float, amount2: float) -> int:
    """Compare two currency amounts (-1, 0, or 1)."""
    cents1 = round(amount1 * 100)
    cents2 = round(amount2 * 100)
    if cents1 < cents2:
        return -1
    if cents1 > cents2:
        return 1
    return 0


def amounts_equal(amount1: float, amount2: float) -> bool:
    """Check if two currency amounts are equal."""
    return round(amount1 * 100) == round(amount2 * 100)


def sum_amounts(amounts: list) -> float:
    """Sum a list of currency amounts."""
    total_cents = sum(round(a * 100) for a in amounts)
    return total_cents / 100


def average_amount(amounts: list) -> float:
    """Calculate average of currency amounts."""
    if not amounts:
        return 0.0
    return round_to_cents(sum_amounts(amounts) / len(amounts))


def min_amount(amounts: list) -> float:
    """Get minimum currency amount."""
    if not amounts:
        return 0.0
    return min(amounts)


def max_amount(amounts: list) -> float:
    """Get maximum currency amount."""
    if not amounts:
        return 0.0
    return max(amounts)


def is_zero(amount: float) -> bool:
    """Check if currency amount is zero."""
    return round(amount * 100) == 0


def is_positive(amount: float) -> bool:
    """Check if currency amount is positive."""
    return round(amount * 100) > 0


def is_negative(amount: float) -> bool:
    """Check if currency amount is negative."""
    return round(amount * 100) < 0


def abs_amount(amount: float) -> float:
    """Get absolute value of currency amount."""
    return abs(amount)


def negate_amount(amount: float) -> float:
    """Negate a currency amount."""
    return -amount


def clamp_amount(amount: float, min_amount: float, max_amount: float) -> float:
    """Clamp a currency amount to a range."""
    return max(min_amount, min(amount, max_amount))
