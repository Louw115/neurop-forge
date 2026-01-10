"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Tax Utilities - Pure functions for tax calculations.
All functions are pure, deterministic, and atomic.
"""


def calculate_tax(amount: float, rate: float) -> float:
    """Calculate tax amount."""
    return round(amount * rate / 100, 2)


def add_tax(amount: float, rate: float) -> float:
    """Add tax to amount."""
    return round(amount * (1 + rate / 100), 2)


def remove_tax(total: float, rate: float) -> float:
    """Remove tax from total (reverse calculation)."""
    return round(total / (1 + rate / 100), 2)


def extract_tax(total: float, rate: float) -> float:
    """Extract tax amount from total."""
    subtotal = remove_tax(total, rate)
    return round(total - subtotal, 2)


def calculate_compound_tax(amount: float, rates: list) -> dict:
    """Calculate compound taxes (each on previous)."""
    current = amount
    taxes = []
    for rate in rates:
        tax = round(current * rate / 100, 2)
        taxes.append(tax)
        current += tax
    return {
        "subtotal": amount,
        "taxes": taxes,
        "total": current
    }


def calculate_parallel_taxes(amount: float, rates: list) -> dict:
    """Calculate parallel taxes (each on subtotal)."""
    taxes = [round(amount * rate / 100, 2) for rate in rates]
    return {
        "subtotal": amount,
        "taxes": taxes,
        "total": round(amount + sum(taxes), 2)
    }


def get_effective_rate(subtotal: float, tax_amount: float) -> float:
    """Calculate effective tax rate."""
    if subtotal == 0:
        return 0
    return round((tax_amount / subtotal) * 100, 4)


def is_tax_exempt(amount: float, threshold: float) -> bool:
    """Check if amount is below tax threshold."""
    return amount < threshold


def apply_tax_bracket(income: float, brackets: list) -> float:
    """Apply progressive tax brackets."""
    total_tax = 0
    remaining = income
    prev_limit = 0
    for bracket in brackets:
        limit = bracket.get("limit", float("inf"))
        rate = bracket["rate"]
        taxable = min(remaining, limit - prev_limit)
        if taxable <= 0:
            break
        total_tax += taxable * rate / 100
        remaining -= taxable
        prev_limit = limit
    return round(total_tax, 2)


def get_marginal_rate(income: float, brackets: list) -> float:
    """Get marginal tax rate for income."""
    prev_limit = 0
    for bracket in brackets:
        limit = bracket.get("limit", float("inf"))
        if income <= limit:
            return bracket["rate"]
        prev_limit = limit
    return brackets[-1]["rate"] if brackets else 0


def calculate_vat(net_amount: float, vat_rate: float) -> dict:
    """Calculate VAT amounts."""
    vat = round(net_amount * vat_rate / 100, 2)
    return {
        "net": net_amount,
        "vat": vat,
        "gross": round(net_amount + vat, 2)
    }


def reverse_vat(gross_amount: float, vat_rate: float) -> dict:
    """Reverse calculate VAT from gross."""
    net = round(gross_amount / (1 + vat_rate / 100), 2)
    vat = round(gross_amount - net, 2)
    return {
        "net": net,
        "vat": vat,
        "gross": gross_amount
    }


def calculate_withholding(income: float, withholding_rate: float) -> dict:
    """Calculate withholding amount."""
    withheld = round(income * withholding_rate / 100, 2)
    return {
        "gross": income,
        "withheld": withheld,
        "net": round(income - withheld, 2)
    }


def combine_tax_rates(rates: list) -> float:
    """Combine multiple tax rates."""
    return sum(rates)


def split_tax(total_tax: float, rates: list) -> list:
    """Split tax proportionally by rates."""
    total_rate = sum(rates)
    if total_rate == 0:
        return [0] * len(rates)
    return [round(total_tax * rate / total_rate, 2) for rate in rates]


def format_tax_amount(amount: float, currency: str) -> str:
    """Format tax amount with currency."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, currency + " ")
    return f"{symbol}{amount:,.2f}"


def calculate_sales_tax(amount: float, state_rate: float, local_rate: float) -> dict:
    """Calculate combined sales tax."""
    state_tax = round(amount * state_rate / 100, 2)
    local_tax = round(amount * local_rate / 100, 2)
    return {
        "subtotal": amount,
        "state_tax": state_tax,
        "local_tax": local_tax,
        "total_tax": round(state_tax + local_tax, 2),
        "total": round(amount + state_tax + local_tax, 2)
    }


def estimate_quarterly_tax(annual_income: float, annual_tax: float, quarter: int) -> float:
    """Estimate quarterly tax payment."""
    return round(annual_tax / 4, 2)


def is_taxable(amount: float, exemption: float) -> bool:
    """Check if amount exceeds exemption."""
    return amount > exemption


def get_taxable_amount(total: float, exemption: float) -> float:
    """Get taxable amount after exemption."""
    return max(0, total - exemption)
