"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Pagination Helpers - Pure functions for pagination calculations.
All functions are pure, deterministic, and atomic.
"""

import base64


def calculate_total_pages(total_items: int, page_size: int) -> int:
    """Calculate total number of pages."""
    if page_size <= 0:
        return 0
    return (total_items + page_size - 1) // page_size


def calculate_offset(page: int, page_size: int) -> int:
    """Calculate offset for given page."""
    return max(0, (page - 1) * page_size)


def calculate_page_from_offset(offset: int, page_size: int) -> int:
    """Calculate page number from offset."""
    if page_size <= 0:
        return 1
    return (offset // page_size) + 1


def get_page_items(items: list, page: int, page_size: int) -> list:
    """Get items for specific page."""
    offset = calculate_offset(page, page_size)
    return items[offset:offset + page_size]


def is_valid_page(page: int, total_pages: int) -> bool:
    """Check if page number is valid."""
    return 1 <= page <= total_pages


def get_page_info(page: int, page_size: int, total_items: int) -> dict:
    """Get comprehensive page info."""
    total_pages = calculate_total_pages(total_items, page_size)
    return {
        "current_page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
        "previous_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
        "first_item": calculate_offset(page, page_size) + 1,
        "last_item": min(page * page_size, total_items)
    }


def get_page_range(current: int, total: int, window: int) -> list:
    """Get range of page numbers around current."""
    if total <= 0:
        return []
    start = max(1, current - window)
    end = min(total, current + window)
    return list(range(start, end + 1))


def get_visible_pages(current: int, total: int, max_visible: int) -> list:
    """Get visible page numbers with ellipses."""
    if total <= max_visible:
        return list(range(1, total + 1))
    pages = []
    half = max_visible // 2
    if current <= half + 1:
        pages = list(range(1, max_visible - 1)) + ["...", total]
    elif current >= total - half:
        pages = [1, "..."] + list(range(total - max_visible + 3, total + 1))
    else:
        pages = [1, "..."] + list(range(current - half + 2, current + half - 1)) + ["...", total]
    return pages


def create_cursor(value: str) -> str:
    """Create cursor from value."""
    return base64.urlsafe_b64encode(value.encode()).decode()


def decode_cursor(cursor: str) -> str:
    """Decode cursor to value."""
    try:
        return base64.urlsafe_b64decode(cursor.encode()).decode()
    except:
        return ""


def get_cursor_page_info(items: list, cursor_field: str, limit: int) -> dict:
    """Get cursor pagination info."""
    if not items:
        return {"items": [], "has_more": False, "end_cursor": None}
    has_more = len(items) > limit
    page_items = items[:limit]
    end_cursor = None
    if page_items:
        last_item = page_items[-1]
        if isinstance(last_item, dict):
            end_cursor = create_cursor(str(last_item.get(cursor_field, "")))
    return {"items": page_items, "has_more": has_more, "end_cursor": end_cursor}


def parse_page_params(page: int, per_page: int, max_per_page: int) -> dict:
    """Parse and validate page parameters."""
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    return {"page": page, "per_page": per_page}


def get_slice_indices(page: int, per_page: int) -> dict:
    """Get slice start and end indices."""
    start = (page - 1) * per_page
    return {"start": start, "end": start + per_page}


def format_page_info_text(current: int, total: int, total_items: int) -> str:
    """Format page info as text."""
    return f"Page {current} of {total} ({total_items} items)"


def format_item_range_text(start: int, end: int, total: int) -> str:
    """Format item range as text."""
    return f"Showing {start}-{end} of {total}"


def calculate_skip_take(page: int, per_page: int) -> dict:
    """Calculate skip/take for some ORMs."""
    return {"skip": (page - 1) * per_page, "take": per_page}


def merge_pages(pages: list) -> list:
    """Merge multiple pages into single list."""
    result = []
    for page in pages:
        result.extend(page)
    return result


def split_into_pages(items: list, page_size: int) -> list:
    """Split list into pages."""
    return [items[i:i + page_size] for i in range(0, len(items), page_size)]


def get_keyset_page_info(items: list, key_field: str, limit: int, sort_order: str) -> dict:
    """Get keyset pagination info."""
    if not items:
        return {"items": [], "has_more": False, "last_key": None}
    has_more = len(items) > limit
    page_items = items[:limit]
    last_key = None
    if page_items:
        last = page_items[-1]
        if isinstance(last, dict):
            last_key = last.get(key_field)
    return {"items": page_items, "has_more": has_more, "last_key": last_key}
