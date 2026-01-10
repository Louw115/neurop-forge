"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Vector Utilities - Pure functions for vector operations.
All functions are pure, deterministic, and atomic.
"""

def create_vector(values: list) -> dict:
    """Create a vector."""
    return {"values": list(values), "dimension": len(values)}


def vector_add(v1: dict, v2: dict) -> dict:
    """Add two vectors."""
    values = [a + b for a, b in zip(v1["values"], v2["values"])]
    return create_vector(values)


def vector_subtract(v1: dict, v2: dict) -> dict:
    """Subtract two vectors."""
    values = [a - b for a, b in zip(v1["values"], v2["values"])]
    return create_vector(values)


def vector_scale(v: dict, scalar: float) -> dict:
    """Scale a vector by a scalar."""
    values = [x * scalar for x in v["values"]]
    return create_vector(values)


def vector_dot_product(v1: dict, v2: dict) -> float:
    """Calculate dot product of two vectors."""
    return sum(a * b for a, b in zip(v1["values"], v2["values"]))


def vector_magnitude(v: dict) -> float:
    """Calculate magnitude (length) of a vector."""
    return sum(x ** 2 for x in v["values"]) ** 0.5


def vector_normalize(v: dict) -> dict:
    """Normalize a vector to unit length."""
    mag = vector_magnitude(v)
    if mag == 0:
        return v
    return vector_scale(v, 1 / mag)


def vector_distance(v1: dict, v2: dict) -> float:
    """Calculate Euclidean distance between two vectors."""
    diff = vector_subtract(v1, v2)
    return vector_magnitude(diff)


def vector_cosine_similarity(v1: dict, v2: dict) -> float:
    """Calculate cosine similarity between two vectors."""
    dot = vector_dot_product(v1, v2)
    mag1 = vector_magnitude(v1)
    mag2 = vector_magnitude(v2)
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def vector_manhattan_distance(v1: dict, v2: dict) -> float:
    """Calculate Manhattan distance between two vectors."""
    return sum(abs(a - b) for a, b in zip(v1["values"], v2["values"]))


def vector_cross_product_3d(v1: dict, v2: dict) -> dict:
    """Calculate cross product of two 3D vectors."""
    a = v1["values"]
    b = v2["values"]
    return create_vector([
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ])


def vector_angle(v1: dict, v2: dict) -> float:
    """Calculate angle between two vectors in radians."""
    import math
    cos_sim = vector_cosine_similarity(v1, v2)
    return math.acos(max(-1, min(1, cos_sim)))


def vector_project(v: dict, onto: dict) -> dict:
    """Project vector onto another vector."""
    dot = vector_dot_product(v, onto)
    onto_mag_sq = sum(x ** 2 for x in onto["values"])
    if onto_mag_sq == 0:
        return create_vector([0] * v["dimension"])
    return vector_scale(onto, dot / onto_mag_sq)


def vector_reflect(v: dict, normal: dict) -> dict:
    """Reflect vector over a normal."""
    projection = vector_project(v, normal)
    scaled = vector_scale(projection, 2)
    return vector_subtract(v, scaled)


def vector_lerp(v1: dict, v2: dict, t: float) -> dict:
    """Linear interpolation between two vectors."""
    values = [a + (b - a) * t for a, b in zip(v1["values"], v2["values"])]
    return create_vector(values)


def vector_element_wise_multiply(v1: dict, v2: dict) -> dict:
    """Element-wise multiplication of two vectors."""
    values = [a * b for a, b in zip(v1["values"], v2["values"])]
    return create_vector(values)


def vector_element_wise_divide(v1: dict, v2: dict) -> dict:
    """Element-wise division of two vectors."""
    values = [a / b if b != 0 else 0 for a, b in zip(v1["values"], v2["values"])]
    return create_vector(values)


def vector_min(v1: dict, v2: dict) -> dict:
    """Element-wise minimum of two vectors."""
    values = [min(a, b) for a, b in zip(v1["values"], v2["values"])]
    return create_vector(values)


def vector_max(v1: dict, v2: dict) -> dict:
    """Element-wise maximum of two vectors."""
    values = [max(a, b) for a, b in zip(v1["values"], v2["values"])]
    return create_vector(values)


def vector_clamp(v: dict, min_val: float, max_val: float) -> dict:
    """Clamp vector values to range."""
    values = [max(min_val, min(max_val, x)) for x in v["values"]]
    return create_vector(values)


def vector_abs(v: dict) -> dict:
    """Absolute value of vector elements."""
    values = [abs(x) for x in v["values"]]
    return create_vector(values)


def vector_sum(v: dict) -> float:
    """Sum of vector elements."""
    return sum(v["values"])


def vector_mean(v: dict) -> float:
    """Mean of vector elements."""
    return vector_sum(v) / v["dimension"] if v["dimension"] > 0 else 0


def vector_variance(v: dict) -> float:
    """Variance of vector elements."""
    mean = vector_mean(v)
    return sum((x - mean) ** 2 for x in v["values"]) / v["dimension"] if v["dimension"] > 0 else 0


def vector_std_dev(v: dict) -> float:
    """Standard deviation of vector elements."""
    return vector_variance(v) ** 0.5


def vector_min_element(v: dict) -> float:
    """Minimum element in vector."""
    return min(v["values"]) if v["values"] else 0


def vector_max_element(v: dict) -> float:
    """Maximum element in vector."""
    return max(v["values"]) if v["values"] else 0


def vector_argmin(v: dict) -> int:
    """Index of minimum element."""
    return v["values"].index(min(v["values"])) if v["values"] else -1


def vector_argmax(v: dict) -> int:
    """Index of maximum element."""
    return v["values"].index(max(v["values"])) if v["values"] else -1


def vector_zero(dimension: int) -> dict:
    """Create a zero vector."""
    return create_vector([0] * dimension)


def vector_ones(dimension: int) -> dict:
    """Create a vector of ones."""
    return create_vector([1] * dimension)


def vector_random(dimension: int, seed: int) -> dict:
    """Create a deterministic pseudo-random vector."""
    import hashlib
    values = []
    for i in range(dimension):
        h = hashlib.sha256(f"{seed}:{i}".encode()).digest()
        values.append((int.from_bytes(h[:4], 'big') / 0xFFFFFFFF) * 2 - 1)
    return create_vector(values)


def vector_equals(v1: dict, v2: dict, tolerance: float) -> bool:
    """Check if two vectors are equal within tolerance."""
    if v1["dimension"] != v2["dimension"]:
        return False
    return all(abs(a - b) <= tolerance for a, b in zip(v1["values"], v2["values"]))
