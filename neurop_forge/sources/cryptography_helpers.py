"""
Cryptography Helpers - Pure functions for cryptographic validation and patterns.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

Note: These are validation and transformation helpers, not actual cryptographic
implementations. They work with tokens, keys, and signatures as data.

License: MIT
"""

import re
import hashlib
import hmac
import base64


def is_valid_hex_string(value: str) -> bool:
    """Check if a string is valid hexadecimal."""
    if not value:
        return False
    try:
        int(value, 16)
        return len(value) % 2 == 0
    except ValueError:
        return False


def is_valid_base64(value: str) -> bool:
    """Check if a string is valid base64."""
    if not value:
        return False
    pattern = r'^[A-Za-z0-9+/]*={0,2}$'
    if not re.match(pattern, value):
        return False
    return len(value) % 4 == 0


def is_valid_base64url(value: str) -> bool:
    """Check if a string is valid base64url (URL-safe base64)."""
    if not value:
        return False
    pattern = r'^[A-Za-z0-9_-]*={0,2}$'
    return bool(re.match(pattern, value))


def hex_to_bytes(hex_string: str) -> bytes:
    """Convert a hex string to bytes."""
    if not is_valid_hex_string(hex_string):
        return b''
    return bytes.fromhex(hex_string)


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to a hex string."""
    return data.hex()


def base64_to_bytes(b64_string: str) -> bytes:
    """Decode base64 string to bytes."""
    if not b64_string:
        return b''
    try:
        return base64.b64decode(b64_string)
    except Exception:
        return b''


def bytes_to_base64(data: bytes) -> str:
    """Encode bytes to base64 string."""
    return base64.b64encode(data).decode('ascii')


def base64url_to_bytes(b64url_string: str) -> bytes:
    """Decode base64url string to bytes."""
    if not b64url_string:
        return b''
    padded = b64url_string + '=' * (4 - len(b64url_string) % 4)
    padded = padded.replace('-', '+').replace('_', '/')
    try:
        return base64.b64decode(padded)
    except Exception:
        return b''


def bytes_to_base64url(data: bytes) -> str:
    """Encode bytes to base64url string."""
    encoded = base64.b64encode(data).decode('ascii')
    return encoded.replace('+', '-').replace('/', '_').rstrip('=')


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


def compute_sha256_base64(data: bytes) -> str:
    """Compute SHA-256 hash of bytes and return as base64."""
    return base64.b64encode(hashlib.sha256(data).digest()).decode('ascii')


def compute_sha512(data: bytes) -> str:
    """Compute SHA-512 hash of bytes."""
    return hashlib.sha512(data).hexdigest()


def compute_md5(data: bytes) -> str:
    """Compute MD5 hash of bytes (for checksums, not security)."""
    return hashlib.md5(data).hexdigest()


def compute_hmac_sha256(key: bytes, message: bytes) -> str:
    """Compute HMAC-SHA256 of a message."""
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def compute_hmac_sha256_base64(key: bytes, message: bytes) -> str:
    """Compute HMAC-SHA256 of a message and return as base64."""
    digest = hmac.new(key, message, hashlib.sha256).digest()
    return base64.b64encode(digest).decode('ascii')


def verify_hmac_sha256(key: bytes, message: bytes, expected_hex: str) -> bool:
    """Verify an HMAC-SHA256 signature."""
    computed = compute_hmac_sha256(key, message)
    return hmac.compare_digest(computed, expected_hex.lower())


def is_valid_jwt_format(token: str) -> bool:
    """Check if a string has valid JWT format (3 base64url parts)."""
    if not token:
        return False
    parts = token.split('.')
    if len(parts) != 3:
        return False
    return all(is_valid_base64url(part) for part in parts)


def decode_jwt_header(token: str) -> dict:
    """Decode the header portion of a JWT (without verification)."""
    import json
    if not is_valid_jwt_format(token):
        return {}
    header_b64 = token.split('.')[0]
    try:
        header_bytes = base64url_to_bytes(header_b64)
        return json.loads(header_bytes.decode('utf-8'))
    except Exception:
        return {}


def decode_jwt_payload(token: str) -> dict:
    """Decode the payload portion of a JWT (without verification)."""
    import json
    if not is_valid_jwt_format(token):
        return {}
    payload_b64 = token.split('.')[1]
    try:
        payload_bytes = base64url_to_bytes(payload_b64)
        return json.loads(payload_bytes.decode('utf-8'))
    except Exception:
        return {}


def get_jwt_algorithm(token: str) -> str:
    """Extract the algorithm from a JWT header."""
    header = decode_jwt_header(token)
    return header.get('alg', '')


def get_jwt_expiration(token: str) -> int:
    """Extract the expiration timestamp from a JWT payload."""
    payload = decode_jwt_payload(token)
    return payload.get('exp', 0)


def get_jwt_issued_at(token: str) -> int:
    """Extract the issued-at timestamp from a JWT payload."""
    payload = decode_jwt_payload(token)
    return payload.get('iat', 0)


def get_jwt_subject(token: str) -> str:
    """Extract the subject claim from a JWT payload."""
    payload = decode_jwt_payload(token)
    return payload.get('sub', '')


def get_jwt_issuer(token: str) -> str:
    """Extract the issuer claim from a JWT payload."""
    payload = decode_jwt_payload(token)
    return payload.get('iss', '')


def is_jwt_expired_at(token: str, current_timestamp: int) -> bool:
    """Check if a JWT is expired at a given timestamp."""
    exp = get_jwt_expiration(token)
    if exp == 0:
        return False
    return current_timestamp >= exp


def is_valid_api_key_format(key: str, prefix: str, length: int) -> bool:
    """Check if a string matches expected API key format."""
    if not key:
        return False
    if prefix and not key.startswith(prefix):
        return False
    key_part = key[len(prefix):] if prefix else key
    return len(key_part) == length and key_part.isalnum()


def mask_api_key(key: str, visible_chars: int) -> str:
    """Mask an API key showing only first N characters."""
    if not key or visible_chars <= 0:
        return '*' * 8
    if len(key) <= visible_chars:
        return key
    return key[:visible_chars] + '*' * (len(key) - visible_chars)


def is_valid_uuid_v4(value: str) -> bool:
    """Check if a string is a valid UUID v4."""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    return bool(re.match(pattern, value.lower()))


def is_valid_sha256_hash(value: str) -> bool:
    """Check if a string is a valid SHA-256 hash."""
    if len(value) != 64:
        return False
    return is_valid_hex_string(value)


def is_valid_sha512_hash(value: str) -> bool:
    """Check if a string is a valid SHA-512 hash."""
    if len(value) != 128:
        return False
    return is_valid_hex_string(value)


def is_valid_md5_hash(value: str) -> bool:
    """Check if a string is a valid MD5 hash."""
    if len(value) != 32:
        return False
    return is_valid_hex_string(value)


def extract_bearer_token(header: str) -> str:
    """Extract the token from a Bearer authorization header."""
    if not header:
        return ""
    if header.startswith('Bearer '):
        return header[7:]
    return ""


def constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time to prevent timing attacks."""
    return hmac.compare_digest(a.encode(), b.encode())


