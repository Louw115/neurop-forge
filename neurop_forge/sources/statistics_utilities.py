"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Statistics Utilities - Pure functions for statistical calculations.
All functions are pure, deterministic, and atomic.
"""

def calculate_mean(values: list) -> float:
    """Calculate arithmetic mean."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def calculate_median(values: list) -> float:
    """Calculate median."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    return sorted_vals[mid]


def calculate_mode(values: list) -> list:
    """Calculate mode(s)."""
    if not values:
        return []
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    max_count = max(counts.values())
    return [k for k, c in counts.items() if c == max_count]


def calculate_variance(values: list, sample: bool) -> float:
    """Calculate variance."""
    if len(values) < 2:
        return 0.0
    mean = calculate_mean(values)
    squared_diff = sum((x - mean) ** 2 for x in values)
    divisor = len(values) - 1 if sample else len(values)
    return squared_diff / divisor


def calculate_std_dev(values: list, sample: bool) -> float:
    """Calculate standard deviation."""
    return calculate_variance(values, sample) ** 0.5


def calculate_range(values: list) -> float:
    """Calculate range."""
    if not values:
        return 0.0
    return max(values) - min(values)


def calculate_iqr(values: list) -> float:
    """Calculate interquartile range."""
    if len(values) < 4:
        return 0.0
    sorted_vals = sorted(values)
    q1 = calculate_percentile(sorted_vals, 25)
    q3 = calculate_percentile(sorted_vals, 75)
    return q3 - q1


def calculate_percentile(values: list, percentile: float) -> float:
    """Calculate percentile."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = (len(sorted_vals) - 1) * percentile / 100
    lower = int(idx)
    upper = lower + 1
    if upper >= len(sorted_vals):
        return sorted_vals[-1]
    weight = idx - lower
    return sorted_vals[lower] * (1 - weight) + sorted_vals[upper] * weight


def calculate_quartiles(values: list) -> dict:
    """Calculate quartiles."""
    return {
        "q1": calculate_percentile(values, 25),
        "q2": calculate_percentile(values, 50),
        "q3": calculate_percentile(values, 75)
    }


def calculate_skewness(values: list) -> float:
    """Calculate skewness."""
    if len(values) < 3:
        return 0.0
    mean = calculate_mean(values)
    std = calculate_std_dev(values, True)
    if std == 0:
        return 0.0
    n = len(values)
    skew = sum(((x - mean) / std) ** 3 for x in values)
    return skew * n / ((n - 1) * (n - 2))


def calculate_kurtosis(values: list) -> float:
    """Calculate kurtosis."""
    if len(values) < 4:
        return 0.0
    mean = calculate_mean(values)
    std = calculate_std_dev(values, True)
    if std == 0:
        return 0.0
    n = len(values)
    kurt = sum(((x - mean) / std) ** 4 for x in values)
    return (n * (n + 1) * kurt - 3 * (n - 1) ** 2) / ((n - 1) * (n - 2) * (n - 3))


def calculate_covariance(x: list, y: list, sample: bool) -> float:
    """Calculate covariance."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)
    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    divisor = len(x) - 1 if sample else len(x)
    return cov / divisor


def calculate_correlation(x: list, y: list) -> float:
    """Calculate Pearson correlation coefficient."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    cov = calculate_covariance(x, y, True)
    std_x = calculate_std_dev(x, True)
    std_y = calculate_std_dev(y, True)
    if std_x == 0 or std_y == 0:
        return 0.0
    return cov / (std_x * std_y)


def calculate_z_score(value: float, mean: float, std: float) -> float:
    """Calculate z-score."""
    if std == 0:
        return 0.0
    return (value - mean) / std


def calculate_z_scores(values: list) -> list:
    """Calculate z-scores for all values."""
    mean = calculate_mean(values)
    std = calculate_std_dev(values, True)
    return [calculate_z_score(v, mean, std) for v in values]


def identify_outliers_iqr(values: list, multiplier: float) -> list:
    """Identify outliers using IQR method."""
    if len(values) < 4:
        return []
    q1 = calculate_percentile(values, 25)
    q3 = calculate_percentile(values, 75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return [(i, v) for i, v in enumerate(values) if v < lower or v > upper]


def identify_outliers_zscore(values: list, threshold: float) -> list:
    """Identify outliers using z-score method."""
    z_scores = calculate_z_scores(values)
    return [(i, v) for i, (v, z) in enumerate(zip(values, z_scores)) if abs(z) > threshold]


def calculate_weighted_mean(values: list, weights: list) -> float:
    """Calculate weighted mean."""
    if not values or len(values) != len(weights):
        return 0.0
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / total_weight


def calculate_geometric_mean(values: list) -> float:
    """Calculate geometric mean."""
    if not values or any(v <= 0 for v in values):
        return 0.0
    product = 1
    for v in values:
        product *= v
    return product ** (1 / len(values))


def calculate_harmonic_mean(values: list) -> float:
    """Calculate harmonic mean."""
    if not values or any(v <= 0 for v in values):
        return 0.0
    return len(values) / sum(1 / v for v in values)


def build_histogram(values: list, num_bins: int) -> list:
    """Build histogram bins."""
    if not values or num_bins <= 0:
        return []
    min_val = min(values)
    max_val = max(values)
    bin_width = (max_val - min_val) / num_bins
    bins = [{"min": min_val + i * bin_width, "max": min_val + (i + 1) * bin_width, "count": 0} for i in range(num_bins)]
    for v in values:
        bin_idx = min(int((v - min_val) / bin_width), num_bins - 1)
        bins[bin_idx]["count"] += 1
    return bins


def calculate_linear_regression(x: list, y: list) -> dict:
    """Calculate simple linear regression."""
    if len(x) != len(y) or len(x) < 2:
        return {"slope": 0, "intercept": 0, "r_squared": 0}
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denominator = sum((xi - mean_x) ** 2 for xi in x)
    if denominator == 0:
        return {"slope": 0, "intercept": mean_y, "r_squared": 0}
    slope = numerator / denominator
    intercept = mean_y - slope * mean_x
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    ss_tot = sum((yi - mean_y) ** 2 for yi in y)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    return {"slope": slope, "intercept": intercept, "r_squared": r_squared}


def build_summary_statistics(values: list) -> dict:
    """Build summary statistics."""
    return {
        "count": len(values),
        "mean": calculate_mean(values),
        "median": calculate_median(values),
        "std_dev": calculate_std_dev(values, True),
        "variance": calculate_variance(values, True),
        "min": min(values) if values else 0,
        "max": max(values) if values else 0,
        "range": calculate_range(values),
        "quartiles": calculate_quartiles(values)
    }
