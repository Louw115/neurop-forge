"""
Authentication Pattern Utilities - Pure functions for auth patterns.
All functions are pure, deterministic, and atomic.
"""

def extract_bearer_token(auth_header: str) -> str:
    """Extract bearer token from Authorization header."""
    if auth_header and auth_header.lower().startswith('bearer '):
        return auth_header[7:].strip()
    return ""


def extract_basic_credentials(auth_header: str) -> tuple:
    """Extract username and password from Basic auth header."""
    import base64
    if not auth_header or not auth_header.lower().startswith('basic '):
        return ("", "")
    try:
        encoded = auth_header[6:].strip()
        decoded = base64.b64decode(encoded).decode('utf-8')
        if ':' in decoded:
            username, password = decoded.split(':', 1)
            return (username, password)
    except Exception:
        pass
    return ("", "")


def build_basic_auth_header(username: str, password: str) -> str:
    """Build a Basic Authorization header value."""
    import base64
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def build_bearer_auth_header(token: str) -> str:
    """Build a Bearer Authorization header value."""
    return f"Bearer {token}"


def parse_jwt_header(token: str) -> dict:
    """Parse the header portion of a JWT (without verification)."""
    import base64
    import json
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return {}
        header = parts[0]
        padding = 4 - len(header) % 4
        if padding != 4:
            header += '=' * padding
        decoded = base64.urlsafe_b64decode(header)
        return json.loads(decoded)
    except Exception:
        return {}


def parse_jwt_payload(token: str) -> dict:
    """Parse the payload portion of a JWT (without verification)."""
    import base64
    import json
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return {}
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception:
        return {}


def extract_jwt_claim(token: str, claim: str) -> str:
    """Extract a specific claim from a JWT payload."""
    payload = parse_jwt_payload(token)
    return str(payload.get(claim, ""))


def is_jwt_expired_by_timestamp(token: str, current_timestamp: int) -> bool:
    """Check if a JWT is expired based on exp claim."""
    payload = parse_jwt_payload(token)
    exp = payload.get("exp")
    if exp is None:
        return False
    return current_timestamp > int(exp)


def get_jwt_expiry_timestamp(token: str) -> int:
    """Get the expiry timestamp from a JWT."""
    payload = parse_jwt_payload(token)
    return int(payload.get("exp", 0))


def get_jwt_issued_at(token: str) -> int:
    """Get the issued-at timestamp from a JWT."""
    payload = parse_jwt_payload(token)
    return int(payload.get("iat", 0))


def get_jwt_subject(token: str) -> str:
    """Get the subject (sub) from a JWT."""
    return extract_jwt_claim(token, "sub")


def get_jwt_issuer(token: str) -> str:
    """Get the issuer (iss) from a JWT."""
    return extract_jwt_claim(token, "iss")


def get_jwt_audience(token: str) -> list:
    """Get the audience (aud) from a JWT."""
    payload = parse_jwt_payload(token)
    aud = payload.get("aud", [])
    if isinstance(aud, str):
        return [aud]
    return list(aud)


def validate_jwt_audience(token: str, expected_audience: str) -> bool:
    """Validate that JWT audience matches expected value."""
    audiences = get_jwt_audience(token)
    return expected_audience in audiences


def validate_jwt_issuer(token: str, expected_issuer: str) -> bool:
    """Validate that JWT issuer matches expected value."""
    return get_jwt_issuer(token) == expected_issuer


def build_jwt_payload(sub: str, iss: str, aud: str, exp: int, iat: int, claims: dict) -> dict:
    """Build a JWT payload dictionary."""
    payload = {
        "sub": sub,
        "iss": iss,
        "aud": aud,
        "exp": exp,
        "iat": iat,
    }
    payload.update(claims)
    return payload


def calculate_token_expiry(current_timestamp: int, duration_seconds: int) -> int:
    """Calculate token expiry timestamp."""
    return current_timestamp + duration_seconds


def is_token_refresh_needed(token: str, current_timestamp: int, buffer_seconds: int) -> bool:
    """Check if token needs refresh (expires within buffer period)."""
    exp = get_jwt_expiry_timestamp(token)
    if exp == 0:
        return False
    return (exp - current_timestamp) <= buffer_seconds


def generate_session_id(prefix: str, timestamp: str, random_part: str) -> str:
    """Generate a session ID."""
    import hashlib
    combined = f"{prefix}:{timestamp}:{random_part}"
    return hashlib.sha256(combined.encode()).hexdigest()


def build_session_cookie(name: str, value: str, max_age: int, secure: bool, http_only: bool, same_site: str, path: str, domain: str) -> str:
    """Build a Set-Cookie header value for a session."""
    parts = [f"{name}={value}"]
    if max_age > 0:
        parts.append(f"Max-Age={max_age}")
    if path:
        parts.append(f"Path={path}")
    if domain:
        parts.append(f"Domain={domain}")
    if secure:
        parts.append("Secure")
    if http_only:
        parts.append("HttpOnly")
    if same_site:
        parts.append(f"SameSite={same_site}")
    return "; ".join(parts)


def parse_cookie_header(cookie_header: str) -> dict:
    """Parse a Cookie header into a dictionary."""
    cookies = {}
    if not cookie_header:
        return cookies
    for pair in cookie_header.split(';'):
        pair = pair.strip()
        if '=' in pair:
            key, value = pair.split('=', 1)
            cookies[key.strip()] = value.strip()
    return cookies


