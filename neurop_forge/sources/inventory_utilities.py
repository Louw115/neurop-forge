"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Inventory Utilities - Pure functions for inventory management.
All functions are pure, deterministic, and atomic.
"""


def create_inventory_item(sku: str, quantity: int, reorder_point: int) -> dict:
    """Create inventory item."""
    return {
        "sku": sku,
        "quantity": quantity,
        "reorder_point": reorder_point,
        "reserved": 0
    }


def update_quantity(item: dict, new_quantity: int) -> dict:
    """Update item quantity."""
    return {**item, "quantity": max(0, new_quantity)}


def add_quantity(item: dict, amount: int) -> dict:
    """Add to quantity."""
    return update_quantity(item, item["quantity"] + amount)


def subtract_quantity(item: dict, amount: int) -> dict:
    """Subtract from quantity."""
    return update_quantity(item, item["quantity"] - amount)


def reserve_quantity(item: dict, amount: int) -> dict:
    """Reserve quantity for order."""
    available = get_available(item)
    if amount > available:
        return item
    return {**item, "reserved": item["reserved"] + amount}


def release_reserved(item: dict, amount: int) -> dict:
    """Release reserved quantity."""
    new_reserved = max(0, item["reserved"] - amount)
    return {**item, "reserved": new_reserved}


def commit_reserved(item: dict, amount: int) -> dict:
    """Commit reserved quantity (subtract from both)."""
    new_reserved = max(0, item["reserved"] - amount)
    new_quantity = max(0, item["quantity"] - amount)
    return {**item, "quantity": new_quantity, "reserved": new_reserved}


def get_available(item: dict) -> int:
    """Get available quantity (total - reserved)."""
    return max(0, item["quantity"] - item["reserved"])


def needs_reorder(item: dict) -> bool:
    """Check if item needs reorder."""
    return item["quantity"] <= item["reorder_point"]


def calculate_reorder_quantity(item: dict, target_days: int, avg_daily_usage: float) -> int:
    """Calculate reorder quantity."""
    target = int(target_days * avg_daily_usage)
    return max(0, target - item["quantity"])


def get_stock_status(item: dict) -> str:
    """Get stock status."""
    available = get_available(item)
    if available <= 0:
        return "out_of_stock"
    if needs_reorder(item):
        return "low_stock"
    return "in_stock"


def can_fulfill(item: dict, quantity: int) -> bool:
    """Check if order can be fulfilled."""
    return get_available(item) >= quantity


def allocate_stock(items: list, required: int) -> dict:
    """Allocate stock from multiple locations."""
    allocated = []
    remaining = required
    for item in items:
        available = get_available(item)
        if available > 0:
            take = min(available, remaining)
            allocated.append({"sku": item["sku"], "quantity": take})
            remaining -= take
            if remaining <= 0:
                break
    return {
        "allocated": allocated,
        "fulfilled": remaining <= 0,
        "shortfall": max(0, remaining)
    }


def calculate_inventory_value(items: list, prices: dict) -> float:
    """Calculate total inventory value."""
    total = 0
    for item in items:
        price = prices.get(item["sku"], 0)
        total += item["quantity"] * price
    return round(total, 2)


def get_low_stock_items(items: list) -> list:
    """Get all low stock items."""
    return [item for item in items if needs_reorder(item)]


def get_out_of_stock_items(items: list) -> list:
    """Get all out of stock items."""
    return [item for item in items if get_available(item) <= 0]


def calculate_turnover(sold: int, average_inventory: float) -> float:
    """Calculate inventory turnover ratio."""
    if average_inventory <= 0:
        return 0
    return round(sold / average_inventory, 2)


def calculate_days_of_stock(quantity: int, daily_usage: float) -> int:
    """Calculate days of stock remaining."""
    if daily_usage <= 0:
        return float("inf")
    return int(quantity / daily_usage)


def create_adjustment(sku: str, quantity_change: int, reason: str, timestamp: int) -> dict:
    """Create inventory adjustment record."""
    return {
        "sku": sku,
        "quantity_change": quantity_change,
        "reason": reason,
        "timestamp": timestamp
    }


def apply_adjustment(item: dict, adjustment: dict) -> dict:
    """Apply adjustment to item."""
    return add_quantity(item, adjustment["quantity_change"])


def calculate_abc_class(items: list, value_percentages: dict) -> dict:
    """Classify items by ABC analysis."""
    a_threshold = value_percentages.get("A", 80)
    b_threshold = value_percentages.get("B", 95)
    total_value = sum(i.get("value", 0) for i in items)
    sorted_items = sorted(items, key=lambda x: -x.get("value", 0))
    classes = {"A": [], "B": [], "C": []}
    cumulative = 0
    for item in sorted_items:
        cumulative += item.get("value", 0)
        percentage = (cumulative / total_value * 100) if total_value > 0 else 0
        if percentage <= a_threshold:
            classes["A"].append(item["sku"])
        elif percentage <= b_threshold:
            classes["B"].append(item["sku"])
        else:
            classes["C"].append(item["sku"])
    return classes


def merge_inventories(inv1: dict, inv2: dict) -> dict:
    """Merge two inventory records."""
    merged = dict(inv1)
    for sku, item in inv2.items():
        if sku in merged:
            merged[sku] = add_quantity(merged[sku], item["quantity"])
        else:
            merged[sku] = item
    return merged
