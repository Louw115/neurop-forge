"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Event Sourcing Utilities - Pure functions for event sourcing patterns.
All functions are pure, deterministic, and atomic.
"""

def generate_event_id(stream_id: str, sequence: int, timestamp: str) -> str:
    """Generate a unique event ID."""
    import hashlib
    combined = f"{stream_id}:{sequence}:{timestamp}"
    return hashlib.sha256(combined.encode()).hexdigest()[:24]


def build_event(event_type: str, stream_id: str, sequence: int, data: dict, metadata: dict, timestamp: str) -> dict:
    """Build an event record."""
    return {
        "id": generate_event_id(stream_id, sequence, timestamp),
        "type": event_type,
        "stream_id": stream_id,
        "sequence": sequence,
        "data": data,
        "metadata": metadata,
        "timestamp": timestamp
    }


def get_event_type(event: dict) -> str:
    """Get the type of an event."""
    return event.get("type", "")


def get_event_data(event: dict) -> dict:
    """Get the data payload of an event."""
    return event.get("data", {})


def get_event_sequence(event: dict) -> int:
    """Get the sequence number of an event."""
    return event.get("sequence", 0)


def get_stream_id(event: dict) -> str:
    """Get the stream ID of an event."""
    return event.get("stream_id", "")


def filter_events_by_type(events: list, event_types: list) -> list:
    """Filter events by type."""
    if not event_types:
        return events
    type_set = set(event_types)
    return [e for e in events if e.get("type") in type_set]


def filter_events_by_stream(events: list, stream_id: str) -> list:
    """Filter events by stream ID."""
    return [e for e in events if e.get("stream_id") == stream_id]


def filter_events_by_time_range(events: list, start_time: str, end_time: str) -> list:
    """Filter events by time range."""
    return [e for e in events if start_time <= e.get("timestamp", "") <= end_time]


def get_latest_event(events: list) -> dict:
    """Get the latest event by sequence."""
    if not events:
        return {}
    return max(events, key=lambda e: e.get("sequence", 0))


def get_events_after_sequence(events: list, after_sequence: int) -> list:
    """Get events after a specific sequence number."""
    return [e for e in events if e.get("sequence", 0) > after_sequence]


def calculate_next_sequence(events: list) -> int:
    """Calculate the next sequence number."""
    if not events:
        return 1
    max_seq = max(e.get("sequence", 0) for e in events)
    return max_seq + 1


def validate_event_sequence(events: list) -> dict:
    """Validate that events have contiguous sequence numbers."""
    sorted_events = sorted(events, key=lambda e: e.get("sequence", 0))
    gaps = []
    for i in range(1, len(sorted_events)):
        prev_seq = sorted_events[i - 1].get("sequence", 0)
        curr_seq = sorted_events[i].get("sequence", 0)
        if curr_seq != prev_seq + 1:
            gaps.append({"expected": prev_seq + 1, "found": curr_seq})
    return {"valid": len(gaps) == 0, "gaps": gaps}


def build_snapshot(stream_id: str, state: dict, last_sequence: int, timestamp: str) -> dict:
    """Build a snapshot record."""
    return {
        "stream_id": stream_id,
        "state": state,
        "last_sequence": last_sequence,
        "timestamp": timestamp
    }


def should_create_snapshot(event_count: int, snapshot_interval: int) -> bool:
    """Determine if a snapshot should be created."""
    return event_count > 0 and event_count % snapshot_interval == 0


def get_events_since_snapshot(events: list, snapshot_sequence: int) -> list:
    """Get events that occurred after a snapshot."""
    return [e for e in events if e.get("sequence", 0) > snapshot_sequence]


def rebuild_state_from_events(events: list, initial_state: dict, reducer_name: str) -> dict:
    """Rebuild state by replaying events (basic implementation)."""
    state = dict(initial_state)
    for event in sorted(events, key=lambda e: e.get("sequence", 0)):
        event_type = event.get("type", "")
        event_data = event.get("data", {})
        state = apply_event_to_state(state, event_type, event_data)
    return state


def apply_event_to_state(state: dict, event_type: str, event_data: dict) -> dict:
    """Apply an event to state (generic handler)."""
    result = dict(state)
    if event_type.endswith("_created"):
        result.update(event_data)
    elif event_type.endswith("_updated"):
        result.update(event_data)
    elif event_type.endswith("_deleted"):
        result["deleted"] = True
    else:
        result.update(event_data)
    result["last_event_type"] = event_type
    return result


def build_event_handler_map(handlers: dict) -> dict:
    """Build an event handler mapping."""
    return {event_type: handler for event_type, handler in handlers.items()}


def get_aggregate_version(events: list) -> int:
    """Get aggregate version (last event sequence)."""
    if not events:
        return 0
    return max(e.get("sequence", 0) for e in events)


def check_optimistic_concurrency(expected_version: int, current_version: int) -> dict:
    """Check for optimistic concurrency conflict."""
    if expected_version != current_version:
        return {
            "valid": False,
            "error": f"Concurrency conflict: expected version {expected_version}, got {current_version}"
        }
    return {"valid": True, "error": None}


def build_command(command_type: str, aggregate_id: str, payload: dict, metadata: dict) -> dict:
    """Build a command object."""
    return {
        "type": command_type,
        "aggregate_id": aggregate_id,
        "payload": payload,
        "metadata": metadata
    }


def extract_events_from_command_result(result: dict) -> list:
    """Extract events from a command result."""
    return result.get("events", [])


def build_projection(projection_name: str, event_types: list, initial_state: dict) -> dict:
    """Build a projection definition."""
    return {
        "name": projection_name,
        "event_types": event_types,
        "state": initial_state,
        "last_processed_sequence": 0
    }


def update_projection_state(projection: dict, new_state: dict, last_sequence: int) -> dict:
    """Update projection with new state."""
    result = dict(projection)
    result["state"] = new_state
    result["last_processed_sequence"] = last_sequence
    return result


def should_projection_handle_event(projection: dict, event: dict) -> bool:
    """Check if projection should handle an event."""
    event_types = projection.get("event_types", [])
    if not event_types:
        return True
    return event.get("type") in event_types


def calculate_event_store_size(events: list) -> dict:
    """Calculate event store statistics."""
    import json
    total_events = len(events)
    by_type = {}
    by_stream = {}
    total_size = 0
    for event in events:
        event_type = event.get("type", "unknown")
        stream_id = event.get("stream_id", "unknown")
        by_type[event_type] = by_type.get(event_type, 0) + 1
        by_stream[stream_id] = by_stream.get(stream_id, 0) + 1
        total_size += len(json.dumps(event))
    return {
        "total_events": total_events,
        "by_type": by_type,
        "by_stream": by_stream,
        "total_size_bytes": total_size
    }


def format_event_log(event: dict) -> str:
    """Format an event for logging."""
    return f"[{event.get('timestamp', '')}] {event.get('stream_id', '')} #{event.get('sequence', 0)}: {event.get('type', '')}"


def build_subscription(subscription_id: str, event_types: list, from_sequence: int) -> dict:
    """Build an event subscription."""
    return {
        "id": subscription_id,
        "event_types": event_types,
        "from_sequence": from_sequence,
        "last_processed": from_sequence,
        "status": "active"
    }


def get_subscription_events(events: list, subscription: dict) -> list:
    """Get events for a subscription."""
    from_seq = subscription.get("last_processed", 0)
    event_types = subscription.get("event_types", [])
    filtered = get_events_after_sequence(events, from_seq)
    if event_types:
        filtered = filter_events_by_type(filtered, event_types)
    return filtered


def update_subscription_position(subscription: dict, last_processed: int) -> dict:
    """Update subscription position."""
    result = dict(subscription)
    result["last_processed"] = last_processed
    return result


def estimate_replay_time(event_count: int, events_per_second: int) -> int:
    """Estimate time to replay events in seconds."""
    if events_per_second <= 0:
        return 0
    return event_count // events_per_second


def partition_events_for_parallel_replay(events: list, partition_count: int) -> list:
    """Partition events by stream for parallel replay."""
    by_stream = {}
    for event in events:
        stream_id = event.get("stream_id", "default")
        if stream_id not in by_stream:
            by_stream[stream_id] = []
        by_stream[stream_id].append(event)
    streams = list(by_stream.values())
    partitions = [[] for _ in range(partition_count)]
    for i, stream_events in enumerate(streams):
        partitions[i % partition_count].extend(stream_events)
    return partitions
