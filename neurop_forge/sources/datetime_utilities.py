"""
Date/Time Utilities - Pure functions for date and time calculations.

Note: These functions work with date components (year, month, day) rather than
datetime objects to maintain purity and determinism.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def days_in_month(year: int, month: int) -> int:
    """Return the number of days in a given month."""
    if month < 1 or month > 12:
        return 0
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2 and is_leap_year(year):
        return 29
    return days[month - 1]


def days_in_year(year: int) -> int:
    """Return the number of days in a given year."""
    return 366 if is_leap_year(year) else 365


def is_valid_date(year: int, month: int, day: int) -> bool:
    """Check if a date is valid."""
    if month < 1 or month > 12:
        return False
    if day < 1:
        return False
    return day <= days_in_month(year, month)


def day_of_week(year: int, month: int, day: int) -> int:
    """Calculate the day of week (0=Monday, 6=Sunday) using Zeller's formula."""
    if month < 3:
        month += 12
        year -= 1
    k = year % 100
    j = year // 100
    h = (day + (13 * (month + 1)) // 5 + k + k // 4 + j // 4 - 2 * j) % 7
    return (h + 5) % 7


def day_of_week_name(year: int, month: int, day: int) -> str:
    """Return the name of the day of week."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[day_of_week(year, month, day)]


def is_weekend(year: int, month: int, day: int) -> bool:
    """Check if a date falls on a weekend (Saturday or Sunday)."""
    dow = day_of_week(year, month, day)
    return dow >= 5


def is_weekday(year: int, month: int, day: int) -> bool:
    """Check if a date falls on a weekday (Monday-Friday)."""
    return not is_weekend(year, month, day)


def day_of_year(year: int, month: int, day: int) -> int:
    """Calculate the day of year (1-366)."""
    days = 0
    for m in range(1, month):
        days += days_in_month(year, m)
    return days + day


def week_of_year(year: int, month: int, day: int) -> int:
    """Calculate the week of year (1-53)."""
    doy = day_of_year(year, month, day)
    first_day_dow = day_of_week(year, 1, 1)
    return (doy + first_day_dow - 1) // 7 + 1


def add_days_to_date(year: int, month: int, day: int, days_to_add: int) -> tuple:
    """Add days to a date and return new (year, month, day)."""
    total_days = day + days_to_add
    
    while total_days > days_in_month(year, month):
        total_days -= days_in_month(year, month)
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    while total_days < 1:
        month -= 1
        if month < 1:
            month = 12
            year -= 1
        total_days += days_in_month(year, month)
    
    return (year, month, total_days)


def subtract_days_from_date(year: int, month: int, day: int, days_to_subtract: int) -> tuple:
    """Subtract days from a date and return new (year, month, day)."""
    return add_days_to_date(year, month, day, -days_to_subtract)


def days_between_dates(year1: int, month1: int, day1: int, year2: int, month2: int, day2: int) -> int:
    """Calculate the number of days between two dates."""
    def to_days(y, m, d):
        days = d
        for mm in range(1, m):
            days += days_in_month(y, mm)
        for yy in range(1, y):
            days += days_in_year(yy)
        return days
    
    return abs(to_days(year2, month2, day2) - to_days(year1, month1, day1))


def compare_dates(year1: int, month1: int, day1: int, year2: int, month2: int, day2: int) -> int:
    """Compare two dates. Returns -1 if first is earlier, 0 if equal, 1 if first is later."""
    if year1 != year2:
        return -1 if year1 < year2 else 1
    if month1 != month2:
        return -1 if month1 < month2 else 1
    if day1 != day2:
        return -1 if day1 < day2 else 1
    return 0


def is_date_before(year1: int, month1: int, day1: int, year2: int, month2: int, day2: int) -> bool:
    """Check if first date is before second date."""
    return compare_dates(year1, month1, day1, year2, month2, day2) < 0


def is_date_after(year1: int, month1: int, day1: int, year2: int, month2: int, day2: int) -> bool:
    """Check if first date is after second date."""
    return compare_dates(year1, month1, day1, year2, month2, day2) > 0


def format_date_iso(year: int, month: int, day: int) -> str:
    """Format a date as ISO 8601 (YYYY-MM-DD)."""
    return f"{year:04d}-{month:02d}-{day:02d}"


def format_date_us(year: int, month: int, day: int) -> str:
    """Format a date as US format (MM/DD/YYYY)."""
    return f"{month:02d}/{day:02d}/{year:04d}"


def format_date_eu(year: int, month: int, day: int) -> str:
    """Format a date as European format (DD/MM/YYYY)."""
    return f"{day:02d}/{month:02d}/{year:04d}"


def month_name(month: int) -> str:
    """Return the name of a month."""
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    if month < 1 or month > 12:
        return ""
    return months[month - 1]


def month_abbreviation(month: int) -> str:
    """Return the abbreviated name of a month."""
    return month_name(month)[:3]


def quarter_of_year(month: int) -> int:
    """Return the quarter of year (1-4) for a given month."""
    if month < 1 or month > 12:
        return 0
    return (month - 1) // 3 + 1


def age_in_years(birth_year: int, birth_month: int, birth_day: int, current_year: int, current_month: int, current_day: int) -> int:
    """Calculate age in years between birth date and current date."""
    age = current_year - birth_year
    if current_month < birth_month:
        age -= 1
    elif current_month == birth_month and current_day < birth_day:
        age -= 1
    return age
