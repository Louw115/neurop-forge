"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Duration Utilities - Pure functions for duration operations.
All functions are pure, deterministic, and atomic.
"""


def seconds_to_minutes(seconds: int) -> float:
    """Convert seconds to minutes."""
    return seconds / 60


def seconds_to_hours(seconds: int) -> float:
    """Convert seconds to hours."""
    return seconds / 3600


def seconds_to_days(seconds: int) -> float:
    """Convert seconds to days."""
    return seconds / 86400


def minutes_to_seconds(minutes: int) -> int:
    """Convert minutes to seconds."""
    return minutes * 60


def hours_to_seconds(hours: int) -> int:
    """Convert hours to seconds."""
    return hours * 3600


def days_to_seconds(days: int) -> int:
    """Convert days to seconds."""
    return days * 86400


def ms_to_seconds(ms: int) -> float:
    """Convert milliseconds to seconds."""
    return ms / 1000


def seconds_to_ms(seconds: float) -> int:
    """Convert seconds to milliseconds."""
    return int(seconds * 1000)


def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds."""
    import re
    total = 0
    patterns = [
        (r'(\d+)\s*d(?:ays?)?', 86400),
        (r'(\d+)\s*h(?:ours?)?', 3600),
        (r'(\d+)\s*m(?:in(?:utes?)?)?', 60),
        (r'(\d+)\s*s(?:ec(?:onds?)?)?', 1)
    ]
    for pattern, multiplier in patterns:
        match = re.search(pattern, duration_str, re.IGNORECASE)
        if match:
            total += int(match.group(1)) * multiplier
    return total


def format_duration(seconds: int) -> str:
    """Format seconds to human readable."""
    if seconds < 0:
        return "-" + format_duration(-seconds)
    parts = []
    if seconds >= 86400:
        days = seconds // 86400
        parts.append(f"{days}d")
        seconds %= 86400
    if seconds >= 3600:
        hours = seconds // 3600
        parts.append(f"{hours}h")
        seconds %= 3600
    if seconds >= 60:
        minutes = seconds // 60
        parts.append(f"{minutes}m")
        seconds %= 60
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def format_duration_long(seconds: int) -> str:
    """Format duration with full words."""
    if seconds < 0:
        return "-" + format_duration_long(-seconds)
    parts = []
    if seconds >= 86400:
        days = seconds // 86400
        parts.append(f"{days} day{'s' if days != 1 else ''}")
        seconds %= 86400
    if seconds >= 3600:
        hours = seconds // 3600
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        seconds %= 3600
    if seconds >= 60:
        minutes = seconds // 60
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        seconds %= 60
    if seconds > 0:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    return ", ".join(parts) if parts else "0 seconds"


def format_duration_iso(seconds: int) -> str:
    """Format duration as ISO 8601."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"PT{hours}H{minutes}M{secs}S"


def parse_iso_duration(iso: str) -> int:
    """Parse ISO 8601 duration to seconds."""
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    secs = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + secs


def add_durations(d1: int, d2: int) -> int:
    """Add two durations in seconds."""
    return d1 + d2


def subtract_durations(d1: int, d2: int) -> int:
    """Subtract durations (d1 - d2)."""
    return d1 - d2


def multiply_duration(duration: int, factor: float) -> int:
    """Multiply duration by factor."""
    return int(duration * factor)


def divide_duration(duration: int, divisor: float) -> int:
    """Divide duration by divisor."""
    if divisor == 0:
        return 0
    return int(duration / divisor)


def compare_durations(d1: int, d2: int) -> int:
    """Compare durations (-1, 0, 1)."""
    if d1 < d2:
        return -1
    if d1 > d2:
        return 1
    return 0


def is_longer_than(d1: int, d2: int) -> bool:
    """Check if d1 is longer than d2."""
    return d1 > d2


def is_shorter_than(d1: int, d2: int) -> bool:
    """Check if d1 is shorter than d2."""
    return d1 < d2


def clamp_duration(duration: int, min_dur: int, max_dur: int) -> int:
    """Clamp duration to range."""
    return max(min_dur, min(max_dur, duration))


def get_percentage_elapsed(elapsed: int, total: int) -> float:
    """Get percentage of duration elapsed."""
    if total <= 0:
        return 0
    return min(100, (elapsed / total) * 100)


def get_remaining(elapsed: int, total: int) -> int:
    """Get remaining duration."""
    return max(0, total - elapsed)


def estimate_completion(elapsed: int, progress: float) -> int:
    """Estimate total duration from progress."""
    if progress <= 0:
        return 0
    return int(elapsed / progress)


def humanize_relative(seconds: int) -> str:
    """Humanize relative time."""
    if abs(seconds) < 60:
        return "just now"
    if seconds > 0:
        if seconds < 3600:
            return f"{seconds // 60} minutes ago"
        if seconds < 86400:
            return f"{seconds // 3600} hours ago"
        return f"{seconds // 86400} days ago"
    else:
        secs = abs(seconds)
        if secs < 3600:
            return f"in {secs // 60} minutes"
        if secs < 86400:
            return f"in {secs // 3600} hours"
        return f"in {secs // 86400} days"
