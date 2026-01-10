"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Discount Utilities - Pure functions for discount calculations.
All functions are pure, deterministic, and atomic.
"""


def apply_percentage_discount(amount: float, percentage: float) -> float:
    """Apply percentage discount."""
    return round(amount * (1 - percentage / 100), 2)


def apply_fixed_discount(amount: float, discount: float) -> float:
    """Apply fixed amount discount."""
    return round(max(0, amount - discount), 2)


def calculate_discount_amount(original: float, percentage: float) -> float:
    """Calculate discount amount from percentage."""
    return round(original * percentage / 100, 2)


def get_discount_percentage(original: float, discounted: float) -> float:
    """Calculate discount percentage from prices."""
    if original == 0:
        return 0
    return round((original - discounted) / original * 100, 2)


def apply_buy_x_get_y(quantity: int, buy_x: int, get_y: int, price: float) -> dict:
    """Apply buy X get Y free discount."""
    if quantity < buy_x:
        return {"paid": quantity, "free": 0, "total": round(quantity * price, 2)}
    sets = quantity // (buy_x + get_y)
    remaining = quantity % (buy_x + get_y)
    paid = sets * buy_x + min(remaining, buy_x)
    free = quantity - paid
    return {"paid": paid, "free": free, "total": round(paid * price, 2)}


def apply_tiered_discount(amount: float, tiers: list) -> dict:
    """Apply tiered discount based on amount."""
    for tier in sorted(tiers, key=lambda t: -t["threshold"]):
        if amount >= tier["threshold"]:
            discount = tier.get("percentage", 0)
            discounted = apply_percentage_discount(amount, discount)
            return {
                "original": amount,
                "discount_percentage": discount,
                "discount_amount": round(amount - discounted, 2),
                "final": discounted
            }
    return {
        "original": amount,
        "discount_percentage": 0,
        "discount_amount": 0,
        "final": amount
    }


def apply_quantity_discount(quantity: int, price: float, discounts: list) -> dict:
    """Apply quantity-based discount."""
    for discount in sorted(discounts, key=lambda d: -d["min_quantity"]):
        if quantity >= discount["min_quantity"]:
            rate = discount.get("percentage", 0)
            original = quantity * price
            final = apply_percentage_discount(original, rate)
            return {
                "quantity": quantity,
                "unit_price": price,
                "original": original,
                "discount_percentage": rate,
                "final": final
            }
    return {
        "quantity": quantity,
        "unit_price": price,
        "original": round(quantity * price, 2),
        "discount_percentage": 0,
        "final": round(quantity * price, 2)
    }


def combine_discounts(amount: float, discounts: list) -> float:
    """Apply multiple discounts sequentially."""
    current = amount
    for discount in discounts:
        if discount["type"] == "percentage":
            current = apply_percentage_discount(current, discount["value"])
        elif discount["type"] == "fixed":
            current = apply_fixed_discount(current, discount["value"])
    return current


def calculate_bundle_discount(items: list, bundle_discount: float) -> dict:
    """Calculate bundle discount."""
    original = sum(item["price"] for item in items)
    final = apply_percentage_discount(original, bundle_discount)
    return {
        "items": len(items),
        "original": original,
        "bundle_discount": bundle_discount,
        "savings": round(original - final, 2),
        "final": final
    }


def validate_coupon_amount(discount: float, min_amount: float, cart_total: float) -> dict:
    """Validate coupon against cart total."""
    if cart_total < min_amount:
        return {
            "valid": False,
            "reason": f"Minimum amount {min_amount} required"
        }
    return {"valid": True, "discount": min(discount, cart_total)}


def cap_discount(discount: float, max_discount: float) -> float:
    """Cap discount at maximum amount."""
    return min(discount, max_discount)


def calculate_savings(original: float, final: float) -> dict:
    """Calculate savings details."""
    savings = round(original - final, 2)
    percentage = get_discount_percentage(original, final)
    return {
        "original": original,
        "final": final,
        "savings": savings,
        "percentage": percentage
    }


def format_discount_display(percentage: float) -> str:
    """Format discount for display."""
    if percentage == int(percentage):
        return f"{int(percentage)}% OFF"
    return f"{percentage}% OFF"


def is_better_discount(discount1: dict, discount2: dict, cart_total: float) -> bool:
    """Compare which discount is better for cart."""
    def get_final(d):
        if d["type"] == "percentage":
            return apply_percentage_discount(cart_total, d["value"])
        return apply_fixed_discount(cart_total, d["value"])
    return get_final(discount1) < get_final(discount2)


def calculate_member_discount(amount: float, tier: str, tiers: dict) -> dict:
    """Calculate member tier discount."""
    rate = tiers.get(tier, 0)
    final = apply_percentage_discount(amount, rate)
    return {
        "tier": tier,
        "discount_rate": rate,
        "original": amount,
        "savings": round(amount - final, 2),
        "final": final
    }


def stackable_discounts(amount: float, discounts: list, stackable: bool) -> float:
    """Apply discounts with stacking rules."""
    if stackable:
        return combine_discounts(amount, discounts)
    best = amount
    for discount in discounts:
        if discount["type"] == "percentage":
            result = apply_percentage_discount(amount, discount["value"])
        else:
            result = apply_fixed_discount(amount, discount["value"])
        best = min(best, result)
    return best
