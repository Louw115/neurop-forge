"""
Color Utilities - Pure functions for color manipulation and conversion.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    if not hex_color:
        return (0, 0, 0)
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return (0, 0, 0)
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    except ValueError:
        return (0, 0, 0)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color string."""
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple:
    """Convert RGB to HSL (hue, saturation, lightness)."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2.0
    
    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6.0 if g < b else 0.0)
        elif max_c == g:
            h = (b - r) / d + 2.0
        else:
            h = (r - g) / d + 4.0
        h /= 6.0
    
    return (round(h * 360), round(s * 100), round(l * 100))


def hsl_to_rgb(h: int, s: int, l: int) -> tuple:
    """Convert HSL to RGB."""
    h, s, l = h / 360.0, s / 100.0, l / 100.0
    
    if s == 0:
        r = g = b = l
    else:
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
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    return (round(r * 255), round(g * 255), round(b * 255))


def get_brightness(r: int, g: int, b: int) -> float:
    """Calculate perceived brightness of a color (0-255)."""
    return (r * 299 + g * 587 + b * 114) / 1000


def is_dark_color(r: int, g: int, b: int) -> bool:
    """Check if a color is considered dark."""
    return get_brightness(r, g, b) < 128


def is_light_color(r: int, g: int, b: int) -> bool:
    """Check if a color is considered light."""
    return get_brightness(r, g, b) >= 128


def get_contrast_color(r: int, g: int, b: int) -> tuple:
    """Get black or white based on which contrasts better."""
    if is_dark_color(r, g, b):
        return (255, 255, 255)
    return (0, 0, 0)


def blend_colors(r1: int, g1: int, b1: int, r2: int, g2: int, b2: int, ratio: float) -> tuple:
    """Blend two colors by a ratio (0.0 = first color, 1.0 = second color)."""
    ratio = max(0.0, min(1.0, ratio))
    r = round(r1 + (r2 - r1) * ratio)
    g = round(g1 + (g2 - g1) * ratio)
    b = round(b1 + (b2 - b1) * ratio)
    return (r, g, b)


def lighten_color(r: int, g: int, b: int, amount: float) -> tuple:
    """Lighten a color by a percentage (0.0 to 1.0)."""
    amount = max(0.0, min(1.0, amount))
    r = round(r + (255 - r) * amount)
    g = round(g + (255 - g) * amount)
    b = round(b + (255 - b) * amount)
    return (r, g, b)


def darken_color(r: int, g: int, b: int, amount: float) -> tuple:
    """Darken a color by a percentage (0.0 to 1.0)."""
    amount = max(0.0, min(1.0, amount))
    r = round(r * (1 - amount))
    g = round(g * (1 - amount))
    b = round(b * (1 - amount))
    return (r, g, b)


def invert_color(r: int, g: int, b: int) -> tuple:
    """Invert a color."""
    return (255 - r, 255 - g, 255 - b)


def grayscale(r: int, g: int, b: int) -> tuple:
    """Convert a color to grayscale."""
    gray = round(0.299 * r + 0.587 * g + 0.114 * b)
    return (gray, gray, gray)


def saturate_color(r: int, g: int, b: int, amount: float) -> tuple:
    """Increase saturation of a color."""
    h, s, l = rgb_to_hsl(r, g, b)
    s = min(100, s + round(amount * 100))
    return hsl_to_rgb(h, s, l)


def desaturate_color(r: int, g: int, b: int, amount: float) -> tuple:
    """Decrease saturation of a color."""
    h, s, l = rgb_to_hsl(r, g, b)
    s = max(0, s - round(amount * 100))
    return hsl_to_rgb(h, s, l)


def get_complementary_color(r: int, g: int, b: int) -> tuple:
    """Get the complementary color (opposite on color wheel)."""
    h, s, l = rgb_to_hsl(r, g, b)
    h = (h + 180) % 360
    return hsl_to_rgb(h, s, l)


def get_triadic_colors(r: int, g: int, b: int) -> list:
    """Get triadic colors (three evenly spaced colors)."""
    h, s, l = rgb_to_hsl(r, g, b)
    return [
        hsl_to_rgb(h, s, l),
        hsl_to_rgb((h + 120) % 360, s, l),
        hsl_to_rgb((h + 240) % 360, s, l),
    ]


def get_analogous_colors(r: int, g: int, b: int) -> list:
    """Get analogous colors (adjacent on color wheel)."""
    h, s, l = rgb_to_hsl(r, g, b)
    return [
        hsl_to_rgb((h - 30) % 360, s, l),
        hsl_to_rgb(h, s, l),
        hsl_to_rgb((h + 30) % 360, s, l),
    ]


def color_distance(r1: int, g1: int, b1: int, r2: int, g2: int, b2: int) -> float:
    """Calculate Euclidean distance between two colors."""
    return ((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2) ** 0.5


def are_similar_colors(r1: int, g1: int, b1: int, r2: int, g2: int, b2: int, threshold: float) -> bool:
    """Check if two colors are similar within a threshold."""
    return color_distance(r1, g1, b1, r2, g2, b2) <= threshold


def rgb_to_cmyk(r: int, g: int, b: int) -> tuple:
    """Convert RGB to CMYK."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    k = 1 - max(r, g, b)
    if k == 1:
        return (0, 0, 0, 100)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return (round(c * 100), round(m * 100), round(y * 100), round(k * 100))


def cmyk_to_rgb(c: int, m: int, y: int, k: int) -> tuple:
    """Convert CMYK to RGB."""
    c, m, y, k = c / 100.0, m / 100.0, y / 100.0, k / 100.0
    r = round(255 * (1 - c) * (1 - k))
    g = round(255 * (1 - m) * (1 - k))
    b = round(255 * (1 - y) * (1 - k))
    return (r, g, b)


def clamp_rgb(r: int, g: int, b: int) -> tuple:
    """Clamp RGB values to valid range 0-255."""
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def average_colors(colors: list) -> tuple:
    """Calculate the average of multiple RGB colors."""
    if not colors:
        return (0, 0, 0)
    total_r = sum(c[0] for c in colors)
    total_g = sum(c[1] for c in colors)
    total_b = sum(c[2] for c in colors)
    n = len(colors)
    return (round(total_r / n), round(total_g / n), round(total_b / n))
