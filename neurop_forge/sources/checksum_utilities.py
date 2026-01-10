"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Checksum Utilities - Pure functions for checksums and data verification.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def crc16(data: bytes) -> int:
    """Calculate CRC-16 checksum."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def crc32(data: bytes) -> int:
    """Calculate CRC-32 checksum."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xEDB88320
            else:
                crc >>= 1
    return crc ^ 0xFFFFFFFF


def adler32(data: bytes) -> int:
    """Calculate Adler-32 checksum."""
    a = 1
    b = 0
    for byte in data:
        a = (a + byte) % 65521
        b = (b + a) % 65521
    return (b << 16) | a


def fletcher16(data: bytes) -> int:
    """Calculate Fletcher-16 checksum."""
    sum1 = 0
    sum2 = 0
    for byte in data:
        sum1 = (sum1 + byte) % 255
        sum2 = (sum2 + sum1) % 255
    return (sum2 << 8) | sum1


def fletcher32(data: bytes) -> int:
    """Calculate Fletcher-32 checksum."""
    sum1 = 0
    sum2 = 0
    for i in range(0, len(data), 2):
        word = data[i]
        if i + 1 < len(data):
            word |= data[i + 1] << 8
        sum1 = (sum1 + word) % 65535
        sum2 = (sum2 + sum1) % 65535
    return (sum2 << 16) | sum1


def xor_checksum(data: bytes) -> int:
    """Calculate XOR checksum."""
    result = 0
    for byte in data:
        result ^= byte
    return result


def sum_checksum(data: bytes) -> int:
    """Calculate simple sum checksum."""
    return sum(data) & 0xFF


def twos_complement_checksum(data: bytes) -> int:
    """Calculate two's complement checksum."""
    total = sum(data) & 0xFF
    return (~total + 1) & 0xFF


def luhn_checksum(digits: str) -> int:
    """Calculate Luhn checksum digit."""
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits_list = digits_of(digits)
    odd_digits = digits_list[-1::-2]
    even_digits = digits_list[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(digits_of(d * 2))
    return (10 - (total % 10)) % 10


def verify_luhn(digits: str) -> bool:
    """Verify Luhn checksum."""
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits_list = digits_of(digits)
    odd_digits = digits_list[-1::-2]
    even_digits = digits_list[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(digits_of(d * 2))
    return total % 10 == 0


def isbn10_checksum(digits: str) -> str:
    """Calculate ISBN-10 check digit."""
    total = 0
    for i, d in enumerate(digits[:9]):
        total += (10 - i) * int(d)
    remainder = (11 - (total % 11)) % 11
    return "X" if remainder == 10 else str(remainder)


def verify_isbn10(isbn: str) -> bool:
    """Verify ISBN-10 checksum."""
    isbn = isbn.replace("-", "")
    if len(isbn) != 10:
        return False
    total = 0
    for i, c in enumerate(isbn):
        val = 10 if c == "X" else int(c)
        total += (10 - i) * val
    return total % 11 == 0


def isbn13_checksum(digits: str) -> str:
    """Calculate ISBN-13 check digit."""
    total = 0
    for i, d in enumerate(digits[:12]):
        weight = 1 if i % 2 == 0 else 3
        total += int(d) * weight
    return str((10 - (total % 10)) % 10)


def verify_isbn13(isbn: str) -> bool:
    """Verify ISBN-13 checksum."""
    isbn = isbn.replace("-", "")
    if len(isbn) != 13:
        return False
    total = 0
    for i, c in enumerate(isbn):
        weight = 1 if i % 2 == 0 else 3
        total += int(c) * weight
    return total % 10 == 0


def ean13_checksum(digits: str) -> str:
    """Calculate EAN-13 check digit."""
    return isbn13_checksum(digits)


def upc_checksum(digits: str) -> str:
    """Calculate UPC-A check digit."""
    odd_sum = sum(int(d) for i, d in enumerate(digits[:11]) if i % 2 == 0)
    even_sum = sum(int(d) for i, d in enumerate(digits[:11]) if i % 2 == 1)
    return str((10 - ((odd_sum * 3 + even_sum) % 10)) % 10)


def md5_hash(data: bytes) -> str:
    """Calculate MD5 hash."""
    return hashlib.md5(data).hexdigest()


def sha1_hash(data: bytes) -> str:
    """Calculate SHA-1 hash."""
    return hashlib.sha1(data).hexdigest()


def sha256_hash(data: bytes) -> str:
    """Calculate SHA-256 hash."""
    return hashlib.sha256(data).hexdigest()


def sha512_hash(data: bytes) -> str:
    """Calculate SHA-512 hash."""
    return hashlib.sha512(data).hexdigest()


def file_checksum(content: bytes, algorithm: str) -> str:
    """Calculate file checksum using specified algorithm."""
    if algorithm == "md5":
        return md5_hash(content)
    elif algorithm == "sha1":
        return sha1_hash(content)
    elif algorithm == "sha256":
        return sha256_hash(content)
    elif algorithm == "crc32":
        return format(crc32(content), "08x")
    return ""


def verify_checksum(data: bytes, expected: str, algorithm: str) -> bool:
    """Verify data matches expected checksum."""
    calculated = file_checksum(data, algorithm)
    return calculated.lower() == expected.lower()


def hmac_sha256(key: bytes, message: bytes) -> str:
    """Calculate HMAC-SHA256."""
    import hmac
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def compare_checksums(checksum1: str, checksum2: str) -> bool:
    """Constant-time comparison of checksums."""
    if len(checksum1) != len(checksum2):
        return False
    result = 0
    for a, b in zip(checksum1.lower(), checksum2.lower()):
        result |= ord(a) ^ ord(b)
    return result == 0
