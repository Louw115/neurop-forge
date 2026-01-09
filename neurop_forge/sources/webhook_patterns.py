"""
Webhook Pattern Utilities - Pure functions for webhook handling.
All functions are pure, deterministic, and atomic.
"""

def generate_webhook_id(prefix: str, timestamp: str, sequence: int) -> str:
    """Generate a unique webhook event ID."""
    import hashlib
    combined = f"{prefix}:{timestamp}:{sequence}"
    hash_part = hashlib.sha256(combined.encode()).hexdigest()[:12]
    return f"wh_{hash_part}"


def generate_webhook_signature(payload: str, secret: str, algorithm: str) -> str:
    """Generate HMAC signature for webhook payload."""
    import hmac
    import hashlib
    if algorithm == "sha256":
        hash_func = hashlib.sha256
    elif algorithm == "sha1":
        hash_func = hashlib.sha1
    else:
        hash_func = hashlib.sha256
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hash_func
    ).hexdigest()
    return signature


def build_signature_header(signature: str, algorithm: str, version: str) -> str:
    """Build a webhook signature header value."""
    if version:
        return f"v{version}={algorithm}={signature}"
    return f"{algorithm}={signature}"


def parse_signature_header(header: str) -> dict:
    """Parse a webhook signature header."""
    result = {"version": "", "algorithm": "", "signature": ""}
    parts = header.split("=")
    if len(parts) == 3:
        result["version"] = parts[0].lstrip("v")
        result["algorithm"] = parts[1]
        result["signature"] = parts[2]
    elif len(parts) == 2:
        result["algorithm"] = parts[0]
        result["signature"] = parts[1]
    return result


def verify_webhook_signature(payload: str, secret: str, expected_signature: str, algorithm: str) -> bool:
    """Verify a webhook signature matches expected."""
    import hmac
    calculated = generate_webhook_signature(payload, secret, algorithm)
    return hmac.compare_digest(calculated, expected_signature)


def build_webhook_payload(event_type: str, event_id: str, timestamp: str, data: dict) -> dict:
    """Build a standard webhook payload."""
    return {
        "id": event_id,
        "type": event_type,
        "created": timestamp,
        "data": data
    }


def build_webhook_envelope(payload: dict, api_version: str, account_id: str) -> dict:
    """Build a webhook envelope with metadata."""
    return {
        "object": "event",
        "api_version": api_version,
        "account": account_id,
        "pending_webhooks": 0,
        **payload
    }


def extract_event_type(payload: dict) -> str:
    """Extract event type from webhook payload."""
    return payload.get("type", "")


def extract_event_id(payload: dict) -> str:
    """Extract event ID from webhook payload."""
    return payload.get("id", "")


def extract_event_data(payload: dict) -> dict:
    """Extract event data from webhook payload."""
    return payload.get("data", {})


def parse_event_type(event_type: str) -> dict:
    """Parse event type into resource and action."""
    parts = event_type.split(".")
    if len(parts) >= 2:
        return {
            "resource": parts[0],
            "action": ".".join(parts[1:])
        }
    return {"resource": event_type, "action": ""}


def build_event_type(resource: str, action: str) -> str:
    """Build an event type from resource and action."""
    return f"{resource}.{action}"


def is_test_event(event_type: str) -> bool:
    """Check if an event is a test/ping event."""
    test_patterns = ["test", "ping", "webhook.test", "webhook.ping"]
    return event_type.lower() in test_patterns


def calculate_retry_delay(attempt: int, base_delay_seconds: int, max_delay_seconds: int) -> int:
    """Calculate exponential backoff delay for webhook retry."""
    delay = base_delay_seconds * (2 ** attempt)
    return min(delay, max_delay_seconds)


def should_retry_webhook(status_code: int, attempt: int, max_attempts: int) -> bool:
    """Determine if webhook should be retried based on response."""
    if attempt >= max_attempts:
        return False
    retriable_codes = {408, 429, 500, 502, 503, 504}
    return status_code in retriable_codes


def calculate_next_retry_timestamp(current_timestamp: int, delay_seconds: int) -> int:
    """Calculate timestamp for next retry attempt."""
    return current_timestamp + delay_seconds


def build_delivery_record(webhook_id: str, endpoint: str, attempt: int, status_code: int, response_body: str, duration_ms: int, timestamp: str) -> dict:
    """Build a webhook delivery attempt record."""
    return {
        "webhook_id": webhook_id,
        "endpoint": endpoint,
        "attempt": attempt,
        "status_code": status_code,
        "response_body": response_body[:1000] if response_body else "",
        "duration_ms": duration_ms,
        "timestamp": timestamp,
        "success": 200 <= status_code < 300
    }


def is_successful_delivery(status_code: int) -> bool:
    """Check if a webhook delivery was successful."""
    return 200 <= status_code < 300


