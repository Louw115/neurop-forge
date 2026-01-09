"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
UI Patterns - Pure functions for UI/UX component logic.
All functions are pure, deterministic, and atomic.
"""

def format_display_name(first_name: str, last_name: str, format_type: str) -> str:
    """Format a display name."""
    if format_type == "first_last":
        return f"{first_name} {last_name}".strip()
    elif format_type == "last_first":
        return f"{last_name}, {first_name}".strip()
    elif format_type == "initials":
        f_init = first_name[0].upper() if first_name else ""
        l_init = last_name[0].upper() if last_name else ""
        return f"{f_init}{l_init}"
    elif format_type == "first_initial":
        return f"{first_name} {last_name[0]}." if last_name else first_name
    return f"{first_name} {last_name}".strip()


def truncate_text(text: str, max_length: int, suffix: str) -> str:
    """Truncate text with suffix if too long."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_file_size(bytes_count: int, precision: int) -> str:
    """Format file size in human-readable form."""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_count)
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    return f"{size:.{precision}f} {units[unit_index]}"


def format_relative_time(seconds_ago: int) -> str:
    """Format relative time (e.g., '5 minutes ago')."""
    if seconds_ago < 60:
        return "just now"
    elif seconds_ago < 3600:
        minutes = seconds_ago // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds_ago < 86400:
        hours = seconds_ago // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds_ago < 604800:
        days = seconds_ago // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds_ago < 2592000:
        weeks = seconds_ago // 604800
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds_ago < 31536000:
        months = seconds_ago // 2592000
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = seconds_ago // 31536000
        return f"{years} year{'s' if years != 1 else ''} ago"


def format_number_compact(number: float) -> str:
    """Format number in compact form (e.g., 1.2K, 3.4M)."""
    if abs(number) >= 1_000_000_000:
        return f"{number/1_000_000_000:.1f}B"
    elif abs(number) >= 1_000_000:
        return f"{number/1_000_000:.1f}M"
    elif abs(number) >= 1_000:
        return f"{number/1_000:.1f}K"
    return str(int(number))


def format_percentage(value: float, decimals: int) -> str:
    """Format a decimal as percentage."""
    return f"{value * 100:.{decimals}f}%"


def calculate_progress_percentage(current: int, total: int) -> float:
    """Calculate progress percentage."""
    if total <= 0:
        return 0.0
    return min(100.0, (current / total) * 100)


def format_progress_bar(progress: float, width: int, filled_char: str, empty_char: str) -> str:
    """Format a text-based progress bar."""
    filled = int(progress / 100 * width)
    empty = width - filled
    return filled_char * filled + empty_char * empty


def generate_avatar_initials(name: str) -> str:
    """Generate avatar initials from name."""
    words = name.strip().split()
    if len(words) >= 2:
        return (words[0][0] + words[-1][0]).upper()
    elif len(words) == 1 and len(words[0]) >= 2:
        return words[0][:2].upper()
    elif len(words) == 1:
        return words[0][0].upper()
    return "?"


def generate_avatar_color(name: str) -> str:
    """Generate a consistent avatar color from name."""
    import hashlib
    colors = [
        "#F44336", "#E91E63", "#9C27B0", "#673AB7", "#3F51B5",
        "#2196F3", "#03A9F4", "#00BCD4", "#009688", "#4CAF50",
        "#8BC34A", "#CDDC39", "#FFC107", "#FF9800", "#FF5722"
    ]
    hash_val = hashlib.sha256(name.encode()).digest()
    index = hash_val[0] % len(colors)
    return colors[index]


def build_breadcrumb(path: str, separator: str) -> list:
    """Build breadcrumb items from a path."""
    parts = path.strip("/").split("/")
    items = []
    current_path = ""
    for part in parts:
        if part:
            current_path += "/" + part
            items.append({"label": part.replace("-", " ").title(), "path": current_path})
    return items


def format_breadcrumb(items: list, separator: str) -> str:
    """Format breadcrumb items as string."""
    return separator.join(item["label"] for item in items)


def calculate_pagination_range(current_page: int, total_pages: int, visible_pages: int) -> list:
    """Calculate which page numbers to show."""
    if total_pages <= visible_pages:
        return list(range(1, total_pages + 1))
    half = visible_pages // 2
    start = max(1, current_page - half)
    end = min(total_pages, start + visible_pages - 1)
    if end - start + 1 < visible_pages:
        start = max(1, end - visible_pages + 1)
    return list(range(start, end + 1))


