"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Data Masking - Pure functions for sensitive data masking.
All functions are pure, deterministic, and atomic.
"""

import re
import hashlib


def mask_email(email: str) -> str:
    """Mask email address."""
    if "@" not in email:
        return email
    local, domain = email.rsplit("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone number showing only last 4 digits."""
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 4:
        return "*" * len(phone)
    masked = "*" * (len(digits) - 4) + digits[-4:]
    return masked


def mask_credit_card(card: str) -> str:
    """Mask credit card showing first 4 and last 4 digits."""
    digits = card.replace(" ", "").replace("-", "")
    if len(digits) < 8:
        return "*" * len(digits)
    masked = digits[:4] + "*" * (len(digits) - 8) + digits[-4:]
    return " ".join(masked[i:i+4] for i in range(0, len(masked), 4))


def mask_ssn(ssn: str) -> str:
    """Mask SSN showing only last 4 digits."""
    digits = re.sub(r'\D', '', ssn)
    if len(digits) < 4:
        return "*" * len(digits)
    return "***-**-" + digits[-4:]


def mask_ip(ip: str) -> str:
    """Mask IP address."""
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.*.*"
    return ip


def mask_name(name: str) -> str:
    """Mask name showing only initials."""
    words = name.split()
    return " ".join(w[0] + "*" * (len(w) - 1) if len(w) > 1 else w for w in words)


def mask_string(text: str, start: int, end: int, mask_char: str) -> str:
    """Mask portion of string."""
    if start >= len(text):
        return text
    end = min(end, len(text))
    return text[:start] + mask_char * (end - start) + text[end:]


def redact_field(value: str) -> str:
    """Fully redact a field."""
    return "[REDACTED]"


def hash_identifier(value: str, salt: str) -> str:
    """Hash identifier for pseudonymization."""
    combined = f"{salt}{value}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def tokenize_value(value: str, salt: str) -> str:
    """Create token for value."""
    return f"TOK_{hash_identifier(value, salt)}"


def mask_date_partial(date_str: str, keep_year: bool) -> str:
    """Partially mask date."""
    if keep_year:
        parts = date_str.split("-")
        if len(parts) >= 3:
            return f"{parts[0]}-**-**"
    return "****-**-**"


def mask_address(address: str) -> str:
    """Mask address keeping only street type."""
    parts = address.split()
    if len(parts) < 2:
        return "*" * len(address)
    masked_parts = ["***" if i < len(parts) - 1 else p for i, p in enumerate(parts)]
    return " ".join(masked_parts)


def generalize_age(age: int, bucket_size: int) -> str:
    """Generalize age to bucket."""
    lower = (age // bucket_size) * bucket_size
    upper = lower + bucket_size - 1
    return f"{lower}-{upper}"


def generalize_zip(zip_code: str, keep_digits: int) -> str:
    """Generalize ZIP code."""
    return zip_code[:keep_digits] + "*" * (len(zip_code) - keep_digits)


def suppress_if_rare(value: str, count: int, threshold: int) -> str:
    """Suppress value if it appears less than threshold times."""
    if count < threshold:
        return "[SUPPRESSED]"
    return value


def apply_noise_to_number(value: float, noise_factor: float, seed: int) -> float:
    """Add deterministic noise to number."""
    h = hashlib.sha256(f"{seed}{value}".encode()).digest()
    random_val = (h[0] / 255.0) * 2 - 1
    return value + value * noise_factor * random_val


def round_to_multiple(value: float, multiple: float) -> float:
    """Round value to nearest multiple."""
    return round(value / multiple) * multiple


def create_masking_config(fields: dict) -> dict:
    """Create masking configuration."""
    return {"fields": fields, "version": 1}


def apply_masking_config(data: dict, config: dict) -> dict:
    """Apply masking configuration to data."""
    result = dict(data)
    for field, mask_type in config.get("fields", {}).items():
        if field in result:
            if mask_type == "email":
                result[field] = mask_email(str(result[field]))
            elif mask_type == "phone":
                result[field] = mask_phone(str(result[field]))
            elif mask_type == "credit_card":
                result[field] = mask_credit_card(str(result[field]))
            elif mask_type == "redact":
                result[field] = redact_field(str(result[field]))
            elif mask_type == "name":
                result[field] = mask_name(str(result[field]))
    return result


def is_pii_field(field_name: str) -> bool:
    """Check if field name suggests PII."""
    pii_patterns = ["email", "phone", "ssn", "name", "address", "dob", "birth", 
                    "password", "credit", "card", "account", "social"]
    return any(p in field_name.lower() for p in pii_patterns)


def detect_pii_fields(fields: list) -> list:
    """Detect potential PII fields from names."""
    return [f for f in fields if is_pii_field(f)]


def mask_json_paths(data: dict, paths: list) -> dict:
    """Mask values at specific JSON paths."""
    import json
    result = json.loads(json.dumps(data))
    for path in paths:
        keys = path.split(".")
        current = result
        for key in keys[:-1]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                break
        else:
            if keys[-1] in current:
                current[keys[-1]] = redact_field(str(current[keys[-1]]))
    return result