def extract_session_from_cookies(cookies: dict, session_name: str) -> str:
    """Extract session ID from cookies."""
    return cookies.get(session_name, "")


def build_oauth_authorize_url(base_url: str, client_id: str, redirect_uri: str, scope: str, state: str, response_type: str) -> str:
    """Build an OAuth authorization URL."""
    from urllib.parse import urlencode
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": response_type,
        "scope": scope,
        "state": state,
    }
    return f"{base_url}?{urlencode(params)}"


def build_oauth_token_request(grant_type: str, client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict:
    """Build OAuth token request parameters."""
    return {
        "grant_type": grant_type,
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
    }


def build_oauth_refresh_request(client_id: str, client_secret: str, refresh_token: str) -> dict:
    """Build OAuth token refresh request parameters."""
    return {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }


def parse_oauth_scopes(scope_string: str) -> list:
    """Parse OAuth scope string into list."""
    if not scope_string:
        return []
    return scope_string.split()


def build_oauth_scope_string(scopes: list) -> str:
    """Build OAuth scope string from list."""
    return " ".join(scopes)


def has_required_scopes(granted_scopes: list, required_scopes: list) -> bool:
    """Check if granted scopes include all required scopes."""
    granted_set = set(granted_scopes)
    required_set = set(required_scopes)
    return required_set.issubset(granted_set)


def generate_pkce_verifier_hash(verifier: str) -> str:
    """Generate PKCE code challenge from verifier (S256 method)."""
    import hashlib
    import base64
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
    return challenge


def build_pkce_authorize_params(client_id: str, redirect_uri: str, scope: str, state: str, code_challenge: str) -> dict:
    """Build OAuth PKCE authorization parameters."""
    return {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }


def extract_api_key_from_header(headers: dict, header_name: str) -> str:
    """Extract API key from a custom header."""
    return headers.get(header_name, "")


def extract_api_key_from_query(query_params: dict, param_name: str) -> str:
    """Extract API key from query parameters."""
    return query_params.get(param_name, "")


def mask_api_key(api_key: str, visible_chars: int) -> str:
    """Mask an API key for logging (show first N chars)."""
    if len(api_key) <= visible_chars:
        return "*" * len(api_key)
    return api_key[:visible_chars] + "*" * (len(api_key) - visible_chars)


def generate_api_key_prefix(service_name: str) -> str:
    """Generate a prefix for API keys."""
    return f"{service_name.lower().replace(' ', '_')}_"


def validate_api_key_format(api_key: str, expected_prefix: str, min_length: int) -> bool:
    """Validate API key format."""
    if not api_key:
        return False
    if expected_prefix and not api_key.startswith(expected_prefix):
        return False
    return len(api_key) >= min_length


def build_digest_auth_header(username: str, realm: str, nonce: str, uri: str, response: str, algorithm: str) -> str:
    """Build a Digest Authorization header value."""
    return f'Digest username="{username}", realm="{realm}", nonce="{nonce}", uri="{uri}", response="{response}", algorithm={algorithm}'


def generate_nonce(timestamp: str, secret: str) -> str:
    """Generate a nonce for digest authentication."""
    import hashlib
    combined = f"{timestamp}:{secret}"
    return hashlib.md5(combined.encode()).hexdigest()


def calculate_password_hash(password: str, salt: str, algorithm: str) -> str:
    """Calculate password hash with salt."""
    import hashlib
    combined = f"{salt}{password}"
    if algorithm == "sha256":
        return hashlib.sha256(combined.encode()).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(combined.encode()).hexdigest()
    return hashlib.sha256(combined.encode()).hexdigest()


def is_strong_password(password: str, min_length: int, require_upper: bool, require_lower: bool, require_digit: bool, require_special: bool) -> dict:
    """Check if a password meets strength requirements."""
    issues = []
    if len(password) < min_length:
        issues.append(f"Must be at least {min_length} characters")
    if require_upper and not any(c.isupper() for c in password):
        issues.append("Must contain uppercase letter")
    if require_lower and not any(c.islower() for c in password):
        issues.append("Must contain lowercase letter")
    if require_digit and not any(c.isdigit() for c in password):
        issues.append("Must contain digit")
    if require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        issues.append("Must contain special character")
    return {"valid": len(issues) == 0, "issues": issues}


def calculate_password_strength_score(password: str) -> int:
    """Calculate password strength score (0-100)."""
    score = 0
    if len(password) >= 8:
        score += 20
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10
    if any(c.isupper() for c in password):
        score += 15
    if any(c.islower() for c in password):
        score += 15
    if any(c.isdigit() for c in password):
        score += 15
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 15
    return min(score, 100)


def build_mfa_secret_uri(account: str, issuer: str, secret: str, algorithm: str, digits: int, period: int) -> str:
    """Build an OTP provisioning URI for MFA."""
    from urllib.parse import quote
    label = f"{quote(issuer)}:{quote(account)}"
    params = f"secret={secret}&issuer={quote(issuer)}&algorithm={algorithm}&digits={digits}&period={period}"
    return f"otpauth://totp/{label}?{params}"


def validate_mfa_code_format(code: str, expected_length: int) -> bool:
    """Validate MFA code format (numeric, correct length)."""
    return code.isdigit() and len(code) == expected_length
