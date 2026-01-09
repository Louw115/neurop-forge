"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
File Utilities - Pure functions for file handling patterns.
All functions are pure, deterministic, and atomic.
"""

def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def get_file_name(path: str) -> str:
    """Get filename from path."""
    return path.replace("\\", "/").rsplit("/", 1)[-1]


def get_file_name_without_extension(filename: str) -> str:
    """Get filename without extension."""
    if "." not in filename:
        return filename
    return filename.rsplit(".", 1)[0]


def get_directory(path: str) -> str:
    """Get directory from path."""
    normalized = path.replace("\\", "/")
    if "/" not in normalized:
        return ""
    return normalized.rsplit("/", 1)[0]


def join_path(parts: list) -> str:
    """Join path parts."""
    return "/".join(p.strip("/") for p in parts if p)


def normalize_path(path: str) -> str:
    """Normalize a file path."""
    parts = path.replace("\\", "/").split("/")
    result = []
    for part in parts:
        if part == "..":
            if result:
                result.pop()
        elif part and part != ".":
            result.append(part)
    return "/".join(result)


def is_absolute_path(path: str) -> bool:
    """Check if path is absolute."""
    return path.startswith("/") or (len(path) > 1 and path[1] == ":")


def make_relative_path(path: str, base: str) -> str:
    """Make path relative to base."""
    path = normalize_path(path)
    base = normalize_path(base)
    if path.startswith(base):
        result = path[len(base):].lstrip("/")
        return result if result else "."
    return path


def get_mime_type(extension: str) -> str:
    """Get MIME type for file extension."""
    mime_types = {
        "html": "text/html",
        "htm": "text/html",
        "css": "text/css",
        "js": "application/javascript",
        "json": "application/json",
        "xml": "application/xml",
        "txt": "text/plain",
        "csv": "text/csv",
        "pdf": "application/pdf",
        "zip": "application/zip",
        "gz": "application/gzip",
        "tar": "application/x-tar",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "webp": "image/webp",
        "ico": "image/x-icon",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "woff": "font/woff",
        "woff2": "font/woff2",
        "ttf": "font/ttf"
    }
    return mime_types.get(extension.lower(), "application/octet-stream")


def is_image_file(filename: str) -> bool:
    """Check if file is an image."""
    ext = get_file_extension(filename)
    return ext in {"png", "jpg", "jpeg", "gif", "svg", "webp", "bmp", "ico"}


def is_video_file(filename: str) -> bool:
    """Check if file is a video."""
    ext = get_file_extension(filename)
    return ext in {"mp4", "webm", "avi", "mov", "mkv", "flv", "wmv"}


def is_audio_file(filename: str) -> bool:
    """Check if file is audio."""
    ext = get_file_extension(filename)
    return ext in {"mp3", "wav", "ogg", "flac", "aac", "m4a"}


def is_document_file(filename: str) -> bool:
    """Check if file is a document."""
    ext = get_file_extension(filename)
    return ext in {"pdf", "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx", "ppt", "pptx"}


def is_archive_file(filename: str) -> bool:
    """Check if file is an archive."""
    ext = get_file_extension(filename)
    return ext in {"zip", "tar", "gz", "rar", "7z", "bz2"}


def is_code_file(filename: str) -> bool:
    """Check if file is a code file."""
    ext = get_file_extension(filename)
    return ext in {"py", "js", "ts", "jsx", "tsx", "java", "c", "cpp", "h", "cs", "go", "rs", "rb", "php"}


def format_file_size(bytes_count: int) -> str:
    """Format file size in human-readable form."""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_count)
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.1f} {units[unit_index]}"


def parse_file_size(size_str: str) -> int:
    """Parse file size string to bytes."""
    import re
    match = re.match(r'^([\d.]+)\s*([KMGT]?B)?$', size_str.upper())
    if not match:
        return 0
    value = float(match.group(1))
    unit = match.group(2) or "B"
    multipliers = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
    return int(value * multipliers.get(unit, 1))


def generate_safe_filename(original: str, max_length: int) -> str:
    """Generate a safe filename from original."""
    import re
    safe = re.sub(r'[^\w\-_. ]', '', original)
    safe = re.sub(r'\s+', '_', safe)
    safe = safe.strip('._')
    if len(safe) > max_length:
        name, ext = safe.rsplit('.', 1) if '.' in safe else (safe, '')
        max_name_len = max_length - len(ext) - 1 if ext else max_length
        safe = name[:max_name_len] + ('.' + ext if ext else '')
    return safe


def generate_unique_filename(base_name: str, existing_names: set, max_attempts: int) -> str:
    """Generate a unique filename."""
    if base_name not in existing_names:
        return base_name
    name, ext = base_name.rsplit('.', 1) if '.' in base_name else (base_name, '')
    for i in range(1, max_attempts + 1):
        candidate = f"{name}_{i}" + (f".{ext}" if ext else "")
        if candidate not in existing_names:
            return candidate
    return f"{name}_{max_attempts + 1}" + (f".{ext}" if ext else "")


def calculate_file_checksum(content: bytes) -> str:
    """Calculate MD5 checksum of file content."""
    import hashlib
    return hashlib.md5(content).hexdigest()


def calculate_file_sha256(content: bytes) -> str:
    """Calculate SHA256 hash of file content."""
    import hashlib
    return hashlib.sha256(content).hexdigest()


def validate_file_size(size: int, max_size: int) -> dict:
    """Validate file size."""
    if size > max_size:
        return {
            "valid": False,
            "error": f"File size ({format_file_size(size)}) exceeds maximum ({format_file_size(max_size)})"
        }
    return {"valid": True, "error": None}


def validate_file_extension(filename: str, allowed_extensions: list) -> dict:
    """Validate file extension."""
    ext = get_file_extension(filename)
    if ext not in [e.lower() for e in allowed_extensions]:
        return {
            "valid": False,
            "error": f"File type .{ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
        }
    return {"valid": True, "error": None}


def build_file_metadata(filename: str, size: int, mime_type: str, checksum: str, uploaded_at: str) -> dict:
    """Build file metadata object."""
    return {
        "filename": filename,
        "size": size,
        "size_formatted": format_file_size(size),
        "mime_type": mime_type,
        "extension": get_file_extension(filename),
        "checksum": checksum,
        "uploaded_at": uploaded_at
    }


def build_upload_result(success: bool, filename: str, url: str, error: str) -> dict:
    """Build file upload result."""
    return {
        "success": success,
        "filename": filename,
        "url": url if success else None,
        "error": error if not success else None
    }


def calculate_upload_progress(bytes_uploaded: int, total_bytes: int) -> float:
    """Calculate upload progress percentage."""
    if total_bytes <= 0:
        return 0.0
    return min(100.0, (bytes_uploaded / total_bytes) * 100)


def estimate_upload_time(bytes_remaining: int, bytes_per_second: float) -> int:
    """Estimate remaining upload time in seconds."""
    if bytes_per_second <= 0:
        return 0
    return int(bytes_remaining / bytes_per_second)


def build_presigned_url_params(bucket: str, key: str, expiration_seconds: int, content_type: str) -> dict:
    """Build parameters for presigned URL generation."""
    return {
        "bucket": bucket,
        "key": key,
        "expiration": expiration_seconds,
        "content_type": content_type
    }


def generate_storage_key(prefix: str, filename: str, timestamp: str) -> str:
    """Generate a storage key/path for uploaded file."""
    date_part = timestamp[:10].replace("-", "/")
    safe_name = generate_safe_filename(filename, 100)
    return f"{prefix}/{date_part}/{safe_name}"


def categorize_file(filename: str) -> str:
    """Categorize file by type."""
    if is_image_file(filename):
        return "image"
    if is_video_file(filename):
        return "video"
    if is_audio_file(filename):
        return "audio"
    if is_document_file(filename):
        return "document"
    if is_archive_file(filename):
        return "archive"
    if is_code_file(filename):
        return "code"
    return "other"
