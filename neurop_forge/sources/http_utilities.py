"""
HTTP Utilities - Pure functions for HTTP-related operations.

All functions are:
- Pure (no side effects, no network calls)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def get_status_text(code: int) -> str:
    """Get the standard text for an HTTP status code."""
    status_texts = {
        100: "Continue",
        101: "Switching Protocols",
        200: "OK",
        201: "Created",
        202: "Accepted",
        204: "No Content",
        206: "Partial Content",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
    }
    return status_texts.get(code, "Unknown Status")


def is_success_status(code: int) -> bool:
    """Check if a status code indicates success (2xx)."""
    return 200 <= code < 300


def is_redirect_status(code: int) -> bool:
    """Check if a status code indicates redirect (3xx)."""
    return 300 <= code < 400


def is_client_error_status(code: int) -> bool:
    """Check if a status code indicates client error (4xx)."""
    return 400 <= code < 500


def is_server_error_status(code: int) -> bool:
    """Check if a status code indicates server error (5xx)."""
    return 500 <= code < 600


def is_error_status(code: int) -> bool:
    """Check if a status code indicates any error (4xx or 5xx)."""
    return 400 <= code < 600


def get_status_category(code: int) -> str:
    """Get the category of an HTTP status code."""
    if 100 <= code < 200:
        return "informational"
    if 200 <= code < 300:
        return "success"
    if 300 <= code < 400:
        return "redirection"
    if 400 <= code < 500:
        return "client_error"
    if 500 <= code < 600:
        return "server_error"
    return "unknown"


def get_mime_type(extension: str) -> str:
    """Get the MIME type for a file extension."""
    extension = extension.lower().lstrip('.')
    mime_types = {
        "html": "text/html",
        "htm": "text/html",
        "css": "text/css",
        "js": "application/javascript",
        "mjs": "application/javascript",
        "json": "application/json",
        "xml": "application/xml",
        "txt": "text/plain",
        "csv": "text/csv",
        "md": "text/markdown",
        "pdf": "application/pdf",
        "zip": "application/zip",
        "gz": "application/gzip",
        "tar": "application/x-tar",
        "rar": "application/vnd.rar",
        "7z": "application/x-7z-compressed",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
        "ico": "image/x-icon",
        "bmp": "image/bmp",
        "tiff": "image/tiff",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
        "aac": "audio/aac",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "avi": "video/x-msvideo",
        "mov": "video/quicktime",
        "mkv": "video/x-matroska",
        "woff": "font/woff",
        "woff2": "font/woff2",
        "ttf": "font/ttf",
        "otf": "font/otf",
        "eot": "application/vnd.ms-fontobject",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    return mime_types.get(extension, "application/octet-stream")


def get_extension_for_mime(mime_type: str) -> str:
    """Get the file extension for a MIME type."""
    mime_type = mime_type.lower().split(';')[0].strip()
    extensions = {
        "text/html": "html",
        "text/css": "css",
        "application/javascript": "js",
        "application/json": "json",
        "application/xml": "xml",
        "text/plain": "txt",
        "text/csv": "csv",
        "text/markdown": "md",
        "application/pdf": "pdf",
        "application/zip": "zip",
        "application/gzip": "gz",
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/svg+xml": "svg",
        "audio/mpeg": "mp3",
        "audio/wav": "wav",
        "video/mp4": "mp4",
        "video/webm": "webm",
        "font/woff": "woff",
        "font/woff2": "woff2",
    }
    return extensions.get(mime_type, "")


def is_text_mime_type(mime_type: str) -> bool:
    """Check if a MIME type represents text content."""
    mime_type = mime_type.lower().split(';')[0].strip()
    if mime_type.startswith("text/"):
        return True
    text_types = [
        "application/json",
        "application/javascript",
        "application/xml",
        "application/xhtml+xml",
    ]
    return mime_type in text_types


def is_image_mime_type(mime_type: str) -> bool:
    """Check if a MIME type represents an image."""
    return mime_type.lower().startswith("image/")


def is_video_mime_type(mime_type: str) -> bool:
    """Check if a MIME type represents video."""
    return mime_type.lower().startswith("video/")


def is_audio_mime_type(mime_type: str) -> bool:
    """Check if a MIME type represents audio."""
    return mime_type.lower().startswith("audio/")


def build_content_type_header(mime_type: str, charset: str) -> str:
    """Build a Content-Type header value."""
    if charset:
        return f"{mime_type}; charset={charset}"
    return mime_type


def parse_content_type(header: str) -> dict:
    """Parse a Content-Type header into components."""
    if not header:
        return {"mime_type": "", "charset": "", "boundary": ""}
    parts = header.split(';')
    result = {"mime_type": parts[0].strip(), "charset": "", "boundary": ""}
    for part in parts[1:]:
        part = part.strip()
        if part.lower().startswith("charset="):
            result["charset"] = part[8:].strip('"\'')
        elif part.lower().startswith("boundary="):
            result["boundary"] = part[9:].strip('"\'')
    return result


def build_accept_header(mime_types: list) -> str:
    """Build an Accept header from a list of MIME types."""
    if not mime_types:
        return "*/*"
    return ", ".join(mime_types)


def build_cache_control(directives: dict) -> str:
    """Build a Cache-Control header from directives."""
    if not directives:
        return ""
    parts = []
    for key, value in directives.items():
        if value is True:
            parts.append(key)
        elif value is not False and value is not None:
            parts.append(f"{key}={value}")
    return ", ".join(parts)


def parse_cache_control(header: str) -> dict:
    """Parse a Cache-Control header into directives."""
    if not header:
        return {}
    result = {}
    parts = header.split(',')
    for part in parts:
        part = part.strip()
        if '=' in part:
            key, value = part.split('=', 1)
            try:
                result[key.strip()] = int(value.strip())
            except ValueError:
                result[key.strip()] = value.strip()
        else:
            result[part] = True
    return result


def build_authorization_basic(username: str, password: str) -> str:
    """Build a Basic Authorization header value."""
    import base64
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def build_authorization_bearer(token: str) -> str:
    """Build a Bearer Authorization header value."""
    return f"Bearer {token}"


def parse_authorization_header(header: str) -> dict:
    """Parse an Authorization header into type and credentials."""
    if not header:
        return {"type": "", "credentials": ""}
    parts = header.split(' ', 1)
    if len(parts) == 2:
        return {"type": parts[0], "credentials": parts[1]}
    return {"type": parts[0], "credentials": ""}


def is_valid_http_method(method: str) -> bool:
    """Check if a string is a valid HTTP method."""
    valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE", "CONNECT"}
    return method.upper() in valid_methods


def is_safe_http_method(method: str) -> bool:
    """Check if an HTTP method is safe (doesn't modify resources)."""
    safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}
    return method.upper() in safe_methods


