"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
E-commerce Patterns - Pure functions for e-commerce business logic.
All functions are pure, deterministic, and atomic.
PREMIUM MODULE - Commercial license required.
"""

def calculate_line_total(quantity: int, unit_price: float) -> float:
    """Calculate line item total."""
    return quantity * unit_price


def calculate_subtotal(line_totals: list) -> float:
    """Calculate order subtotal from line totals."""
    return sum(line_totals)


def calculate_discount_amount(subtotal: float, discount_percent: float) -> float:
    """Calculate discount amount."""
    return subtotal * (discount_percent / 100)


def apply_discount(subtotal: float, discount_amount: float) -> float:
    """Apply discount to subtotal."""
    return max(0, subtotal - discount_amount)


def calculate_tax_amount(amount: float, tax_rate: float) -> float:
    """Calculate tax amount."""
    return amount * (tax_rate / 100)


def calculate_order_total(subtotal: float, discount: float, tax: float, shipping: float) -> float:
    """Calculate final order total."""
    return subtotal - discount + tax + shipping


def calculate_shipping_cost(weight: float, distance: float, base_rate: float, per_kg_rate: float, per_km_rate: float) -> float:
    """Calculate shipping cost."""
    return base_rate + (weight * per_kg_rate) + (distance * per_km_rate)


def is_free_shipping_eligible(subtotal: float, threshold: float) -> bool:
    """Check if order qualifies for free shipping."""
    return subtotal >= threshold


def calculate_quantity_discount(quantity: int, tiers: list) -> float:
    """Calculate quantity-based discount percentage."""
    discount = 0.0
    for tier in sorted(tiers, key=lambda t: t["min_qty"], reverse=True):
        if quantity >= tier["min_qty"]:
            discount = tier["discount_percent"]
            break
    return discount


def validate_coupon_code(code: str, valid_codes: dict, current_date: str) -> dict:
    """Validate a coupon code."""
    if code not in valid_codes:
        return {"valid": False, "error": "Invalid coupon code"}
    coupon = valid_codes[code]
    if coupon.get("expires") and current_date > coupon["expires"]:
        return {"valid": False, "error": "Coupon has expired"}
    if coupon.get("uses_remaining", 1) <= 0:
        return {"valid": False, "error": "Coupon usage limit reached"}
    return {"valid": True, "discount": coupon.get("discount", 0), "type": coupon.get("type", "percent")}


def apply_coupon_discount(subtotal: float, coupon: dict) -> float:
    """Apply coupon discount to subtotal."""
    if coupon["type"] == "percent":
        return subtotal * (coupon["discount"] / 100)
    elif coupon["type"] == "fixed":
        return min(subtotal, coupon["discount"])
    return 0


def calculate_cart_weight(items: list) -> float:
    """Calculate total cart weight."""
    return sum(item.get("weight", 0) * item.get("quantity", 1) for item in items)


def is_in_stock(available_qty: int, requested_qty: int) -> bool:
    """Check if requested quantity is available."""
    return available_qty >= requested_qty


def calculate_backorder_qty(available_qty: int, requested_qty: int) -> int:
    """Calculate quantity that would be backordered."""
    return max(0, requested_qty - available_qty)


def format_sku(prefix: str, category: str, product_id: int, variant: str) -> str:
    """Format a SKU code."""
    return f"{prefix}-{category}-{product_id:06d}-{variant}".upper()


def parse_sku(sku: str) -> dict:
    """Parse a SKU code into components."""
    parts = sku.split("-")
    if len(parts) >= 4:
        return {
            "prefix": parts[0],
            "category": parts[1],
            "product_id": parts[2],
            "variant": parts[3]
        }
    return {"raw": sku}


def generate_order_number(prefix: str, timestamp: str, sequence: int) -> str:
    """Generate an order number."""
    date_part = timestamp[:10].replace("-", "")
    return f"{prefix}{date_part}{sequence:06d}"


def calculate_loyalty_points(order_total: float, points_per_dollar: float) -> int:
    """Calculate loyalty points earned."""
    return int(order_total * points_per_dollar)


def calculate_points_value(points: int, value_per_point: float) -> float:
    """Calculate monetary value of loyalty points."""
    return points * value_per_point


def is_eligible_for_return(purchase_date: str, current_date: str, return_window_days: int) -> bool:
    """Check if item is eligible for return."""
    from datetime import datetime
    purchase = datetime.fromisoformat(purchase_date)
    current = datetime.fromisoformat(current_date)
    days_since = (current - purchase).days
    return days_since <= return_window_days


def calculate_refund_amount(original_price: float, condition: str, restocking_fee_percent: float) -> float:
    """Calculate refund amount based on condition."""
    if condition == "unopened":
        return original_price
    elif condition == "like_new":
        return original_price * (1 - restocking_fee_percent / 100)
    elif condition == "used":
        return original_price * 0.5
    elif condition == "damaged":
        return 0
    return original_price


def format_price(amount: float, currency_symbol: str, decimals: int) -> str:
    """Format price for display."""
    return f"{currency_symbol}{amount:,.{decimals}f}"


def format_price_range(min_price: float, max_price: float, currency_symbol: str) -> str:
    """Format a price range."""
    if min_price == max_price:
        return format_price(min_price, currency_symbol, 2)
    return f"{format_price(min_price, currency_symbol, 2)} - {format_price(max_price, currency_symbol, 2)}"


def calculate_savings(original_price: float, sale_price: float) -> dict:
    """Calculate savings amount and percentage."""
    savings = original_price - sale_price
    percent = (savings / original_price * 100) if original_price > 0 else 0
    return {"amount": savings, "percent": percent}


def is_on_sale(original_price: float, current_price: float) -> bool:
    """Check if item is on sale."""
    return current_price < original_price


def calculate_installment_amount(total: float, num_installments: int, fee_percent: float) -> float:
    """Calculate installment payment amount."""
    total_with_fee = total * (1 + fee_percent / 100)
    return total_with_fee / num_installments


def validate_payment_amount(paid: float, expected: float, tolerance: float) -> bool:
    """Validate payment amount within tolerance."""
    return abs(paid - expected) <= tolerance


def calculate_commission(sale_amount: float, commission_rate: float) -> float:
    """Calculate sales commission."""
    return sale_amount * (commission_rate / 100)


def calculate_profit_margin(revenue: float, cost: float) -> float:
    """Calculate profit margin percentage."""
    if revenue <= 0:
        return 0.0
    return ((revenue - cost) / revenue) * 100


def calculate_markup(cost: float, markup_percent: float) -> float:
    """Calculate selling price with markup."""
    return cost * (1 + markup_percent / 100)


def build_order_summary(items: list, subtotal: float, discount: float, tax: float, shipping: float, total: float) -> dict:
    """Build an order summary."""
    return {
        "item_count": sum(item.get("quantity", 1) for item in items),
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "shipping": shipping,
        "total": total
    }


def calculate_average_order_value(total_revenue: float, order_count: int) -> float:
    """Calculate average order value."""
    if order_count <= 0:
        return 0.0
    return total_revenue / order_count


def calculate_conversion_rate(purchases: int, visitors: int) -> float:
    """Calculate conversion rate percentage."""
    if visitors <= 0:
        return 0.0
    return (purchases / visitors) * 100


def calculate_cart_abandonment_rate(carts_created: int, carts_completed: int) -> float:
    """Calculate cart abandonment rate percentage."""
    if carts_created <= 0:
        return 0.0
    return ((carts_created - carts_completed) / carts_created) * 100


def is_bundle_complete(bundle_items: list, cart_items: list) -> bool:
    """Check if cart contains all items in a bundle."""
    cart_skus = {item.get("sku") for item in cart_items}
    return all(item.get("sku") in cart_skus for item in bundle_items)


def calculate_bundle_discount(bundle_price: float, individual_total: float) -> float:
    """Calculate savings from bundle purchase."""
    return individual_total - bundle_price


def suggest_upsell(current_price: float, upsell_products: list, max_increase_percent: float) -> list:
    """Suggest upsell products within price range."""
    max_price = current_price * (1 + max_increase_percent / 100)
    return [p for p in upsell_products if current_price < p.get("price", 0) <= max_price]


def calculate_subscription_price(base_price: float, frequency: str, discount_percent: float) -> float:
    """Calculate subscription price with frequency discount."""
    frequency_multipliers = {"weekly": 4, "monthly": 1, "quarterly": 0.9, "yearly": 0.8}
    multiplier = frequency_multipliers.get(frequency, 1)
    return base_price * multiplier * (1 - discount_percent / 100)
