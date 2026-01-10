"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Order Utilities - Pure functions for order management.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def create_order_id(prefix: str, timestamp: int, sequence: int) -> str:
    """Create order ID."""
    return f"{prefix}{timestamp}{sequence:04d}"


def create_order(order_id: str, customer_id: str, items: list, timestamp: int) -> dict:
    """Create order record."""
    return {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": items,
        "status": "pending",
        "created_at": timestamp,
        "updated_at": timestamp
    }


def calculate_order_subtotal(items: list) -> float:
    """Calculate order subtotal."""
    return round(sum(item["price"] * item["quantity"] for item in items), 2)


def calculate_order_total(subtotal: float, tax: float, shipping: float, discount: float) -> float:
    """Calculate order total."""
    return round(subtotal + tax + shipping - discount, 2)


def add_item_to_order(order: dict, item: dict) -> dict:
    """Add item to order."""
    new_items = order["items"] + [item]
    return {**order, "items": new_items}


def remove_item_from_order(order: dict, item_id: str) -> dict:
    """Remove item from order."""
    new_items = [i for i in order["items"] if i.get("item_id") != item_id]
    return {**order, "items": new_items}


def update_item_quantity(order: dict, item_id: str, quantity: int) -> dict:
    """Update item quantity in order."""
    new_items = []
    for item in order["items"]:
        if item.get("item_id") == item_id:
            new_items.append({**item, "quantity": quantity})
        else:
            new_items.append(item)
    return {**order, "items": new_items}


def update_order_status(order: dict, status: str, timestamp: int) -> dict:
    """Update order status."""
    return {**order, "status": status, "updated_at": timestamp}


def is_order_status(order: dict, status: str) -> bool:
    """Check order status."""
    return order.get("status") == status


def can_cancel_order(order: dict) -> bool:
    """Check if order can be cancelled."""
    return order.get("status") in ["pending", "processing"]


def can_modify_order(order: dict) -> bool:
    """Check if order can be modified."""
    return order.get("status") == "pending"


def validate_order_items(items: list) -> dict:
    """Validate order items."""
    errors = []
    for i, item in enumerate(items):
        if not item.get("sku"):
            errors.append(f"Item {i}: SKU required")
        if item.get("quantity", 0) <= 0:
            errors.append(f"Item {i}: Invalid quantity")
        if item.get("price", 0) < 0:
            errors.append(f"Item {i}: Invalid price")
    return {"valid": len(errors) == 0, "errors": errors}


def get_order_item_count(order: dict) -> int:
    """Get total item count in order."""
    return sum(item.get("quantity", 0) for item in order.get("items", []))


def get_unique_item_count(order: dict) -> int:
    """Get unique item count."""
    return len(order.get("items", []))


def split_order(order: dict, item_ids: list) -> dict:
    """Split order into two orders."""
    split_items = []
    remaining_items = []
    for item in order.get("items", []):
        if item.get("item_id") in item_ids:
            split_items.append(item)
        else:
            remaining_items.append(item)
    return {
        "split": {**order, "items": split_items},
        "remaining": {**order, "items": remaining_items}
    }


def merge_orders(order1: dict, order2: dict) -> dict:
    """Merge two orders."""
    combined_items = order1.get("items", []) + order2.get("items", [])
    return {
        **order1,
        "items": combined_items,
        "merged_from": [order1["order_id"], order2["order_id"]]
    }


def create_order_summary(order: dict) -> dict:
    """Create order summary."""
    items = order.get("items", [])
    return {
        "order_id": order["order_id"],
        "status": order["status"],
        "item_count": get_order_item_count(order),
        "unique_items": get_unique_item_count(order),
        "subtotal": calculate_order_subtotal(items)
    }


def calculate_order_weight(items: list, weights: dict) -> float:
    """Calculate total order weight."""
    total = 0
    for item in items:
        weight = weights.get(item.get("sku"), 0)
        total += weight * item.get("quantity", 1)
    return round(total, 2)


def generate_order_hash(order: dict) -> str:
    """Generate order hash for verification."""
    data = f"{order['order_id']}{order['customer_id']}{len(order.get('items', []))}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def apply_order_discount(order: dict, discount_code: str, amount: float) -> dict:
    """Apply discount to order."""
    return {
        **order,
        "discount_code": discount_code,
        "discount_amount": amount
    }


def create_order_timeline(order: dict) -> list:
    """Create order timeline from status changes."""
    return [
        {"status": order["status"], "timestamp": order["updated_at"]}
    ]
