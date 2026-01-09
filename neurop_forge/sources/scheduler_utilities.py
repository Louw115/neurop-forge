"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Scheduler Utilities - Pure functions for scheduling and time-based logic.
All functions are pure, deterministic, and atomic.
"""

def parse_cron_expression(expression: str) -> dict:
    """Parse a cron expression."""
    parts = expression.split()
    if len(parts) != 5:
        return {"valid": False}
    return {
        "valid": True,
        "minute": parts[0],
        "hour": parts[1],
        "day_of_month": parts[2],
        "month": parts[3],
        "day_of_week": parts[4]
    }


def matches_cron_field(value: int, field: str) -> bool:
    """Check if value matches cron field pattern."""
    if field == "*":
        return True
    if field.isdigit():
        return value == int(field)
    if "," in field:
        return value in [int(v) for v in field.split(",")]
    if "-" in field:
        start, end = field.split("-")
        return int(start) <= value <= int(end)
    if "/" in field:
        base, step = field.split("/")
        if base == "*":
            return value % int(step) == 0
    return False


def matches_cron(cron: dict, minute: int, hour: int, day: int, month: int, weekday: int) -> bool:
    """Check if time matches cron expression."""
    return (matches_cron_field(minute, cron["minute"]) and
            matches_cron_field(hour, cron["hour"]) and
            matches_cron_field(day, cron["day_of_month"]) and
            matches_cron_field(month, cron["month"]) and
            matches_cron_field(weekday, cron["day_of_week"]))


def build_schedule(schedule_id: str, cron_expression: str, task_name: str, enabled: bool) -> dict:
    """Build a schedule definition."""
    cron = parse_cron_expression(cron_expression)
    return {
        "id": schedule_id,
        "cron": cron_expression,
        "parsed_cron": cron,
        "task": task_name,
        "enabled": enabled,
        "last_run": None,
        "next_run": None
    }


def calculate_interval_schedule(interval_seconds: int, last_run_timestamp: int) -> int:
    """Calculate next run timestamp for interval schedule."""
    return last_run_timestamp + interval_seconds


def is_schedule_due(schedule: dict, current_minute: int, current_hour: int, current_day: int, current_month: int, current_weekday: int) -> bool:
    """Check if schedule is due to run."""
    if not schedule.get("enabled", True):
        return False
    cron = schedule.get("parsed_cron", {})
    if not cron.get("valid"):
        return False
    return matches_cron(cron, current_minute, current_hour, current_day, current_month, current_weekday)


def build_recurring_schedule(recurrence_type: str, interval: int, start_time: str, end_time: str, days: list) -> dict:
    """Build a human-friendly recurring schedule."""
    return {
        "type": recurrence_type,
        "interval": interval,
        "start_time": start_time,
        "end_time": end_time,
        "days": days
    }


def is_within_schedule_window(current_time: str, start_time: str, end_time: str) -> bool:
    """Check if current time is within schedule window."""
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    return current_time >= start_time or current_time <= end_time


def is_scheduled_day(current_weekday: int, scheduled_days: list) -> bool:
    """Check if current weekday is a scheduled day."""
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    current_day_name = day_names[current_weekday]
    return current_day_name in [d.lower() for d in scheduled_days]


def calculate_next_occurrence(recurrence: dict, current_weekday: int, current_time: str) -> dict:
    """Calculate next occurrence of recurring schedule."""
    days = recurrence.get("days", [])
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for offset in range(7):
        check_day = (current_weekday + offset) % 7
        if day_names[check_day] in [d.lower() for d in days]:
            return {
                "day_offset": offset,
                "day_name": day_names[check_day],
                "time": recurrence.get("start_time")
            }
    return {"day_offset": 0, "day_name": day_names[current_weekday], "time": recurrence.get("start_time")}


def build_one_time_schedule(schedule_id: str, run_at: str, task_name: str) -> dict:
    """Build a one-time schedule."""
    return {
        "id": schedule_id,
        "type": "one_time",
        "run_at": run_at,
        "task": task_name,
        "executed": False
    }


def is_one_time_due(schedule: dict, current_timestamp: str) -> bool:
    """Check if one-time schedule is due."""
    if schedule.get("executed"):
        return False
    return current_timestamp >= schedule.get("run_at", "")


def mark_schedule_executed(schedule: dict, timestamp: str) -> dict:
    """Mark schedule as executed."""
    result = dict(schedule)
    result["last_run"] = timestamp
    if schedule.get("type") == "one_time":
        result["executed"] = True
    return result


def calculate_schedule_delay(target_timestamp: str, current_timestamp: str) -> int:
    """Calculate delay in seconds until target time."""
    from datetime import datetime
    target = datetime.fromisoformat(target_timestamp.replace('Z', '+00:00'))
    current = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
    diff = (target - current).total_seconds()
    return max(0, int(diff))


def format_schedule_description(schedule: dict) -> str:
    """Format schedule as human-readable description."""
    if schedule.get("type") == "one_time":
        return f"Once at {schedule.get('run_at')}"
    cron = schedule.get("cron", "")
    return f"Cron: {cron}" if cron else "Unknown schedule"


def build_maintenance_window(start_time: str, duration_minutes: int, days: list) -> dict:
    """Build a maintenance window definition."""
    return {
        "start_time": start_time,
        "duration_minutes": duration_minutes,
        "days": days
    }


def is_in_maintenance_window(window: dict, current_weekday: int, current_hour: int, current_minute: int) -> bool:
    """Check if currently in maintenance window."""
    if not is_scheduled_day(current_weekday, window.get("days", [])):
        return False
    start_parts = window.get("start_time", "00:00").split(":")
    start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
    current_minutes = current_hour * 60 + current_minute
    end_minutes = start_minutes + window.get("duration_minutes", 0)
    return start_minutes <= current_minutes < end_minutes


def build_blackout_period(start_date: str, end_date: str, reason: str) -> dict:
    """Build a blackout period (no schedules run)."""
    return {
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason
    }


def is_in_blackout(blackouts: list, current_date: str) -> bool:
    """Check if current date is in a blackout period."""
    for blackout in blackouts:
        if blackout["start_date"] <= current_date <= blackout["end_date"]:
            return True
    return False


def calculate_rate_limit_window(requests: int, window_seconds: int, current_count: int) -> dict:
    """Calculate rate limit status."""
    remaining = max(0, requests - current_count)
    return {
        "limit": requests,
        "remaining": remaining,
        "reset_after_seconds": window_seconds,
        "exceeded": remaining == 0
    }


def should_retry_with_backoff(attempt: int, max_attempts: int, base_delay: int, max_delay: int) -> dict:
    """Calculate retry with exponential backoff."""
    if attempt >= max_attempts:
        return {"should_retry": False, "delay": 0}
    delay = min(base_delay * (2 ** attempt), max_delay)
    return {"should_retry": True, "delay": delay}


def add_jitter(delay: int, jitter_percent: float, seed: int) -> int:
    """Add jitter to delay to prevent thundering herd."""
    import hashlib
    hash_val = hashlib.sha256(str(seed).encode()).digest()
    jitter_factor = (hash_val[0] / 255.0 - 0.5) * 2 * (jitter_percent / 100)
    return int(delay * (1 + jitter_factor))