def is_idempotent_http_method(method: str) -> bool:
    """Check if an HTTP method is idempotent."""
    idempotent_methods = {"GET", "PUT", "DELETE", "HEAD", "OPTIONS", "TRACE"}
    return method.upper() in idempotent_methods


def build_cookie_header(cookies: dict) -> str:
    """Build a Cookie header from a dictionary."""
    if not cookies:
        return ""
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


def parse_cookie_header(header: str) -> dict:
    """Parse a Cookie header into a dictionary."""
    if not header:
        return {}
    result = {}
    pairs = header.split(';')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            result[key.strip()] = value.strip()
    return result


def build_set_cookie(name: str, value: str, max_age: int, path: str, secure: bool, http_only: bool) -> str:
    """Build a Set-Cookie header value."""
    parts = [f"{name}={value}"]
    if max_age is not None and max_age >= 0:
        parts.append(f"Max-Age={max_age}")
    if path:
        parts.append(f"Path={path}")
    if secure:
        parts.append("Secure")
    if http_only:
        parts.append("HttpOnly")
    return "; ".join(parts)


def build_content_disposition(disposition: str, filename: str) -> str:
    """Build a Content-Disposition header."""
    if filename:
        return f'{disposition}; filename="{filename}"'
    return disposition


def parse_content_length(header: str) -> int:
    """Parse a Content-Length header to integer."""
    if not header:
        return 0
    try:
        return int(header)
    except ValueError:
        return 0


def build_range_header(start: int, end: int) -> str:
    """Build a Range header for byte ranges."""
    if end is None:
        return f"bytes={start}-"
    return f"bytes={start}-{end}"


def parse_range_header(header: str) -> list:
    """Parse a Range header into list of tuples."""
    if not header or not header.startswith("bytes="):
        return []
    ranges = []
    range_spec = header[6:]
    for part in range_spec.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start) if start else None
            end = int(end) if end else None
            ranges.append((start, end))
    return ranges


def build_etag(content_hash: str, weak: bool) -> str:
    """Build an ETag header value."""
    if weak:
        return f'W/"{content_hash}"'
    return f'"{content_hash}"'


def parse_etag(header: str) -> dict:
    """Parse an ETag header."""
    if not header:
        return {"value": "", "weak": False}
    weak = header.startswith('W/')
    if weak:
        header = header[2:]
    value = header.strip('"')
    return {"value": value, "weak": weak}


def is_cacheable_status(code: int) -> bool:
    """Check if a status code is cacheable by default."""
    cacheable = {200, 203, 204, 206, 300, 301, 308, 404, 405, 410, 414, 501}
    return code in cacheable


def get_retry_after_seconds(header: str) -> int:
    """Parse Retry-After header to seconds."""
    if not header:
        return 0
    try:
        return int(header)
    except ValueError:
        return 0


def build_link_header(url: str, rel: str) -> str:
    """Build a Link header."""
    return f'<{url}>; rel="{rel}"'


def build_cors_headers(origin: str, methods: list, headers: list, max_age: int) -> dict:
    """Build CORS response headers."""
    result = {}
    if origin:
        result["Access-Control-Allow-Origin"] = origin
    if methods:
        result["Access-Control-Allow-Methods"] = ", ".join(methods)
    if headers:
        result["Access-Control-Allow-Headers"] = ", ".join(headers)
    if max_age > 0:
        result["Access-Control-Max-Age"] = str(max_age)
    return result


def normalize_header_name(name: str) -> str:
    """Normalize an HTTP header name to title case."""
    return '-'.join(word.capitalize() for word in name.split('-'))


def is_hop_by_hop_header(name: str) -> bool:
    """Check if a header is hop-by-hop (not forwarded by proxies)."""
    hop_by_hop = {
        "connection", "keep-alive", "proxy-authenticate",
        "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade"
    }
    return name.lower() in hop_by_hop
