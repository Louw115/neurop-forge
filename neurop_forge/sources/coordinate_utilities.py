"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Coordinate Utilities - Pure functions for geographic coordinates.
All functions are pure, deterministic, and atomic.
"""

import math


def is_valid_latitude(lat: float) -> bool:
    """Check if latitude is valid."""
    return -90 <= lat <= 90


def is_valid_longitude(lng: float) -> bool:
    """Check if longitude is valid."""
    return -180 <= lng <= 180


def is_valid_coordinate(lat: float, lng: float) -> bool:
    """Check if coordinate is valid."""
    return is_valid_latitude(lat) and is_valid_longitude(lng)


def normalize_longitude(lng: float) -> float:
    """Normalize longitude to [-180, 180]."""
    while lng > 180:
        lng -= 360
    while lng < -180:
        lng += 360
    return lng


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180 / math.pi


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points in kilometers."""
    R = 6371
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    dlat = degrees_to_radians(lat2 - lat1)
    dlng = degrees_to_radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_bearing(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate initial bearing from point 1 to point 2 in degrees."""
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    dlng = degrees_to_radians(lng2 - lng1)
    y = math.sin(dlng) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlng)
    bearing = radians_to_degrees(math.atan2(y, x))
    return (bearing + 360) % 360


def destination_point(lat: float, lng: float, bearing: float, distance_km: float) -> dict:
    """Calculate destination point given bearing and distance."""
    R = 6371
    lat_rad = degrees_to_radians(lat)
    bearing_rad = degrees_to_radians(bearing)
    d = distance_km / R
    new_lat = math.asin(math.sin(lat_rad) * math.cos(d) + 
                        math.cos(lat_rad) * math.sin(d) * math.cos(bearing_rad))
    new_lng = degrees_to_radians(lng) + math.atan2(
        math.sin(bearing_rad) * math.sin(d) * math.cos(lat_rad),
        math.cos(d) - math.sin(lat_rad) * math.sin(new_lat)
    )
    return {
        "lat": radians_to_degrees(new_lat),
        "lng": normalize_longitude(radians_to_degrees(new_lng))
    }


def midpoint(lat1: float, lng1: float, lat2: float, lng2: float) -> dict:
    """Calculate midpoint between two coordinates."""
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    dlng = degrees_to_radians(lng2 - lng1)
    bx = math.cos(lat2_rad) * math.cos(dlng)
    by = math.cos(lat2_rad) * math.sin(dlng)
    mid_lat = math.atan2(
        math.sin(lat1_rad) + math.sin(lat2_rad),
        math.sqrt((math.cos(lat1_rad) + bx) ** 2 + by ** 2)
    )
    mid_lng = degrees_to_radians(lng1) + math.atan2(by, math.cos(lat1_rad) + bx)
    return {
        "lat": radians_to_degrees(mid_lat),
        "lng": normalize_longitude(radians_to_degrees(mid_lng))
    }


def bounding_box(lat: float, lng: float, radius_km: float) -> dict:
    """Calculate bounding box around a point."""
    R = 6371
    lat_rad = degrees_to_radians(lat)
    d = radius_km / R
    lat_delta = radians_to_degrees(d)
    lng_delta = radians_to_degrees(d / math.cos(lat_rad))
    return {
        "min_lat": lat - lat_delta,
        "max_lat": lat + lat_delta,
        "min_lng": lng - lng_delta,
        "max_lng": lng + lng_delta
    }


def point_in_bounds(lat: float, lng: float, bounds: dict) -> bool:
    """Check if point is within bounding box."""
    return (bounds["min_lat"] <= lat <= bounds["max_lat"] and
            bounds["min_lng"] <= lng <= bounds["max_lng"])


def decimal_to_dms(decimal: float, is_longitude: bool) -> dict:
    """Convert decimal degrees to degrees/minutes/seconds."""
    direction = ""
    if is_longitude:
        direction = "E" if decimal >= 0 else "W"
    else:
        direction = "N" if decimal >= 0 else "S"
    decimal = abs(decimal)
    degrees = int(decimal)
    minutes_decimal = (decimal - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    return {
        "degrees": degrees,
        "minutes": minutes,
        "seconds": round(seconds, 2),
        "direction": direction
    }


def dms_to_decimal(degrees: int, minutes: int, seconds: float, direction: str) -> float:
    """Convert DMS to decimal degrees."""
    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ["S", "W"]:
        decimal = -decimal
    return decimal


def format_coordinate(lat: float, lng: float, format_type: str) -> str:
    """Format coordinate as string."""
    if format_type == "decimal":
        return f"{lat:.6f}, {lng:.6f}"
    elif format_type == "dms":
        lat_dms = decimal_to_dms(lat, False)
        lng_dms = decimal_to_dms(lng, True)
        return (f"{lat_dms['degrees']}°{lat_dms['minutes']}'{lat_dms['seconds']}\"{lat_dms['direction']} "
                f"{lng_dms['degrees']}°{lng_dms['minutes']}'{lng_dms['seconds']}\"{lng_dms['direction']}")
    return ""


def geohash_encode(lat: float, lng: float, precision: int) -> str:
    """Encode coordinate to geohash."""
    BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    lat_range = (-90.0, 90.0)
    lng_range = (-180.0, 180.0)
    hash_str = []
    bits = 0
    char_bits = 0
    is_lng = True
    while len(hash_str) < precision:
        if is_lng:
            mid = (lng_range[0] + lng_range[1]) / 2
            if lng >= mid:
                char_bits = (char_bits << 1) | 1
                lng_range = (mid, lng_range[1])
            else:
                char_bits = char_bits << 1
                lng_range = (lng_range[0], mid)
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat >= mid:
                char_bits = (char_bits << 1) | 1
                lat_range = (mid, lat_range[1])
            else:
                char_bits = char_bits << 1
                lat_range = (lat_range[0], mid)
        is_lng = not is_lng
        bits += 1
        if bits == 5:
            hash_str.append(BASE32[char_bits])
            bits = 0
            char_bits = 0
    return "".join(hash_str)


def compass_direction(bearing: float) -> str:
    """Convert bearing to compass direction."""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(bearing / 22.5) % 16
    return directions[index]
