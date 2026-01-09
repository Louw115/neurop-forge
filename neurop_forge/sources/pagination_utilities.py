"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Pagination Utilities - Pure functions for pagination calculations.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def calculate_offset(page: int, page_size: int) -> int:
    """Calculate the offset for a given page number."""
    return max(0, (page - 1) * page_size)


def calculate_page_from_offset(offset: int, page_size: int) -> int:
    """Calculate the page number from an offset."""
    if page_size <= 0:
        return 1
    return (offset // page_size) + 1


def calculate_total_pages(total_items: int, page_size: int) -> int:
    """Calculate the total number of pages."""
    if page_size <= 0:
        return 0
    return (total_items + page_size - 1) // page_size


def has_next_page(current_page: int, total_pages: int) -> bool:
    """Check if there is a next page."""
    return current_page < total_pages


def has_previous_page(current_page: int) -> bool:
    """Check if there is a previous page."""
    return current_page > 1


def get_next_page(current_page: int, total_pages: int) -> int:
    """Get the next page number (or current if at end)."""
    return min(current_page + 1, total_pages)


def get_previous_page(current_page: int) -> int:
    """Get the previous page number (or 1 if at start)."""
    return max(current_page - 1, 1)


def get_first_page() -> int:
    """Get the first page number."""
    return 1


def get_last_page(total_pages: int) -> int:
    """Get the last page number."""
    return max(1, total_pages)


def is_valid_page(page: int, total_pages: int) -> bool:
    """Check if a page number is valid."""
    return 1 <= page <= total_pages


def clamp_page(page: int, total_pages: int) -> int:
    """Clamp a page number to valid range."""
    return max(1, min(page, max(1, total_pages)))


def get_start_index(page: int, page_size: int) -> int:
    """Get the start index (1-based) for items on a page."""
    return calculate_offset(page, page_size) + 1


def get_end_index(page: int, page_size: int, total_items: int) -> int:
    """Get the end index (1-based) for items on a page."""
    return min(page * page_size, total_items)


def get_items_on_page(page: int, page_size: int, total_items: int) -> int:
    """Calculate how many items are on a specific page."""
    if page < 1:
        return 0
    total_pages = calculate_total_pages(total_items, page_size)
    if page > total_pages:
        return 0
    if page == total_pages:
        remaining = total_items % page_size
        return remaining if remaining != 0 else page_size
    return page_size


def slice_for_page(items: list, page: int, page_size: int) -> list:
    """Get the slice of items for a specific page."""
    offset = calculate_offset(page, page_size)
    return items[offset:offset + page_size]


def get_page_range(current_page: int, total_pages: int, visible_pages: int) -> list:
    """Get a range of page numbers to display."""
    if total_pages <= visible_pages:
        return list(range(1, total_pages + 1))
    half = visible_pages // 2
    start = max(1, current_page - half)
    end = min(total_pages, start + visible_pages - 1)
    if end - start + 1 < visible_pages:
        start = max(1, end - visible_pages + 1)
    return list(range(start, end + 1))


def get_page_range_with_ellipsis(current_page: int, total_pages: int, visible_pages: int) -> list:
    """Get page range with ellipsis markers for gaps."""
    if total_pages <= visible_pages + 2:
        return list(range(1, total_pages + 1))
    result = []
    half = visible_pages // 2
    start = max(2, current_page - half)
    end = min(total_pages - 1, current_page + half)
    result.append(1)
    if start > 2:
        result.append('...')
    result.extend(range(start, end + 1))
    if end < total_pages - 1:
        result.append('...')
    result.append(total_pages)
    return result


def encode_cursor(offset: int, sort_key: str) -> str:
    """Encode pagination cursor from offset and sort key."""
    import base64
    cursor_data = f"{offset}:{sort_key}"
    return base64.b64encode(cursor_data.encode()).decode()


def decode_cursor(cursor: str) -> dict:
    """Decode pagination cursor to offset and sort key."""
    import base64
    try:
        decoded = base64.b64decode(cursor.encode()).decode()
        parts = decoded.split(':', 1)
        return {'offset': int(parts[0]), 'sort_key': parts[1] if len(parts) > 1 else ''}
    except (ValueError, UnicodeDecodeError):
        return {'offset': 0, 'sort_key': ''}


def create_page_info(page: int, page_size: int, total_items: int) -> dict:
    """Create a page info object with all pagination details."""
    total_pages = calculate_total_pages(total_items, page_size)
    return {
        'current_page': page,
        'page_size': page_size,
        'total_items': total_items,
        'total_pages': total_pages,
        'has_next': has_next_page(page, total_pages),
        'has_previous': has_previous_page(page),
        'start_index': get_start_index(page, page_size),
        'end_index': get_end_index(page, page_size, total_items),
    }


def create_cursor_page_info(has_more: bool, cursor: str, count: int) -> dict:
    """Create cursor-based pagination info."""
    return {
        'has_more': has_more,
        'cursor': cursor,
        'count': count,
    }


def calculate_skip_limit(page: int, page_size: int) -> tuple:
    """Calculate skip and limit values for database queries."""
    return (calculate_offset(page, page_size), page_size)


def parse_page_params(page_str: str, size_str: str, default_size: int, max_size: int) -> tuple:
    """Parse page parameters from strings."""
    try:
        page = max(1, int(page_str) if page_str else 1)
    except ValueError:
        page = 1
    try:
        size = int(size_str) if size_str else default_size
        size = max(1, min(size, max_size))
    except ValueError:
        size = default_size
    return (page, size)


def format_pagination_summary(page: int, page_size: int, total_items: int) -> str:
    """Format a human-readable pagination summary."""
    if total_items == 0:
        return "No items"
    start = get_start_index(page, page_size)
    end = get_end_index(page, page_size, total_items)
    return f"Showing {start}-{end} of {total_items}"


def calculate_pages_array(total_pages: int) -> list:
    """Generate an array of all page numbers."""
    return list(range(1, total_pages + 1))


def is_first_page(page: int) -> bool:
    """Check if on the first page."""
    return page == 1


def is_last_page(page: int, total_pages: int) -> bool:
    """Check if on the last page."""
    return page >= total_pages


def get_remaining_items(page: int, page_size: int, total_items: int) -> int:
    """Calculate remaining items after current page."""
    shown = page * page_size
    return max(0, total_items - shown)


def get_remaining_pages(page: int, total_pages: int) -> int:
    """Calculate remaining pages after current page."""
    return max(0, total_pages - page)


def normalize_page_size(requested_size: int, min_size: int, max_size: int, default_size: int) -> int:
    """Normalize page size to valid range."""
    if requested_size <= 0:
        return default_size
    return max(min_size, min(requested_size, max_size))


def build_page_url(base_url: str, page: int, page_param: str) -> str:
    """Build a URL for a specific page."""
    if '?' in base_url:
        if page_param + '=' in base_url:
            import re
            return re.sub(f'{page_param}=\\d+', f'{page_param}={page}', base_url)
        return f"{base_url}&{page_param}={page}"
    return f"{base_url}?{page_param}={page}"


def calculate_batch_ranges(total_items: int, batch_size: int) -> list:
    """Calculate (start, end) ranges for batch processing."""
    ranges = []
    for i in range(0, total_items, batch_size):
        ranges.append((i, min(i + batch_size, total_items)))
    return ranges


def is_page_empty(page: int, page_size: int, total_items: int) -> bool:
    """Check if a page would be empty."""
    return get_items_on_page(page, page_size, total_items) == 0


def get_middle_page(total_pages: int) -> int:
    """Get the middle page number."""
    return (total_pages + 1) // 2


def pages_between(start_page: int, end_page: int) -> list:
    """Get list of page numbers between start and end (inclusive)."""
    return list(range(max(1, start_page), end_page + 1))
