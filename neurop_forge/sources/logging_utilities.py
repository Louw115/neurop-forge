"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Logging Utilities - Pure functions for structured logging.
All functions are pure, deterministic, and atomic.
"""

def build_log_entry(level: str, message: str, timestamp: str, context: dict) -> dict:
    """Build a structured log entry."""
    return {
        "level": level.upper(),
        "message": message,
        "timestamp": timestamp,
        "context": context
    }


def build_debug_entry(message: str, timestamp: str, context: dict) -> dict:
    """Build a debug log entry."""
    return build_log_entry("DEBUG", message, timestamp, context)


def build_info_entry(message: str, timestamp: str, context: dict) -> dict:
    """Build an info log entry."""
    return build_log_entry("INFO", message, timestamp, context)


def build_warning_entry(message: str, timestamp: str, context: dict) -> dict:
    """Build a warning log entry."""
    return build_log_entry("WARN", message, timestamp, context)


def build_error_entry(message: str, timestamp: str, error: str, stack_trace: str, context: dict) -> dict:
    """Build an error log entry."""
    entry = build_log_entry("ERROR", message, timestamp, context)
    entry["error"] = error
    entry["stack_trace"] = stack_trace
    return entry


def get_log_level_priority(level: str) -> int:
    """Get numeric priority for log level."""
    priorities = {"TRACE": 0, "DEBUG": 1, "INFO": 2, "WARN": 3, "ERROR": 4, "FATAL": 5}
    return priorities.get(level.upper(), 2)


def should_log(entry_level: str, min_level: str) -> bool:
    """Check if entry should be logged based on minimum level."""
    return get_log_level_priority(entry_level) >= get_log_level_priority(min_level)


def format_log_text(entry: dict) -> str:
    """Format log entry as text."""
    timestamp = entry.get("timestamp", "")
    level = entry.get("level", "INFO")
    message = entry.get("message", "")
    return f"[{timestamp}] {level}: {message}"


def format_log_json(entry: dict) -> str:
    """Format log entry as JSON."""
    import json
    return json.dumps(entry)


def format_log_compact(entry: dict) -> str:
    """Format log entry in compact form."""
    level_chars = {"DEBUG": "D", "INFO": "I", "WARN": "W", "ERROR": "E", "FATAL": "F"}
    level = level_chars.get(entry.get("level", "INFO"), "?")
    time_part = entry.get("timestamp", "")[-8:]
    return f"{time_part} {level} {entry.get('message', '')}"


def add_context_to_entry(entry: dict, additional_context: dict) -> dict:
    """Add context to log entry."""
    result = dict(entry)
    result["context"] = {**entry.get("context", {}), **additional_context}
    return result


def add_request_id(entry: dict, request_id: str) -> dict:
    """Add request ID to log entry."""
    return add_context_to_entry(entry, {"request_id": request_id})


def add_user_id(entry: dict, user_id: str) -> dict:
    """Add user ID to log entry."""
    return add_context_to_entry(entry, {"user_id": user_id})


def add_trace_id(entry: dict, trace_id: str, span_id: str) -> dict:
    """Add distributed tracing IDs to log entry."""
    return add_context_to_entry(entry, {"trace_id": trace_id, "span_id": span_id})


def mask_sensitive_fields(entry: dict, sensitive_fields: list, mask: str) -> dict:
    """Mask sensitive fields in log entry."""
    result = dict(entry)
    context = dict(entry.get("context", {}))
    for field in sensitive_fields:
        if field in context:
            context[field] = mask
    result["context"] = context
    return result


def truncate_log_message(message: str, max_length: int) -> str:
    """Truncate log message if too long."""
    if len(message) <= max_length:
        return message
    return message[:max_length - 3] + "..."


def parse_log_line(line: str) -> dict:
    """Parse a standard log line."""
    import re
    pattern = r'\[([^\]]+)\]\s+(\w+):\s+(.*)'
    match = re.match(pattern, line)
    if match:
        return {
            "timestamp": match.group(1),
            "level": match.group(2),
            "message": match.group(3)
        }
    return {"raw": line}


def filter_logs_by_level(entries: list, min_level: str) -> list:
    """Filter log entries by minimum level."""
    return [e for e in entries if should_log(e.get("level", "INFO"), min_level)]


def filter_logs_by_time(entries: list, start_time: str, end_time: str) -> list:
    """Filter log entries by time range."""
    return [e for e in entries if start_time <= e.get("timestamp", "") <= end_time]


def filter_logs_by_context(entries: list, key: str, value: str) -> list:
    """Filter log entries by context value."""
    return [e for e in entries if e.get("context", {}).get(key) == value]


def count_logs_by_level(entries: list) -> dict:
    """Count log entries by level."""
    counts = {}
    for entry in entries:
        level = entry.get("level", "INFO")
        counts[level] = counts.get(level, 0) + 1
    return counts


def group_logs_by_request(entries: list) -> dict:
    """Group log entries by request ID."""
    groups = {}
    for entry in entries:
        request_id = entry.get("context", {}).get("request_id", "unknown")
        if request_id not in groups:
            groups[request_id] = []
        groups[request_id].append(entry)
    return groups


def extract_error_entries(entries: list) -> list:
    """Extract error and fatal entries."""
    return [e for e in entries if e.get("level") in ["ERROR", "FATAL"]]


def build_log_summary(entries: list) -> dict:
    """Build summary of log entries."""
    level_counts = count_logs_by_level(entries)
    error_count = level_counts.get("ERROR", 0) + level_counts.get("FATAL", 0)
    return {
        "total_entries": len(entries),
        "by_level": level_counts,
        "error_count": error_count,
        "first_timestamp": entries[0].get("timestamp") if entries else None,
        "last_timestamp": entries[-1].get("timestamp") if entries else None
    }


def build_structured_logger_config(min_level: str, format_type: str, output: str) -> dict:
    """Build logger configuration."""
    return {
        "min_level": min_level.upper(),
        "format": format_type,
        "output": output
    }


def calculate_log_rate(entry_count: int, interval_seconds: float) -> float:
    """Calculate log entries per second."""
    if interval_seconds <= 0:
        return 0.0
    return entry_count / interval_seconds


def should_sample_log(sample_rate: float, seed: int) -> bool:
    """Determine if log should be sampled."""
    import hashlib
    hash_val = hashlib.sha256(str(seed).encode()).digest()
    normalized = hash_val[0] / 255.0
    return normalized < sample_rate


def build_correlation_context(trace_id: str, span_id: str, parent_span_id: str) -> dict:
    """Build correlation context for distributed tracing."""
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id
    }
