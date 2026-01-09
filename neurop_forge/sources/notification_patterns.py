"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Notification Patterns - Pure functions for notification and messaging logic.
All functions are pure, deterministic, and atomic.
"""

def build_notification(notification_type: str, title: str, body: str, data: dict, recipient: str, channel: str) -> dict:
    """Build a notification object."""
    return {
        "type": notification_type,
        "title": title,
        "body": body,
        "data": data,
        "recipient": recipient,
        "channel": channel,
        "status": "pending",
        "created_at": "",
        "sent_at": None,
        "read_at": None
    }


def format_notification_title(template: str, variables: dict) -> str:
    """Format notification title with variables."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def format_notification_body(template: str, variables: dict) -> str:
    """Format notification body with variables."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def build_email_notification(to: str, subject: str, body_html: str, body_text: str, from_address: str, reply_to: str) -> dict:
    """Build an email notification."""
    return {
        "channel": "email",
        "to": to,
        "from": from_address,
        "reply_to": reply_to,
        "subject": subject,
        "body_html": body_html,
        "body_text": body_text
    }


def build_sms_notification(to: str, body: str, from_number: str) -> dict:
    """Build an SMS notification."""
    return {
        "channel": "sms",
        "to": to,
        "from": from_number,
        "body": body[:160]
    }


def build_push_notification(device_token: str, title: str, body: str, data: dict, badge: int, sound: str) -> dict:
    """Build a push notification."""
    return {
        "channel": "push",
        "device_token": device_token,
        "title": title,
        "body": body,
        "data": data,
        "badge": badge,
        "sound": sound
    }


def build_in_app_notification(user_id: str, title: str, body: str, action_url: str, icon: str) -> dict:
    """Build an in-app notification."""
    return {
        "channel": "in_app",
        "user_id": user_id,
        "title": title,
        "body": body,
        "action_url": action_url,
        "icon": icon,
        "read": False
    }


def should_send_notification(user_preferences: dict, channel: str, notification_type: str) -> bool:
    """Check if notification should be sent based on preferences."""
    channel_enabled = user_preferences.get(f"{channel}_enabled", True)
    type_enabled = user_preferences.get(f"{notification_type}_enabled", True)
    return channel_enabled and type_enabled


def is_quiet_hours(current_hour: int, quiet_start: int, quiet_end: int) -> bool:
    """Check if current time is during quiet hours."""
    if quiet_start <= quiet_end:
        return quiet_start <= current_hour < quiet_end
    return current_hour >= quiet_start or current_hour < quiet_end


def should_batch_notification(notification_type: str, batch_types: list) -> bool:
    """Check if notification should be batched."""
    return notification_type in batch_types


def calculate_send_delay(priority: str, is_quiet_hours: bool) -> int:
    """Calculate notification send delay in seconds."""
    if priority == "urgent":
        return 0
    if priority == "high":
        return 60 if is_quiet_hours else 0
    if priority == "normal":
        return 3600 if is_quiet_hours else 300
    return 3600


def format_digest_notification(notifications: list, digest_title: str) -> dict:
    """Format multiple notifications into a digest."""
    return {
        "channel": "email",
        "title": digest_title,
        "notification_count": len(notifications),
        "items": [{"title": n.get("title"), "body": n.get("body")[:100]} for n in notifications]
    }


def count_unread_notifications(notifications: list) -> int:
    """Count unread notifications."""
    return sum(1 for n in notifications if not n.get("read"))


def group_notifications_by_type(notifications: list) -> dict:
    """Group notifications by type."""
    result = {}
    for n in notifications:
        n_type = n.get("type", "other")
        if n_type not in result:
            result[n_type] = []
        result[n_type].append(n)
    return result


def mark_notification_read(notification: dict, timestamp: str) -> dict:
    """Mark a notification as read."""
    result = dict(notification)
    result["read"] = True
    result["read_at"] = timestamp
    return result


def mark_all_notifications_read(notifications: list, timestamp: str) -> list:
    """Mark all notifications as read."""
    return [mark_notification_read(n, timestamp) for n in notifications]


def filter_notifications_by_date(notifications: list, after_date: str) -> list:
    """Filter notifications after a date."""
    return [n for n in notifications if n.get("created_at", "") >= after_date]


def truncate_notification_body(body: str, max_length: int) -> str:
    """Truncate notification body for preview."""
    if len(body) <= max_length:
        return body
    return body[:max_length - 3] + "..."


def build_notification_action(action_id: str, label: str, url: str, is_destructive: bool) -> dict:
    """Build a notification action button."""
    return {
        "id": action_id,
        "label": label,
        "url": url,
        "is_destructive": is_destructive
    }


def calculate_notification_stats(notifications: list) -> dict:
    """Calculate notification statistics."""
    total = len(notifications)
    sent = sum(1 for n in notifications if n.get("sent_at"))
    read = sum(1 for n in notifications if n.get("read"))
    by_channel = {}
    by_type = {}
    for n in notifications:
        channel = n.get("channel", "unknown")
        n_type = n.get("type", "unknown")
        by_channel[channel] = by_channel.get(channel, 0) + 1
        by_type[n_type] = by_type.get(n_type, 0) + 1
    return {
        "total": total,
        "sent": sent,
        "read": read,
        "read_rate": (read / sent * 100) if sent > 0 else 0,
        "by_channel": by_channel,
        "by_type": by_type
    }


def calculate_engagement_rate(sent: int, opened: int, clicked: int) -> dict:
    """Calculate notification engagement rates."""
    return {
        "open_rate": (opened / sent * 100) if sent > 0 else 0,
        "click_rate": (clicked / sent * 100) if sent > 0 else 0,
        "click_to_open_rate": (clicked / opened * 100) if opened > 0 else 0
    }


def build_reminder_notification(reminder_id: str, message: str, remind_at: str, repeat: str) -> dict:
    """Build a reminder notification."""
    return {
        "type": "reminder",
        "reminder_id": reminder_id,
        "message": message,
        "remind_at": remind_at,
        "repeat": repeat,
        "dismissed": False
    }


def calculate_next_reminder_time(last_reminder: str, repeat: str) -> str:
    """Calculate next reminder time based on repeat setting."""
    from datetime import datetime, timedelta
    last = datetime.fromisoformat(last_reminder.replace('Z', '+00:00'))
    intervals = {
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
        "monthly": timedelta(days=30),
        "yearly": timedelta(days=365)
    }
    interval = intervals.get(repeat, timedelta(days=1))
    return (last + interval).isoformat()


def is_notification_expired(notification: dict, expiry_hours: int, current_timestamp: str) -> bool:
    """Check if a notification has expired."""
    from datetime import datetime, timedelta
    created = datetime.fromisoformat(notification.get("created_at", current_timestamp).replace('Z', '+00:00'))
    current = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
    return (current - created) > timedelta(hours=expiry_hours)


def filter_active_notifications(notifications: list, expiry_hours: int, current_timestamp: str) -> list:
    """Filter out expired notifications."""
    return [n for n in notifications if not is_notification_expired(n, expiry_hours, current_timestamp)]


def build_broadcast_notification(title: str, body: str, target_segment: str, channels: list) -> dict:
    """Build a broadcast notification to a segment."""
    return {
        "type": "broadcast",
        "title": title,
        "body": body,
        "target_segment": target_segment,
        "channels": channels,
        "status": "draft"
    }


def estimate_broadcast_recipients(segment_size: int, opt_in_rate: float) -> int:
    """Estimate number of broadcast recipients."""
    return int(segment_size * opt_in_rate)
