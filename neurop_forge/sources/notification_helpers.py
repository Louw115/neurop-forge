"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Notification Helpers - Pure functions for notification operations.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def create_notification(type_name: str, title: str, message: str, timestamp: int) -> dict:
    """Create notification object."""
    return {
        "id": generate_notification_id(type_name, timestamp),
        "type": type_name,
        "title": title,
        "message": message,
        "timestamp": timestamp,
        "read": False,
        "dismissed": False
    }


def generate_notification_id(type_name: str, timestamp: int) -> str:
    """Generate notification ID."""
    data = f"{type_name}{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def mark_as_read(notification: dict) -> dict:
    """Mark notification as read."""
    return {**notification, "read": True}


def mark_as_unread(notification: dict) -> dict:
    """Mark notification as unread."""
    return {**notification, "read": False}


def dismiss_notification(notification: dict) -> dict:
    """Dismiss notification."""
    return {**notification, "dismissed": True}


def is_read(notification: dict) -> bool:
    """Check if notification is read."""
    return notification.get("read", False)


def is_dismissed(notification: dict) -> bool:
    """Check if notification is dismissed."""
    return notification.get("dismissed", False)


def filter_unread(notifications: list) -> list:
    """Filter unread notifications."""
    return [n for n in notifications if not n.get("read", False)]


def filter_by_type(notifications: list, type_name: str) -> list:
    """Filter notifications by type."""
    return [n for n in notifications if n.get("type") == type_name]


def count_unread(notifications: list) -> int:
    """Count unread notifications."""
    return len(filter_unread(notifications))


def sort_by_timestamp(notifications: list, newest_first: bool) -> list:
    """Sort notifications by timestamp."""
    return sorted(notifications, key=lambda n: n.get("timestamp", 0), reverse=newest_first)


def get_recent(notifications: list, count: int) -> list:
    """Get most recent notifications."""
    sorted_notifs = sort_by_timestamp(notifications, True)
    return sorted_notifs[:count]


def mark_all_read(notifications: list) -> list:
    """Mark all notifications as read."""
    return [mark_as_read(n) for n in notifications]


def dismiss_all(notifications: list) -> list:
    """Dismiss all notifications."""
    return [dismiss_notification(n) for n in notifications]


def group_by_date(notifications: list, date_fn) -> dict:
    """Group notifications by date."""
    groups = {}
    for n in notifications:
        date_key = date_fn(n.get("timestamp", 0))
        if date_key not in groups:
            groups[date_key] = []
        groups[date_key].append(n)
    return groups


def get_notification_summary(notifications: list) -> dict:
    """Get notification summary."""
    unread = count_unread(notifications)
    by_type = {}
    for n in notifications:
        t = n.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    return {
        "total": len(notifications),
        "unread": unread,
        "by_type": by_type
    }


def should_show_badge(notifications: list, threshold: int) -> bool:
    """Check if notification badge should show."""
    return count_unread(notifications) >= threshold


def format_badge_count(count: int, max_display: int) -> str:
    """Format badge count for display."""
    if count <= 0:
        return ""
    if count > max_display:
        return f"{max_display}+"
    return str(count)


def create_push_payload(notification: dict) -> dict:
    """Create push notification payload."""
    return {
        "title": notification.get("title", ""),
        "body": notification.get("message", ""),
        "data": {
            "id": notification.get("id"),
            "type": notification.get("type")
        }
    }


def is_expired(notification: dict, current_time: int, ttl: int) -> bool:
    """Check if notification is expired."""
    created = notification.get("timestamp", 0)
    return current_time - created > ttl


def cleanup_expired(notifications: list, current_time: int, ttl: int) -> list:
    """Remove expired notifications."""
    return [n for n in notifications if not is_expired(n, current_time, ttl)]


def add_action(notification: dict, action_type: str, label: str, url: str) -> dict:
    """Add action to notification."""
    actions = notification.get("actions", [])
    actions.append({"type": action_type, "label": label, "url": url})
    return {**notification, "actions": actions}


def get_priority(notification: dict) -> int:
    """Get notification priority."""
    priorities = {"urgent": 3, "high": 2, "normal": 1, "low": 0}
    return priorities.get(notification.get("priority", "normal"), 1)


def sort_by_priority(notifications: list) -> list:
    """Sort notifications by priority."""
    return sorted(notifications, key=get_priority, reverse=True)
