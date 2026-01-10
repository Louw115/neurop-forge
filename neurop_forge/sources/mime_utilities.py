"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
MIME Utilities - Pure functions for MIME type operations.
All functions are pure, deterministic, and atomic.
"""


def get_mime_type(extension: str) -> str:
    """Get MIME type from file extension."""
    mime_types = {
        ".html": "text/html",
        ".htm": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".xml": "application/xml",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".pdf": "application/pdf",
        ".zip": "application/zip",
        ".tar": "application/x-tar",
        ".gz": "application/gzip",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".ico": "image/x-icon",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".avi": "video/x-msvideo",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".otf": "font/otf",
        ".eot": "application/vnd.ms-fontobject"
    }
    return mime_types.get(extension.lower(), "application/octet-stream")


def get_extension(mime_type: str) -> str:
    """Get file extension from MIME type."""
    extensions = {
        "text/html": ".html",
        "text/css": ".css",
        "application/javascript": ".js",
        "application/json": ".json",
        "application/xml": ".xml",
        "text/plain": ".txt",
        "text/csv": ".csv",
        "application/pdf": ".pdf",
        "application/zip": ".zip",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/gif": ".gif",
        "image/svg+xml": ".svg",
        "image/webp": ".webp",
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "video/mp4": ".mp4",
        "video/webm": ".webm"
    }
    return extensions.get(mime_type.lower(), "")


def is_text_type(mime_type: str) -> bool:
    """Check if MIME type is text."""
    return mime_type.startswith("text/") or mime_type in [
        "application/json", "application/xml", "application/javascript"
    ]


def is_image_type(mime_type: str) -> bool:
    """Check if MIME type is image."""
    return mime_type.startswith("image/")


def is_video_type(mime_type: str) -> bool:
    """Check if MIME type is video."""
    return mime_type.startswith("video/")


def is_audio_type(mime_type: str) -> bool:
    """Check if MIME type is audio."""
    return mime_type.startswith("audio/")


def is_font_type(mime_type: str) -> bool:
    """Check if MIME type is font."""
    return mime_type.startswith("font/") or mime_type in [
        "application/vnd.ms-fontobject"
    ]


def is_binary_type(mime_type: str) -> bool:
    """Check if MIME type is binary."""
    return not is_text_type(mime_type)


def get_media_type(mime_type: str) -> str:
    """Get media type category."""
    if is_image_type(mime_type):
        return "image"
    if is_video_type(mime_type):
        return "video"
    if is_audio_type(mime_type):
        return "audio"
    if is_text_type(mime_type):
        return "text"
    if is_font_type(mime_type):
        return "font"
    return "application"


def parse_content_type(header: str) -> dict:
    """Parse Content-Type header."""
    parts = header.split(";")
    mime_type = parts[0].strip()
    params = {}
    for part in parts[1:]:
        if "=" in part:
            key, value = part.strip().split("=", 1)
            params[key.strip()] = value.strip().strip('"')
    return {"mime_type": mime_type, "params": params}


def get_charset(content_type: str) -> str:
    """Extract charset from content type."""
    parsed = parse_content_type(content_type)
    return parsed["params"].get("charset", "")


def is_compressible(mime_type: str) -> bool:
    """Check if content is compressible."""
    compressible = [
        "text/", "application/json", "application/javascript",
        "application/xml", "image/svg+xml"
    ]
    return any(mime_type.startswith(c) if c.endswith("/") else mime_type == c 
               for c in compressible)


def get_accept_header(types: list) -> str:
    """Build Accept header."""
    return ", ".join(types)


def matches_accept(mime_type: str, accept: str) -> bool:
    """Check if MIME type matches Accept header."""
    accepts = [a.strip().split(";")[0] for a in accept.split(",")]
    for a in accepts:
        if a == "*/*":
            return True
        if a.endswith("/*") and mime_type.startswith(a[:-1]):
            return True
        if a == mime_type:
            return True
    return False


def format_content_type(mime_type: str, charset: str) -> str:
    """Format Content-Type header."""
    if charset:
        return f"{mime_type}; charset={charset}"
    return mime_type


def is_safe_upload_type(mime_type: str) -> bool:
    """Check if type is safe for upload."""
    unsafe = ["application/x-httpd-php", "text/x-php", "application/x-executable"]
    return mime_type not in unsafe
