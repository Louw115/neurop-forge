"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Analytics Patterns - Pure functions for analytics and metrics.
All functions are pure, deterministic, and atomic.
"""

def build_event(event_name: str, properties: dict, user_id: str, session_id: str, timestamp: str) -> dict:
    """Build an analytics event."""
    return {
        "event": event_name,
        "properties": properties,
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": timestamp
    }


def build_page_view(page_path: str, page_title: str, referrer: str, user_id: str, timestamp: str) -> dict:
    """Build a page view event."""
    return {
        "event": "page_view",
        "properties": {
            "path": page_path,
            "title": page_title,
            "referrer": referrer
        },
        "user_id": user_id,
        "timestamp": timestamp
    }


def build_conversion_event(conversion_type: str, value: float, currency: str, user_id: str, timestamp: str) -> dict:
    """Build a conversion event."""
    return {
        "event": "conversion",
        "properties": {
            "type": conversion_type,
            "value": value,
            "currency": currency
        },
        "user_id": user_id,
        "timestamp": timestamp
    }


def calculate_session_duration(start_timestamp: int, end_timestamp: int) -> int:
    """Calculate session duration in seconds."""
    return max(0, end_timestamp - start_timestamp)


def calculate_bounce_rate(single_page_sessions: int, total_sessions: int) -> float:
    """Calculate bounce rate percentage."""
    if total_sessions <= 0:
        return 0.0
    return (single_page_sessions / total_sessions) * 100


def calculate_pages_per_session(total_page_views: int, total_sessions: int) -> float:
    """Calculate average pages per session."""
    if total_sessions <= 0:
        return 0.0
    return total_page_views / total_sessions


def calculate_average_session_duration(total_duration_seconds: int, total_sessions: int) -> float:
    """Calculate average session duration in seconds."""
    if total_sessions <= 0:
        return 0.0
    return total_duration_seconds / total_sessions


def calculate_retention_rate(returning_users: int, total_users: int) -> float:
    """Calculate user retention rate percentage."""
    if total_users <= 0:
        return 0.0
    return (returning_users / total_users) * 100


def calculate_churn_rate(churned_users: int, total_users: int) -> float:
    """Calculate user churn rate percentage."""
    if total_users <= 0:
        return 0.0
    return (churned_users / total_users) * 100


def calculate_dau_mau_ratio(daily_active: int, monthly_active: int) -> float:
    """Calculate DAU/MAU ratio (stickiness)."""
    if monthly_active <= 0:
        return 0.0
    return daily_active / monthly_active


def calculate_ltv(average_revenue_per_user: float, average_lifespan_months: float) -> float:
    """Calculate customer lifetime value."""
    return average_revenue_per_user * average_lifespan_months


def calculate_cac(total_acquisition_cost: float, new_customers: int) -> float:
    """Calculate customer acquisition cost."""
    if new_customers <= 0:
        return 0.0
    return total_acquisition_cost / new_customers


def calculate_ltv_cac_ratio(ltv: float, cac: float) -> float:
    """Calculate LTV to CAC ratio."""
    if cac <= 0:
        return 0.0
    return ltv / cac


def calculate_growth_rate(current_value: float, previous_value: float) -> float:
    """Calculate period-over-period growth rate percentage."""
    if previous_value <= 0:
        return 0.0
    return ((current_value - previous_value) / previous_value) * 100


def calculate_cagr(start_value: float, end_value: float, years: int) -> float:
    """Calculate compound annual growth rate."""
    if start_value <= 0 or years <= 0:
        return 0.0
    return ((end_value / start_value) ** (1 / years) - 1) * 100


def group_events_by_date(events: list) -> dict:
    """Group events by date."""
    result = {}
    for event in events:
        date = event.get("timestamp", "")[:10]
        if date not in result:
            result[date] = []
        result[date].append(event)
    return result


def group_events_by_type(events: list) -> dict:
    """Group events by event type."""
    result = {}
    for event in events:
        event_type = event.get("event", "unknown")
        if event_type not in result:
            result[event_type] = []
        result[event_type].append(event)
    return result


def count_events_by_type(events: list) -> dict:
    """Count events by type."""
    result = {}
    for event in events:
        event_type = event.get("event", "unknown")
        result[event_type] = result.get(event_type, 0) + 1
    return result


def count_unique_users(events: list) -> int:
    """Count unique users from events."""
    users = {event.get("user_id") for event in events if event.get("user_id")}
    return len(users)


def calculate_funnel_conversion(steps: list, step_counts: list) -> list:
    """Calculate funnel conversion rates between steps."""
    if len(steps) != len(step_counts) or not step_counts:
        return []
    result = []
    for i, (step, count) in enumerate(zip(steps, step_counts)):
        if i == 0:
            conversion = 100.0
        else:
            prev_count = step_counts[i - 1]
            conversion = (count / prev_count * 100) if prev_count > 0 else 0
        result.append({
            "step": step,
            "count": count,
            "conversion_rate": conversion
        })
    return result


def calculate_funnel_dropoff(step_counts: list) -> list:
    """Calculate dropoff at each funnel step."""
    if len(step_counts) < 2:
        return []
    result = []
    for i in range(1, len(step_counts)):
        dropoff = step_counts[i - 1] - step_counts[i]
        dropoff_rate = (dropoff / step_counts[i - 1] * 100) if step_counts[i - 1] > 0 else 0
        result.append({"step": i, "dropoff": dropoff, "dropoff_rate": dropoff_rate})
    return result


def build_cohort(cohort_id: str, start_date: str, users: list) -> dict:
    """Build a cohort definition."""
    return {
        "cohort_id": cohort_id,
        "start_date": start_date,
        "user_count": len(users),
        "users": users
    }


def calculate_cohort_retention(cohort_users: list, active_users_by_period: list) -> list:
    """Calculate cohort retention over periods."""
    total = len(cohort_users)
    if total <= 0:
        return []
    result = []
    for i, active_count in enumerate(active_users_by_period):
        result.append({
            "period": i,
            "retained": active_count,
            "retention_rate": (active_count / total) * 100
        })
    return result


def calculate_moving_average(values: list, window: int) -> list:
    """Calculate moving average."""
    if window <= 0 or not values:
        return []
    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        window_values = values[start:i + 1]
        result.append(sum(window_values) / len(window_values))
    return result


def detect_anomaly_zscore(value: float, mean: float, std: float, threshold: float) -> bool:
    """Detect if value is an anomaly using z-score."""
    if std == 0:
        return False
    z_score = abs((value - mean) / std)
    return z_score > threshold


def calculate_percentile(values: list, percentile: float) -> float:
    """Calculate percentile value."""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = (percentile / 100) * (len(sorted_values) - 1)
    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = index - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction


def build_metric(name: str, value: float, unit: str, timestamp: str, dimensions: dict) -> dict:
    """Build a metric data point."""
    return {
        "name": name,
        "value": value,
        "unit": unit,
        "timestamp": timestamp,
        "dimensions": dimensions
    }


def aggregate_metrics(metrics: list, aggregation: str) -> float:
    """Aggregate metric values."""
    if not metrics:
        return 0.0
    values = [m.get("value", 0) for m in metrics]
    if aggregation == "sum":
        return sum(values)
    elif aggregation == "avg":
        return sum(values) / len(values)
    elif aggregation == "min":
        return min(values)
    elif aggregation == "max":
        return max(values)
    elif aggregation == "count":
        return len(values)
    return sum(values)


def format_metric_value(value: float, format_type: str) -> str:
    """Format a metric value for display."""
    if format_type == "percent":
        return f"{value:.1f}%"
    elif format_type == "currency":
        return f"${value:,.2f}"
    elif format_type == "number":
        return f"{value:,.0f}"
    elif format_type == "decimal":
        return f"{value:.2f}"
    elif format_type == "duration":
        if value < 60:
            return f"{value:.0f}s"
        elif value < 3600:
            return f"{value/60:.1f}m"
        else:
            return f"{value/3600:.1f}h"
    return str(value)


def compare_periods(current: float, previous: float) -> dict:
    """Compare current vs previous period."""
    change = current - previous
    change_percent = ((change / previous) * 100) if previous != 0 else 0
    trend = "up" if change > 0 else "down" if change < 0 else "flat"
    return {
        "current": current,
        "previous": previous,
        "change": change,
        "change_percent": change_percent,
        "trend": trend
    }
