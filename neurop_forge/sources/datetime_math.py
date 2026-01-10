"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Datetime Math - Pure functions for date/time calculations.
All functions are pure, deterministic, and atomic.
"""

def is_leap_year(year: int) -> bool:
    """Check if year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month(year: int, month: int) -> int:
    """Get number of days in a month."""
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2 and is_leap_year(year):
        return 29
    return days[month - 1] if 1 <= month <= 12 else 0


def days_in_year(year: int) -> int:
    """Get number of days in a year."""
    return 366 if is_leap_year(year) else 365


def day_of_year(year: int, month: int, day: int) -> int:
    """Get day of year (1-366)."""
    total = 0
    for m in range(1, month):
        total += days_in_month(year, m)
    return total + day


def day_of_week(year: int, month: int, day: int) -> int:
    """Get day of week (0=Monday, 6=Sunday) using Zeller's formula."""
    if month < 3:
        month += 12
        year -= 1
    k = year % 100
    j = year // 100
    h = (day + (13 * (month + 1)) // 5 + k + k // 4 + j // 4 - 2 * j) % 7
    return (h + 5) % 7


def week_of_year(year: int, month: int, day: int) -> int:
    """Get ISO week number."""
    doy = day_of_year(year, month, day)
    dow = day_of_week(year, month, day)
    week = (doy - dow + 10) // 7
    if week < 1:
        return 52
    if week > 52:
        return 1
    return week


def add_days(year: int, month: int, day: int, days_to_add: int) -> dict:
    """Add days to a date."""
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
    return {"year": year, "month": month, "day": total_days}


def subtract_days(year: int, month: int, day: int, days_to_sub: int) -> dict:
    """Subtract days from a date."""
    return add_days(year, month, day, -days_to_sub)


def add_months(year: int, month: int, day: int, months_to_add: int) -> dict:
    """Add months to a date."""
    total_months = month + months_to_add - 1
    new_year = year + total_months // 12
    new_month = (total_months % 12) + 1
    new_day = min(day, days_in_month(new_year, new_month))
    return {"year": new_year, "month": new_month, "day": new_day}


def add_years(year: int, month: int, day: int, years_to_add: int) -> dict:
    """Add years to a date."""
    new_year = year + years_to_add
    new_day = min(day, days_in_month(new_year, month))
    return {"year": new_year, "month": month, "day": new_day}


def days_between(y1: int, m1: int, d1: int, y2: int, m2: int, d2: int) -> int:
    """Calculate days between two dates."""
    def to_days(y, m, d):
        days = d
        for year in range(1, y):
            days += days_in_year(year)
        for month in range(1, m):
            days += days_in_month(y, month)
        return days
    return to_days(y2, m2, d2) - to_days(y1, m1, d1)


def months_between(y1: int, m1: int, d1: int, y2: int, m2: int, d2: int) -> int:
    """Calculate months between two dates."""
    months = (y2 - y1) * 12 + (m2 - m1)
    if d2 < d1:
        months -= 1
    return months


def years_between(y1: int, m1: int, d1: int, y2: int, m2: int, d2: int) -> int:
    """Calculate complete years between two dates."""
    years = y2 - y1
    if m2 < m1 or (m2 == m1 and d2 < d1):
        years -= 1
    return years


def is_weekend(year: int, month: int, day: int) -> bool:
    """Check if date is a weekend."""
    dow = day_of_week(year, month, day)
    return dow >= 5


def is_weekday(year: int, month: int, day: int) -> bool:
    """Check if date is a weekday."""
    return not is_weekend(year, month, day)


def next_weekday(year: int, month: int, day: int) -> dict:
    """Get next weekday."""
    result = add_days(year, month, day, 1)
    while is_weekend(result["year"], result["month"], result["day"]):
        result = add_days(result["year"], result["month"], result["day"], 1)
    return result


def prev_weekday(year: int, month: int, day: int) -> dict:
    """Get previous weekday."""
    result = subtract_days(year, month, day, 1)
    while is_weekend(result["year"], result["month"], result["day"]):
        result = subtract_days(result["year"], result["month"], result["day"], 1)
    return result


def start_of_week(year: int, month: int, day: int) -> dict:
    """Get start of week (Monday)."""
    dow = day_of_week(year, month, day)
    return subtract_days(year, month, day, dow)


def end_of_week(year: int, month: int, day: int) -> dict:
    """Get end of week (Sunday)."""
    dow = day_of_week(year, month, day)
    return add_days(year, month, day, 6 - dow)


def start_of_month(year: int, month: int) -> dict:
    """Get start of month."""
    return {"year": year, "month": month, "day": 1}


def end_of_month(year: int, month: int) -> dict:
    """Get end of month."""
    return {"year": year, "month": month, "day": days_in_month(year, month)}


def start_of_year(year: int) -> dict:
    """Get start of year."""
    return {"year": year, "month": 1, "day": 1}


def end_of_year(year: int) -> dict:
    """Get end of year."""
    return {"year": year, "month": 12, "day": 31}


def quarter_of_year(month: int) -> int:
    """Get quarter of year (1-4)."""
    return (month - 1) // 3 + 1


def start_of_quarter(year: int, quarter: int) -> dict:
    """Get start of quarter."""
    month = (quarter - 1) * 3 + 1
    return {"year": year, "month": month, "day": 1}


def end_of_quarter(year: int, quarter: int) -> dict:
    """Get end of quarter."""
    month = quarter * 3
    return {"year": year, "month": month, "day": days_in_month(year, month)}


def workdays_between(y1: int, m1: int, d1: int, y2: int, m2: int, d2: int) -> int:
    """Count workdays between two dates."""
    count = 0
    current = {"year": y1, "month": m1, "day": d1}
    end = {"year": y2, "month": m2, "day": d2}
    while days_between(current["year"], current["month"], current["day"],
                       end["year"], end["month"], end["day"]) > 0:
        if is_weekday(current["year"], current["month"], current["day"]):
            count += 1
        current = add_days(current["year"], current["month"], current["day"], 1)
    return count


def add_workdays(year: int, month: int, day: int, workdays: int) -> dict:
    """Add workdays to a date."""
    result = {"year": year, "month": month, "day": day}
    remaining = workdays
    while remaining > 0:
        result = add_days(result["year"], result["month"], result["day"], 1)
        if is_weekday(result["year"], result["month"], result["day"]):
            remaining -= 1
    return result


def compare_dates(y1: int, m1: int, d1: int, y2: int, m2: int, d2: int) -> int:
    """Compare two dates. Returns -1, 0, or 1."""
    if y1 != y2:
        return -1 if y1 < y2 else 1
    if m1 != m2:
        return -1 if m1 < m2 else 1
    if d1 != d2:
        return -1 if d1 < d2 else 1
    return 0


def is_same_day(y1: int, m1: int, d1: int, y2: int, m2: int, d2: int) -> bool:
    """Check if two dates are the same day."""
    return y1 == y2 and m1 == m2 and d1 == d2


def is_before(y1: int, m1: int, d1: int, y2: int, m2: int, d2: int) -> bool:
    """Check if first date is before second."""
    return compare_dates(y1, m1, d1, y2, m2, d2) < 0


def is_after(y1: int, m1: int, d1: int, y2: int, m2: int, d2: int) -> bool:
    """Check if first date is after second."""
    return compare_dates(y1, m1, d1, y2, m2, d2) > 0
