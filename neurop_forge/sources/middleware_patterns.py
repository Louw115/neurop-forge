"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Middleware Pattern Utilities - Pure functions for middleware logic.
All functions are pure, deterministic, and atomic.
"""

def extract_request_id(headers: dict, header_names: list) -> str:
    """Extract request ID from headers."""
    for name in header_names:
        if name in headers:
            return headers[name]
        if name.lower() in headers:
            return headers[name.lower()]
    return ""


def generate_request_id(timestamp: str, sequence: int, node_id: str) -> str:
    """Generate a request ID."""
    import hashlib
    combined = f"{timestamp}:{sequence}:{node_id}"
    return hashlib.sha256(combined.encode()).hexdigest()[:32]


def build_request_context(request_id: str, user_id: str, ip_address: str, user_agent: str, timestamp: str) -> dict:
    """Build a request context object."""
    return {
        "request_id": request_id,
        "user_id": user_id,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "timestamp": timestamp,
        "attributes": {}
    }


def add_context_attribute(context: dict, key: str, value) -> dict:
    """Add an attribute to request context."""
    result = dict(context)
    result["attributes"] = dict(result.get("attributes", {}))
    result["attributes"][key] = value
    return result


def extract_client_ip(headers: dict, remote_addr: str) -> str:
    """Extract client IP address considering proxies."""
    forwarded_for = headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = headers.get("X-Real-IP", "")
    if real_ip:
        return real_ip
    return remote_addr


def is_trusted_proxy(ip: str, trusted_proxies: list) -> bool:
    """Check if an IP is a trusted proxy."""
    return ip in trusted_proxies


def extract_user_agent(headers: dict) -> str:
    """Extract User-Agent from headers."""
    return headers.get("User-Agent", headers.get("user-agent", ""))


def parse_user_agent(user_agent: str) -> dict:
    """Parse user agent string (basic parsing)."""
    import re
    result = {"browser": "", "version": "", "os": "", "device": "desktop"}
    if "Mobile" in user_agent:
        result["device"] = "mobile"
    elif "Tablet" in user_agent:
        result["device"] = "tablet"
    browsers = [
        ("Chrome", r"Chrome/(\d+)"),
        ("Firefox", r"Firefox/(\d+)"),
        ("Safari", r"Version/(\d+).*Safari"),
        ("Edge", r"Edg/(\d+)"),
        ("MSIE", r"MSIE (\d+)"),
    ]
    for browser, pattern in browsers:
        match = re.search(pattern, user_agent)
        if match:
            result["browser"] = browser
            result["version"] = match.group(1)
            break
    if "Windows" in user_agent:
        result["os"] = "Windows"
    elif "Mac" in user_agent:
        result["os"] = "macOS"
    elif "Linux" in user_agent:
        result["os"] = "Linux"
    elif "Android" in user_agent:
        result["os"] = "Android"
    elif "iOS" in user_agent or "iPhone" in user_agent:
        result["os"] = "iOS"
    return result


def calculate_request_duration(start_time: int, end_time: int) -> int:
    """Calculate request duration in milliseconds."""
    return end_time - start_time


def format_access_log(method: str, path: str, status_code: int, duration_ms: int, request_id: str, client_ip: str, timestamp: str) -> str:
    """Format an access log entry."""
    return f'{timestamp} {client_ip} "{method} {path}" {status_code} {duration_ms}ms [{request_id}]'


def should_log_request(path: str, excluded_paths: list) -> bool:
    """Determine if a request should be logged."""
    for excluded in excluded_paths:
        if path.startswith(excluded):
            return False
    return True


def build_timing_header(server_time_ms: int, db_time_ms: int, cache_time_ms: int) -> str:
    """Build Server-Timing header value."""
    parts = []
    if server_time_ms >= 0:
        parts.append(f'total;dur={server_time_ms}')
    if db_time_ms >= 0:
        parts.append(f'db;dur={db_time_ms}')
    if cache_time_ms >= 0:
        parts.append(f'cache;dur={cache_time_ms}')
    return ", ".join(parts)


def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """Calculate compression ratio."""
    if original_size <= 0:
        return 0.0
    return 1.0 - (compressed_size / original_size)


def should_compress(content_type: str, content_length: int, min_size: int) -> bool:
    """Determine if response should be compressed."""
    if content_length < min_size:
        return False
    compressible_types = [
        "text/", "application/json", "application/javascript",
        "application/xml", "application/xhtml", "image/svg"
    ]
    return any(ct in content_type for ct in compressible_types)


def select_compression_encoding(accept_encoding: str, supported: list) -> str:
    """Select best compression encoding from Accept-Encoding header."""
    if not accept_encoding:
        return ""
    accepted = [e.strip().split(";")[0] for e in accept_encoding.split(",")]
    for encoding in supported:
        if encoding in accepted:
            return encoding
    return ""


def build_security_headers(csp: str, hsts_max_age: int, frame_options: str, content_type_options: bool, xss_protection: bool) -> dict:
    """Build security response headers."""
    headers = {}
    if csp:
        headers["Content-Security-Policy"] = csp
    if hsts_max_age > 0:
        headers["Strict-Transport-Security"] = f"max-age={hsts_max_age}; includeSubDomains"
    if frame_options:
        headers["X-Frame-Options"] = frame_options
    if content_type_options:
        headers["X-Content-Type-Options"] = "nosniff"
    if xss_protection:
        headers["X-XSS-Protection"] = "1; mode=block"
    return headers


def build_csp_header(default_src: list, script_src: list, style_src: list, img_src: list, connect_src: list) -> str:
    """Build Content-Security-Policy header value."""
    parts = []
    if default_src:
        parts.append(f"default-src {' '.join(default_src)}")
    if script_src:
        parts.append(f"script-src {' '.join(script_src)}")
    if style_src:
        parts.append(f"style-src {' '.join(style_src)}")
    if img_src:
        parts.append(f"img-src {' '.join(img_src)}")
    if connect_src:
        parts.append(f"connect-src {' '.join(connect_src)}")
    return "; ".join(parts)


def check_rate_limit(key: str, requests: int, limit: int, window_seconds: int) -> dict:
    """Check rate limit status."""
    remaining = max(0, limit - requests)
    exceeded = requests > limit
    return {
        "allowed": not exceeded,
        "remaining": remaining,
        "limit": limit,
        "window_seconds": window_seconds,
        "key": key
    }


def calculate_rate_limit_reset(window_start: int, window_seconds: int) -> int:
    """Calculate when rate limit window resets."""
    return window_start + window_seconds


def build_rate_limit_key(identifier: str, endpoint: str, window: str) -> str:
    """Build a rate limit key."""
    return f"ratelimit:{identifier}:{endpoint}:{window}"


def is_maintenance_mode(config: dict) -> bool:
    """Check if maintenance mode is enabled."""
    return config.get("maintenance_mode", False)


def should_bypass_maintenance(ip: str, allowed_ips: list, bypass_header: str, bypass_value: str) -> bool:
    """Check if request should bypass maintenance mode."""
    if ip in allowed_ips:
        return True
    return False


def build_maintenance_response(message: str, retry_after: int) -> dict:
    """Build maintenance mode response."""
    return {
        "success": False,
        "error": {
            "code": 503,
            "message": message or "Service temporarily unavailable for maintenance",
            "retry_after": retry_after
        }
    }


def normalize_request_path(path: str) -> str:
    """Normalize a request path."""
    normalized = path.rstrip('/')
    if not normalized:
        normalized = '/'
    return normalized


def match_path_pattern(path: str, pattern: str) -> dict:
    """Match a path against a pattern with placeholders."""
    import re
    param_pattern = re.sub(r':(\w+)', r'(?P<\1>[^/]+)', pattern)
    param_pattern = f'^{param_pattern}$'
    match = re.match(param_pattern, path)
    if match:
        return {"matched": True, "params": match.groupdict()}
    return {"matched": False, "params": {}}


def extract_path_params(path: str, pattern: str) -> dict:
    """Extract path parameters from URL."""
    result = match_path_pattern(path, pattern)
    return result.get("params", {})


def build_request_metadata(method: str, path: str, query_params: dict, headers: dict, body_size: int) -> dict:
    """Build request metadata for logging/tracing."""
    return {
        "method": method,
        "path": path,
        "query_params": query_params,
        "content_length": body_size,
        "content_type": headers.get("Content-Type", ""),
        "accept": headers.get("Accept", "")
    }


def should_trace_request(sample_rate: float, request_hash: int) -> bool:
    """Determine if request should be traced based on sample rate."""
    if sample_rate >= 1.0:
        return True
    if sample_rate <= 0.0:
        return False
    threshold = int(sample_rate * 100)
    return (request_hash % 100) < threshold


def build_trace_context(trace_id: str, span_id: str, parent_span_id: str, sampled: bool) -> dict:
    """Build distributed trace context."""
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "sampled": sampled
    }


def format_traceparent_header(trace_id: str, span_id: str, sampled: bool) -> str:
    """Format W3C Trace Context traceparent header."""
    flags = "01" if sampled else "00"
    return f"00-{trace_id}-{span_id}-{flags}"


def parse_traceparent_header(header: str) -> dict:
    """Parse W3C Trace Context traceparent header."""
    import re
    pattern = r'^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$'
    match = re.match(pattern, header.lower())
    if match:
        return {
            "trace_id": match.group(1),
            "span_id": match.group(2),
            "sampled": match.group(3) == "01"
        }
    return {}


def calculate_request_priority(path: str, method: str, priority_rules: list) -> int:
    """Calculate request priority based on rules."""
    for rule in priority_rules:
        if path.startswith(rule.get("path_prefix", "")):
            if not rule.get("method") or rule.get("method") == method:
                return rule.get("priority", 5)
    return 5


def should_throttle_request(priority: int, current_load: float, threshold: float) -> bool:
    """Determine if request should be throttled."""
    if priority <= 1:
        return False
    return current_load > threshold
