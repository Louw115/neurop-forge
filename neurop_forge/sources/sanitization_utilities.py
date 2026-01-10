"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Sanitization Utilities - Pure functions for input sanitization.
All functions are pure, deterministic, and atomic.
"""

import re


def sanitize_string(text: str, allowed_pattern: str) -> str:
    """Sanitize string to only allowed characters."""
    return re.sub(f"[^{allowed_pattern}]", "", text)


def sanitize_alphanumeric(text: str) -> str:
    """Keep only alphanumeric characters."""
    return re.sub(r"[^a-zA-Z0-9]", "", text)


def sanitize_alpha(text: str) -> str:
    """Keep only alphabetic characters."""
    return re.sub(r"[^a-zA-Z]", "", text)


def sanitize_numeric(text: str) -> str:
    """Keep only numeric characters."""
    return re.sub(r"[^0-9]", "", text)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename removing unsafe characters."""
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    filename = filename.strip(". ")
    return filename[:255] if filename else "unnamed"


def sanitize_path(path: str) -> str:
    """Sanitize path removing directory traversal."""
    path = path.replace("\\", "/")
    path = re.sub(r"\.\./", "", path)
    path = re.sub(r"//+", "/", path)
    return path.strip("/")


def sanitize_url(url: str) -> str:
    """Sanitize URL removing dangerous schemes."""
    url = url.strip()
    if re.match(r"^javascript:", url, re.IGNORECASE):
        return ""
    if re.match(r"^data:", url, re.IGNORECASE):
        return ""
    if re.match(r"^vbscript:", url, re.IGNORECASE):
        return ""
    return url


def sanitize_html(html: str) -> str:
    """Escape HTML special characters."""
    return (html
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;"))


def strip_html_tags(html: str) -> str:
    """Remove all HTML tags."""
    return re.sub(r"<[^>]+>", "", html)


def sanitize_sql_identifier(identifier: str) -> str:
    """Sanitize SQL identifier."""
    identifier = re.sub(r"[^a-zA-Z0-9_]", "", identifier)
    if identifier and identifier[0].isdigit():
        identifier = "_" + identifier
    return identifier[:64]


def sanitize_email(email: str) -> str:
    """Sanitize email address."""
    email = email.strip().lower()
    email = re.sub(r"\s+", "", email)
    return email


def sanitize_phone(phone: str) -> str:
    """Sanitize phone number to digits only."""
    return re.sub(r"[^0-9+]", "", phone)


def sanitize_whitespace(text: str) -> str:
    """Normalize whitespace to single spaces."""
    return " ".join(text.split())


def trim_to_length(text: str, max_length: int) -> str:
    """Trim text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length]


def remove_null_bytes(text: str) -> str:
    """Remove null bytes from string."""
    return text.replace("\x00", "")


def remove_control_characters(text: str) -> str:
    """Remove control characters."""
    return "".join(c for c in text if ord(c) >= 32 or c in "\n\r\t")


def sanitize_json_string(text: str) -> str:
    """Sanitize string for JSON embedding."""
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "\\r")
    text = text.replace("\t", "\\t")
    return text


def sanitize_regex(text: str) -> str:
    """Escape regex special characters."""
    return re.escape(text)


def sanitize_shell_argument(arg: str) -> str:
    """Sanitize shell argument."""
    return "'" + arg.replace("'", "'\\''") + "'"


def sanitize_ldap(text: str) -> str:
    """Sanitize for LDAP filter."""
    text = text.replace("\\", "\\5c")
    text = text.replace("*", "\\2a")
    text = text.replace("(", "\\28")
    text = text.replace(")", "\\29")
    text = text.replace("\x00", "\\00")
    return text


def sanitize_xpath(text: str) -> str:
    """Sanitize for XPath."""
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'
    return "concat('" + text.replace("'", "',\"'\",'" ) + "')"


def normalize_newlines(text: str) -> str:
    """Normalize line endings to LF."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def remove_bom(text: str) -> str:
    """Remove UTF-8 BOM."""
    if text.startswith("\ufeff"):
        return text[1:]
    return text


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def sanitize_username(username: str, min_length: int, max_length: int) -> dict:
    """Sanitize and validate username."""
    username = username.strip().lower()
    username = re.sub(r"[^a-z0-9_-]", "", username)
    if len(username) < min_length:
        return {"valid": False, "value": username, "error": "too_short"}
    if len(username) > max_length:
        username = username[:max_length]
    return {"valid": True, "value": username, "error": None}
