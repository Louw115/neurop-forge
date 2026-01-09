"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Queue Pattern Utilities - Pure functions for message queue patterns.
All functions are pure, deterministic, and atomic.
"""

def generate_message_id(queue_name: str, timestamp: str, sequence: int) -> str:
    """Generate a unique message ID."""
    import hashlib
    combined = f"{queue_name}:{timestamp}:{sequence}"
    return hashlib.sha256(combined.encode()).hexdigest()[:24]


def build_message(message_id: str, body: dict, headers: dict, timestamp: str, priority: int) -> dict:
    """Build a queue message."""
    return {
        "id": message_id,
        "body": body,
        "headers": headers,
        "timestamp": timestamp,
        "priority": priority,
        "delivery_count": 0,
        "first_delivery": None,
        "last_delivery": None
    }


def get_message_body(message: dict) -> dict:
    """Get message body."""
    return message.get("body", {})


def get_message_headers(message: dict) -> dict:
    """Get message headers."""
    return message.get("headers", {})


def get_message_priority(message: dict) -> int:
    """Get message priority."""
    return message.get("priority", 0)


def increment_delivery_count(message: dict, timestamp: str) -> dict:
    """Increment message delivery count."""
    result = dict(message)
    result["delivery_count"] = result.get("delivery_count", 0) + 1
    if result["first_delivery"] is None:
        result["first_delivery"] = timestamp
    result["last_delivery"] = timestamp
    return result


def is_poison_message(message: dict, max_deliveries: int) -> bool:
    """Check if message is a poison message (exceeded max deliveries)."""
    return message.get("delivery_count", 0) >= max_deliveries


def calculate_visibility_timeout(base_timeout: int, delivery_count: int, max_timeout: int) -> int:
    """Calculate visibility timeout with backoff."""
    timeout = base_timeout * (2 ** delivery_count)
    return min(timeout, max_timeout)


def is_message_visible(message: dict, current_time: int) -> bool:
    """Check if message is visible (not being processed)."""
    invisible_until = message.get("invisible_until", 0)
    return current_time >= invisible_until


def set_message_invisible(message: dict, until_time: int) -> dict:
    """Set message invisibility timeout."""
    result = dict(message)
    result["invisible_until"] = until_time
    return result


def sort_messages_by_priority(messages: list) -> list:
    """Sort messages by priority (highest first) then by timestamp."""
    return sorted(messages, key=lambda m: (-m.get("priority", 0), m.get("timestamp", "")))


def filter_visible_messages(messages: list, current_time: int) -> list:
    """Filter to only visible messages."""
    return [m for m in messages if is_message_visible(m, current_time)]


def calculate_queue_depth(messages: list) -> int:
    """Calculate total queue depth."""
    return len(messages)


def calculate_queue_age(messages: list, current_time: int) -> dict:
    """Calculate queue age statistics."""
    if not messages:
        return {"oldest_seconds": 0, "average_seconds": 0}
    from datetime import datetime
    ages = []
    for m in messages:
        try:
            ts = datetime.fromisoformat(m.get("timestamp", "").replace('Z', '+00:00'))
            age = current_time - int(ts.timestamp())
            ages.append(age)
        except:
            pass
    if not ages:
        return {"oldest_seconds": 0, "average_seconds": 0}
    return {
        "oldest_seconds": max(ages),
        "average_seconds": sum(ages) // len(ages)
    }


def build_dead_letter_message(original: dict, reason: str, timestamp: str) -> dict:
    """Build a dead letter queue message."""
    return {
        "original_message": original,
        "reason": reason,
        "moved_at": timestamp,
        "original_queue": original.get("queue_name", "")
    }


def should_move_to_dlq(message: dict, max_deliveries: int, max_age_seconds: int, message_age: int) -> bool:
    """Determine if message should move to dead letter queue."""
    if is_poison_message(message, max_deliveries):
        return True
    if max_age_seconds > 0 and message_age > max_age_seconds:
        return True
    return False


def build_batch_receive(messages: list, batch_size: int) -> list:
    """Build a batch of messages for receiving."""
    sorted_messages = sort_messages_by_priority(messages)
    return sorted_messages[:batch_size]


def calculate_throughput(processed_count: int, time_window_seconds: int) -> float:
    """Calculate messages per second throughput."""
    if time_window_seconds <= 0:
        return 0.0
    return processed_count / time_window_seconds


def build_queue_metrics(messages: list, processed_count: int, failed_count: int, time_window: int) -> dict:
    """Build queue metrics."""
    return {
        "depth": calculate_queue_depth(messages),
        "throughput": calculate_throughput(processed_count, time_window),
        "processed": processed_count,
        "failed": failed_count,
        "failure_rate": (failed_count / max(processed_count, 1)) * 100
    }


def build_routing_key(parts: list, separator: str) -> str:
    """Build a routing key from parts."""
    return separator.join(parts)


def parse_routing_key(key: str, separator: str) -> list:
    """Parse a routing key into parts."""
    return key.split(separator)


def matches_routing_pattern(key: str, pattern: str, separator: str, wildcard: str, hash_wildcard: str) -> bool:
    """Check if routing key matches a pattern."""
    key_parts = key.split(separator)
    pattern_parts = pattern.split(separator)
    key_idx = 0
    for i, p in enumerate(pattern_parts):
        if p == hash_wildcard:
            return True
        if key_idx >= len(key_parts):
            return False
        if p == wildcard:
            key_idx += 1
        elif p == key_parts[key_idx]:
            key_idx += 1
        else:
            return False
    return key_idx == len(key_parts)


def build_exchange(name: str, exchange_type: str, bindings: list) -> dict:
    """Build an exchange definition."""
    return {
        "name": name,
        "type": exchange_type,
        "bindings": bindings
    }


def route_message_to_queues(routing_key: str, exchange: dict) -> list:
    """Route a message to queues based on exchange bindings."""
    queues = []
    exchange_type = exchange.get("type", "direct")
    for binding in exchange.get("bindings", []):
        pattern = binding.get("pattern", "")
        queue = binding.get("queue", "")
        if exchange_type == "fanout":
            queues.append(queue)
        elif exchange_type == "direct":
            if pattern == routing_key:
                queues.append(queue)
        elif exchange_type == "topic":
            if matches_routing_pattern(routing_key, pattern, ".", "*", "#"):
                queues.append(queue)
    return list(set(queues))


def build_consumer_config(consumer_id: str, queue: str, prefetch_count: int, auto_ack: bool) -> dict:
    """Build a consumer configuration."""
    return {
        "consumer_id": consumer_id,
        "queue": queue,
        "prefetch_count": prefetch_count,
        "auto_ack": auto_ack,
        "status": "active"
    }


def calculate_prefetch_count(avg_processing_time_ms: int, target_latency_ms: int) -> int:
    """Calculate optimal prefetch count."""
    if avg_processing_time_ms <= 0:
        return 1
    return max(1, target_latency_ms // avg_processing_time_ms)


def build_acknowledgment(message_id: str, status: str, timestamp: str) -> dict:
    """Build a message acknowledgment."""
    return {
        "message_id": message_id,
        "status": status,
        "timestamp": timestamp
    }


def is_ack(ack: dict) -> bool:
    """Check if acknowledgment is positive."""
    return ack.get("status") == "ack"


def is_nack(ack: dict) -> bool:
    """Check if acknowledgment is negative."""
    return ack.get("status") == "nack"


def is_reject(ack: dict) -> bool:
    """Check if acknowledgment is reject."""
    return ack.get("status") == "reject"


def calculate_redelivery_delay(attempt: int, base_delay: int, max_delay: int) -> int:
    """Calculate redelivery delay with exponential backoff."""
    delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)


def build_scheduled_message(message: dict, deliver_at: int) -> dict:
    """Build a scheduled/delayed message."""
    result = dict(message)
    result["scheduled_delivery"] = deliver_at
    result["status"] = "scheduled"
    return result


def is_scheduled_ready(message: dict, current_time: int) -> bool:
    """Check if a scheduled message is ready for delivery."""
    scheduled_at = message.get("scheduled_delivery", 0)
    return current_time >= scheduled_at


def filter_ready_scheduled_messages(messages: list, current_time: int) -> list:
    """Filter scheduled messages that are ready for delivery."""
    return [m for m in messages if m.get("status") == "scheduled" and is_scheduled_ready(m, current_time)]


def format_queue_log(queue_name: str, action: str, message_id: str, timestamp: str) -> str:
    """Format a queue log entry."""
    return f"[{timestamp}] Queue {queue_name}: {action} message {message_id}"


def estimate_processing_time(queue_depth: int, throughput: float) -> int:
    """Estimate time to process all messages in seconds."""
    if throughput <= 0:
        return 0
    return int(queue_depth / throughput)
