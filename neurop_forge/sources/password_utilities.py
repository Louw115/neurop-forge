"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Password Utilities - Pure functions for password operations.
All functions are pure, deterministic, and atomic.
"""

import hashlib
import re


def check_length(password: str, min_length: int) -> bool:
    """Check if password meets minimum length."""
    return len(password) >= min_length


def check_max_length(password: str, max_length: int) -> bool:
    """Check if password is under maximum length."""
    return len(password) <= max_length


def has_uppercase(password: str) -> bool:
    """Check if password has uppercase letter."""
    return any(c.isupper() for c in password)


def has_lowercase(password: str) -> bool:
    """Check if password has lowercase letter."""
    return any(c.islower() for c in password)


def has_digit(password: str) -> bool:
    """Check if password has digit."""
    return any(c.isdigit() for c in password)


def has_special_char(password: str) -> bool:
    """Check if password has special character."""
    special = set("!@#$%^&*()_+-=[]{}|;':\",./<>?`~")
    return any(c in special for c in password)


def count_uppercase(password: str) -> int:
    """Count uppercase letters."""
    return sum(1 for c in password if c.isupper())


def count_lowercase(password: str) -> int:
    """Count lowercase letters."""
    return sum(1 for c in password if c.islower())


def count_digits(password: str) -> int:
    """Count digits."""
    return sum(1 for c in password if c.isdigit())


def count_special(password: str) -> int:
    """Count special characters."""
    special = set("!@#$%^&*()_+-=[]{}|;':\",./<>?`~")
    return sum(1 for c in password if c in special)


def calculate_strength_score(password: str) -> int:
    """Calculate password strength score 0-100."""
    score = 0
    length = len(password)
    if length >= 8:
        score += 20
    if length >= 12:
        score += 10
    if length >= 16:
        score += 10
    if has_uppercase(password):
        score += 15
    if has_lowercase(password):
        score += 15
    if has_digit(password):
        score += 15
    if has_special_char(password):
        score += 15
    return min(100, score)


def get_strength_label(score: int) -> str:
    """Get strength label from score."""
    if score < 20:
        return "very_weak"
    elif score < 40:
        return "weak"
    elif score < 60:
        return "fair"
    elif score < 80:
        return "strong"
    return "very_strong"


def validate_password(password: str, rules: dict) -> dict:
    """Validate password against rules."""
    errors = []
    if rules.get("min_length") and not check_length(password, rules["min_length"]):
        errors.append(f"Must be at least {rules['min_length']} characters")
    if rules.get("max_length") and not check_max_length(password, rules["max_length"]):
        errors.append(f"Must be at most {rules['max_length']} characters")
    if rules.get("require_uppercase") and not has_uppercase(password):
        errors.append("Must contain uppercase letter")
    if rules.get("require_lowercase") and not has_lowercase(password):
        errors.append("Must contain lowercase letter")
    if rules.get("require_digit") and not has_digit(password):
        errors.append("Must contain digit")
    if rules.get("require_special") and not has_special_char(password):
        errors.append("Must contain special character")
    return {"valid": len(errors) == 0, "errors": errors}


def has_repeating_chars(password: str, max_repeat: int) -> bool:
    """Check for repeating characters."""
    pattern = r'(.)\1{' + str(max_repeat) + r',}'
    return bool(re.search(pattern, password))


def has_sequential_chars(password: str, length: int) -> bool:
    """Check for sequential characters."""
    sequences = "abcdefghijklmnopqrstuvwxyz0123456789"
    lower = password.lower()
    for i in range(len(sequences) - length + 1):
        seq = sequences[i:i+length]
        if seq in lower or seq[::-1] in lower:
            return True
    return False


def is_common_password(password: str, common_list: list) -> bool:
    """Check if password is in common passwords list."""
    return password.lower() in [p.lower() for p in common_list]


def contains_username(password: str, username: str) -> bool:
    """Check if password contains username."""
    return username.lower() in password.lower()


def generate_requirements_text(rules: dict) -> str:
    """Generate password requirements text."""
    reqs = []
    if rules.get("min_length"):
        reqs.append(f"At least {rules['min_length']} characters")
    if rules.get("require_uppercase"):
        reqs.append("One uppercase letter")
    if rules.get("require_lowercase"):
        reqs.append("One lowercase letter")
    if rules.get("require_digit"):
        reqs.append("One number")
    if rules.get("require_special"):
        reqs.append("One special character")
    return ", ".join(reqs)


def mask_password(password: str, mask_char: str) -> str:
    """Mask password with character."""
    return mask_char * len(password)


def hash_password_sha256(password: str, salt: str) -> str:
    """Hash password with SHA256 and salt."""
    combined = (password + salt).encode()
    return hashlib.sha256(combined).hexdigest()


def generate_salt_deterministic(seed: str) -> str:
    """Generate deterministic salt from seed."""
    return hashlib.sha256(seed.encode()).hexdigest()[:32]


def entropy_bits(password: str) -> float:
    """Calculate password entropy in bits."""
    import math
    charset_size = 0
    if has_lowercase(password):
        charset_size += 26
    if has_uppercase(password):
        charset_size += 26
    if has_digit(password):
        charset_size += 10
    if has_special_char(password):
        charset_size += 32
    if charset_size == 0:
        return 0
    return len(password) * math.log2(charset_size)


def is_strong_enough(password: str, min_entropy: float) -> bool:
    """Check if password has enough entropy."""
    return entropy_bits(password) >= min_entropy
