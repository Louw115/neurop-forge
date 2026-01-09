"""
Geolocation Utilities - Pure functions for geographic calculations.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import math


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180 / math.pi


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in kilometers."""
    earth_radius_km = 6371.0
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    delta_lat = degrees_to_radians(lat2 - lat1)
    delta_lon = degrees_to_radians(lon2 - lon1)
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius_km * c


def haversine_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in miles."""
    km = haversine_distance(lat1, lon1, lat2, lon2)
    return km * 0.621371


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the initial bearing from point 1 to point 2 in degrees."""
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    delta_lon = degrees_to_radians(lon2 - lon1)
    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    bearing = math.atan2(x, y)
    return (radians_to_degrees(bearing) + 360) % 360


def calculate_midpoint(lat1: float, lon1: float, lat2: float, lon2: float) -> tuple:
    """Calculate the geographic midpoint between two points."""
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    lon1_rad = degrees_to_radians(lon1)
    delta_lon = degrees_to_radians(lon2 - lon1)
    bx = math.cos(lat2_rad) * math.cos(delta_lon)
    by = math.cos(lat2_rad) * math.sin(delta_lon)
    lat_mid = math.atan2(
        math.sin(lat1_rad) + math.sin(lat2_rad),
        math.sqrt((math.cos(lat1_rad) + bx) ** 2 + by ** 2)
    )
    lon_mid = lon1_rad + math.atan2(by, math.cos(lat1_rad) + bx)
    return (radians_to_degrees(lat_mid), radians_to_degrees(lon_mid))


def destination_point(lat: float, lon: float, bearing: float, distance_km: float) -> tuple:
    """Calculate the destination point given start, bearing, and distance."""
    earth_radius_km = 6371.0
    lat_rad = degrees_to_radians(lat)
    lon_rad = degrees_to_radians(lon)
    bearing_rad = degrees_to_radians(bearing)
    angular_distance = distance_km / earth_radius_km
    lat2 = math.asin(
        math.sin(lat_rad) * math.cos(angular_distance) +
        math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
    )
    lon2 = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
        math.cos(angular_distance) - math.sin(lat_rad) * math.sin(lat2)
    )
    return (radians_to_degrees(lat2), radians_to_degrees(lon2))


def is_valid_latitude(lat: float) -> bool:
    """Check if a latitude value is valid (-90 to 90)."""
    return -90 <= lat <= 90


def is_valid_longitude(lon: float) -> bool:
    """Check if a longitude value is valid (-180 to 180)."""
    return -180 <= lon <= 180


def is_valid_coordinate(lat: float, lon: float) -> bool:
    """Check if a coordinate pair is valid."""
    return is_valid_latitude(lat) and is_valid_longitude(lon)


def normalize_longitude(lon: float) -> float:
    """Normalize longitude to -180 to 180 range."""
    while lon > 180:
        lon -= 360
    while lon < -180:
        lon += 360
    return lon


def dms_to_decimal(degrees: float, minutes: float, seconds: float, direction: str) -> float:
    """Convert degrees/minutes/seconds to decimal degrees."""
    decimal = abs(degrees) + minutes / 60 + seconds / 3600
    if direction.upper() in ['S', 'W']:
        decimal = -decimal
    return decimal


