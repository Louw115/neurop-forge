"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
PREMIUM MODULE - Commercial license required.
"""

"""
Financial Utilities - Pure functions for financial calculations.
All functions are pure, deterministic, and atomic.
"""

def calculate_simple_interest(principal: float, rate: float, years: float) -> float:
    """Calculate simple interest."""
    return principal * (rate / 100) * years


def calculate_compound_interest(principal: float, rate: float, compounds_per_year: int, years: float) -> float:
    """Calculate compound interest amount."""
    return principal * ((1 + (rate / 100) / compounds_per_year) ** (compounds_per_year * years)) - principal


def calculate_future_value(principal: float, rate: float, compounds_per_year: int, years: float) -> float:
    """Calculate future value with compound interest."""
    return principal * ((1 + (rate / 100) / compounds_per_year) ** (compounds_per_year * years))


def calculate_present_value(future_value: float, rate: float, years: float) -> float:
    """Calculate present value."""
    return future_value / ((1 + rate / 100) ** years)


def calculate_monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """Calculate monthly loan payment."""
    if annual_rate == 0:
        return principal / months if months > 0 else 0
    monthly_rate = annual_rate / 100 / 12
    return principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)


def calculate_loan_amortization(principal: float, annual_rate: float, months: int) -> list:
    """Calculate loan amortization schedule."""
    schedule = []
    monthly_payment = calculate_monthly_payment(principal, annual_rate, months)
    monthly_rate = annual_rate / 100 / 12
    balance = principal
    for month in range(1, months + 1):
        interest = balance * monthly_rate
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        schedule.append({
            "month": month,
            "payment": round(monthly_payment, 2),
            "principal": round(principal_payment, 2),
            "interest": round(interest, 2),
            "balance": round(max(0, balance), 2)
        })
    return schedule


def calculate_total_interest_paid(principal: float, annual_rate: float, months: int) -> float:
    """Calculate total interest paid over loan term."""
    monthly_payment = calculate_monthly_payment(principal, annual_rate, months)
    return (monthly_payment * months) - principal


def calculate_roi(gain: float, cost: float) -> float:
    """Calculate return on investment percentage."""
    if cost <= 0:
        return 0.0
    return ((gain - cost) / cost) * 100


def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
    """Calculate compound annual growth rate."""
    if start_value <= 0 or years <= 0:
        return 0.0
    return ((end_value / start_value) ** (1 / years) - 1) * 100


def calculate_npv(cash_flows: list, discount_rate: float) -> float:
    """Calculate net present value."""
    npv = 0.0
    for i, cf in enumerate(cash_flows):
        npv += cf / ((1 + discount_rate / 100) ** i)
    return npv


def calculate_irr_approx(cash_flows: list, max_iterations: int, tolerance: float) -> float:
    """Calculate approximate internal rate of return."""
    if not cash_flows:
        return 0.0
    low_rate, high_rate = -50.0, 100.0
    for _ in range(max_iterations):
        mid_rate = (low_rate + high_rate) / 2
        npv = calculate_npv(cash_flows, mid_rate)
        if abs(npv) < tolerance:
            return mid_rate
        if npv > 0:
            low_rate = mid_rate
        else:
            high_rate = mid_rate
    return (low_rate + high_rate) / 2


def calculate_payback_period(initial_investment: float, annual_cash_flows: list) -> float:
    """Calculate payback period in years."""
    cumulative = 0.0
    for i, cf in enumerate(annual_cash_flows):
        cumulative += cf
        if cumulative >= initial_investment:
            if i == 0:
                return initial_investment / cf if cf > 0 else 0
            prev_cumulative = cumulative - cf
            remaining = initial_investment - prev_cumulative
            return i + (remaining / cf if cf > 0 else 0)
    return float('inf')


def calculate_break_even(fixed_costs: float, price_per_unit: float, variable_cost_per_unit: float) -> float:
    """Calculate break-even quantity."""
    margin = price_per_unit - variable_cost_per_unit
    if margin <= 0:
        return float('inf')
    return fixed_costs / margin


def calculate_profit_margin(revenue: float, cost: float) -> float:
    """Calculate profit margin percentage."""
    if revenue <= 0:
        return 0.0
    return ((revenue - cost) / revenue) * 100


def calculate_gross_margin(revenue: float, cogs: float) -> float:
    """Calculate gross margin percentage."""
    return calculate_profit_margin(revenue, cogs)


def calculate_debt_to_equity(total_debt: float, total_equity: float) -> float:
    """Calculate debt to equity ratio."""
    if total_equity <= 0:
        return 0.0
    return total_debt / total_equity


def calculate_current_ratio(current_assets: float, current_liabilities: float) -> float:
    """Calculate current ratio."""
    if current_liabilities <= 0:
        return 0.0
    return current_assets / current_liabilities


def calculate_quick_ratio(current_assets: float, inventory: float, current_liabilities: float) -> float:
    """Calculate quick ratio (acid test)."""
    if current_liabilities <= 0:
        return 0.0
    return (current_assets - inventory) / current_liabilities


def convert_currency(amount: float, exchange_rate: float) -> float:
    """Convert currency amount."""
    return amount * exchange_rate


def calculate_exchange_spread(bid: float, ask: float) -> float:
    """Calculate exchange rate spread percentage."""
    if ask <= 0:
        return 0.0
    return ((ask - bid) / ask) * 100


def calculate_depreciation_straight_line(cost: float, salvage_value: float, useful_life_years: int) -> float:
    """Calculate annual straight-line depreciation."""
    if useful_life_years <= 0:
        return 0.0
    return (cost - salvage_value) / useful_life_years


def calculate_depreciation_declining(cost: float, rate: float, year: int) -> float:
    """Calculate depreciation using declining balance method."""
    remaining = cost
    for _ in range(year - 1):
        remaining -= remaining * (rate / 100)
    return remaining * (rate / 100)


def format_currency(amount: float, symbol: str, decimals: int) -> str:
    """Format amount as currency."""
    return f"{symbol}{amount:,.{decimals}f}"


def format_percentage(value: float, decimals: int) -> str:
    """Format value as percentage."""
    return f"{value:.{decimals}f}%"


def calculate_tax_amount(amount: float, tax_rate: float) -> float:
    """Calculate tax amount."""
    return amount * (tax_rate / 100)


def calculate_after_tax(amount: float, tax_rate: float) -> float:
    """Calculate amount after tax deduction."""
    return amount * (1 - tax_rate / 100)


def calculate_price_with_tax(price: float, tax_rate: float) -> float:
    """Calculate price including tax."""
    return price * (1 + tax_rate / 100)


def extract_tax_from_total(total_with_tax: float, tax_rate: float) -> dict:
    """Extract tax amount from total that includes tax."""
    price = total_with_tax / (1 + tax_rate / 100)
    tax = total_with_tax - price
    return {"price": price, "tax": tax}
