"""
Audit Logging Utilities - Pure functions for database audit logging patterns.
All functions are pure, deterministic, and atomic.
"""

def generate_audit_id(timestamp: str, table: str, operation: str, sequence: int) -> str:
    """Generate a unique audit log ID."""
    import hashlib
    combined = f"{timestamp}:{table}:{operation}:{sequence}"
    hash_part = hashlib.sha256(combined.encode()).hexdigest()[:8]
    return f"audit_{hash_part}"


def build_audit_record(table: str, operation: str, record_id: str, user_id: str, timestamp: str, old_values: dict, new_values: dict) -> dict:
    """Build an audit record dictionary."""
    return {
        "table_name": table,
        "operation": operation,
        "record_id": record_id,
        "user_id": user_id,
        "timestamp": timestamp,
        "old_values": old_values,
        "new_values": new_values
    }


def detect_field_changes(old_record: dict, new_record: dict) -> dict:
    """Detect which fields changed between old and new record."""
    changes = {}
    all_keys = set(old_record.keys()) | set(new_record.keys())
    for key in all_keys:
        old_val = old_record.get(key)
        new_val = new_record.get(key)
        if old_val != new_val:
            changes[key] = {"old": old_val, "new": new_val}
    return changes


def format_operation_type(operation: str) -> str:
    """Format operation type to standard form."""
    op_map = {
        "insert": "INSERT",
        "create": "INSERT",
        "update": "UPDATE",
        "modify": "UPDATE",
        "delete": "DELETE",
        "remove": "DELETE",
        "select": "SELECT",
        "read": "SELECT"
    }
    return op_map.get(operation.lower(), operation.upper())


def is_sensitive_field(field_name: str, sensitive_patterns: list) -> bool:
    """Check if a field name matches sensitive patterns."""
    field_lower = field_name.lower()
    for pattern in sensitive_patterns:
        if pattern.lower() in field_lower:
            return True
    return False


def mask_sensitive_values(record: dict, sensitive_fields: list) -> dict:
    """Mask sensitive field values in a record for audit logging."""
    result = dict(record)
    for field in sensitive_fields:
        if field in result and result[field] is not None:
            result[field] = "***REDACTED***"
    return result


def auto_detect_sensitive_fields(record: dict) -> list:
    """Auto-detect potentially sensitive fields in a record."""
    sensitive_patterns = [
        "password", "secret", "token", "key", "credential",
        "ssn", "social_security", "credit_card", "card_number",
        "cvv", "pin", "auth", "api_key", "private"
    ]
    sensitive = []
    for field in record.keys():
        if is_sensitive_field(field, sensitive_patterns):
            sensitive.append(field)
    return sensitive


def build_audit_insert_sql(audit_table: str) -> str:
    """Build SQL for inserting audit records."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    columns = ["table_name", "operation", "record_id", "user_id", "timestamp", "old_values", "new_values"]
    col_list = ", ".join(escape_sql_identifier(c) for c in columns)
    placeholders = ", ".join(f"${i+1}" for i in range(len(columns)))
    return f"INSERT INTO {escape_sql_identifier(audit_table)} ({col_list}) VALUES ({placeholders})"


def build_audit_query_sql(audit_table: str, table_filter: str, operation_filter: str, limit: int) -> str:
    """Build SQL for querying audit records."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    sql = f"SELECT * FROM {escape_sql_identifier(audit_table)} WHERE 1=1"
    placeholder = 1
    if table_filter:
        sql += f" AND table_name = ${placeholder}"
        placeholder += 1
    if operation_filter:
        sql += f" AND operation = ${placeholder}"
        placeholder += 1
    sql += " ORDER BY timestamp DESC"
    if limit > 0:
        sql += f" LIMIT {limit}"
    return sql


def build_audit_trigger_function(function_name: str, audit_table: str) -> str:
    """Build a PostgreSQL trigger function for automatic auditing."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"""
