"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Shipping Utilities - Pure functions for shipping calculations.
All functions are pure, deterministic, and atomic.
"""


def calculate_shipping_cost(weight: float, rate_per_unit: float) -> float:
    """Calculate shipping cost by weight."""
    return round(weight * rate_per_unit, 2)


def calculate_dimensional_weight(length: float, width: float, height: float, dim_factor: float) -> float:
    """Calculate dimensional weight."""
    return (length * width * height) / dim_factor


def get_billable_weight(actual_weight: float, dim_weight: float) -> float:
    """Get billable weight (greater of actual or dim)."""
    return max(actual_weight, dim_weight)


def calculate_zone_rate(zone: int, base_rate: float, zone_multiplier: float) -> float:
    """Calculate zone-based rate."""
    return round(base_rate * (1 + (zone - 1) * zone_multiplier), 2)


def estimate_delivery_days(distance: float, speed_factor: float, processing_days: int) -> int:
    """Estimate delivery days."""
    transit_days = int(distance / speed_factor) + 1
    return processing_days + transit_days


def is_expedited_available(distance: float, max_distance: float) -> bool:
    """Check if expedited shipping available."""
    return distance <= max_distance


def calculate_insurance(value: float, rate: float, min_fee: float) -> float:
    """Calculate shipping insurance."""
    fee = value * rate / 100
    return round(max(fee, min_fee), 2)


def validate_address_for_shipping(address: dict) -> dict:
    """Validate address for shipping."""
    errors = []
    if not address.get("street"):
        errors.append("Street address required")
    if not address.get("city"):
        errors.append("City required")
    if not address.get("zip"):
        errors.append("ZIP code required")
    return {"valid": len(errors) == 0, "errors": errors}


def is_po_box_allowed(service: str, po_box_services: list) -> bool:
    """Check if service delivers to PO boxes."""
    return service in po_box_services


def get_package_type(length: float, width: float, height: float) -> str:
    """Determine package type from dimensions."""
    max_dim = max(length, width, height)
    min_dim = min(length, width, height)
    if max_dim <= 6 and min_dim <= 4:
        return "small"
    if max_dim <= 12 and min_dim <= 8:
        return "medium"
    if max_dim <= 24 and min_dim <= 16:
        return "large"
    return "oversized"


def is_hazmat(product_flags: dict) -> bool:
    """Check if product is hazmat."""
    return product_flags.get("hazmat", False)


def requires_signature(value: float, threshold: float) -> bool:
    """Check if shipment requires signature."""
    return value >= threshold


def calculate_fuel_surcharge(base_cost: float, fuel_rate: float) -> float:
    """Calculate fuel surcharge."""
    return round(base_cost * fuel_rate / 100, 2)


def calculate_residential_surcharge(is_residential: bool, surcharge: float) -> float:
    """Calculate residential delivery surcharge."""
    return surcharge if is_residential else 0


def get_carrier_options(weight: float, value: float, carriers: dict) -> list:
    """Get available carrier options."""
    available = []
    for carrier, limits in carriers.items():
        if weight <= limits.get("max_weight", float("inf")):
            if value <= limits.get("max_value", float("inf")):
                available.append(carrier)
    return available


def calculate_total_shipping(base: float, surcharges: list, discounts: list) -> float:
    """Calculate total shipping cost."""
    total = base + sum(surcharges)
    for discount in discounts:
        if discount["type"] == "percentage":
            total *= (1 - discount["value"] / 100)
        else:
            total -= discount["value"]
    return round(max(0, total), 2)


def create_shipment(order_id: str, weight: float, dims: dict, service: str) -> dict:
    """Create shipment record."""
    return {
        "order_id": order_id,
        "weight": weight,
        "dimensions": dims,
        "service": service,
        "status": "pending"
    }


def update_tracking_status(shipment: dict, status: str, timestamp: int) -> dict:
    """Update shipment tracking status."""
    history = shipment.get("history", [])
    history.append({"status": status, "timestamp": timestamp})
    return {**shipment, "status": status, "history": history}


def is_delivered(shipment: dict) -> bool:
    """Check if shipment is delivered."""
    return shipment.get("status") == "delivered"


def calculate_return_shipping(original_cost: float, return_rate: float) -> float:
    """Calculate return shipping cost."""
    return round(original_cost * return_rate, 2)


def get_cutoff_time(service: str, cutoffs: dict) -> str:
    """Get shipping cutoff time for service."""
    return cutoffs.get(service, "00:00")


def is_before_cutoff(current_hour: int, cutoff_hour: int) -> bool:
    """Check if before shipping cutoff."""
    return current_hour < cutoff_hour
