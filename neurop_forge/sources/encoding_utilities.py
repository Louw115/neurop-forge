"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Encoding and Hashing Utilities - Pure functions for encoding and checksums.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import hashlib
import base64


def md5_hash(text: str) -> str:
    """Calculate the MD5 hash of a string."""
    if not text:
        return ""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def sha1_hash(text: str) -> str:
    """Calculate the SHA1 hash of a string."""
    if not text:
        return ""
    return hashlib.sha1(text.encode('utf-8')).hexdigest()


def sha256_hash(text: str) -> str:
    """Calculate the SHA256 hash of a string."""
    if not text:
        return ""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def sha512_hash(text: str) -> str:
    """Calculate the SHA512 hash of a string."""
    if not text:
        return ""
    return hashlib.sha512(text.encode('utf-8')).hexdigest()


def base64_encode(text: str) -> str:
    """Encode a string to base64."""
    if not text:
        return ""
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')


def base64_decode(encoded: str) -> str:
    """Decode a base64 string."""
    if not encoded:
        return ""
    try:
        return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
    except Exception:
        return ""


def base64_url_encode(text: str) -> str:
    """Encode a string to URL-safe base64."""
    if not text:
        return ""
    return base64.urlsafe_b64encode(text.encode('utf-8')).decode('utf-8')


def base64_url_decode(encoded: str) -> str:
    """Decode a URL-safe base64 string."""
    if not encoded:
        return ""
    try:
        return base64.urlsafe_b64decode(encoded.encode('utf-8')).decode('utf-8')
    except Exception:
        return ""


def hex_encode(text: str) -> str:
    """Encode a string to hexadecimal."""
    if not text:
        return ""
    return text.encode('utf-8').hex()


def hex_decode(encoded: str) -> str:
    """Decode a hexadecimal string."""
    if not encoded:
        return ""
    try:
        return bytes.fromhex(encoded).decode('utf-8')
    except Exception:
        return ""


def url_encode(text: str) -> str:
    """URL-encode a string."""
    if not text:
        return ""
    result = []
    for char in text:
        if char.isalnum() or char in '-_.~':
            result.append(char)
        elif char == ' ':
            result.append('+')
        else:
            encoded = char.encode('utf-8')
            for byte in encoded:
                result.append(f'%{byte:02X}')
    return ''.join(result)


def url_decode(encoded: str) -> str:
    """URL-decode a string."""
    if not encoded:
        return ""
    result = []
    i = 0
    while i < len(encoded):
        if encoded[i] == '%' and i + 2 < len(encoded):
            try:
                byte_val = int(encoded[i+1:i+3], 16)
                result.append(chr(byte_val))
                i += 3
            except ValueError:
                result.append(encoded[i])
                i += 1
        elif encoded[i] == '+':
            result.append(' ')
            i += 1
        else:
            result.append(encoded[i])
            i += 1
    return ''.join(result)


def rot13(text: str) -> str:
    """Apply ROT13 encoding/decoding to a string."""
    if not text:
        return ""
    result = []
    for char in text:
        if 'a' <= char <= 'z':
            result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
        elif 'A' <= char <= 'Z':
            result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
        else:
            result.append(char)
    return ''.join(result)


def caesar_cipher(text: str, shift: int) -> str:
    """Apply Caesar cipher to a string with a given shift."""
    if not text:
        return ""
    result = []
    shift = shift % 26
    for char in text:
        if 'a' <= char <= 'z':
            result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
        elif 'A' <= char <= 'Z':
            result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
        else:
            result.append(char)
    return ''.join(result)


def reverse_bits(byte_val: int) -> int:
    """Reverse the bits of a byte."""
    if byte_val < 0 or byte_val > 255:
        return 0
    result = 0
    for _ in range(8):
        result = (result << 1) | (byte_val & 1)
        byte_val >>= 1
    return result


def xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR data with a repeating key."""
    if not data or not key:
        return data or b''
    result = bytearray(len(data))
    key_len = len(key)
    for i, byte in enumerate(data):
        result[i] = byte ^ key[i % key_len]
    return bytes(result)


def simple_checksum(text: str) -> int:
    """Calculate a simple checksum (sum of byte values mod 256)."""
    if not text:
        return 0
    return sum(text.encode('utf-8')) % 256


def crc32(text: str) -> int:
    """Calculate the CRC32 checksum of a string."""
    import zlib
    if not text:
        return 0
    return zlib.crc32(text.encode('utf-8')) & 0xffffffff


def adler32(text: str) -> int:
    """Calculate the Adler32 checksum of a string."""
    import zlib
    if not text:
        return 1
    return zlib.adler32(text.encode('utf-8')) & 0xffffffff


def escape_html(text: str) -> str:
    """Escape HTML special characters in a string."""
    if not text:
        return ""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def unescape_html(text: str) -> str:
    """Unescape HTML entities in a string."""
    if not text:
        return ""
    return (text
            .replace('&amp;', '&')
            .replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&quot;', '"')
            .replace('&#39;', "'"))


def escape_json_string(text: str) -> str:
    """Escape special characters for JSON string."""
    if not text:
        return ""
    return (text
            .replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '\\r')
            .replace('\t', '\\t'))


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in a string to single spaces."""
    if not text:
        return ""
    return ' '.join(text.split())


def slugify(text: str) -> str:
    """Convert a string to a URL-friendly slug."""
    if not text:
        return ""
    result = []
    for char in text.lower():
        if char.isalnum():
            result.append(char)
        elif char in ' -_':
            if result and result[-1] != '-':
                result.append('-')
    slug = ''.join(result)
    return slug.strip('-')
