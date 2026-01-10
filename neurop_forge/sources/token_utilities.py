"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Token Utilities - Pure functions for token operations.
All functions are pure, deterministic, and atomic.
"""

import hashlib
import base64


def generate_token(seed: str, length: int) -> str:
    """Generate token of specified length."""
    h = hashlib.sha256(seed.encode()).hexdigest()
    return h[:length]


def generate_secure_token(seed: str, salt: str) -> str:
    """Generate secure token with salt."""
    combined = f"{seed}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()


def generate_refresh_token(user_id: str, timestamp: int, secret: str) -> str:
    """Generate refresh token."""
    data = f"{user_id}{timestamp}{secret}"
    return hashlib.sha256(data.encode()).hexdigest()


def hash_token(token: str) -> str:
    """Hash token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, stored_hash: str) -> bool:
    """Verify token against stored hash."""
    return hash_token(token) == stored_hash


def create_token_payload(user_id: str, issued_at: int, expires_at: int, claims: dict) -> dict:
    """Create token payload."""
    return {
        "sub": user_id,
        "iat": issued_at,
        "exp": expires_at,
        **claims
    }


def is_token_expired(payload: dict, current_time: int) -> bool:
    """Check if token is expired."""
    return current_time >= payload.get("exp", 0)


def is_token_valid_time(payload: dict, current_time: int) -> bool:
    """Check if token is within valid time window."""
    iat = payload.get("iat", 0)
    exp = payload.get("exp", 0)
    return iat <= current_time < exp


def get_token_subject(payload: dict) -> str:
    """Get subject from token payload."""
    return payload.get("sub", "")


def get_token_claim(payload: dict, claim: str, default=None):
    """Get claim from token payload."""
    return payload.get(claim, default)


def encode_token_base64(payload: str) -> str:
    """Encode payload as base64."""
    return base64.urlsafe_b64encode(payload.encode()).decode()


def decode_token_base64(encoded: str) -> str:
    """Decode base64 payload."""
    try:
        return base64.urlsafe_b64decode(encoded.encode()).decode()
    except:
        return ""


def split_bearer_token(header: str) -> str:
    """Extract token from Bearer header."""
    if header.startswith("Bearer "):
        return header[7:]
    return ""


def format_bearer_header(token: str) -> str:
    """Format token as Bearer header."""
    return f"Bearer {token}"


def create_api_key(prefix: str, seed: str) -> str:
    """Create API key with prefix."""
    key = hashlib.sha256(seed.encode()).hexdigest()[:32]
    return f"{prefix}_{key}"


def parse_api_key(api_key: str) -> dict:
    """Parse API key into prefix and key."""
    if "_" not in api_key:
        return {"valid": False, "prefix": "", "key": ""}
    prefix, key = api_key.split("_", 1)
    return {"valid": True, "prefix": prefix, "key": key}


def is_valid_api_key_format(api_key: str, expected_prefix: str) -> bool:
    """Validate API key format."""
    parsed = parse_api_key(api_key)
    return parsed["valid"] and parsed["prefix"] == expected_prefix


def rotate_token(old_token: str, salt: str) -> str:
    """Rotate token generating new one."""
    return hashlib.sha256(f"{old_token}{salt}".encode()).hexdigest()


def create_one_time_token(seed: str, purpose: str, timestamp: int) -> str:
    """Create one-time use token."""
    data = f"{seed}{purpose}{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:24]


def validate_token_purpose(token_data: dict, expected_purpose: str) -> bool:
    """Validate token purpose matches."""
    return token_data.get("purpose") == expected_purpose


def create_password_reset_token(user_id: str, timestamp: int, secret: str) -> str:
    """Create password reset token."""
    return create_one_time_token(f"{user_id}{secret}", "password_reset", timestamp)


def create_email_verification_token(user_id: str, email: str, secret: str) -> str:
    """Create email verification token."""
    data = f"{user_id}{email}{secret}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


def mask_token(token: str, visible_chars: int) -> str:
    """Mask token showing only last N characters."""
    if len(token) <= visible_chars:
        return "*" * len(token)
    return "*" * (len(token) - visible_chars) + token[-visible_chars:]


def get_token_fingerprint(token: str) -> str:
    """Get short fingerprint of token."""
    return hashlib.sha256(token.encode()).hexdigest()[:8]
