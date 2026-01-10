"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Validation Rules - Pure functions for data validation.
All functions are pure, deterministic, and atomic.
"""

import re


def is_required(value) -> dict:
    """Check if value is present."""
    valid = value is not None and value != ""
    return {"valid": valid, "error": "Value is required" if not valid else None}


def is_string(value) -> dict:
    """Check if value is a string."""
    valid = isinstance(value, str)
    return {"valid": valid, "error": "Must be a string" if not valid else None}


def is_number(value) -> dict:
    """Check if value is a number."""
    valid = isinstance(value, (int, float)) and not isinstance(value, bool)
    return {"valid": valid, "error": "Must be a number" if not valid else None}


def is_integer(value) -> dict:
    """Check if value is an integer."""
    valid = isinstance(value, int) and not isinstance(value, bool)
    return {"valid": valid, "error": "Must be an integer" if not valid else None}


def is_boolean(value) -> dict:
    """Check if value is a boolean."""
    valid = isinstance(value, bool)
    return {"valid": valid, "error": "Must be a boolean" if not valid else None}


def is_list(value) -> dict:
    """Check if value is a list."""
    valid = isinstance(value, list)
    return {"valid": valid, "error": "Must be a list" if not valid else None}


def is_dict(value) -> dict:
    """Check if value is a dictionary."""
    valid = isinstance(value, dict)
    return {"valid": valid, "error": "Must be an object" if not valid else None}


def min_length(value: str, length: int) -> dict:
    """Check minimum length."""
    valid = len(value) >= length
    return {"valid": valid, "error": f"Must be at least {length} characters" if not valid else None}


def max_length(value: str, length: int) -> dict:
    """Check maximum length."""
    valid = len(value) <= length
    return {"valid": valid, "error": f"Must be at most {length} characters" if not valid else None}


def exact_length(value: str, length: int) -> dict:
    """Check exact length."""
    valid = len(value) == length
    return {"valid": valid, "error": f"Must be exactly {length} characters" if not valid else None}


def min_value(value, minimum) -> dict:
    """Check minimum value."""
    valid = value >= minimum
    return {"valid": valid, "error": f"Must be at least {minimum}" if not valid else None}


def max_value(value, maximum) -> dict:
    """Check maximum value."""
    valid = value <= maximum
    return {"valid": valid, "error": f"Must be at most {maximum}" if not valid else None}


def in_range(value, minimum, maximum) -> dict:
    """Check if value is in range."""
    valid = minimum <= value <= maximum
    return {"valid": valid, "error": f"Must be between {minimum} and {maximum}" if not valid else None}


def matches_pattern(value: str, pattern: str) -> dict:
    """Check if value matches regex pattern."""
    valid = bool(re.match(pattern, value))
    return {"valid": valid, "error": "Invalid format" if not valid else None}


def is_email_format(value: str) -> dict:
    """Check email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    valid = bool(re.match(pattern, value))
    return {"valid": valid, "error": "Invalid email format" if not valid else None}


def is_url_format(value: str) -> dict:
    """Check URL format."""
    pattern = r'^https?://[^\s]+$'
    valid = bool(re.match(pattern, value))
    return {"valid": valid, "error": "Invalid URL format" if not valid else None}


def is_phone_format(value: str) -> dict:
    """Check phone number format."""
    pattern = r'^[\d\s\-\+\(\)]{7,20}$'
    valid = bool(re.match(pattern, value))
    return {"valid": valid, "error": "Invalid phone format" if not valid else None}


def is_uuid_format(value: str) -> dict:
    """Check UUID format."""
    pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    valid = bool(re.match(pattern, value))
    return {"valid": valid, "error": "Invalid UUID format" if not valid else None}


def is_alphanumeric(value: str) -> dict:
    """Check if value is alphanumeric."""
    valid = value.isalnum()
    return {"valid": valid, "error": "Must be alphanumeric" if not valid else None}


def is_alpha(value: str) -> dict:
    """Check if value is alphabetic."""
    valid = value.isalpha()
    return {"valid": valid, "error": "Must contain only letters" if not valid else None}


def is_numeric(value: str) -> dict:
    """Check if value is numeric string."""
    valid = value.isdigit()
    return {"valid": valid, "error": "Must contain only digits" if not valid else None}


def is_in_list(value, allowed_values: list) -> dict:
    """Check if value is in allowed list."""
    valid = value in allowed_values
    return {"valid": valid, "error": f"Must be one of: {allowed_values}" if not valid else None}


def is_not_in_list(value, forbidden_values: list) -> dict:
    """Check if value is not in forbidden list."""
    valid = value not in forbidden_values
    return {"valid": valid, "error": "Value is not allowed" if not valid else None}


def has_uppercase(value: str) -> dict:
    """Check if value has uppercase letter."""
    valid = any(c.isupper() for c in value)
    return {"valid": valid, "error": "Must contain uppercase letter" if not valid else None}


def has_lowercase(value: str) -> dict:
    """Check if value has lowercase letter."""
    valid = any(c.islower() for c in value)
    return {"valid": valid, "error": "Must contain lowercase letter" if not valid else None}


def has_digit(value: str) -> dict:
    """Check if value has digit."""
    valid = any(c.isdigit() for c in value)
    return {"valid": valid, "error": "Must contain a digit" if not valid else None}


def has_special_char(value: str) -> dict:
    """Check if value has special character."""
    special = set("!@#$%^&*()_+-=[]{}|;':\",./<>?")
    valid = any(c in special for c in value)
    return {"valid": valid, "error": "Must contain a special character" if not valid else None}


def validate_password_strength(password: str, min_length: int) -> dict:
    """Validate password strength."""
    checks = [
        min_length(password, min_length),
        has_uppercase(password),
        has_lowercase(password),
        has_digit(password),
    ]
    errors = [c["error"] for c in checks if not c["valid"]]
    return {"valid": len(errors) == 0, "errors": errors}


def validate_multiple(value, rules: list) -> dict:
    """Apply multiple validation rules."""
    errors = []
    for rule in rules:
        result = rule(value)
        if not result["valid"]:
            errors.append(result["error"])
    return {"valid": len(errors) == 0, "errors": errors}


def validate_object(obj: dict, schema: dict) -> dict:
    """Validate object against schema."""
    errors = {}
    for field, rules in schema.items():
        value = obj.get(field)
        result = validate_multiple(value, rules)
        if not result["valid"]:
            errors[field] = result["errors"]
    return {"valid": len(errors) == 0, "errors": errors}


def is_positive(value) -> dict:
    """Check if value is positive."""
    valid = value > 0
    return {"valid": valid, "error": "Must be positive" if not valid else None}


def is_negative(value) -> dict:
    """Check if value is negative."""
    valid = value < 0
    return {"valid": valid, "error": "Must be negative" if not valid else None}


def is_non_negative(value) -> dict:
    """Check if value is non-negative."""
    valid = value >= 0
    return {"valid": valid, "error": "Must be non-negative" if not valid else None}
