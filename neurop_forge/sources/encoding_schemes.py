"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Encoding Schemes - Pure functions for various encoding/decoding operations.
All functions are pure, deterministic, and atomic.
"""

import base64
import json


def base64_encode(data: bytes) -> str:
    """Encode bytes to standard base64."""
    return base64.b64encode(data).decode("ascii")


def base64_decode(encoded: str) -> bytes:
    """Decode standard base64 to bytes."""
    return base64.b64decode(encoded)


def base64_url_encode(data: bytes) -> str:
    """Encode bytes to URL-safe base64."""
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def base64_url_decode(encoded: str) -> bytes:
    """Decode URL-safe base64 to bytes."""
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


def url_encode(text: str) -> str:
    """URL encode a string."""
    from urllib.parse import quote
    return quote(text, safe="")


def url_decode(encoded: str) -> str:
    """URL decode a string."""
    from urllib.parse import unquote
    return unquote(encoded)


def url_encode_component(text: str) -> str:
    """URL encode a component."""
    from urllib.parse import quote
    return quote(text, safe="~-_.!*'()")


def html_encode(text: str) -> str:
    """HTML encode a string."""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;"))


def html_decode(encoded: str) -> str:
    """HTML decode a string."""
    return (encoded
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#x27;", "'"))


def json_encode(data) -> str:
    """JSON encode data."""
    return json.dumps(data)


def json_decode(encoded: str):
    """JSON decode string."""
    return json.loads(encoded)


def ascii_to_int(char: str) -> int:
    """Get ASCII value of character."""
    return ord(char)


def int_to_ascii(code: int) -> str:
    """Get character from ASCII code."""
    return chr(code)


def unicode_escape(text: str) -> str:
    """Escape non-ASCII to unicode escapes."""
    return text.encode("unicode_escape").decode("ascii")


def unicode_unescape(escaped: str) -> str:
    """Unescape unicode escapes."""
    return escaped.encode("ascii").decode("unicode_escape")


def rot13(text: str) -> str:
    """Apply ROT13 encoding."""
    result = []
    for c in text:
        if "a" <= c <= "z":
            result.append(chr((ord(c) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= c <= "Z":
            result.append(chr((ord(c) - ord("A") + 13) % 26 + ord("A")))
        else:
            result.append(c)
    return "".join(result)


def caesar_cipher(text: str, shift: int) -> str:
    """Apply Caesar cipher."""
    result = []
    for c in text:
        if "a" <= c <= "z":
            result.append(chr((ord(c) - ord("a") + shift) % 26 + ord("a")))
        elif "A" <= c <= "Z":
            result.append(chr((ord(c) - ord("A") + shift) % 26 + ord("A")))
        else:
            result.append(c)
    return "".join(result)


def atbash_cipher(text: str) -> str:
    """Apply Atbash cipher."""
    result = []
    for c in text:
        if "a" <= c <= "z":
            result.append(chr(ord("z") - (ord(c) - ord("a"))))
        elif "A" <= c <= "Z":
            result.append(chr(ord("Z") - (ord(c) - ord("A"))))
        else:
            result.append(c)
    return "".join(result)


def base32_encode(data: bytes) -> str:
    """Encode bytes to base32."""
    return base64.b32encode(data).decode("ascii")


def base32_decode(encoded: str) -> bytes:
    """Decode base32 to bytes."""
    return base64.b32decode(encoded)


def punycode_encode(text: str) -> str:
    """Encode text to Punycode."""
    return text.encode("punycode").decode("ascii")


def punycode_decode(encoded: str) -> str:
    """Decode Punycode to text."""
    return encoded.encode("ascii").decode("punycode")


def binary_to_text(binary: str) -> str:
    """Convert binary string to text."""
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return "".join(chr(int(c, 2)) for c in chars)


def text_to_binary(text: str) -> str:
    """Convert text to binary string."""
    return "".join(format(ord(c), "08b") for c in text)


def morse_encode(text: str) -> str:
    """Encode text to Morse code."""
    morse = {
        "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
        "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
        "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
        "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
        "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---",
        "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...",
        "8": "---..", "9": "----.", " ": "/"
    }
    return " ".join(morse.get(c.upper(), "") for c in text)


def morse_decode(morse: str) -> str:
    """Decode Morse code to text."""
    decode = {
        ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F",
        "--.": "G", "....": "H", "..": "I", ".---": "J", "-.-": "K", ".-..": "L",
        "--": "M", "-.": "N", "---": "O", ".--.": "P", "--.-": "Q", ".-.": "R",
        "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
        "-.--": "Y", "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
        "...--": "3", "....-": "4", ".....": "5", "-....": "6", "--...": "7",
        "---..": "8", "----.": "9", "/": " "
    }
    return "".join(decode.get(code, "") for code in morse.split(" "))


def quoted_printable_encode(text: str) -> str:
    """Encode to quoted-printable."""
    import quopri
    return quopri.encodestring(text.encode()).decode()


def quoted_printable_decode(encoded: str) -> str:
    """Decode quoted-printable."""
    import quopri
    return quopri.decodestring(encoded.encode()).decode()