def format_delivery_log(delivery: dict) -> str:
    """Format a delivery record for logging."""
    status = "SUCCESS" if delivery.get("success") else "FAILED"
    return f"[{delivery.get('timestamp')}] {status} - {delivery.get('endpoint')} - {delivery.get('status_code')} ({delivery.get('duration_ms')}ms)"


def calculate_delivery_stats(deliveries: list) -> dict:
    """Calculate delivery statistics from a list of attempts."""
    if not deliveries:
        return {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0.0,
            "avg_duration_ms": 0
        }
    total = len(deliveries)
    successful = sum(1 for d in deliveries if d.get("success"))
    failed = total - successful
    avg_duration = sum(d.get("duration_ms", 0) for d in deliveries) / total
    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / total) * 100,
        "avg_duration_ms": int(avg_duration)
    }


def filter_events_by_type(events: list, event_types: list) -> list:
    """Filter events by allowed event types."""
    if not event_types:
        return events
    type_set = set(event_types)
    return [e for e in events if e.get("type") in type_set]


def filter_events_by_resource(events: list, resource: str) -> list:
    """Filter events by resource type."""
    return [e for e in events if e.get("type", "").startswith(f"{resource}.")]


def build_webhook_endpoint_config(url: str, events: list, secret: str, enabled: bool) -> dict:
    """Build a webhook endpoint configuration."""
    return {
        "url": url,
        "events": events,
        "secret": secret,
        "enabled": enabled,
        "created": "",
        "status": "active" if enabled else "disabled"
    }


def validate_webhook_url(url: str) -> dict:
    """Validate a webhook endpoint URL."""
    issues = []
    if not url:
        issues.append("URL is required")
    elif not url.startswith("https://"):
        if not url.startswith("http://localhost"):
            issues.append("URL must use HTTPS")
    if len(url) > 2048:
        issues.append("URL too long (max 2048 characters)")
    return {"valid": len(issues) == 0, "issues": issues}


def mask_webhook_secret(secret: str) -> str:
    """Mask a webhook secret for display."""
    if len(secret) <= 8:
        return "*" * len(secret)
    return secret[:4] + "*" * (len(secret) - 8) + secret[-4:]


def generate_webhook_secret(length: int, seed: str) -> str:
    """Generate a deterministic webhook secret."""
    import hashlib
    return hashlib.sha256(seed.encode()).hexdigest()[:length]


def build_retry_schedule(max_attempts: int, base_delay: int) -> list:
    """Build a list of retry delays."""
    schedule = []
    for attempt in range(max_attempts):
        delay = calculate_retry_delay(attempt, base_delay, 86400)
        schedule.append({"attempt": attempt + 1, "delay_seconds": delay})
    return schedule


def is_endpoint_healthy(success_count: int, failure_count: int, threshold: float) -> bool:
    """Check if an endpoint is healthy based on success rate."""
    total = success_count + failure_count
    if total == 0:
        return True
    success_rate = success_count / total
    return success_rate >= threshold


def calculate_endpoint_score(success_rate: float, avg_latency_ms: int, max_latency_ms: int) -> float:
    """Calculate an endpoint health score (0-100)."""
    latency_score = max(0, 100 - (avg_latency_ms / max_latency_ms * 100))
    return (success_rate * 70) + (latency_score * 0.3)


def should_disable_endpoint(consecutive_failures: int, threshold: int) -> bool:
    """Check if endpoint should be disabled due to failures."""
    return consecutive_failures >= threshold


def build_webhook_headers(signature: str, signature_header: str, event_id: str, timestamp: str) -> dict:
    """Build standard webhook request headers."""
    return {
        signature_header: signature,
        "X-Webhook-Id": event_id,
        "X-Webhook-Timestamp": timestamp,
        "Content-Type": "application/json"
    }


def parse_webhook_timestamp_header(header: str) -> int:
    """Parse a webhook timestamp header to Unix timestamp."""
    try:
        return int(header)
    except (ValueError, TypeError):
        return 0


def is_webhook_timestamp_valid(timestamp: int, current_time: int, tolerance_seconds: int) -> bool:
    """Check if webhook timestamp is within tolerance (replay protection)."""
    return abs(current_time - timestamp) <= tolerance_seconds


def build_idempotency_key(event_id: str, endpoint: str) -> str:
    """Build an idempotency key for webhook delivery."""
    import hashlib
    combined = f"{event_id}:{endpoint}"
    return hashlib.sha256(combined.encode()).hexdigest()[:32]


def format_event_for_log(event: dict, max_data_length: int) -> str:
    """Format an event for logging (truncate large data)."""
    import json
    event_copy = dict(event)
    if "data" in event_copy:
        data_str = json.dumps(event_copy["data"])
        if len(data_str) > max_data_length:
            event_copy["data"] = f"[truncated: {len(data_str)} chars]"
    return json.dumps(event_copy)