def derive_key_id(key: bytes) -> str:
    """Derive a short identifier from a key (first 8 chars of SHA-256)."""
    full_hash = compute_sha256(key)
    return full_hash[:8]


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte sequences of equal length."""
    if len(a) != len(b):
        return b''
    return bytes(x ^ y for x, y in zip(a, b))


def pad_pkcs7(data: bytes, block_size: int) -> bytes:
    """Apply PKCS7 padding to data."""
    if block_size <= 0 or block_size > 255:
        return data
    padding_length = block_size - (len(data) % block_size)
    return data + bytes([padding_length] * padding_length)


def unpad_pkcs7(data: bytes) -> bytes:
    """Remove PKCS7 padding from data."""
    if not data:
        return b''
    padding_length = data[-1]
    if padding_length == 0 or padding_length > len(data):
        return data
    if all(b == padding_length for b in data[-padding_length:]):
        return data[:-padding_length]
    return data


def is_valid_pem_format(pem: str) -> bool:
    """Check if a string appears to be valid PEM format."""
    if not pem:
        return False
    lines = pem.strip().split('\n')
    if len(lines) < 3:
        return False
    has_begin = lines[0].startswith('-----BEGIN ')
    has_end = lines[-1].startswith('-----END ')
    return has_begin and has_end


def get_pem_type(pem: str) -> str:
    """Extract the type from a PEM header."""
    if not pem:
        return ""
    first_line = pem.strip().split('\n')[0]
    if first_line.startswith('-----BEGIN ') and first_line.endswith('-----'):
        return first_line[11:-5]
    return ""


def is_valid_fingerprint(value: str, algorithm: str) -> bool:
    """Check if a string is a valid key fingerprint."""
    value = value.replace(':', '').replace(' ', '').lower()
    expected_lengths = {
        'md5': 32,
        'sha1': 40,
        'sha256': 64,
    }
    expected = expected_lengths.get(algorithm.lower(), 0)
    if expected == 0:
        return False
    return len(value) == expected and is_valid_hex_string(value)


def format_fingerprint(hex_value: str, separator: str) -> str:
    """Format a hex fingerprint with separators."""
    hex_value = hex_value.lower().replace(':', '').replace(' ', '')
    if not is_valid_hex_string(hex_value):
        return ""
    pairs = [hex_value[i:i+2] for i in range(0, len(hex_value), 2)]
    return separator.join(pairs)


def entropy_bits(password: str) -> float:
    """Estimate entropy bits of a password."""
    import math
    if not password:
        return 0.0
    char_sets = 0
    if any(c.islower() for c in password):
        char_sets += 26
    if any(c.isupper() for c in password):
        char_sets += 26
    if any(c.isdigit() for c in password):
        char_sets += 10
    if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        char_sets += 32
    if char_sets == 0:
        return 0.0
    return len(password) * math.log2(char_sets)
