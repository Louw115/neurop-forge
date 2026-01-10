"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Social Utilities - Pure functions for social media operations.
All functions are pure, deterministic, and atomic.
"""

import re


def extract_hashtags(text: str) -> list:
    """Extract hashtags from text."""
    return re.findall(r'#(\w+)', text)


def extract_mentions(text: str) -> list:
    """Extract @mentions from text."""
    return re.findall(r'@(\w+)', text)


def extract_urls(text: str) -> list:
    """Extract URLs from text."""
    pattern = r'https?://[^\s<>"\'\\]+'
    return re.findall(pattern, text)


def count_hashtags(text: str) -> int:
    """Count hashtags in text."""
    return len(extract_hashtags(text))


def count_mentions(text: str) -> int:
    """Count mentions in text."""
    return len(extract_mentions(text))


def is_valid_username(username: str, min_len: int, max_len: int) -> bool:
    """Validate username format."""
    if len(username) < min_len or len(username) > max_len:
        return False
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username))


def is_valid_handle(handle: str) -> bool:
    """Validate social media handle format."""
    if handle.startswith("@"):
        handle = handle[1:]
    return bool(re.match(r'^[a-zA-Z0-9_]{1,30}$', handle))


def normalize_handle(handle: str) -> str:
    """Normalize handle (remove @, lowercase)."""
    if handle.startswith("@"):
        handle = handle[1:]
    return handle.lower()


def create_hashtag(text: str) -> str:
    """Create hashtag from text."""
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', text)
    return "#" + cleaned if cleaned else ""


def format_share_text(title: str, url: str, max_length: int) -> str:
    """Format text for sharing (Twitter style)."""
    url_length = len(url) + 1
    available = max_length - url_length
    if len(title) <= available:
        return f"{title} {url}"
    return f"{title[:available-3]}... {url}"


def calculate_engagement_rate(likes: int, comments: int, shares: int, followers: int) -> float:
    """Calculate engagement rate."""
    if followers == 0:
        return 0
    return (likes + comments + shares) / followers * 100


def format_follower_count(count: int) -> str:
    """Format follower count (1.2K, 3.4M, etc.)."""
    if count < 1000:
        return str(count)
    if count < 1000000:
        return f"{count / 1000:.1f}K".replace(".0K", "K")
    if count < 1000000000:
        return f"{count / 1000000:.1f}M".replace(".0M", "M")
    return f"{count / 1000000000:.1f}B".replace(".0B", "B")


def parse_follower_count(formatted: str) -> int:
    """Parse formatted follower count back to integer."""
    formatted = formatted.strip().upper()
    if formatted.endswith("K"):
        return int(float(formatted[:-1]) * 1000)
    if formatted.endswith("M"):
        return int(float(formatted[:-1]) * 1000000)
    if formatted.endswith("B"):
        return int(float(formatted[:-1]) * 1000000000)
    return int(formatted)


def is_trending_hashtag(tag: str, count: int, threshold: int) -> bool:
    """Check if hashtag is trending."""
    return count >= threshold


def calculate_virality_score(shares: int, impressions: int) -> float:
    """Calculate virality coefficient."""
    if impressions == 0:
        return 0
    return shares / impressions


def format_relative_time(seconds_ago: int) -> str:
    """Format time as relative (2h ago, etc.)."""
    if seconds_ago < 60:
        return "just now"
    if seconds_ago < 3600:
        mins = seconds_ago // 60
        return f"{mins}m ago"
    if seconds_ago < 86400:
        hours = seconds_ago // 3600
        return f"{hours}h ago"
    if seconds_ago < 604800:
        days = seconds_ago // 86400
        return f"{days}d ago"
    if seconds_ago < 2592000:
        weeks = seconds_ago // 604800
        return f"{weeks}w ago"
    if seconds_ago < 31536000:
        months = seconds_ago // 2592000
        return f"{months}mo ago"
    years = seconds_ago // 31536000
    return f"{years}y ago"


def extract_twitter_handle(url: str) -> str:
    """Extract Twitter handle from URL."""
    match = re.search(r'(?:twitter|x)\.com/(@?\w+)', url, re.IGNORECASE)
    return match.group(1) if match else ""


def extract_instagram_handle(url: str) -> str:
    """Extract Instagram handle from URL."""
    match = re.search(r'instagram\.com/(@?\w+)', url, re.IGNORECASE)
    return match.group(1) if match else ""


def extract_youtube_video_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def build_youtube_embed_url(video_id: str) -> str:
    """Build YouTube embed URL."""
    return f"https://www.youtube.com/embed/{video_id}"


def build_twitter_share_url(text: str, url: str) -> str:
    """Build Twitter share URL."""
    from urllib.parse import quote
    return f"https://twitter.com/intent/tweet?text={quote(text)}&url={quote(url)}"


def build_facebook_share_url(url: str) -> str:
    """Build Facebook share URL."""
    from urllib.parse import quote
    return f"https://www.facebook.com/sharer/sharer.php?u={quote(url)}"


def build_linkedin_share_url(url: str, title: str) -> str:
    """Build LinkedIn share URL."""
    from urllib.parse import quote
    return f"https://www.linkedin.com/shareArticle?mini=true&url={quote(url)}&title={quote(title)}"


def sanitize_bio(bio: str, max_length: int) -> str:
    """Sanitize and truncate bio."""
    bio = re.sub(r'\s+', ' ', bio.strip())
    if len(bio) > max_length:
        return bio[:max_length-3] + "..."
    return bio


def parse_emoji_shortcode(shortcode: str) -> str:
    """Convert emoji shortcode to name."""
    return shortcode.strip(":").replace("_", " ")


def count_emojis(text: str) -> int:
    """Count emoji characters in text."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "]+", 
        flags=re.UNICODE
    )
    return len(emoji_pattern.findall(text))
