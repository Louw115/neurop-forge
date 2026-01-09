"""
Security Utilities - Pure functions for data sanitization and masking.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import re


def sanitize_html(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    return re.sub(r'<[^>]+>', '', text)


def strip_scripts(html: str) -> str:
    """Remove script tags and their contents from HTML."""
    if not html:
        return ""
    return re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)


def strip_styles(html: str) -> str:
    """Remove style tags and their contents from HTML."""
    if not html:
        return ""
    return re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing unsafe characters."""
    if not filename:
        return ""
    unsafe = '<>:"/\\|?*\x00'
    result = ''.join(c for c in filename if c not in unsafe)
    result = result.strip('. ')
    return result or 'unnamed'


def sanitize_path_component(component: str) -> str:
    """Sanitize a single path component to prevent traversal."""
    if not component:
        return ""
    sanitized = component.replace('..', '').replace('/', '').replace('\\', '')
    return sanitize_filename(sanitized)


def mask_email(email: str) -> str:
    """Mask an email address for privacy."""
    if not email or '@' not in email:
        return email
    local, domain = email.rsplit('@', 1)
    if len(local) <= 2:
        masked_local = '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask a phone number showing only last 4 digits."""
    if not phone:
        return ""
    digits = ''.join(c for c in phone if c.isdigit())
    if len(digits) <= 4:
        return '*' * len(digits)
    return '*' * (len(digits) - 4) + digits[-4:]


def mask_ip_address(ip: str) -> str:
    """Mask an IP address for privacy."""
    if not ip:
        return ""
    parts = ip.split('.')
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.***.***"
    return '***.***.***.***'


def mask_string(text: str, visible_start: int, visible_end: int, mask_char: str) -> str:
    """Mask a string keeping only specified start and end characters visible."""
    if not text:
        return ""
    if not mask_char:
        mask_char = '*'
    if len(text) <= visible_start + visible_end:
        return text
    start = text[:visible_start]
    end = text[-visible_end:] if visible_end > 0 else ""
    middle_len = len(text) - visible_start - visible_end
    return start + (mask_char * middle_len) + end


def redact_patterns(text: str, patterns: list, replacement: str) -> str:
    """Redact text matching any of the given regex patterns."""
    if not text:
        return ""
    result = text
    for pattern in patterns:
        try:
            result = re.sub(pattern, replacement, result)
        except re.error:
            continue
    return result


def remove_null_bytes(text: str) -> str:
    """Remove null bytes from text."""
    return text.replace('\x00', '')


def escape_shell_arg(arg: str) -> str:
    """Escape a string for safe use as a shell argument."""
    if not arg:
        return "''"
    return "'" + arg.replace("'", "'\"'\"'") + "'"


def escape_regex(text: str) -> str:
    """Escape special regex characters in text."""
    if not text:
        return ""
    special = r'\.^$*+?{}[]|()/'
    return ''.join('\\' + c if c in special else c for c in text)


def normalize_unicode(text: str) -> str:
    """Normalize unicode text to NFC form."""
    import unicodedata
    if not text:
        return ""
    return unicodedata.normalize('NFC', text)


def remove_control_characters(text: str) -> str:
    """Remove control characters from text."""
    if not text:
        return ""
    return ''.join(c for c in text if ord(c) >= 32 or c in '\t\n\r')


def limit_string_length(text: str, max_length: int) -> str:
    """Limit string to maximum length."""
    if not text or max_length <= 0:
        return ""
    return text[:max_length]


def validate_alphanumeric(text: str) -> bool:
    """Check if text contains only alphanumeric characters."""
    if not text:
        return False
    return text.isalnum()


def validate_alpha(text: str) -> bool:
    """Check if text contains only alphabetic characters."""
    if not text:
        return False
    return text.isalpha()


def validate_numeric(text: str) -> bool:
    """Check if text contains only numeric characters."""
    if not text:
        return False
    return text.isnumeric()


def contains_sql_injection_patterns(text: str) -> bool:
    """Check if text contains common SQL injection patterns."""
    if not text:
        return False
    patterns = [
        r"('\s*OR\s+')",
        r"('\s*AND\s+')",
        r"(--\s*$)",
        r"(;\s*DROP\s+)",
        r"(;\s*DELETE\s+)",
        r"(UNION\s+SELECT)",
        r"(INSERT\s+INTO)",
        r"(UPDATE\s+\w+\s+SET)",
    ]
    text_upper = text.upper()
    for pattern in patterns:
        if re.search(pattern, text_upper, re.IGNORECASE):
            return True
    return False


def contains_xss_patterns(text: str) -> bool:
    """Check if text contains common XSS patterns."""
    if not text:
        return False
    patterns = [
        r'<script',
        r'javascript:',
        r'onerror\s*=',
        r'onload\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'onfocus\s*=',
        r'onblur\s*=',
    ]
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False


def strip_dangerous_attributes(html: str) -> str:
    """Remove dangerous HTML attributes like onclick, onerror, etc."""
    if not html:
        return ""
    dangerous = [
        r'\s+on\w+\s*=\s*["\'][^"\']*["\']',
        r'\s+on\w+\s*=\s*[^\s>]+',
    ]
    result = html
    for pattern in dangerous:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    return result


def is_safe_url(url: str) -> bool:
    """Check if a URL is considered safe (no javascript: or data: schemes)."""
    if not url:
        return False
    url_lower = url.strip().lower()
    dangerous_schemes = ['javascript:', 'data:', 'vbscript:', 'file:']
    for scheme in dangerous_schemes:
        if url_lower.startswith(scheme):
            return False
    return True


def generate_password_strength_score(password: str) -> int:
    """Calculate password strength score (0-100)."""
    if not password:
        return 0
    score = 0
    if len(password) >= 8:
        score += 20
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10
    if any(c.islower() for c in password):
        score += 15
    if any(c.isupper() for c in password):
        score += 15
    if any(c.isdigit() for c in password):
        score += 15
    if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        score += 15
    return min(score, 100)