CREATE OR REPLACE FUNCTION {escape_sql_identifier(function_name)}()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO {escape_sql_identifier(audit_table)} (table_name, operation, record_id, new_values, timestamp)
        VALUES (TG_TABLE_NAME, 'INSERT', NEW.id::text, to_jsonb(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO {escape_sql_identifier(audit_table)} (table_name, operation, record_id, old_values, new_values, timestamp)
        VALUES (TG_TABLE_NAME, 'UPDATE', NEW.id::text, to_jsonb(OLD), to_jsonb(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO {escape_sql_identifier(audit_table)} (table_name, operation, record_id, old_values, timestamp)
        VALUES (TG_TABLE_NAME, 'DELETE', OLD.id::text, to_jsonb(OLD), CURRENT_TIMESTAMP);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
"""


def build_audit_trigger(trigger_name: str, table: str, function_name: str) -> str:
    """Build a CREATE TRIGGER statement for auditing."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"""
CREATE TRIGGER {escape_sql_identifier(trigger_name)}
AFTER INSERT OR UPDATE OR DELETE ON {escape_sql_identifier(table)}
FOR EACH ROW EXECUTE FUNCTION {escape_sql_identifier(function_name)}();
"""


def calculate_retention_cutoff(current_timestamp: str, retention_days: int) -> str:
    """Calculate the cutoff timestamp for audit retention."""
    from datetime import datetime, timedelta
    dt = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
    cutoff = dt - timedelta(days=retention_days)
    return cutoff.isoformat()


def build_audit_cleanup_sql(audit_table: str, retention_days: int) -> str:
    """Build SQL to clean up old audit records."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"""
DELETE FROM {escape_sql_identifier(audit_table)}
WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '{retention_days} days'
"""


def summarize_changes(changes: dict) -> str:
    """Summarize changes as a human-readable string."""
    if not changes:
        return "No changes"
    parts = []
    for field, change in changes.items():
        parts.append(f"{field}: {change.get('old')} -> {change.get('new')}")
    return "; ".join(parts)


def count_changes(changes: dict) -> int:
    """Count the number of field changes."""
    return len(changes)


def is_significant_change(old_value, new_value, threshold: float) -> bool:
    """Check if a numeric change is significant (exceeds threshold percentage)."""
    if not isinstance(old_value, (int, float)) or not isinstance(new_value, (int, float)):
        return old_value != new_value
    if old_value == 0:
        return new_value != 0
    change_percent = abs((new_value - old_value) / old_value) * 100
    return change_percent >= threshold


def filter_audit_by_operation(audit_records: list, operation: str) -> list:
    """Filter audit records by operation type."""
    return [r for r in audit_records if r.get("operation") == operation]


def filter_audit_by_user(audit_records: list, user_id: str) -> list:
    """Filter audit records by user ID."""
    return [r for r in audit_records if r.get("user_id") == user_id]


def filter_audit_by_date_range(audit_records: list, start_date: str, end_date: str) -> list:
    """Filter audit records by date range."""
    return [r for r in audit_records if start_date <= r.get("timestamp", "") <= end_date]


def group_audit_by_record(audit_records: list) -> dict:
    """Group audit records by record ID."""
    result = {}
    for record in audit_records:
        record_id = record.get("record_id")
        if record_id not in result:
            result[record_id] = []
        result[record_id].append(record)
    return result


def reconstruct_record_at_time(audit_records: list, target_timestamp: str) -> dict:
    """Reconstruct a record's state at a specific time using audit trail."""
    sorted_records = sorted(audit_records, key=lambda r: r.get("timestamp", ""))
    current_state = {}
    for record in sorted_records:
        if record.get("timestamp", "") > target_timestamp:
            break
        operation = record.get("operation")
        if operation == "INSERT":
            current_state = dict(record.get("new_values", {}))
        elif operation == "UPDATE":
            current_state.update(record.get("new_values", {}))
        elif operation == "DELETE":
            current_state = {}
    return current_state


def calculate_audit_statistics(audit_records: list) -> dict:
    """Calculate statistics from audit records."""
    total = len(audit_records)
    by_operation = {}
    by_table = {}
    by_user = {}
    for record in audit_records:
        op = record.get("operation", "UNKNOWN")
        table = record.get("table_name", "UNKNOWN")
        user = record.get("user_id", "UNKNOWN")
        by_operation[op] = by_operation.get(op, 0) + 1
        by_table[table] = by_table.get(table, 0) + 1
        by_user[user] = by_user.get(user, 0) + 1
    return {
        "total_records": total,
        "by_operation": by_operation,
        "by_table": by_table,
        "by_user": by_user
    }


def format_audit_entry(record: dict) -> str:
    """Format an audit entry for display."""
    timestamp = record.get("timestamp", "")
    user = record.get("user_id", "system")
    operation = record.get("operation", "UNKNOWN")
    table = record.get("table_name", "unknown")
    record_id = record.get("record_id", "")
    return f"[{timestamp}] {user} {operation} {table}#{record_id}"


def detect_suspicious_activity(audit_records: list, threshold_per_minute: int) -> list:
    """Detect potentially suspicious activity patterns."""
    by_user_minute = {}
    suspicious = []
    for record in audit_records:
        user = record.get("user_id", "")
        timestamp = record.get("timestamp", "")[:16]
        key = f"{user}:{timestamp}"
        by_user_minute[key] = by_user_minute.get(key, 0) + 1
    for key, count in by_user_minute.items():
        if count > threshold_per_minute:
            user, minute = key.split(":")
            suspicious.append({"user_id": user, "minute": minute, "count": count})
    return suspicious


def generate_compliance_report(audit_records: list, table: str, start_date: str, end_date: str) -> dict:
    """Generate a compliance report from audit records."""
    filtered = [r for r in audit_records 
                if r.get("table_name") == table 
                and start_date <= r.get("timestamp", "") <= end_date]
    stats = calculate_audit_statistics(filtered)
    return {
        "report_type": "compliance_audit",
        "table": table,
        "period_start": start_date,
        "period_end": end_date,
        "statistics": stats,
        "record_count": len(filtered)
    }
