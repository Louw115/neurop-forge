"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Address Utilities - Pure functions for address operations.
All functions are pure, deterministic, and atomic.
"""

import re


def parse_address_lines(address: str) -> list:
    """Parse address into lines."""
    return [line.strip() for line in address.split("\n") if line.strip()]


def format_address(lines: list) -> str:
    """Format address lines to string."""
    return "\n".join(lines)


def format_single_line(lines: list, separator: str) -> str:
    """Format address as single line."""
    return separator.join(lines)


def extract_zip_code(address: str) -> str:
    """Extract ZIP/postal code from address."""
    patterns = [
        r'\b\d{5}(?:-\d{4})?\b',
        r'\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b',
        r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, address, re.IGNORECASE)
        if match:
            return match.group().upper()
    return ""


def extract_state(address: str) -> str:
    """Extract US state from address."""
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
    ]
    for state in states:
        if re.search(rf'\b{state}\b', address.upper()):
            return state
    return ""


def normalize_address(address: str) -> str:
    """Normalize address formatting."""
    address = " ".join(address.split())
    abbreviations = {
        r'\bStreet\b': 'St',
        r'\bAvenue\b': 'Ave',
        r'\bBoulevard\b': 'Blvd',
        r'\bDrive\b': 'Dr',
        r'\bRoad\b': 'Rd',
        r'\bLane\b': 'Ln',
        r'\bCourt\b': 'Ct',
        r'\bPlace\b': 'Pl',
        r'\bApartment\b': 'Apt',
        r'\bSuite\b': 'Ste',
        r'\bUnit\b': '#'
    }
    for pattern, replacement in abbreviations.items():
        address = re.sub(pattern, replacement, address, flags=re.IGNORECASE)
    return address


def parse_us_address(address: str) -> dict:
    """Parse US address into components."""
    lines = parse_address_lines(address)
    result = {
        "street1": "",
        "street2": "",
        "city": "",
        "state": "",
        "zip": ""
    }
    if lines:
        result["street1"] = lines[0]
    if len(lines) > 1:
        last_line = lines[-1]
        city_state_zip = re.match(r'^(.+?),?\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$', last_line, re.IGNORECASE)
        if city_state_zip:
            result["city"] = city_state_zip.group(1).strip(",")
            result["state"] = city_state_zip.group(2).upper()
            result["zip"] = city_state_zip.group(3)
        if len(lines) > 2:
            result["street2"] = lines[1]
    return result


def format_us_address(components: dict) -> str:
    """Format US address from components."""
    lines = []
    if components.get("street1"):
        lines.append(components["street1"])
    if components.get("street2"):
        lines.append(components["street2"])
    city_line = []
    if components.get("city"):
        city_line.append(components["city"] + ",")
    if components.get("state"):
        city_line.append(components["state"])
    if components.get("zip"):
        city_line.append(components["zip"])
    if city_line:
        lines.append(" ".join(city_line))
    return "\n".join(lines)


def is_po_box(address: str) -> bool:
    """Check if address is a PO Box."""
    return bool(re.search(r'\bP\.?O\.?\s*Box\b', address, re.IGNORECASE))


def has_unit_number(address: str) -> bool:
    """Check if address has unit/apartment number."""
    patterns = [r'\bApt\.?\s*\d', r'\bSte\.?\s*\d', r'\bUnit\s*\d', r'#\s*\d']
    return any(re.search(p, address, re.IGNORECASE) for p in patterns)


def extract_street_number(address: str) -> str:
    """Extract street number from address."""
    match = re.match(r'^(\d+(?:-\d+)?)\s', address)
    return match.group(1) if match else ""


def compare_addresses(addr1: str, addr2: str) -> bool:
    """Compare addresses for similarity."""
    def normalize(a):
        a = normalize_address(a)
        a = re.sub(r'[^\w\s]', '', a)
        return a.lower().split()
    words1 = set(normalize(addr1))
    words2 = set(normalize(addr2))
    if not words1 or not words2:
        return False
    intersection = len(words1 & words2)
    return intersection / max(len(words1), len(words2)) > 0.8


def mask_address(address: str) -> str:
    """Mask address for privacy."""
    lines = parse_address_lines(address)
    if not lines:
        return address
    masked = ["*** ***"]
    if len(lines) > 1:
        masked.append(lines[-1])
    return "\n".join(masked)


def get_country_from_zip(zip_code: str) -> str:
    """Guess country from ZIP code format."""
    if re.match(r'^\d{5}(-\d{4})?$', zip_code):
        return "US"
    if re.match(r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$', zip_code, re.IGNORECASE):
        return "CA"
    if re.match(r'^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$', zip_code, re.IGNORECASE):
        return "GB"
    return ""


def format_zip(zip_code: str, country: str) -> str:
    """Format ZIP code for country."""
    zip_code = zip_code.upper().replace(" ", "")
    if country == "US":
        if len(zip_code) > 5 and "-" not in zip_code:
            zip_code = zip_code[:5] + "-" + zip_code[5:9]
    elif country == "CA":
        if len(zip_code) == 6:
            zip_code = zip_code[:3] + " " + zip_code[3:]
    elif country == "GB":
        if len(zip_code) >= 5:
            zip_code = zip_code[:-3] + " " + zip_code[-3:]
    return zip_code
