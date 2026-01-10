"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Protocol Utilities - Pure functions for protocol handling.
All functions are pure, deterministic, and atomic.
"""

import re


def parse_uri(uri: str) -> dict:
    """Parse URI into components."""
    pattern = r'^(?:([a-z][a-z0-9+.-]*):)?(?://([^/?#]*))?([^?#]*)(?:\?([^#]*))?(?:#(.*))?$'
    match = re.match(pattern, uri, re.IGNORECASE)
    if not match:
        return None
    scheme, authority, path, query, fragment = match.groups()
    host = None
    port = None
    userinfo = None
    if authority:
        auth_match = re.match(r'^(?:([^@]*)@)?([^:]*)?(?::(\d+))?$', authority)
        if auth_match:
            userinfo, host, port = auth_match.groups()
            port = int(port) if port else None
    return {
        "scheme": scheme,
        "authority": authority,
        "userinfo": userinfo,
        "host": host,
        "port": port,
        "path": path,
        "query": query,
        "fragment": fragment
    }


def build_uri(components: dict) -> str:
    """Build URI from components."""
    result = ""
    if components.get("scheme"):
        result += components["scheme"] + ":"
    if components.get("host"):
        result += "//"
        if components.get("userinfo"):
            result += components["userinfo"] + "@"
        result += components["host"]
        if components.get("port"):
            result += ":" + str(components["port"])
    if components.get("path"):
        result += components["path"]
    if components.get("query"):
        result += "?" + components["query"]
    if components.get("fragment"):
        result += "#" + components["fragment"]
    return result


def normalize_path(path: str) -> str:
    """Normalize URI path."""
    segments = path.split("/")
    result = []
    for seg in segments:
        if seg == "..":
            if result and result[-1] != "":
                result.pop()
        elif seg != ".":
            result.append(seg)
    return "/".join(result)


def get_default_port(scheme: str) -> int:
    """Get default port for scheme."""
    ports = {
        "http": 80,
        "https": 443,
        "ftp": 21,
        "ssh": 22,
        "telnet": 23,
        "smtp": 25,
        "dns": 53,
        "pop3": 110,
        "imap": 143,
        "ldap": 389,
        "smtps": 465,
        "imaps": 993,
        "pop3s": 995,
        "mysql": 3306,
        "postgresql": 5432,
        "mongodb": 27017,
        "redis": 6379
    }
    return ports.get(scheme.lower(), 0)


def is_secure_scheme(scheme: str) -> bool:
    """Check if scheme is secure."""
    return scheme.lower() in ["https", "wss", "ftps", "sftp", "ssh", "imaps", "pop3s", "smtps"]


def parse_query_string(query: str) -> dict:
    """Parse query string into dictionary."""
    if not query:
        return {}
    result = {}
    for pair in query.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            result[key] = value
        else:
            result[pair] = ""
    return result


def build_query_string(params: dict) -> str:
    """Build query string from dictionary."""
    return "&".join(f"{k}={v}" for k, v in params.items())


def parse_data_uri(uri: str) -> dict:
    """Parse data URI."""
    match = re.match(r'^data:([^;,]*)?(?:;(base64))?,(.*)$', uri)
    if not match:
        return None
    mime_type, encoding, data = match.groups()
    return {
        "mime_type": mime_type or "text/plain",
        "encoding": encoding,
        "data": data
    }


def parse_mailto(uri: str) -> dict:
    """Parse mailto URI."""
    if not uri.lower().startswith("mailto:"):
        return None
    rest = uri[7:]
    email, query = (rest.split("?", 1) + [None])[:2]
    result = {"to": email, "cc": None, "bcc": None, "subject": None, "body": None}
    if query:
        params = parse_query_string(query)
        result.update(params)
    return result


def parse_tel(uri: str) -> dict:
    """Parse tel URI."""
    if not uri.lower().startswith("tel:"):
        return None
    number = uri[4:]
    ext = None
    if ";ext=" in number:
        number, ext = number.split(";ext=", 1)
    return {"number": number, "extension": ext}


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


def parse_authorization(header: str) -> dict:
    """Parse Authorization header."""
    parts = header.split(" ", 1)
    if len(parts) == 1:
        return {"scheme": parts[0], "credentials": ""}
    return {"scheme": parts[0], "credentials": parts[1]}


def parse_cookie(header: str) -> dict:
    """Parse Cookie header."""
    cookies = {}
    for pair in header.split(";"):
        pair = pair.strip()
        if "=" in pair:
            key, value = pair.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


def build_cookie(name: str, value: str, options: dict) -> str:
    """Build Set-Cookie header value."""
    result = f"{name}={value}"
    if options.get("expires"):
        result += f"; Expires={options['expires']}"
    if options.get("max_age") is not None:
        result += f"; Max-Age={options['max_age']}"
    if options.get("domain"):
        result += f"; Domain={options['domain']}"
    if options.get("path"):
        result += f"; Path={options['path']}"
    if options.get("secure"):
        result += "; Secure"
    if options.get("httponly"):
        result += "; HttpOnly"
    if options.get("samesite"):
        result += f"; SameSite={options['samesite']}"
    return result


def parse_accept(header: str) -> list:
    """Parse Accept header into sorted list."""
    types = []
    for part in header.split(","):
        part = part.strip()
        quality = 1.0
        if ";q=" in part:
            type_part, q = part.split(";q=", 1)
            part = type_part.strip()
            quality = float(q.strip())
        types.append({"type": part, "quality": quality})
    return sorted(types, key=lambda x: -x["quality"])


def format_range_header(start: int, end: int, total: int) -> str:
    """Format Content-Range header."""
    return f"bytes {start}-{end}/{total}"


def parse_range(header: str) -> dict:
    """Parse Range header."""
    if not header.startswith("bytes="):
        return None
    ranges = []
    for r in header[6:].split(","):
        if "-" in r:
            start, end = r.split("-", 1)
            ranges.append({
                "start": int(start) if start else None,
                "end": int(end) if end else None
            })
    return {"unit": "bytes", "ranges": ranges}
