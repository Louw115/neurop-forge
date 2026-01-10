"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Session Utilities - Pure functions for session management.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def generate_session_id(seed: str, timestamp: int) -> str:
    """Generate session ID."""
    data = f"{seed}{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


def create_session(session_id: str, user_id: str, created_at: int, expires_at: int) -> dict:
    """Create session object."""
    return {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": created_at,
        "expires_at": expires_at,
        "data": {},
        "active": True
    }


def is_session_expired(session: dict, current_time: int) -> bool:
    """Check if session is expired."""
    return current_time >= session.get("expires_at", 0)


def is_session_valid(session: dict, current_time: int) -> bool:
    """Check if session is valid."""
    return session.get("active", False) and not is_session_expired(session, current_time)


def extend_session(session: dict, extension_seconds: int) -> dict:
    """Extend session expiration."""
    new_expires = session["expires_at"] + extension_seconds
    return {**session, "expires_at": new_expires}


def refresh_session(session: dict, current_time: int, ttl_seconds: int) -> dict:
    """Refresh session with new TTL."""
    return {**session, "expires_at": current_time + ttl_seconds}


def invalidate_session(session: dict) -> dict:
    """Invalidate session."""
    return {**session, "active": False}


def set_session_data(session: dict, key: str, value) -> dict:
    """Set session data."""
    new_data = {**session.get("data", {}), key: value}
    return {**session, "data": new_data}


def get_session_data(session: dict, key: str, default=None):
    """Get session data."""
    return session.get("data", {}).get(key, default)


def remove_session_data(session: dict, key: str) -> dict:
    """Remove session data."""
    new_data = {k: v for k, v in session.get("data", {}).items() if k != key}
    return {**session, "data": new_data}


def clear_session_data(session: dict) -> dict:
    """Clear all session data."""
    return {**session, "data": {}}


def get_session_age(session: dict, current_time: int) -> int:
    """Get session age in seconds."""
    return current_time - session.get("created_at", current_time)


def get_remaining_ttl(session: dict, current_time: int) -> int:
    """Get remaining TTL in seconds."""
    return max(0, session.get("expires_at", 0) - current_time)


def should_renew(session: dict, current_time: int, threshold_ratio: float) -> bool:
    """Check if session should be renewed."""
    created = session.get("created_at", 0)
    expires = session.get("expires_at", 0)
    total_ttl = expires - created
    remaining = get_remaining_ttl(session, current_time)
    return remaining < total_ttl * threshold_ratio


def create_session_token(session_id: str, secret: str) -> str:
    """Create signed session token."""
    data = f"{session_id}{secret}"
    signature = hashlib.sha256(data.encode()).hexdigest()[:16]
    return f"{session_id}.{signature}"


def verify_session_token(token: str, secret: str) -> dict:
    """Verify session token."""
    parts = token.split(".")
    if len(parts) != 2:
        return {"valid": False, "session_id": None}
    session_id, signature = parts
    expected = hashlib.sha256(f"{session_id}{secret}".encode()).hexdigest()[:16]
    return {"valid": signature == expected, "session_id": session_id if signature == expected else None}


def get_sessions_for_user(sessions: dict, user_id: str) -> list:
    """Get all sessions for user."""
    return [s for s in sessions.values() if s.get("user_id") == user_id]


def count_active_sessions(sessions: dict, current_time: int) -> int:
    """Count active sessions."""
    return sum(1 for s in sessions.values() if is_session_valid(s, current_time))


def cleanup_expired_sessions(sessions: dict, current_time: int) -> dict:
    """Remove expired sessions."""
    return {k: v for k, v in sessions.items() if not is_session_expired(v, current_time)}


def limit_user_sessions(sessions: dict, user_id: str, max_sessions: int) -> list:
    """Get sessions to remove for user limit."""
    user_sessions = get_sessions_for_user(sessions, user_id)
    if len(user_sessions) <= max_sessions:
        return []
    sorted_sessions = sorted(user_sessions, key=lambda s: s.get("created_at", 0))
    return [s["session_id"] for s in sorted_sessions[:-max_sessions]]


def create_session_summary(session: dict, current_time: int) -> dict:
    """Create session summary."""
    return {
        "session_id": session["session_id"],
        "user_id": session["user_id"],
        "active": is_session_valid(session, current_time),
        "age_seconds": get_session_age(session, current_time),
        "remaining_seconds": get_remaining_ttl(session, current_time)
    }