def decimal_to_dms(decimal: float) -> tuple:
    """Convert decimal degrees to degrees/minutes/seconds."""
    is_negative = decimal < 0
    decimal = abs(decimal)
    degrees = int(decimal)
    minutes_float = (decimal - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60
    return (degrees if not is_negative else -degrees, minutes, seconds)


def format_dms(decimal: float, is_latitude: bool) -> str:
    """Format decimal degrees as DMS string."""
    d, m, s = decimal_to_dms(decimal)
    direction = ''
    if is_latitude:
        direction = 'N' if d >= 0 else 'S'
    else:
        direction = 'E' if d >= 0 else 'W'
    return f"{abs(d)}°{m}'{s:.2f}\"{direction}"


def calculate_bounding_box(lat: float, lon: float, radius_km: float) -> dict:
    """Calculate a bounding box around a point."""
    earth_radius_km = 6371.0
    lat_delta = radians_to_degrees(radius_km / earth_radius_km)
    lon_delta = radians_to_degrees(radius_km / (earth_radius_km * math.cos(degrees_to_radians(lat))))
    return {
        'min_lat': lat - lat_delta,
        'max_lat': lat + lat_delta,
        'min_lon': normalize_longitude(lon - lon_delta),
        'max_lon': normalize_longitude(lon + lon_delta)
    }


def is_point_in_bounding_box(lat: float, lon: float, bbox: dict) -> bool:
    """Check if a point is within a bounding box."""
    lat_in = bbox['min_lat'] <= lat <= bbox['max_lat']
    if bbox['min_lon'] <= bbox['max_lon']:
        lon_in = bbox['min_lon'] <= lon <= bbox['max_lon']
    else:
        lon_in = lon >= bbox['min_lon'] or lon <= bbox['max_lon']
    return lat_in and lon_in


def calculate_area_of_polygon(coordinates: list) -> float:
    """Calculate the approximate area of a polygon in square kilometers."""
    if len(coordinates) < 3:
        return 0.0
    n = len(coordinates)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        lat1, lon1 = coordinates[i]
        lat2, lon2 = coordinates[j]
        area += degrees_to_radians(lon2 - lon1) * (2 + math.sin(degrees_to_radians(lat1)) + math.sin(degrees_to_radians(lat2)))
    area = abs(area) * 6371.0 ** 2 / 2.0
    return area


def calculate_polygon_centroid(coordinates: list) -> tuple:
    """Calculate the centroid of a polygon."""
    if not coordinates:
        return (0.0, 0.0)
    lat_sum = sum(c[0] for c in coordinates)
    lon_sum = sum(c[1] for c in coordinates)
    n = len(coordinates)
    return (lat_sum / n, lon_sum / n)


def km_to_miles(km: float) -> float:
    """Convert kilometers to miles."""
    return km * 0.621371


def miles_to_km(miles: float) -> float:
    """Convert miles to kilometers."""
    return miles / 0.621371


def km_to_nautical_miles(km: float) -> float:
    """Convert kilometers to nautical miles."""
    return km / 1.852


def nautical_miles_to_km(nm: float) -> float:
    """Convert nautical miles to kilometers."""
    return nm * 1.852


def meters_to_feet(meters: float) -> float:
    """Convert meters to feet."""
    return meters * 3.28084


def feet_to_meters(feet: float) -> float:
    """Convert feet to meters."""
    return feet / 3.28084


def is_northern_hemisphere(lat: float) -> bool:
    """Check if a latitude is in the northern hemisphere."""
    return lat >= 0


def is_southern_hemisphere(lat: float) -> bool:
    """Check if a latitude is in the southern hemisphere."""
    return lat < 0


def is_eastern_hemisphere(lon: float) -> bool:
    """Check if a longitude is in the eastern hemisphere."""
    return 0 <= lon <= 180


def is_western_hemisphere(lon: float) -> bool:
    """Check if a longitude is in the western hemisphere."""
    return -180 <= lon < 0


def get_quadrant(lat: float, lon: float) -> str:
    """Get the geographic quadrant (NE, NW, SE, SW)."""
    ns = 'N' if lat >= 0 else 'S'
    ew = 'E' if lon >= 0 else 'W'
    return ns + ew


def calculate_cross_track_distance(lat: float, lon: float, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> float:
    """Calculate the cross-track distance from a point to a great circle path."""
    earth_radius_km = 6371.0
    d13 = haversine_distance(start_lat, start_lon, lat, lon) / earth_radius_km
    theta13 = degrees_to_radians(calculate_bearing(start_lat, start_lon, lat, lon))
    theta12 = degrees_to_radians(calculate_bearing(start_lat, start_lon, end_lat, end_lon))
    dxt = math.asin(math.sin(d13) * math.sin(theta13 - theta12)) * earth_radius_km
    return abs(dxt)


def calculate_along_track_distance(lat: float, lon: float, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> float:
    """Calculate the along-track distance from start to the closest point on the path."""
    earth_radius_km = 6371.0
    d13 = haversine_distance(start_lat, start_lon, lat, lon) / earth_radius_km
    dxt = calculate_cross_track_distance(lat, lon, start_lat, start_lon, end_lat, end_lon) / earth_radius_km
    dat = math.acos(math.cos(d13) / math.cos(dxt)) * earth_radius_km
    return dat


def interpolate_point(lat1: float, lon1: float, lat2: float, lon2: float, fraction: float) -> tuple:
    """Interpolate a point along the great circle path."""
    if fraction <= 0:
        return (lat1, lon1)
    if fraction >= 1:
        return (lat2, lon2)
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    bearing = calculate_bearing(lat1, lon1, lat2, lon2)
    return destination_point(lat1, lon1, bearing, distance * fraction)


def calculate_total_distance(coordinates: list) -> float:
    """Calculate total distance along a path of coordinates in km."""
    if len(coordinates) < 2:
        return 0.0
    total = 0.0
    for i in range(len(coordinates) - 1):
        lat1, lon1 = coordinates[i]
        lat2, lon2 = coordinates[i + 1]
        total += haversine_distance(lat1, lon1, lat2, lon2)
    return total


def simplify_path(coordinates: list, tolerance_km: float) -> list:
    """Simplify a path using distance-based tolerance."""
    if len(coordinates) <= 2:
        return coordinates
    result = [coordinates[0]]
    for i in range(1, len(coordinates) - 1):
        prev = result[-1]
        curr = coordinates[i]
        distance = haversine_distance(prev[0], prev[1], curr[0], curr[1])
        if distance >= tolerance_km:
            result.append(curr)
    result.append(coordinates[-1])
    return result


def compass_direction(bearing: float) -> str:
    """Convert bearing to compass direction."""
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(bearing / 22.5) % 16
    return directions[index]


def reverse_bearing(bearing: float) -> float:
    """Calculate the reverse bearing."""
    return (bearing + 180) % 360


def format_coordinate(lat: float, lon: float) -> str:
    """Format a coordinate as a string."""
    lat_dir = 'N' if lat >= 0 else 'S'
    lon_dir = 'E' if lon >= 0 else 'W'
    return f"{abs(lat):.6f}°{lat_dir}, {abs(lon):.6f}°{lon_dir}"


def parse_coordinate_string(coord_str: str) -> tuple:
    """Parse a coordinate string like '40.7128°N, 74.0060°W'."""
    import re
    pattern = r'([\d.]+)°?([NS]),?\s*([\d.]+)°?([EW])'
    match = re.search(pattern, coord_str, re.IGNORECASE)
    if not match:
        return (0.0, 0.0)
    lat = float(match.group(1))
    if match.group(2).upper() == 'S':
        lat = -lat
    lon = float(match.group(3))
    if match.group(4).upper() == 'W':
        lon = -lon
    return (lat, lon)


def calculate_spherical_law_of_cosines(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance using spherical law of cosines (less accurate than haversine)."""
    earth_radius_km = 6371.0
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    delta_lon = degrees_to_radians(lon2 - lon1)
    distance = math.acos(
        math.sin(lat1_rad) * math.sin(lat2_rad) +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    ) * earth_radius_km
    return distance


def equirectangular_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate approximate distance using equirectangular projection (fast but less accurate)."""
    earth_radius_km = 6371.0
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    delta_lat = lat2_rad - lat1_rad
    delta_lon = degrees_to_radians(lon2 - lon1) * math.cos((lat1_rad + lat2_rad) / 2)
    return math.sqrt(delta_lat ** 2 + delta_lon ** 2) * earth_radius_km
