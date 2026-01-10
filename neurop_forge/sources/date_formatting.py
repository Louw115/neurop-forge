"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Date Formatting - Pure functions for date formatting.
All functions are pure, deterministic, and atomic.
"""

def format_date_iso(year: int, month: int, day: int) -> str:
    """Format date as ISO 8601."""
    return f"{year:04d}-{month:02d}-{day:02d}"


def format_date_us(month: int, day: int, year: int) -> str:
    """Format date as MM/DD/YYYY."""
    return f"{month:02d}/{day:02d}/{year:04d}"


def format_date_eu(day: int, month: int, year: int) -> str:
    """Format date as DD/MM/YYYY."""
    return f"{day:02d}/{month:02d}/{year:04d}"


def format_date_long(year: int, month: int, day: int) -> str:
    """Format date in long form."""
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    return f"{months[month-1]} {day}, {year}"


def format_date_short(year: int, month: int, day: int) -> str:
    """Format date in short form."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[month-1]} {day}, {year}"


def format_weekday(day_of_week: int) -> str:
    """Format day of week."""
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return days[day_of_week % 7]


def format_weekday_short(day_of_week: int) -> str:
    """Format day of week short form."""
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    return days[day_of_week % 7]


def format_month_name(month: int) -> str:
    """Get month name."""
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    return months[(month - 1) % 12]


def format_month_short(month: int) -> str:
    """Get month short name."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return months[(month - 1) % 12]


def format_ordinal_day(day: int) -> str:
    """Format day with ordinal suffix."""
    if 11 <= day <= 13:
        suffix = "th"
    elif day % 10 == 1:
        suffix = "st"
    elif day % 10 == 2:
        suffix = "nd"
    elif day % 10 == 3:
        suffix = "rd"
    else:
        suffix = "th"
    return f"{day}{suffix}"


def format_time_24h(hours: int, minutes: int) -> str:
    """Format time in 24-hour format."""
    return f"{hours:02d}:{minutes:02d}"


def format_time_12h(hours: int, minutes: int) -> str:
    """Format time in 12-hour format."""
    period = "AM" if hours < 12 else "PM"
    display_hours = hours % 12
    if display_hours == 0:
        display_hours = 12
    return f"{display_hours}:{minutes:02d} {period}"


def format_time_with_seconds(hours: int, minutes: int, seconds: int) -> str:
    """Format time with seconds."""
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_datetime_iso(year: int, month: int, day: int, hours: int, minutes: int, seconds: int) -> str:
    """Format datetime as ISO 8601."""
    return f"{year:04d}-{month:02d}-{day:02d}T{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_datetime_rfc2822(year: int, month: int, day: int, hours: int, minutes: int, dow: int) -> str:
    """Format datetime in RFC 2822 style."""
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{days[dow]}, {day:02d} {months[month-1]} {year} {hours:02d}:{minutes:02d}"


def format_relative_date(days_ago: int) -> str:
    """Format relative date."""
    if days_ago == 0:
        return "today"
    elif days_ago == 1:
        return "yesterday"
    elif days_ago == -1:
        return "tomorrow"
    elif days_ago > 0:
        if days_ago < 7:
            return f"{days_ago} days ago"
        elif days_ago < 30:
            weeks = days_ago // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif days_ago < 365:
            months = days_ago // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = days_ago // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
    else:
        future = abs(days_ago)
        if future < 7:
            return f"in {future} days"
        elif future < 30:
            weeks = future // 7
            return f"in {weeks} week{'s' if weeks > 1 else ''}"
        else:
            months = future // 30
            return f"in {months} month{'s' if months > 1 else ''}"


def format_duration_short(seconds: int) -> str:
    """Format duration in short form."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s" if secs else f"{mins}m"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m" if mins else f"{hours}h"


def format_duration_long(seconds: int) -> str:
    """Format duration in long form."""
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    elif seconds < 3600:
        mins = seconds // 60
        return f"{mins} minute{'s' if mins != 1 else ''}"
    else:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"


def parse_month_name(name: str) -> int:
    """Parse month name to number."""
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7,
        "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    return months.get(name.lower(), 0)


def format_quarter(month: int) -> str:
    """Get quarter name from month."""
    if month <= 3:
        return "Q1"
    elif month <= 6:
        return "Q2"
    elif month <= 9:
        return "Q3"
    return "Q4"


def format_fiscal_year(year: int, month: int, fiscal_start: int) -> str:
    """Format fiscal year."""
    if month >= fiscal_start:
        return f"FY{year + 1}"
    return f"FY{year}"
