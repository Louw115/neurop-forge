"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Content Utilities - Pure functions for content management.
All functions are pure, deterministic, and atomic.
"""

def build_content_item(item_id: str, title: str, body: str, content_type: str, status: str) -> dict:
    """Build a content item."""
    return {
        "id": item_id,
        "title": title,
        "body": body,
        "type": content_type,
        "status": status,
        "metadata": {},
        "created_at": None,
        "updated_at": None
    }


def set_content_status(item: dict, status: str, timestamp: str) -> dict:
    """Set content item status."""
    result = dict(item)
    result["status"] = status
    result["updated_at"] = timestamp
    return result


def publish_content(item: dict, timestamp: str) -> dict:
    """Publish content item."""
    return set_content_status(item, "published", timestamp)


def unpublish_content(item: dict, timestamp: str) -> dict:
    """Unpublish content item."""
    return set_content_status(item, "draft", timestamp)


def archive_content(item: dict, timestamp: str) -> dict:
    """Archive content item."""
    return set_content_status(item, "archived", timestamp)


def add_content_metadata(item: dict, key: str, value) -> dict:
    """Add metadata to content item."""
    result = dict(item)
    result["metadata"] = dict(item.get("metadata", {}))
    result["metadata"][key] = value
    return result


def build_content_version(item_id: str, version_number: int, content: dict, created_at: str) -> dict:
    """Build a content version."""
    return {
        "item_id": item_id,
        "version": version_number,
        "content": content,
        "created_at": created_at
    }


def extract_text_from_html(html: str) -> str:
    """Extract plain text from HTML."""
    import re
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def calculate_reading_time(text: str, words_per_minute: int) -> int:
    """Calculate reading time in minutes."""
    word_count = len(text.split())
    return max(1, (word_count + words_per_minute - 1) // words_per_minute)


def calculate_word_count(text: str) -> int:
    """Calculate word count."""
    return len(text.split())


def calculate_character_count(text: str, include_spaces: bool) -> int:
    """Calculate character count."""
    if include_spaces:
        return len(text)
    return len(text.replace(" ", ""))


def truncate_content(text: str, max_length: int, suffix: str) -> str:
    """Truncate content with suffix."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(" ")
    if last_space > max_length // 2:
        truncated = truncated[:last_space]
    return truncated + suffix


def generate_excerpt(body: str, max_length: int) -> str:
    """Generate excerpt from body."""
    text = extract_text_from_html(body)
    return truncate_content(text, max_length, "...")


def generate_slug(title: str) -> str:
    """Generate URL slug from title."""
    import re
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def validate_slug(slug: str) -> bool:
    """Validate slug format."""
    import re
    return bool(re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug))


def ensure_unique_slug(base_slug: str, existing_slugs: set, max_suffix: int) -> str:
    """Ensure slug is unique by adding suffix if needed."""
    if base_slug not in existing_slugs:
        return base_slug
    for i in range(1, max_suffix + 1):
        candidate = f"{base_slug}-{i}"
        if candidate not in existing_slugs:
            return candidate
    return f"{base_slug}-{max_suffix + 1}"


def build_content_tag(tag_id: str, name: str, slug: str) -> dict:
    """Build a content tag."""
    return {
        "id": tag_id,
        "name": name,
        "slug": slug
    }


def add_tags_to_content(item: dict, tag_ids: list) -> dict:
    """Add tags to content item."""
    result = dict(item)
    result["tags"] = list(set(item.get("tags", []) + tag_ids))
    return result


def remove_tags_from_content(item: dict, tag_ids: list) -> dict:
    """Remove tags from content item."""
    result = dict(item)
    result["tags"] = [t for t in item.get("tags", []) if t not in tag_ids]
    return result


def filter_content_by_status(items: list, status: str) -> list:
    """Filter content items by status."""
    return [item for item in items if item.get("status") == status]


def filter_content_by_type(items: list, content_type: str) -> list:
    """Filter content items by type."""
    return [item for item in items if item.get("type") == content_type]


def filter_content_by_tag(items: list, tag_id: str) -> list:
    """Filter content items by tag."""
    return [item for item in items if tag_id in item.get("tags", [])]


def sort_content_by_date(items: list, date_field: str, descending: bool) -> list:
    """Sort content items by date field."""
    return sorted(items, key=lambda x: x.get(date_field, ""), reverse=descending)


def build_content_summary(item: dict, excerpt_length: int) -> dict:
    """Build content summary for listings."""
    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "excerpt": generate_excerpt(item.get("body", ""), excerpt_length),
        "type": item.get("type"),
        "status": item.get("status"),
        "created_at": item.get("created_at")
    }


def calculate_content_stats(items: list) -> dict:
    """Calculate content statistics."""
    total = len(items)
    by_status = {}
    by_type = {}
    for item in items:
        status = item.get("status", "unknown")
        content_type = item.get("type", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
        by_type[content_type] = by_type.get(content_type, 0) + 1
    return {
        "total": total,
        "by_status": by_status,
        "by_type": by_type
    }


def build_content_tree(items: list, parent_field: str) -> list:
    """Build hierarchical content tree."""
    by_parent = {}
    roots = []
    for item in items:
        parent_id = item.get(parent_field)
        if parent_id:
            if parent_id not in by_parent:
                by_parent[parent_id] = []
            by_parent[parent_id].append(item)
        else:
            roots.append(item)
    def attach_children(node):
        children = by_parent.get(node["id"], [])
        return {**node, "children": [attach_children(c) for c in children]}
    return [attach_children(root) for root in roots]
