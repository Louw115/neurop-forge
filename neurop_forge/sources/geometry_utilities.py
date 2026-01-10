"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Geometry Utilities - Pure functions for 2D geometry.
All functions are pure, deterministic, and atomic.
"""

import math


def create_point(x: float, y: float) -> dict:
    """Create a 2D point."""
    return {"x": x, "y": y}


def create_line(p1: dict, p2: dict) -> dict:
    """Create a line from two points."""
    return {"p1": p1, "p2": p2}


def create_circle(center: dict, radius: float) -> dict:
    """Create a circle."""
    return {"center": center, "radius": radius}


def create_rectangle(x: float, y: float, width: float, height: float) -> dict:
    """Create a rectangle."""
    return {"x": x, "y": y, "width": width, "height": height}


def point_distance(p1: dict, p2: dict) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2["x"] - p1["x"]) ** 2 + (p2["y"] - p1["y"]) ** 2)


def point_manhattan_distance(p1: dict, p2: dict) -> float:
    """Calculate Manhattan distance between two points."""
    return abs(p2["x"] - p1["x"]) + abs(p2["y"] - p1["y"])


def point_midpoint(p1: dict, p2: dict) -> dict:
    """Calculate midpoint between two points."""
    return create_point((p1["x"] + p2["x"]) / 2, (p1["y"] + p2["y"]) / 2)


def point_translate(point: dict, dx: float, dy: float) -> dict:
    """Translate point by offset."""
    return create_point(point["x"] + dx, point["y"] + dy)


def point_rotate(point: dict, origin: dict, angle_rad: float) -> dict:
    """Rotate point around origin."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    dx = point["x"] - origin["x"]
    dy = point["y"] - origin["y"]
    new_x = origin["x"] + dx * cos_a - dy * sin_a
    new_y = origin["y"] + dx * sin_a + dy * cos_a
    return create_point(new_x, new_y)


def point_scale(point: dict, origin: dict, factor: float) -> dict:
    """Scale point relative to origin."""
    new_x = origin["x"] + (point["x"] - origin["x"]) * factor
    new_y = origin["y"] + (point["y"] - origin["y"]) * factor
    return create_point(new_x, new_y)


def line_length(line: dict) -> float:
    """Calculate line length."""
    return point_distance(line["p1"], line["p2"])


def line_slope(line: dict) -> float:
    """Calculate line slope."""
    dx = line["p2"]["x"] - line["p1"]["x"]
    if dx == 0:
        return float("inf")
    return (line["p2"]["y"] - line["p1"]["y"]) / dx


def line_angle(line: dict) -> float:
    """Calculate angle of line in radians."""
    return math.atan2(line["p2"]["y"] - line["p1"]["y"], line["p2"]["x"] - line["p1"]["x"])


def point_on_line(point: dict, line: dict, tolerance: float) -> bool:
    """Check if point is on line segment."""
    d1 = point_distance(line["p1"], point)
    d2 = point_distance(point, line["p2"])
    line_len = line_length(line)
    return abs(d1 + d2 - line_len) <= tolerance


def lines_intersect(l1: dict, l2: dict) -> bool:
    """Check if two line segments intersect."""
    def ccw(a, b, c):
        return (c["y"] - a["y"]) * (b["x"] - a["x"]) > (b["y"] - a["y"]) * (c["x"] - a["x"])
    a, b = l1["p1"], l1["p2"]
    c, d = l2["p1"], l2["p2"]
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


def line_intersection(l1: dict, l2: dict) -> dict:
    """Calculate intersection point of two lines."""
    x1, y1 = l1["p1"]["x"], l1["p1"]["y"]
    x2, y2 = l1["p2"]["x"], l1["p2"]["y"]
    x3, y3 = l2["p1"]["x"], l2["p1"]["y"]
    x4, y4 = l2["p2"]["x"], l2["p2"]["y"]
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)
    return create_point(x, y)


def circle_area(circle: dict) -> float:
    """Calculate circle area."""
    return math.pi * circle["radius"] ** 2


def circle_circumference(circle: dict) -> float:
    """Calculate circle circumference."""
    return 2 * math.pi * circle["radius"]


def point_in_circle(point: dict, circle: dict) -> bool:
    """Check if point is inside circle."""
    return point_distance(point, circle["center"]) <= circle["radius"]


def circles_intersect(c1: dict, c2: dict) -> bool:
    """Check if two circles intersect."""
    d = point_distance(c1["center"], c2["center"])
    return d <= c1["radius"] + c2["radius"]


def rectangle_area(rect: dict) -> float:
    """Calculate rectangle area."""
    return rect["width"] * rect["height"]


def rectangle_perimeter(rect: dict) -> float:
    """Calculate rectangle perimeter."""
    return 2 * (rect["width"] + rect["height"])


def point_in_rectangle(point: dict, rect: dict) -> bool:
    """Check if point is inside rectangle."""
    return (rect["x"] <= point["x"] <= rect["x"] + rect["width"] and
            rect["y"] <= point["y"] <= rect["y"] + rect["height"])


def rectangles_intersect(r1: dict, r2: dict) -> bool:
    """Check if two rectangles intersect."""
    return not (r1["x"] + r1["width"] < r2["x"] or
                r2["x"] + r2["width"] < r1["x"] or
                r1["y"] + r1["height"] < r2["y"] or
                r2["y"] + r2["height"] < r1["y"])


def rectangle_intersection(r1: dict, r2: dict) -> dict:
    """Calculate intersection rectangle."""
    x = max(r1["x"], r2["x"])
    y = max(r1["y"], r2["y"])
    x2 = min(r1["x"] + r1["width"], r2["x"] + r2["width"])
    y2 = min(r1["y"] + r1["height"], r2["y"] + r2["height"])
    if x < x2 and y < y2:
        return create_rectangle(x, y, x2 - x, y2 - y)
    return None


def polygon_area(vertices: list) -> float:
    """Calculate polygon area using shoelace formula."""
    n = len(vertices)
    if n < 3:
        return 0
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i]["x"] * vertices[j]["y"]
        area -= vertices[j]["x"] * vertices[i]["y"]
    return abs(area) / 2


def polygon_centroid(vertices: list) -> dict:
    """Calculate polygon centroid."""
    n = len(vertices)
    if n == 0:
        return create_point(0, 0)
    cx = sum(v["x"] for v in vertices) / n
    cy = sum(v["y"] for v in vertices) / n
    return create_point(cx, cy)


def triangle_area(p1: dict, p2: dict, p3: dict) -> float:
    """Calculate triangle area."""
    return abs((p2["x"] - p1["x"]) * (p3["y"] - p1["y"]) -
               (p3["x"] - p1["x"]) * (p2["y"] - p1["y"])) / 2


def point_in_triangle(point: dict, p1: dict, p2: dict, p3: dict) -> bool:
    """Check if point is inside triangle."""
    def sign(a, b, c):
        return (a["x"] - c["x"]) * (b["y"] - c["y"]) - (b["x"] - c["x"]) * (a["y"] - c["y"])
    d1 = sign(point, p1, p2)
    d2 = sign(point, p2, p3)
    d3 = sign(point, p3, p1)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180 / math.pi


def angle_between_points(p1: dict, p2: dict) -> float:
    """Calculate angle from p1 to p2 in radians."""
    return math.atan2(p2["y"] - p1["y"], p2["x"] - p1["x"])


def normalize_angle(angle: float) -> float:
    """Normalize angle to [0, 2*pi)."""
    while angle < 0:
        angle += 2 * math.pi
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    return angle
