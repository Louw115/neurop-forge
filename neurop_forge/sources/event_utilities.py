"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Event Utilities - Pure functions for event handling patterns.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def create_event(event_type: str, payload: dict, timestamp: int) -> dict:
    """Create an event."""
    return {
        "type": event_type,
        "payload": payload,
        "timestamp": timestamp,
        "id": generate_event_id(event_type, timestamp)
    }


def generate_event_id(event_type: str, timestamp: int) -> str:
    """Generate unique event ID."""
    data = f"{event_type}-{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def is_valid_event(event: dict) -> bool:
    """Validate event structure."""
    required = ["type", "payload", "timestamp"]
    return all(key in event for key in required)


def filter_events_by_type(events: list, event_type: str) -> list:
    """Filter events by type."""
    return [e for e in events if e.get("type") == event_type]


def filter_events_by_time_range(events: list, start: int, end: int) -> list:
    """Filter events by time range."""
    return [e for e in events if start <= e.get("timestamp", 0) <= end]


def sort_events_chronologically(events: list, ascending: bool) -> list:
    """Sort events by timestamp."""
    return sorted(events, key=lambda e: e.get("timestamp", 0), reverse=not ascending)


def group_events_by_type(events: list) -> dict:
    """Group events by type."""
    groups = {}
    for event in events:
        event_type = event.get("type", "unknown")
        if event_type not in groups:
            groups[event_type] = []
        groups[event_type].append(event)
    return groups


def count_events_by_type(events: list) -> dict:
    """Count events by type."""
    counts = {}
    for event in events:
        event_type = event.get("type", "unknown")
        counts[event_type] = counts.get(event_type, 0) + 1
    return counts


def get_latest_event(events: list) -> dict:
    """Get most recent event."""
    if not events:
        return None
    return max(events, key=lambda e: e.get("timestamp", 0))


def get_first_event(events: list) -> dict:
    """Get earliest event."""
    if not events:
        return None
    return min(events, key=lambda e: e.get("timestamp", 0))


def aggregate_events(events: list, window_size: int) -> list:
    """Aggregate events into time windows."""
    if not events:
        return []
    sorted_events = sort_events_chronologically(events, True)
    windows = []
    current_window = {"start": sorted_events[0]["timestamp"], "events": []}
    for event in sorted_events:
        if event["timestamp"] - current_window["start"] < window_size:
            current_window["events"].append(event)
        else:
            current_window["end"] = current_window["start"] + window_size
            current_window["count"] = len(current_window["events"])
            windows.append(current_window)
            current_window = {"start": event["timestamp"], "events": [event]}
    if current_window["events"]:
        current_window["end"] = current_window["start"] + window_size
        current_window["count"] = len(current_window["events"])
        windows.append(current_window)
    return windows


def deduplicate_events(events: list) -> list:
    """Remove duplicate events by ID."""
    seen = set()
    result = []
    for event in events:
        event_id = event.get("id")
        if event_id not in seen:
            seen.add(event_id)
            result.append(event)
    return result


def merge_events(events1: list, events2: list) -> list:
    """Merge two event lists."""
    merged = events1 + events2
    return deduplicate_events(sort_events_chronologically(merged, True))


def transform_event(event: dict, transformer) -> dict:
    """Transform event payload."""
    return {
        **event,
        "payload": transformer(event.get("payload", {}))
    }


def enrich_event(event: dict, additional_data: dict) -> dict:
    """Enrich event with additional data."""
    return {
        **event,
        "payload": {**event.get("payload", {}), **additional_data}
    }


def create_event_envelope(event: dict, source: str, version: str) -> dict:
    """Wrap event in envelope."""
    return {
        "source": source,
        "version": version,
        "event": event,
        "envelope_id": generate_event_id(f"{source}-{version}", event.get("timestamp", 0))
    }


def unwrap_envelope(envelope: dict) -> dict:
    """Extract event from envelope."""
    return envelope.get("event", {})


def is_event_in_sequence(event: dict, sequence: list) -> bool:
    """Check if event belongs to sequence."""
    return event.get("id") in [e.get("id") for e in sequence]


def get_event_rate(events: list, window_seconds: int) -> float:
    """Calculate event rate per second."""
    if len(events) < 2:
        return 0
    sorted_events = sort_events_chronologically(events, True)
    time_span = sorted_events[-1]["timestamp"] - sorted_events[0]["timestamp"]
    if time_span == 0:
        return len(events)
    return len(events) / time_span


def detect_event_burst(events: list, threshold: int, window: int) -> list:
    """Detect event bursts."""
    windows = aggregate_events(events, window)
    return [w for w in windows if w["count"] >= threshold]


def create_correlation_id(events: list) -> str:
    """Create correlation ID for event chain."""
    event_ids = "-".join(e.get("id", "") for e in events)
    return hashlib.sha256(event_ids.encode()).hexdigest()[:16]


def add_causation(event: dict, cause_event_id: str) -> dict:
    """Add causation link to event."""
    return {**event, "caused_by": cause_event_id}


def get_event_chain(events: list, start_id: str) -> list:
    """Get chain of causally linked events."""
    events_by_cause = {e.get("caused_by"): e for e in events if "caused_by" in e}
    chain = []
    current_id = start_id
    while current_id:
        for event in events:
            if event.get("id") == current_id:
                chain.append(event)
                current_id = events_by_cause.get(current_id, {}).get("id")
                break
        else:
            break
    return chain
