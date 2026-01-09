"""
URL and Network Utilities - Pure functions for URL manipulation.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def parse_url(url: str) -> dict:
    """Parse a URL into its components."""
    if not url:
        return {'scheme': '', 'host': '', 'port': '', 'path': '', 'query': '', 'fragment': ''}
    
    result = {'scheme': '', 'host': '', 'port': '', 'path': '', 'query': '', 'fragment': ''}
    
    if '#' in url:
        url, result['fragment'] = url.split('#', 1)
    
    if '?' in url:
        url, result['query'] = url.split('?', 1)
    
    if '://' in url:
        result['scheme'], url = url.split('://', 1)
    
    if '/' in url:
        host_part, result['path'] = url.split('/', 1)
        result['path'] = '/' + result['path']
    else:
        host_part = url
    
    if ':' in host_part:
        result['host'], result['port'] = host_part.rsplit(':', 1)
    else:
        result['host'] = host_part
    
    return result


def build_url(scheme: str, host: str, port: str, path: str, query: str, fragment: str) -> str:
    """Build a URL from components."""
    url = ""
    if scheme:
        url = scheme + "://"
    if host:
        url += host
    if port:
        url += ":" + port
    if path:
        if not path.startswith('/'):
            path = '/' + path
        url += path
    if query:
        url += "?" + query
    if fragment:
        url += "#" + fragment
    return url


def get_scheme(url: str) -> str:
    """Extract the scheme from a URL."""
    return parse_url(url)['scheme']


def get_host(url: str) -> str:
    """Extract the host from a URL."""
    return parse_url(url)['host']


def get_port(url: str) -> str:
    """Extract the port from a URL."""
    return parse_url(url)['port']


def get_path(url: str) -> str:
    """Extract the path from a URL."""
    return parse_url(url)['path']


def get_query_string(url: str) -> str:
    """Extract the query string from a URL."""
    return parse_url(url)['query']


def get_fragment(url: str) -> str:
    """Extract the fragment from a URL."""
    return parse_url(url)['fragment']


def parse_query_string(query: str) -> dict:
    """Parse a query string into a dictionary."""
    if not query:
        return {}
    if query.startswith('?'):
        query = query[1:]
    result = {}
    pairs = query.split('&')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            result[key] = value
        elif pair:
            result[pair] = ''
    return result


def build_query_string(params: dict) -> str:
    """Build a query string from a dictionary."""
    if not params:
        return ""
    pairs = [f"{k}={v}" for k, v in params.items()]
    return '&'.join(pairs)


def add_query_param(url: str, key: str, value: str) -> str:
    """Add a query parameter to a URL."""
    if not url or not key:
        return url
    parsed = parse_url(url)
    params = parse_query_string(parsed['query'])
    params[key] = value
    parsed['query'] = build_query_string(params)
    return build_url(
        parsed['scheme'], parsed['host'], parsed['port'],
        parsed['path'], parsed['query'], parsed['fragment']
    )


def remove_query_param(url: str, key: str) -> str:
    """Remove a query parameter from a URL."""
    if not url or not key:
        return url
    parsed = parse_url(url)
    params = parse_query_string(parsed['query'])
    params.pop(key, None)
    parsed['query'] = build_query_string(params)
    return build_url(
        parsed['scheme'], parsed['host'], parsed['port'],
        parsed['path'], parsed['query'], parsed['fragment']
    )


def get_query_param(url: str, key: str) -> str:
    """Get a query parameter value from a URL."""
    if not url or not key:
        return ""
    parsed = parse_url(url)
    params = parse_query_string(parsed['query'])
    return params.get(key, "")


def is_absolute_url(url: str) -> bool:
    """Check if a URL is absolute (has a scheme)."""
    if not url:
        return False
    return '://' in url


def is_relative_url(url: str) -> bool:
    """Check if a URL is relative."""
    return not is_absolute_url(url)


def is_secure_url(url: str) -> bool:
    """Check if a URL uses HTTPS."""
    return get_scheme(url).lower() == 'https'


def normalize_url(url: str) -> str:
    """Normalize a URL by lowercasing scheme and host."""
    if not url:
        return ""
    parsed = parse_url(url)
    parsed['scheme'] = parsed['scheme'].lower()
    parsed['host'] = parsed['host'].lower()
    return build_url(
        parsed['scheme'], parsed['host'], parsed['port'],
        parsed['path'], parsed['query'], parsed['fragment']
    )


def get_domain(url: str) -> str:
    """Extract the domain from a URL (host without subdomain)."""
    host = get_host(url)
    if not host:
        return ""
    parts = host.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return host


def get_subdomain(url: str) -> str:
    """Extract the subdomain from a URL."""
    host = get_host(url)
    if not host:
        return ""
    parts = host.split('.')
    if len(parts) > 2:
        return '.'.join(parts[:-2])
    return ""


def join_url_paths(base: str, path: str) -> str:
    """Join a base URL with a path."""
    if not base:
        return path
    if not path:
        return base
    if path.startswith('/'):
        parsed = parse_url(base)
        return build_url(
            parsed['scheme'], parsed['host'], parsed['port'],
            path, '', ''
        )
    if base.endswith('/'):
        return base + path
    return base + '/' + path


def strip_query_and_fragment(url: str) -> str:
    """Remove query string and fragment from a URL."""
    if not url:
        return ""
    parsed = parse_url(url)
    return build_url(
        parsed['scheme'], parsed['host'], parsed['port'],
        parsed['path'], '', ''
    )


def get_file_from_url(url: str) -> str:
    """Extract the filename from a URL path."""
    path = get_path(url)
    if not path:
        return ""
    if '/' in path:
        return path.rsplit('/', 1)[-1]
    return path


def change_url_scheme(url: str, new_scheme: str) -> str:
    """Change the scheme of a URL."""
    if not url or not new_scheme:
        return url
    parsed = parse_url(url)
    parsed['scheme'] = new_scheme
    return build_url(
        parsed['scheme'], parsed['host'], parsed['port'],
        parsed['path'], parsed['query'], parsed['fragment']
    )


def is_same_origin(url1: str, url2: str) -> bool:
    """Check if two URLs have the same origin (scheme, host, port)."""
    p1 = parse_url(url1)
    p2 = parse_url(url2)
    return (
        p1['scheme'].lower() == p2['scheme'].lower() and
        p1['host'].lower() == p2['host'].lower() and
        p1['port'] == p2['port']
    )


def extract_emails_from_text(text: str) -> list:
    """Extract email addresses from text."""
    if not text:
        return []
    import re
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def extract_urls_from_text(text: str) -> list:
    """Extract URLs from text."""
    if not text:
        return []
    import re
    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(pattern, text)
