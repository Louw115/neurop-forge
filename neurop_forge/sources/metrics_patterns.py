"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Metrics Patterns - Pure functions for metrics and monitoring.
All functions are pure, deterministic, and atomic.
"""

def build_counter_metric(name: str, value: int, labels: dict, timestamp: str) -> dict:
    """Build a counter metric."""
    return {
        "type": "counter",
        "name": name,
        "value": value,
        "labels": labels,
        "timestamp": timestamp
    }


def build_gauge_metric(name: str, value: float, labels: dict, timestamp: str) -> dict:
    """Build a gauge metric."""
    return {
        "type": "gauge",
        "name": name,
        "value": value,
        "labels": labels,
        "timestamp": timestamp
    }


def build_histogram_bucket(le: float, count: int) -> dict:
    """Build a histogram bucket."""
    return {"le": le, "count": count}


def build_histogram_metric(name: str, buckets: list, sum_value: float, count: int, labels: dict, timestamp: str) -> dict:
    """Build a histogram metric."""
    return {
        "type": "histogram",
        "name": name,
        "buckets": buckets,
        "sum": sum_value,
        "count": count,
        "labels": labels,
        "timestamp": timestamp
    }


def build_summary_metric(name: str, quantiles: dict, sum_value: float, count: int, labels: dict, timestamp: str) -> dict:
    """Build a summary metric."""
    return {
        "type": "summary",
        "name": name,
        "quantiles": quantiles,
        "sum": sum_value,
        "count": count,
        "labels": labels,
        "timestamp": timestamp
    }


def increment_counter(current_value: int, increment: int) -> int:
    """Increment a counter value."""
    return current_value + increment


def set_gauge(new_value: float) -> float:
    """Set a gauge value."""
    return new_value


def add_to_histogram(buckets: list, value: float) -> list:
    """Add a value to histogram buckets."""
    result = []
    for bucket in buckets:
        new_count = bucket["count"] + (1 if value <= bucket["le"] else 0)
        result.append({"le": bucket["le"], "count": new_count})
    return result


def create_histogram_buckets(boundaries: list) -> list:
    """Create histogram buckets from boundaries."""
    buckets = [{"le": b, "count": 0} for b in boundaries]
    buckets.append({"le": float("inf"), "count": 0})
    return buckets


def calculate_histogram_percentile(buckets: list, total_count: int, percentile: float) -> float:
    """Calculate percentile from histogram buckets."""
    if total_count <= 0:
        return 0.0
    target = percentile * total_count / 100
    for i, bucket in enumerate(buckets):
        if bucket["count"] >= target:
            if i == 0:
                return bucket["le"]
            prev_count = buckets[i - 1]["count"] if i > 0 else 0
            prev_le = buckets[i - 1]["le"] if i > 0 else 0
            ratio = (target - prev_count) / (bucket["count"] - prev_count) if bucket["count"] > prev_count else 0
            return prev_le + ratio * (bucket["le"] - prev_le)
    return buckets[-1]["le"] if buckets else 0.0


def format_prometheus_counter(metric: dict) -> str:
    """Format counter metric in Prometheus format."""
    labels_str = ",".join(f'{k}="{v}"' for k, v in metric.get("labels", {}).items())
    name = metric["name"]
    if labels_str:
        return f'{name}{{{labels_str}}} {metric["value"]}'
    return f'{name} {metric["value"]}'


def format_prometheus_gauge(metric: dict) -> str:
    """Format gauge metric in Prometheus format."""
    return format_prometheus_counter(metric)


def format_prometheus_histogram(metric: dict) -> str:
    """Format histogram metric in Prometheus format."""
    lines = []
    name = metric["name"]
    labels_str = ",".join(f'{k}="{v}"' for k, v in metric.get("labels", {}).items())
    for bucket in metric["buckets"]:
        le = bucket["le"]
        le_str = "+Inf" if le == float("inf") else str(le)
        if labels_str:
            lines.append(f'{name}_bucket{{{labels_str},le="{le_str}"}} {bucket["count"]}')
        else:
            lines.append(f'{name}_bucket{{le="{le_str}"}} {bucket["count"]}')
    if labels_str:
        lines.append(f'{name}_sum{{{labels_str}}} {metric["sum"]}')
        lines.append(f'{name}_count{{{labels_str}}} {metric["count"]}')
    else:
        lines.append(f'{name}_sum {metric["sum"]}')
        lines.append(f'{name}_count {metric["count"]}')
    return "\n".join(lines)


def calculate_rate(current_value: int, previous_value: int, interval_seconds: float) -> float:
    """Calculate rate per second."""
    if interval_seconds <= 0:
        return 0.0
    return (current_value - previous_value) / interval_seconds


def calculate_increase(current_value: int, previous_value: int) -> int:
    """Calculate increase in counter."""
    return max(0, current_value - previous_value)


def calculate_sla_uptime(uptime_seconds: int, total_seconds: int) -> float:
    """Calculate SLA uptime percentage."""
    if total_seconds <= 0:
        return 100.0
    return (uptime_seconds / total_seconds) * 100


def calculate_error_rate(error_count: int, total_count: int) -> float:
    """Calculate error rate percentage."""
    if total_count <= 0:
        return 0.0
    return (error_count / total_count) * 100


def calculate_success_rate(success_count: int, total_count: int) -> float:
    """Calculate success rate percentage."""
    if total_count <= 0:
        return 0.0
    return (success_count / total_count) * 100


def calculate_throughput(request_count: int, interval_seconds: float) -> float:
    """Calculate throughput (requests per second)."""
    if interval_seconds <= 0:
        return 0.0
    return request_count / interval_seconds


def calculate_latency_percentiles(latencies: list) -> dict:
    """Calculate common latency percentiles."""
    if not latencies:
        return {"p50": 0, "p90": 0, "p95": 0, "p99": 0}
    sorted_latencies = sorted(latencies)
    n = len(sorted_latencies)
    return {
        "p50": sorted_latencies[int(n * 0.50)],
        "p90": sorted_latencies[int(n * 0.90)],
        "p95": sorted_latencies[int(n * 0.95)],
        "p99": sorted_latencies[min(int(n * 0.99), n - 1)]
    }


def is_within_sla(actual_value: float, sla_target: float, comparison: str) -> bool:
    """Check if metric is within SLA."""
    if comparison == "below":
        return actual_value < sla_target
    elif comparison == "above":
        return actual_value > sla_target
    elif comparison == "equals":
        return abs(actual_value - sla_target) < 0.001
    return False


def build_alert_rule(name: str, metric_name: str, threshold: float, comparison: str, duration_seconds: int) -> dict:
    """Build an alert rule definition."""
    return {
        "name": name,
        "metric": metric_name,
        "threshold": threshold,
        "comparison": comparison,
        "duration": duration_seconds,
        "status": "inactive"
    }


def evaluate_alert_rule(rule: dict, current_value: float) -> bool:
    """Evaluate if alert rule is triggered."""
    threshold = rule["threshold"]
    comparison = rule["comparison"]
    if comparison == "above":
        return current_value > threshold
    elif comparison == "below":
        return current_value < threshold
    elif comparison == "equals":
        return abs(current_value - threshold) < 0.001
    return False


def build_metric_aggregation(values: list) -> dict:
    """Build metric aggregation summary."""
    if not values:
        return {"count": 0, "sum": 0, "min": 0, "max": 0, "avg": 0}
    return {
        "count": len(values),
        "sum": sum(values),
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values)
    }


def downsample_metrics(metrics: list, target_count: int) -> list:
    """Downsample metrics to target count."""
    if len(metrics) <= target_count:
        return metrics
    step = len(metrics) / target_count
    return [metrics[int(i * step)] for i in range(target_count)]
