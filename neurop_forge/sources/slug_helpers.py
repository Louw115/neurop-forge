"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Slug Helpers - Pure functions for URL slug operations.
All functions are pure, deterministic, and atomic.
"""

import re
import unicodedata


def slugify(text: str) -> str:
    """Convert text to URL slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def slugify_preserve_unicode(text: str) -> str:
    """Slugify preserving unicode characters."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def is_valid_slug(slug: str) -> bool:
    """Check if string is valid slug."""
    return bool(re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$", slug))


def ensure_unique_slug(slug: str, existing: list, separator: str) -> str:
    """Ensure slug is unique by adding suffix."""
    if slug not in existing:
        return slug
    counter = 1
    while f"{slug}{separator}{counter}" in existing:
        counter += 1
    return f"{slug}{separator}{counter}"


def truncate_slug(slug: str, max_length: int) -> str:
    """Truncate slug to maximum length."""
    if len(slug) <= max_length:
        return slug
    truncated = slug[:max_length]
    if truncated.endswith("-"):
        truncated = truncated[:-1]
    last_dash = truncated.rfind("-")
    if last_dash > max_length // 2:
        truncated = truncated[:last_dash]
    return truncated


def slug_from_filename(filename: str) -> str:
    """Create slug from filename."""
    name = filename.rsplit(".", 1)[0]
    return slugify(name)


def slug_from_url(url: str) -> str:
    """Create slug from URL path."""
    path = url.split("?")[0].split("#")[0]
    path = path.rstrip("/").split("/")[-1]
    return slugify(path) or "index"


def combine_slugs(slugs: list, separator: str) -> str:
    """Combine multiple slugs."""
    return separator.join(s for s in slugs if s)


def split_slug(slug: str, separator: str) -> list:
    """Split slug into parts."""
    return slug.split(separator)


def slug_to_title(slug: str) -> str:
    """Convert slug back to title case."""
    words = slug.replace("-", " ").replace("_", " ").split()
    return " ".join(word.capitalize() for word in words)


def add_prefix(slug: str, prefix: str, separator: str) -> str:
    """Add prefix to slug."""
    return f"{prefix}{separator}{slug}"


def add_suffix(slug: str, suffix: str, separator: str) -> str:
    """Add suffix to slug."""
    return f"{slug}{separator}{suffix}"


def remove_prefix(slug: str, prefix: str, separator: str) -> str:
    """Remove prefix from slug."""
    full_prefix = f"{prefix}{separator}"
    if slug.startswith(full_prefix):
        return slug[len(full_prefix):]
    return slug


def remove_suffix(slug: str, suffix: str, separator: str) -> str:
    """Remove suffix from slug."""
    full_suffix = f"{separator}{suffix}"
    if slug.endswith(full_suffix):
        return slug[:-len(full_suffix)]
    return slug


def has_numeric_suffix(slug: str, separator: str) -> bool:
    """Check if slug has numeric suffix."""
    parts = slug.rsplit(separator, 1)
    return len(parts) == 2 and parts[1].isdigit()


def extract_numeric_suffix(slug: str, separator: str) -> dict:
    """Extract numeric suffix from slug."""
    parts = slug.rsplit(separator, 1)
    if len(parts) == 2 and parts[1].isdigit():
        return {"base": parts[0], "number": int(parts[1])}
    return {"base": slug, "number": None}


def increment_slug(slug: str, separator: str) -> str:
    """Increment numeric suffix of slug."""
    info = extract_numeric_suffix(slug, separator)
    if info["number"] is not None:
        return f"{info['base']}{separator}{info['number'] + 1}"
    return f"{slug}{separator}1"


def normalize_slug(slug: str) -> str:
    """Normalize slug removing extra dashes."""
    return re.sub(r"-+", "-", slug).strip("-")


def compare_slugs(slug1: str, slug2: str) -> bool:
    """Compare slugs case-insensitively."""
    return slugify(slug1) == slugify(slug2)


def create_hierarchical_slug(parts: list, separator: str) -> str:
    """Create hierarchical slug from parts."""
    return separator.join(slugify(part) for part in parts if part)


def extract_slug_from_path(path: str) -> str:
    """Extract slug from URL path."""
    parts = path.strip("/").split("/")
    return parts[-1] if parts else ""
