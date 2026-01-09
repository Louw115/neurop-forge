"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Compression Utilities - Pure functions for data compression patterns.
All functions are pure, deterministic, and atomic.
"""

def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """Calculate compression ratio."""
    if compressed_size <= 0:
        return 0.0
    return original_size / compressed_size


def calculate_space_savings(original_size: int, compressed_size: int) -> float:
    """Calculate space savings percentage."""
    if original_size <= 0:
        return 0.0
    return ((original_size - compressed_size) / original_size) * 100


def run_length_encode(data: list) -> list:
    """Run-length encode a list."""
    if not data:
        return []
    result = []
    current = data[0]
    count = 1
    for item in data[1:]:
        if item == current:
            count += 1
        else:
            result.append((current, count))
            current = item
            count = 1
    result.append((current, count))
    return result


def run_length_decode(encoded: list) -> list:
    """Run-length decode a list."""
    result = []
    for value, count in encoded:
        result.extend([value] * count)
    return result


def delta_encode(values: list) -> list:
    """Delta encode a list of numbers."""
    if not values:
        return []
    result = [values[0]]
    for i in range(1, len(values)):
        result.append(values[i] - values[i - 1])
    return result


def delta_decode(encoded: list) -> list:
    """Delta decode a list of numbers."""
    if not encoded:
        return []
    result = [encoded[0]]
    for i in range(1, len(encoded)):
        result.append(result[-1] + encoded[i])
    return result


def build_frequency_table(data: bytes) -> dict:
    """Build frequency table for bytes."""
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    return freq


def build_huffman_tree(frequencies: dict) -> dict:
    """Build Huffman tree structure from frequencies."""
    if not frequencies:
        return {}
    nodes = [{"symbol": k, "freq": v, "left": None, "right": None} for k, v in frequencies.items()]
    while len(nodes) > 1:
        nodes.sort(key=lambda x: x["freq"])
        left = nodes.pop(0)
        right = nodes.pop(0)
        merged = {
            "symbol": None,
            "freq": left["freq"] + right["freq"],
            "left": left,
            "right": right
        }
        nodes.append(merged)
    return nodes[0] if nodes else {}


def generate_huffman_codes(tree: dict, prefix: str, codes: dict) -> dict:
    """Generate Huffman codes from tree."""
    if not tree:
        return codes
    if tree.get("symbol") is not None:
        codes[tree["symbol"]] = prefix or "0"
        return codes
    if tree.get("left"):
        generate_huffman_codes(tree["left"], prefix + "0", codes)
    if tree.get("right"):
        generate_huffman_codes(tree["right"], prefix + "1", codes)
    return codes


def calculate_huffman_size(data: bytes, codes: dict) -> int:
    """Calculate size of Huffman encoded data in bits."""
    return sum(len(codes.get(byte, "")) for byte in data)


def estimate_entropy(frequencies: dict) -> float:
    """Estimate Shannon entropy from frequency table."""
    import math
    total = sum(frequencies.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for freq in frequencies.values():
        if freq > 0:
            p = freq / total
            entropy -= p * math.log2(p)
    return entropy


def calculate_theoretical_minimum(data_length: int, entropy: float) -> float:
    """Calculate theoretical minimum compression size in bits."""
    return data_length * entropy


def lz77_find_match(data: bytes, position: int, window_size: int) -> tuple:
    """Find longest match in LZ77 window."""
    best_length = 0
    best_offset = 0
    window_start = max(0, position - window_size)
    for offset in range(1, position - window_start + 1):
        length = 0
        while (position + length < len(data) and 
               data[position + length] == data[position - offset + (length % offset)]):
            length += 1
            if length > 255:
                break
        if length > best_length:
            best_length = length
            best_offset = offset
    return (best_offset, best_length)


def build_dictionary_entry(index: int, string: str) -> dict:
    """Build a dictionary entry for LZW-style compression."""
    return {"index": index, "string": string}


def find_in_dictionary(dictionary: list, string: str) -> int:
    """Find string in dictionary, return index or -1."""
    for entry in dictionary:
        if entry["string"] == string:
            return entry["index"]
    return -1


def add_to_dictionary(dictionary: list, string: str, max_size: int) -> list:
    """Add string to dictionary."""
    if len(dictionary) >= max_size:
        return dictionary
    result = list(dictionary)
    result.append(build_dictionary_entry(len(result), string))
    return result


def calculate_bit_width(value: int) -> int:
    """Calculate minimum bits needed to represent value."""
    if value <= 0:
        return 1
    bits = 0
    while value > 0:
        bits += 1
        value >>= 1
    return bits


def pack_integers(values: list, bit_width: int) -> list:
    """Pack integers into byte-aligned groups."""
    result = []
    buffer = 0
    bits_in_buffer = 0
    for value in values:
        buffer = (buffer << bit_width) | (value & ((1 << bit_width) - 1))
        bits_in_buffer += bit_width
        while bits_in_buffer >= 8:
            bits_in_buffer -= 8
            result.append((buffer >> bits_in_buffer) & 0xFF)
    if bits_in_buffer > 0:
        result.append((buffer << (8 - bits_in_buffer)) & 0xFF)
    return result


def unpack_integers(packed: list, bit_width: int, count: int) -> list:
    """Unpack integers from byte-aligned groups."""
    result = []
    buffer = 0
    bits_in_buffer = 0
    byte_idx = 0
    for _ in range(count):
        while bits_in_buffer < bit_width and byte_idx < len(packed):
            buffer = (buffer << 8) | packed[byte_idx]
            bits_in_buffer += 8
            byte_idx += 1
        bits_in_buffer -= bit_width
        result.append((buffer >> bits_in_buffer) & ((1 << bit_width) - 1))
    return result


def create_bitmap(values: list, max_value: int) -> list:
    """Create bitmap representation of values."""
    bitmap = [0] * ((max_value + 7) // 8)
    for value in values:
        if 0 <= value <= max_value:
            bitmap[value // 8] |= (1 << (value % 8))
    return bitmap


def check_bitmap(bitmap: list, value: int) -> bool:
    """Check if value is set in bitmap."""
    byte_idx = value // 8
    if byte_idx >= len(bitmap):
        return False
    return bool(bitmap[byte_idx] & (1 << (value % 8)))


def count_bitmap_bits(bitmap: list) -> int:
    """Count set bits in bitmap."""
    count = 0
    for byte in bitmap:
        while byte:
            count += byte & 1
            byte >>= 1
    return count


def estimate_compression_benefit(data_size: int, unique_values: int, total_values: int) -> float:
    """Estimate potential compression benefit."""
    if unique_values <= 0 or total_values <= 0:
        return 0.0
    original_bits = data_size * 8
    estimated_bits = total_values * calculate_bit_width(unique_values)
    return (original_bits - estimated_bits) / original_bits * 100 if original_bits > 0 else 0.0
