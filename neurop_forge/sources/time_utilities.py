"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Time Utilities - Pure functions for time calculations.
All functions are pure, deterministic, and atomic.
"""

def create_time(hours: int, minutes: int, seconds: int) -> dict:
    """Create a time object."""
    return {"hours": hours, "minutes": minutes, "seconds": seconds}


def to_seconds(hours: int, minutes: int, seconds: int) -> int:
    """Convert time to total seconds."""
    return hours * 3600 + minutes * 60 + seconds


def from_seconds(total_seconds: int) -> dict:
    """Convert total seconds to time."""
    hours = total_seconds // 3600
    remaining = total_seconds % 3600
    minutes = remaining // 60
    seconds = remaining % 60
    return {"hours": hours, "minutes": minutes, "seconds": seconds}


def add_seconds(time: dict, secs: int) -> dict:
    """Add seconds to time."""
    total = to_seconds(time["hours"], time["minutes"], time["seconds"]) + secs
    return from_seconds(total % 86400)


def subtract_seconds(time: dict, secs: int) -> dict:
    """Subtract seconds from time."""
    total = to_seconds(time["hours"], time["minutes"], time["seconds"]) - secs
    if total < 0:
        total += 86400
    return from_seconds(total)


def add_minutes(time: dict, mins: int) -> dict:
    """Add minutes to time."""
    return add_seconds(time, mins * 60)


def add_hours(time: dict, hrs: int) -> dict:
    """Add hours to time."""
    return add_seconds(time, hrs * 3600)


def seconds_between(t1: dict, t2: dict) -> int:
    """Calculate seconds between two times."""
    s1 = to_seconds(t1["hours"], t1["minutes"], t1["seconds"])
    s2 = to_seconds(t2["hours"], t2["minutes"], t2["seconds"])
    return s2 - s1


def is_before_time(t1: dict, t2: dict) -> bool:
    """Check if t1 is before t2."""
    return seconds_between(t1, t2) > 0


def is_after_time(t1: dict, t2: dict) -> bool:
    """Check if t1 is after t2."""
    return seconds_between(t1, t2) < 0


def is_same_time(t1: dict, t2: dict) -> bool:
    """Check if times are equal."""
    return (t1["hours"] == t2["hours"] and 
            t1["minutes"] == t2["minutes"] and 
            t1["seconds"] == t2["seconds"])


def is_midnight(time: dict) -> bool:
    """Check if time is midnight."""
    return time["hours"] == 0 and time["minutes"] == 0 and time["seconds"] == 0


def is_noon(time: dict) -> bool:
    """Check if time is noon."""
    return time["hours"] == 12 and time["minutes"] == 0 and time["seconds"] == 0


def is_am(time: dict) -> bool:
    """Check if time is AM."""
    return time["hours"] < 12


def is_pm(time: dict) -> bool:
    """Check if time is PM."""
    return time["hours"] >= 12


def to_12_hour(time: dict) -> dict:
    """Convert to 12-hour format."""
    hour = time["hours"]
    period = "AM" if hour < 12 else "PM"
    if hour == 0:
        hour = 12
    elif hour > 12:
        hour -= 12
    return {"hours": hour, "minutes": time["minutes"], "seconds": time["seconds"], "period": period}


def to_24_hour(time12: dict) -> dict:
    """Convert from 12-hour to 24-hour format."""
    hour = time12["hours"]
    if time12["period"] == "AM":
        if hour == 12:
            hour = 0
    else:
        if hour != 12:
            hour += 12
    return {"hours": hour, "minutes": time12["minutes"], "seconds": time12["seconds"]}


def format_time_hms(time: dict) -> str:
    """Format time as HH:MM:SS."""
    return f"{time['hours']:02d}:{time['minutes']:02d}:{time['seconds']:02d}"


def format_time_hm(time: dict) -> str:
    """Format time as HH:MM."""
    return f"{time['hours']:02d}:{time['minutes']:02d}"


def format_duration(seconds: int) -> str:
    """Format duration in human readable form."""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s" if secs else f"{mins}m"
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    return f"{hrs}h {mins}m" if mins else f"{hrs}h"


def parse_time(time_str: str) -> dict:
    """Parse time string (HH:MM:SS or HH:MM)."""
    parts = time_str.split(":")
    hours = int(parts[0]) if parts else 0
    minutes = int(parts[1]) if len(parts) > 1 else 0
    seconds = int(parts[2]) if len(parts) > 2 else 0
    return {"hours": hours, "minutes": minutes, "seconds": seconds}


def round_to_minute(time: dict) -> dict:
    """Round time to nearest minute."""
    if time["seconds"] >= 30:
        return add_seconds(time, 60 - time["seconds"])
    return {"hours": time["hours"], "minutes": time["minutes"], "seconds": 0}


def round_to_hour(time: dict) -> dict:
    """Round time to nearest hour."""
    total_minutes = time["hours"] * 60 + time["minutes"]
    if time["minutes"] >= 30:
        total_minutes = (time["hours"] + 1) * 60
    return {"hours": (total_minutes // 60) % 24, "minutes": 0, "seconds": 0}


def start_of_hour(time: dict) -> dict:
    """Get start of hour."""
    return {"hours": time["hours"], "minutes": 0, "seconds": 0}


def end_of_hour(time: dict) -> dict:
    """Get end of hour."""
    return {"hours": time["hours"], "minutes": 59, "seconds": 59}


def time_in_range(time: dict, start: dict, end: dict) -> bool:
    """Check if time is in range (inclusive)."""
    t = to_seconds(time["hours"], time["minutes"], time["seconds"])
    s = to_seconds(start["hours"], start["minutes"], start["seconds"])
    e = to_seconds(end["hours"], end["minutes"], end["seconds"])
    if s <= e:
        return s <= t <= e
    return t >= s or t <= e


def overlap_duration(start1: dict, end1: dict, start2: dict, end2: dict) -> int:
    """Calculate overlap duration in seconds."""
    s1 = to_seconds(start1["hours"], start1["minutes"], start1["seconds"])
    e1 = to_seconds(end1["hours"], end1["minutes"], end1["seconds"])
    s2 = to_seconds(start2["hours"], start2["minutes"], start2["seconds"])
    e2 = to_seconds(end2["hours"], end2["minutes"], end2["seconds"])
    overlap_start = max(s1, s2)
    overlap_end = min(e1, e2)
    return max(0, overlap_end - overlap_start)


def milliseconds_to_time(ms: int) -> dict:
    """Convert milliseconds to time."""
    return from_seconds(ms // 1000)


def time_to_milliseconds(time: dict) -> int:
    """Convert time to milliseconds."""
    return to_seconds(time["hours"], time["minutes"], time["seconds"]) * 1000


def timezone_offset_hours(offset_minutes: int) -> str:
    """Format timezone offset."""
    sign = "+" if offset_minutes >= 0 else "-"
    hours = abs(offset_minutes) // 60
    mins = abs(offset_minutes) % 60
    return f"{sign}{hours:02d}:{mins:02d}"