def build_pagination_info(current_page: int, per_page: int, total_items: int) -> dict:
    """Build pagination display info."""
    total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 0
    start_item = (current_page - 1) * per_page + 1
    end_item = min(current_page * per_page, total_items)
    return {
        "current_page": current_page,
        "total_pages": total_pages,
        "start_item": start_item,
        "end_item": end_item,
        "total_items": total_items,
        "has_prev": current_page > 1,
        "has_next": current_page < total_pages
    }


def format_pagination_text(info: dict) -> str:
    """Format pagination text."""
    return f"Showing {info['start_item']}-{info['end_item']} of {info['total_items']}"


def build_select_options(items: list, value_key: str, label_key: str) -> list:
    """Build select dropdown options."""
    return [{"value": item[value_key], "label": item[label_key]} for item in items]


def filter_options_by_search(options: list, search_term: str, label_key: str) -> list:
    """Filter select options by search term."""
    term = search_term.lower()
    return [opt for opt in options if term in opt[label_key].lower()]


def validate_form_field(value: str, required: bool, min_length: int, max_length: int, pattern: str) -> dict:
    """Validate a form field."""
    errors = []
    if required and not value:
        errors.append("This field is required")
    elif value:
        if min_length > 0 and len(value) < min_length:
            errors.append(f"Minimum {min_length} characters required")
        if max_length > 0 and len(value) > max_length:
            errors.append(f"Maximum {max_length} characters allowed")
        if pattern:
            import re
            if not re.match(pattern, value):
                errors.append("Invalid format")
    return {"valid": len(errors) == 0, "errors": errors}


def combine_form_validation(field_results: dict) -> dict:
    """Combine multiple field validations."""
    all_errors = {}
    is_valid = True
    for field, result in field_results.items():
        if not result["valid"]:
            is_valid = False
            all_errors[field] = result["errors"]
    return {"valid": is_valid, "errors": all_errors}


def build_table_column(key: str, label: str, sortable: bool, width: str) -> dict:
    """Build a table column definition."""
    return {
        "key": key,
        "label": label,
        "sortable": sortable,
        "width": width
    }


def sort_table_data(data: list, sort_key: str, sort_direction: str) -> list:
    """Sort table data by column."""
    reverse = sort_direction.lower() == "desc"
    return sorted(data, key=lambda x: x.get(sort_key, ""), reverse=reverse)


def filter_table_data(data: list, filters: dict) -> list:
    """Filter table data by column values."""
    result = data
    for key, value in filters.items():
        if value:
            result = [row for row in result if str(value).lower() in str(row.get(key, "")).lower()]
    return result


def build_toast_message(message: str, toast_type: str, duration_ms: int) -> dict:
    """Build a toast notification message."""
    return {
        "message": message,
        "type": toast_type,
        "duration": duration_ms,
        "dismissible": True
    }


def build_modal_config(title: str, size: str, closable: bool) -> dict:
    """Build a modal configuration."""
    return {
        "title": title,
        "size": size,
        "closable": closable,
        "backdrop": True
    }


def calculate_grid_columns(container_width: int, item_min_width: int, gap: int) -> int:
    """Calculate number of grid columns that fit."""
    if item_min_width <= 0:
        return 1
    available = container_width + gap
    return max(1, available // (item_min_width + gap))


def build_responsive_breakpoints() -> dict:
    """Build standard responsive breakpoints."""
    return {
        "xs": 0,
        "sm": 576,
        "md": 768,
        "lg": 992,
        "xl": 1200,
        "xxl": 1400
    }


def get_current_breakpoint(width: int, breakpoints: dict) -> str:
    """Get current breakpoint name for width."""
    current = "xs"
    for name, min_width in sorted(breakpoints.items(), key=lambda x: x[1]):
        if width >= min_width:
            current = name
    return current


def format_list_as_sentence(items: list, conjunction: str) -> str:
    """Format a list as a sentence (e.g., 'a, b, and c')."""
    if not items:
        return ""
    if len(items) == 1:
        return str(items[0])
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return ", ".join(str(i) for i in items[:-1]) + f", {conjunction} {items[-1]}"


def pluralize_word(word: str, count: int) -> str:
    """Pluralize a word based on count."""
    if count == 1:
        return word
    if word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    if word.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    return word + 's'


def format_count_label(count: int, singular: str, plural: str) -> str:
    """Format a count with appropriate label."""
    label = singular if count == 1 else plural
    return f"{count} {label}"
