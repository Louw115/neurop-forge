"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Color Math - Pure functions for color space conversions and manipulation.
All functions are pure, deterministic, and atomic.
"""

import math


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(hex_color: str) -> dict:
    """Convert hex color to RGB."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return {"r": r, "g": g, "b": b}


def rgb_to_hsl(r: int, g: int, b: int) -> dict:
    """Convert RGB to HSL."""
    r_norm = r / 255
    g_norm = g / 255
    b_norm = b / 255
    max_c = max(r_norm, g_norm, b_norm)
    min_c = min(r_norm, g_norm, b_norm)
    l = (max_c + min_c) / 2
    if max_c == min_c:
        h = s = 0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r_norm:
            h = ((g_norm - b_norm) / d + (6 if g_norm < b_norm else 0)) / 6
        elif max_c == g_norm:
            h = ((b_norm - r_norm) / d + 2) / 6
        else:
            h = ((r_norm - g_norm) / d + 4) / 6
    return {"h": round(h * 360), "s": round(s * 100), "l": round(l * 100)}


def hsl_to_rgb(h: int, s: int, l: int) -> dict:
    """Convert HSL to RGB."""
    h_norm = h / 360
    s_norm = s / 100
    l_norm = l / 100
    if s_norm == 0:
        r = g = b = round(l_norm * 255)
        return {"r": r, "g": g, "b": b}
    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            return p + (q - p) * (2/3 - t) * 6
        return p
    q = l_norm * (1 + s_norm) if l_norm < 0.5 else l_norm + s_norm - l_norm * s_norm
    p = 2 * l_norm - q
    r = round(hue_to_rgb(p, q, h_norm + 1/3) * 255)
    g = round(hue_to_rgb(p, q, h_norm) * 255)
    b = round(hue_to_rgb(p, q, h_norm - 1/3) * 255)
    return {"r": r, "g": g, "b": b}


def rgb_to_hsv(r: int, g: int, b: int) -> dict:
    """Convert RGB to HSV."""
    r_norm = r / 255
    g_norm = g / 255
    b_norm = b / 255
    max_c = max(r_norm, g_norm, b_norm)
    min_c = min(r_norm, g_norm, b_norm)
    v = max_c
    d = max_c - min_c
    s = 0 if max_c == 0 else d / max_c
    if max_c == min_c:
        h = 0
    else:
        if max_c == r_norm:
            h = ((g_norm - b_norm) / d + (6 if g_norm < b_norm else 0)) / 6
        elif max_c == g_norm:
            h = ((b_norm - r_norm) / d + 2) / 6
        else:
            h = ((r_norm - g_norm) / d + 4) / 6
    return {"h": round(h * 360), "s": round(s * 100), "v": round(v * 100)}


def hsv_to_rgb(h: int, s: int, v: int) -> dict:
    """Convert HSV to RGB."""
    h_norm = h / 360
    s_norm = s / 100
    v_norm = v / 100
    i = int(h_norm * 6)
    f = h_norm * 6 - i
    p = v_norm * (1 - s_norm)
    q = v_norm * (1 - f * s_norm)
    t = v_norm * (1 - (1 - f) * s_norm)
    i %= 6
    if i == 0:
        r, g, b = v_norm, t, p
    elif i == 1:
        r, g, b = q, v_norm, p
    elif i == 2:
        r, g, b = p, v_norm, t
    elif i == 3:
        r, g, b = p, q, v_norm
    elif i == 4:
        r, g, b = t, p, v_norm
    else:
        r, g, b = v_norm, p, q
    return {"r": round(r * 255), "g": round(g * 255), "b": round(b * 255)}


def rgb_to_cmyk(r: int, g: int, b: int) -> dict:
    """Convert RGB to CMYK."""
    if r == 0 and g == 0 and b == 0:
        return {"c": 0, "m": 0, "y": 0, "k": 100}
    r_norm = r / 255
    g_norm = g / 255
    b_norm = b / 255
    k = 1 - max(r_norm, g_norm, b_norm)
    c = (1 - r_norm - k) / (1 - k) if k < 1 else 0
    m = (1 - g_norm - k) / (1 - k) if k < 1 else 0
    y = (1 - b_norm - k) / (1 - k) if k < 1 else 0
    return {"c": round(c * 100), "m": round(m * 100), "y": round(y * 100), "k": round(k * 100)}


def cmyk_to_rgb(c: int, m: int, y: int, k: int) -> dict:
    """Convert CMYK to RGB."""
    r = round(255 * (1 - c / 100) * (1 - k / 100))
    g = round(255 * (1 - m / 100) * (1 - k / 100))
    b = round(255 * (1 - y / 100) * (1 - k / 100))
    return {"r": r, "g": g, "b": b}


def luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance."""
    def linearize(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def contrast_ratio(r1: int, g1: int, b1: int, r2: int, g2: int, b2: int) -> float:
    """Calculate contrast ratio between two colors."""
    l1 = luminance(r1, g1, b1)
    l2 = luminance(r2, g2, b2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def is_light_color(r: int, g: int, b: int) -> bool:
    """Check if color is light."""
    return luminance(r, g, b) > 0.5


def blend_colors(r1: int, g1: int, b1: int, r2: int, g2: int, b2: int, ratio: float) -> dict:
    """Blend two colors."""
    r = round(r1 + (r2 - r1) * ratio)
    g = round(g1 + (g2 - g1) * ratio)
    b = round(b1 + (b2 - b1) * ratio)
    return {"r": r, "g": g, "b": b}


def lighten(r: int, g: int, b: int, amount: float) -> dict:
    """Lighten a color."""
    return blend_colors(r, g, b, 255, 255, 255, amount)


def darken(r: int, g: int, b: int, amount: float) -> dict:
    """Darken a color."""
    return blend_colors(r, g, b, 0, 0, 0, amount)


def saturate(r: int, g: int, b: int, amount: float) -> dict:
    """Increase saturation."""
    hsl = rgb_to_hsl(r, g, b)
    new_s = min(100, hsl["s"] + amount * 100)
    return hsl_to_rgb(hsl["h"], round(new_s), hsl["l"])


def desaturate(r: int, g: int, b: int, amount: float) -> dict:
    """Decrease saturation."""
    hsl = rgb_to_hsl(r, g, b)
    new_s = max(0, hsl["s"] - amount * 100)
    return hsl_to_rgb(hsl["h"], round(new_s), hsl["l"])


def grayscale(r: int, g: int, b: int) -> dict:
    """Convert to grayscale."""
    gray = round(0.299 * r + 0.587 * g + 0.114 * b)
    return {"r": gray, "g": gray, "b": gray}


def invert_color(r: int, g: int, b: int) -> dict:
    """Invert a color."""
    return {"r": 255 - r, "g": 255 - g, "b": 255 - b}


def complement_color(r: int, g: int, b: int) -> dict:
    """Get complementary color."""
    hsl = rgb_to_hsl(r, g, b)
    new_h = (hsl["h"] + 180) % 360
    return hsl_to_rgb(new_h, hsl["s"], hsl["l"])


def color_distance(r1: int, g1: int, b1: int, r2: int, g2: int, b2: int) -> float:
    """Calculate Euclidean distance between colors."""
    return math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)


def adjust_hue(r: int, g: int, b: int, degrees: int) -> dict:
    """Adjust hue by degrees."""
    hsl = rgb_to_hsl(r, g, b)
    new_h = (hsl["h"] + degrees) % 360
    return hsl_to_rgb(new_h, hsl["s"], hsl["l"])
