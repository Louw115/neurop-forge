"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Bitwise Utilities - Pure functions for bit manipulation.
All functions are pure, deterministic, and atomic.
"""

def bit_and(a: int, b: int) -> int:
    """Bitwise AND."""
    return a & b


def bit_or(a: int, b: int) -> int:
    """Bitwise OR."""
    return a | b


def bit_xor(a: int, b: int) -> int:
    """Bitwise XOR."""
    return a ^ b


def bit_not(a: int) -> int:
    """Bitwise NOT."""
    return ~a


def left_shift(value: int, positions: int) -> int:
    """Left shift by positions."""
    return value << positions


def right_shift(value: int, positions: int) -> int:
    """Right shift by positions."""
    return value >> positions


def unsigned_right_shift(value: int, positions: int, bits: int) -> int:
    """Unsigned right shift (logical shift)."""
    mask = (1 << bits) - 1
    return (value & mask) >> positions


def get_bit(value: int, position: int) -> int:
    """Get bit at position."""
    return (value >> position) & 1


def set_bit(value: int, position: int) -> int:
    """Set bit at position to 1."""
    return value | (1 << position)


def clear_bit(value: int, position: int) -> int:
    """Clear bit at position to 0."""
    return value & ~(1 << position)


def toggle_bit(value: int, position: int) -> int:
    """Toggle bit at position."""
    return value ^ (1 << position)


def count_set_bits(value: int) -> int:
    """Count number of set bits (popcount)."""
    count = 0
    while value:
        count += value & 1
        value >>= 1
    return count


def count_trailing_zeros(value: int) -> int:
    """Count trailing zero bits."""
    if value == 0:
        return 0
    count = 0
    while (value & 1) == 0:
        count += 1
        value >>= 1
    return count


def count_leading_zeros(value: int, bits: int) -> int:
    """Count leading zero bits for given bit width."""
    if value == 0:
        return bits
    count = 0
    mask = 1 << (bits - 1)
    while (value & mask) == 0:
        count += 1
        mask >>= 1
    return count


def is_power_of_two(value: int) -> bool:
    """Check if value is power of two."""
    return value > 0 and (value & (value - 1)) == 0


def next_power_of_two(value: int) -> int:
    """Get next power of two >= value."""
    if value <= 0:
        return 1
    value -= 1
    value |= value >> 1
    value |= value >> 2
    value |= value >> 4
    value |= value >> 8
    value |= value >> 16
    return value + 1


def lowest_set_bit(value: int) -> int:
    """Get lowest set bit position."""
    if value == 0:
        return -1
    return count_trailing_zeros(value)


def highest_set_bit(value: int, bits: int) -> int:
    """Get highest set bit position."""
    if value == 0:
        return -1
    return bits - 1 - count_leading_zeros(value, bits)


def extract_bits(value: int, start: int, count: int) -> int:
    """Extract count bits starting at position start."""
    mask = (1 << count) - 1
    return (value >> start) & mask


def insert_bits(value: int, bits: int, start: int, count: int) -> int:
    """Insert bits at position."""
    mask = (1 << count) - 1
    cleared = value & ~(mask << start)
    return cleared | ((bits & mask) << start)


def reverse_bits(value: int, bits: int) -> int:
    """Reverse bit order."""
    result = 0
    for i in range(bits):
        if value & (1 << i):
            result |= 1 << (bits - 1 - i)
    return result


def rotate_left(value: int, positions: int, bits: int) -> int:
    """Rotate bits left."""
    positions = positions % bits
    mask = (1 << bits) - 1
    return ((value << positions) | (value >> (bits - positions))) & mask


def rotate_right(value: int, positions: int, bits: int) -> int:
    """Rotate bits right."""
    positions = positions % bits
    mask = (1 << bits) - 1
    return ((value >> positions) | (value << (bits - positions))) & mask


def swap_bits(value: int, pos1: int, pos2: int) -> int:
    """Swap two bits at given positions."""
    bit1 = get_bit(value, pos1)
    bit2 = get_bit(value, pos2)
    if bit1 == bit2:
        return value
    result = toggle_bit(value, pos1)
    result = toggle_bit(result, pos2)
    return result


def interleave_bits(x: int, y: int) -> int:
    """Interleave bits of two values (Morton code)."""
    result = 0
    for i in range(32):
        result |= ((x >> i) & 1) << (2 * i)
        result |= ((y >> i) & 1) << (2 * i + 1)
    return result


def deinterleave_bits(z: int) -> dict:
    """Deinterleave Morton code into two values."""
    x, y = 0, 0
    for i in range(32):
        x |= ((z >> (2 * i)) & 1) << i
        y |= ((z >> (2 * i + 1)) & 1) << i
    return {"x": x, "y": y}


def parity(value: int) -> int:
    """Calculate parity (1 if odd number of set bits)."""
    result = 0
    while value:
        result ^= value & 1
        value >>= 1
    return result


def sign_extend(value: int, from_bits: int, to_bits: int) -> int:
    """Sign extend from smaller to larger bit width."""
    sign_bit = 1 << (from_bits - 1)
    if value & sign_bit:
        extension = ((1 << (to_bits - from_bits)) - 1) << from_bits
        return value | extension
    return value


def to_binary_string(value: int, bits: int) -> str:
    """Convert to binary string with fixed width."""
    return format(value & ((1 << bits) - 1), f'0{bits}b')


def from_binary_string(binary_str: str) -> int:
    """Convert binary string to integer."""
    return int(binary_str, 2)


def to_hex_string(value: int, bits: int) -> str:
    """Convert to hex string with fixed width."""
    hex_digits = (bits + 3) // 4
    return format(value & ((1 << bits) - 1), f'0{hex_digits}x')


def from_hex_string(hex_str: str) -> int:
    """Convert hex string to integer."""
    return int(hex_str, 16)


def create_bitmask(start: int, end: int) -> int:
    """Create bitmask from start to end (inclusive)."""
    return ((1 << (end - start + 1)) - 1) << start


def apply_bitmask(value: int, mask: int) -> int:
    """Apply bitmask to value."""
    return value & mask


def bit_difference(a: int, b: int) -> int:
    """Count bit positions that differ (Hamming distance)."""
    return count_set_bits(a ^ b)
