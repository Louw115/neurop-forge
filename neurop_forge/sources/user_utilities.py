"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
User Utilities - Pure functions for user operations.
All functions are pure, deterministic, and atomic.
"""

import hashlib
import re


def create_user(user_id: str, email: str, created_at: int) -> dict:
    """Create user object."""
    return {
        "user_id": user_id,
        "email": email,
        "created_at": created_at,
        "active": True,
        "verified": False,
        "roles": []
    }


def normalize_email(email: str) -> str:
    """Normalize email address."""
    return email.strip().lower()


def validate_email_format(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def generate_user_id(email: str, timestamp: int) -> str:
    """Generate user ID from email."""
    data = f"{email}{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def hash_password(password: str, salt: str) -> str:
    """Hash password with salt."""
    combined = f"{password}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()


def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    """Verify password against stored hash."""
    return hash_password(password, salt) == stored_hash


def add_role(user: dict, role: str) -> dict:
    """Add role to user."""
    if role in user.get("roles", []):
        return user
    new_roles = user.get("roles", []) + [role]
    return {**user, "roles": new_roles}


def remove_role(user: dict, role: str) -> dict:
    """Remove role from user."""
    new_roles = [r for r in user.get("roles", []) if r != role]
    return {**user, "roles": new_roles}


def has_role(user: dict, role: str) -> bool:
    """Check if user has role."""
    return role in user.get("roles", [])


def has_any_role(user: dict, roles: list) -> bool:
    """Check if user has any of the roles."""
    user_roles = set(user.get("roles", []))
    return bool(user_roles & set(roles))


def has_all_roles(user: dict, roles: list) -> bool:
    """Check if user has all roles."""
    user_roles = set(user.get("roles", []))
    return set(roles).issubset(user_roles)


def activate_user(user: dict) -> dict:
    """Activate user account."""
    return {**user, "active": True}


def deactivate_user(user: dict) -> dict:
    """Deactivate user account."""
    return {**user, "active": False}


def verify_user(user: dict) -> dict:
    """Mark user as verified."""
    return {**user, "verified": True}


def is_active(user: dict) -> bool:
    """Check if user is active."""
    return user.get("active", False)


def is_verified(user: dict) -> bool:
    """Check if user is verified."""
    return user.get("verified", False)


def update_email(user: dict, new_email: str) -> dict:
    """Update user email."""
    return {**user, "email": normalize_email(new_email), "verified": False}


def set_user_data(user: dict, key: str, value) -> dict:
    """Set user metadata."""
    metadata = user.get("metadata", {})
    new_metadata = {**metadata, key: value}
    return {**user, "metadata": new_metadata}


def get_user_data(user: dict, key: str, default=None):
    """Get user metadata."""
    return user.get("metadata", {}).get(key, default)


def get_display_name(user: dict) -> str:
    """Get user display name."""
    if user.get("display_name"):
        return user["display_name"]
    email = user.get("email", "")
    return email.split("@")[0] if email else "User"


def get_initials(name: str) -> str:
    """Get initials from name."""
    words = name.split()
    return "".join(w[0].upper() for w in words[:2])


def format_user_summary(user: dict) -> dict:
    """Create user summary."""
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "display_name": get_display_name(user),
        "active": is_active(user),
        "verified": is_verified(user),
        "roles": user.get("roles", [])
    }


def can_login(user: dict) -> dict:
    """Check if user can login."""
    if not is_active(user):
        return {"allowed": False, "reason": "Account deactivated"}
    return {"allowed": True, "reason": None}


def generate_avatar_url(email: str, size: int) -> str:
    """Generate Gravatar URL."""
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    return f"https://gravatar.com/avatar/{email_hash}?s={size}&d=identicon"


def anonymize_user(user: dict) -> dict:
    """Anonymize user data."""
    return {
        "user_id": user["user_id"],
        "email": f"deleted_{user['user_id']}@deleted.local",
        "active": False,
        "verified": False,
        "roles": [],
        "deleted": True
    }
