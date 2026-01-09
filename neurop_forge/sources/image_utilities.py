"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Image Utilities - Pure functions for image processing patterns.
All functions are pure, deterministic, and atomic.
"""

def calculate_aspect_ratio(width: int, height: int) -> float:
    """Calculate aspect ratio."""
    if height <= 0:
        return 0.0
    return width / height


def get_aspect_ratio_name(width: int, height: int) -> str:
    """Get common aspect ratio name."""
    ratio = calculate_aspect_ratio(width, height)
    if abs(ratio - 1.0) < 0.01:
        return "1:1"
    elif abs(ratio - 1.33) < 0.05:
        return "4:3"
    elif abs(ratio - 1.5) < 0.05:
        return "3:2"
    elif abs(ratio - 1.78) < 0.05:
        return "16:9"
    elif abs(ratio - 2.35) < 0.1:
        return "21:9"
    return f"{width}:{height}"


def calculate_scaled_dimensions(width: int, height: int, max_width: int, max_height: int) -> dict:
    """Calculate scaled dimensions maintaining aspect ratio."""
    if width <= 0 or height <= 0:
        return {"width": 0, "height": 0}
    ratio = min(max_width / width, max_height / height)
    if ratio >= 1:
        return {"width": width, "height": height}
    return {
        "width": int(width * ratio),
        "height": int(height * ratio)
    }


def calculate_crop_dimensions(source_width: int, source_height: int, target_width: int, target_height: int) -> dict:
    """Calculate crop dimensions for center crop."""
    source_ratio = source_width / source_height if source_height > 0 else 1
    target_ratio = target_width / target_height if target_height > 0 else 1
    if source_ratio > target_ratio:
        new_width = int(source_height * target_ratio)
        x = (source_width - new_width) // 2
        return {"x": x, "y": 0, "width": new_width, "height": source_height}
    else:
        new_height = int(source_width / target_ratio)
        y = (source_height - new_height) // 2
        return {"x": 0, "y": y, "width": source_width, "height": new_height}


def calculate_thumbnail_dimensions(width: int, height: int, max_size: int) -> dict:
    """Calculate thumbnail dimensions."""
    if width <= max_size and height <= max_size:
        return {"width": width, "height": height}
    if width > height:
        return {
            "width": max_size,
            "height": int(height * max_size / width)
        }
    return {
        "width": int(width * max_size / height),
        "height": max_size
    }


def hex_to_rgb(hex_color: str) -> dict:
    """Convert hex color to RGB."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return {"r": 0, "g": 0, "b": 0}
    return {
        "r": int(hex_color[0:2], 16),
        "g": int(hex_color[2:4], 16),
        "b": int(hex_color[4:6], 16)
    }


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> dict:
    """Convert RGB to HSL."""
    r, g, b = r / 255, g / 255, b / 255
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2
    if max_c == min_c:
        h = s = 0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    return {"h": int(h * 360), "s": int(s * 100), "l": int(l * 100)}


def calculate_brightness(r: int, g: int, b: int) -> float:
    """Calculate perceived brightness (0-1)."""
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def is_dark_color(r: int, g: int, b: int) -> bool:
    """Check if color is dark."""
    return calculate_brightness(r, g, b) < 0.5


def get_contrast_color(r: int, g: int, b: int) -> str:
    """Get contrasting text color (black or white)."""
    return "#000000" if calculate_brightness(r, g, b) > 0.5 else "#ffffff"


def blend_colors(color1: dict, color2: dict, ratio: float) -> dict:
    """Blend two RGB colors."""
    ratio = max(0, min(1, ratio))
    return {
        "r": int(color1["r"] * (1 - ratio) + color2["r"] * ratio),
        "g": int(color1["g"] * (1 - ratio) + color2["g"] * ratio),
        "b": int(color1["b"] * (1 - ratio) + color2["b"] * ratio)
    }


def calculate_color_distance(color1: dict, color2: dict) -> float:
    """Calculate Euclidean distance between colors."""
    dr = color1["r"] - color2["r"]
    dg = color1["g"] - color2["g"]
    db = color1["b"] - color2["b"]
    return (dr**2 + dg**2 + db**2) ** 0.5


def generate_gradient_colors(start: dict, end: dict, steps: int) -> list:
    """Generate gradient color steps."""
    if steps <= 1:
        return [start]
    colors = []
    for i in range(steps):
        ratio = i / (steps - 1)
        colors.append(blend_colors(start, end, ratio))
    return colors


def calculate_image_data_url_size(width: int, height: int, bytes_per_pixel: int) -> int:
    """Estimate base64 data URL size."""
    raw_size = width * height * bytes_per_pixel
    base64_size = int(raw_size * 4 / 3) + 4
    return base64_size + 22


def build_image_srcset(base_url: str, widths: list) -> str:
    """Build responsive image srcset."""
    parts = []
    for width in widths:
        parts.append(f"{base_url}?w={width} {width}w")
    return ", ".join(parts)


def build_image_sizes(breakpoints: list) -> str:
    """Build responsive image sizes attribute."""
    parts = []
    for bp in breakpoints:
        parts.append(f"(max-width: {bp['max_width']}px) {bp['image_width']}")
    parts.append("100vw")
    return ", ".join(parts)


def get_image_format_from_mime(mime_type: str) -> str:
    """Get image format from MIME type."""
    formats = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/svg+xml": "svg",
        "image/bmp": "bmp",
        "image/tiff": "tiff"
    }
    return formats.get(mime_type.lower(), "unknown")


def get_mime_from_image_format(format_name: str) -> str:
    """Get MIME type from image format."""
    mimes = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
        "bmp": "image/bmp",
        "tiff": "image/tiff"
    }
    return mimes.get(format_name.lower(), "application/octet-stream")


def calculate_quality_size_estimate(width: int, height: int, quality: int, format_type: str) -> int:
    """Estimate file size based on quality and format."""
    base_size = width * height
    quality_factor = quality / 100
    format_factors = {"jpg": 0.15, "png": 0.5, "webp": 0.1, "gif": 0.3}
    factor = format_factors.get(format_type, 0.2)
    return int(base_size * factor * quality_factor)


def build_placeholder_color(seed: str) -> str:
    """Generate a placeholder color from seed."""
    import hashlib
    hash_val = hashlib.sha256(seed.encode()).hexdigest()
    return f"#{hash_val[:6]}"


def calculate_focal_point(width: int, height: int, x_percent: float, y_percent: float) -> dict:
    """Calculate focal point coordinates."""
    return {
        "x": int(width * x_percent / 100),
        "y": int(height * y_percent / 100)
    }


def calculate_smart_crop_offset(source_width: int, source_height: int, crop_width: int, crop_height: int, focal_x: int, focal_y: int) -> dict:
    """Calculate smart crop offset based on focal point."""
    x = max(0, min(focal_x - crop_width // 2, source_width - crop_width))
    y = max(0, min(focal_y - crop_height // 2, source_height - crop_height))
    return {"x": x, "y": y}
