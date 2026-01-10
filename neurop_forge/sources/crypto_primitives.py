"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Crypto Primitives - Pure functions for cryptographic operations.
All functions are pure, deterministic, and atomic.
"""

import hashlib
import hmac
import base64


def md5_hash(data: bytes) -> str:
    """Calculate MD5 hash."""
    return hashlib.md5(data).hexdigest()


def sha1_hash(data: bytes) -> str:
    """Calculate SHA-1 hash."""
    return hashlib.sha1(data).hexdigest()


def sha256_hash(data: bytes) -> str:
    """Calculate SHA-256 hash."""
    return hashlib.sha256(data).hexdigest()


def sha384_hash(data: bytes) -> str:
    """Calculate SHA-384 hash."""
    return hashlib.sha384(data).hexdigest()


def sha512_hash(data: bytes) -> str:
    """Calculate SHA-512 hash."""
    return hashlib.sha512(data).hexdigest()


def sha3_256_hash(data: bytes) -> str:
    """Calculate SHA3-256 hash."""
    return hashlib.sha3_256(data).hexdigest()


def sha3_512_hash(data: bytes) -> str:
    """Calculate SHA3-512 hash."""
    return hashlib.sha3_512(data).hexdigest()


def blake2b_hash(data: bytes, digest_size: int) -> str:
    """Calculate BLAKE2b hash."""
    return hashlib.blake2b(data, digest_size=digest_size).hexdigest()


def blake2s_hash(data: bytes, digest_size: int) -> str:
    """Calculate BLAKE2s hash."""
    return hashlib.blake2s(data, digest_size=digest_size).hexdigest()


def hmac_md5(key: bytes, message: bytes) -> str:
    """Calculate HMAC-MD5."""
    return hmac.new(key, message, hashlib.md5).hexdigest()


def hmac_sha1(key: bytes, message: bytes) -> str:
    """Calculate HMAC-SHA1."""
    return hmac.new(key, message, hashlib.sha1).hexdigest()


def hmac_sha256(key: bytes, message: bytes) -> str:
    """Calculate HMAC-SHA256."""
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def hmac_sha512(key: bytes, message: bytes) -> str:
    """Calculate HMAC-SHA512."""
    return hmac.new(key, message, hashlib.sha512).hexdigest()


def verify_hmac(key: bytes, message: bytes, signature: str, algorithm: str) -> bool:
    """Verify HMAC signature."""
    if algorithm == "md5":
        expected = hmac_md5(key, message)
    elif algorithm == "sha1":
        expected = hmac_sha1(key, message)
    elif algorithm == "sha256":
        expected = hmac_sha256(key, message)
    elif algorithm == "sha512":
        expected = hmac_sha512(key, message)
    else:
        return False
    return hmac.compare_digest(expected, signature)


def base64_encode(data: bytes) -> str:
    """Encode bytes to base64."""
    return base64.b64encode(data).decode("ascii")


def base64_decode(encoded: str) -> bytes:
    """Decode base64 to bytes."""
    return base64.b64decode(encoded)


def base64_url_encode(data: bytes) -> str:
    """URL-safe base64 encode."""
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def base64_url_decode(encoded: str) -> bytes:
    """URL-safe base64 decode."""
    padding = 4 - len(encoded) % 4
    if padding != 4:
        encoded += "=" * padding
    return base64.urlsafe_b64decode(encoded)


def hex_encode(data: bytes) -> str:
    """Encode bytes to hex string."""
    return data.hex()


def hex_decode(encoded: str) -> bytes:
    """Decode hex string to bytes."""
    return bytes.fromhex(encoded)


def pbkdf2_derive(password: str, salt: bytes, iterations: int, key_length: int) -> bytes:
    """Derive key using PBKDF2."""
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations, key_length)


def create_password_hash(password: str, salt: bytes, iterations: int) -> dict:
    """Create password hash with salt."""
    key = pbkdf2_derive(password, salt, iterations, 32)
    return {
        "hash": hex_encode(key),
        "salt": hex_encode(salt),
        "iterations": iterations
    }


def verify_password_hash(password: str, stored_hash: str, salt_hex: str, iterations: int) -> bool:
    """Verify password against stored hash."""
    salt = hex_decode(salt_hex)
    key = pbkdf2_derive(password, salt, iterations, 32)
    return hmac.compare_digest(hex_encode(key), stored_hash)


def constant_time_compare(a: bytes, b: bytes) -> bool:
    """Constant-time comparison."""
    return hmac.compare_digest(a, b)


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte sequences."""
    return bytes(x ^ y for x, y in zip(a, b))


def hash_file_content(content: bytes, algorithm: str) -> str:
    """Hash file content with specified algorithm."""
    if algorithm == "md5":
        return md5_hash(content)
    elif algorithm == "sha1":
        return sha1_hash(content)
    elif algorithm == "sha256":
        return sha256_hash(content)
    elif algorithm == "sha512":
        return sha512_hash(content)
    return ""


def create_checksum(data: bytes, algorithm: str) -> str:
    """Create checksum for data."""
    return hash_file_content(data, algorithm)


def verify_checksum(data: bytes, expected: str, algorithm: str) -> bool:
    """Verify data checksum."""
    calculated = create_checksum(data, algorithm)
    return hmac.compare_digest(calculated.lower(), expected.lower())


def derive_key_from_password(password: str, salt: bytes, length: int) -> bytes:
    """Derive encryption key from password."""
    return pbkdf2_derive(password, salt, 100000, length)


def create_deterministic_id(data: str, namespace: str) -> str:
    """Create deterministic ID from data."""
    combined = f"{namespace}:{data}".encode()
    return sha256_hash(combined)[:32]


def hash_chain(data: bytes, iterations: int, algorithm: str) -> str:
    """Apply hash function iteratively."""
    result = data
    for _ in range(iterations):
        if algorithm == "sha256":
            result = hashlib.sha256(result).digest()
        elif algorithm == "sha512":
            result = hashlib.sha512(result).digest()
    return hex_encode(result)
