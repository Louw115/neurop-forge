"""
Transaction Helper Utilities - Pure functions for transaction management patterns.
All functions are pure, deterministic, and atomic.
No actual database connections - just transaction logic helpers.
"""

def generate_begin_transaction() -> str:
    """Generate BEGIN TRANSACTION SQL."""
    return "BEGIN"


def generate_commit() -> str:
    """Generate COMMIT SQL."""
    return "COMMIT"


def generate_rollback() -> str:
    """Generate ROLLBACK SQL."""
    return "ROLLBACK"


def generate_savepoint(name: str) -> str:
    """Generate SAVEPOINT SQL."""
    return f"SAVEPOINT {name}"


def generate_release_savepoint(name: str) -> str:
    """Generate RELEASE SAVEPOINT SQL."""
    return f"RELEASE SAVEPOINT {name}"


def generate_rollback_to_savepoint(name: str) -> str:
    """Generate ROLLBACK TO SAVEPOINT SQL."""
    return f"ROLLBACK TO SAVEPOINT {name}"


def generate_set_transaction_isolation(level: str) -> str:
    """Generate SET TRANSACTION ISOLATION LEVEL SQL."""
    valid_levels = {"READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"}
    normalized = level.upper()
    if normalized not in valid_levels:
        normalized = "READ COMMITTED"
    return f"SET TRANSACTION ISOLATION LEVEL {normalized}"


def generate_set_read_only() -> str:
    """Generate SET TRANSACTION READ ONLY SQL."""
    return "SET TRANSACTION READ ONLY"


def generate_set_read_write() -> str:
    """Generate SET TRANSACTION READ WRITE SQL."""
    return "SET TRANSACTION READ WRITE"


def generate_lock_table(table: str, mode: str) -> str:
    """Generate LOCK TABLE SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    valid_modes = {
        "ACCESS SHARE", "ROW SHARE", "ROW EXCLUSIVE", 
        "SHARE UPDATE EXCLUSIVE", "SHARE", "SHARE ROW EXCLUSIVE",
        "EXCLUSIVE", "ACCESS EXCLUSIVE"
    }
    normalized = mode.upper()
    if normalized not in valid_modes:
        normalized = "ACCESS SHARE"
    return f"LOCK TABLE {escape_sql_identifier(table)} IN {normalized} MODE"


def generate_advisory_lock(key: int) -> str:
    """Generate advisory lock acquisition SQL."""
    return f"SELECT pg_advisory_lock({key})"


def generate_advisory_unlock(key: int) -> str:
    """Generate advisory lock release SQL."""
    return f"SELECT pg_advisory_unlock({key})"


def generate_try_advisory_lock(key: int) -> str:
    """Generate try advisory lock SQL (non-blocking)."""
    return f"SELECT pg_try_advisory_lock({key})"


def generate_advisory_xact_lock(key: int) -> str:
    """Generate advisory transaction lock SQL (auto-released on commit)."""
    return f"SELECT pg_advisory_xact_lock({key})"


def calculate_lock_key(namespace: str, resource_id: str) -> int:
    """Calculate a deterministic lock key from namespace and resource ID."""
    import hashlib
    combined = f"{namespace}:{resource_id}"
    hash_bytes = hashlib.sha256(combined.encode()).digest()
    return int.from_bytes(hash_bytes[:8], 'big') % (2**31)


def is_serializable_isolation(level: str) -> bool:
    """Check if isolation level is SERIALIZABLE."""
    return level.upper() == "SERIALIZABLE"


def is_read_committed_isolation(level: str) -> bool:
    """Check if isolation level is READ COMMITTED."""
    return level.upper() == "READ COMMITTED"


def is_repeatable_read_isolation(level: str) -> bool:
    """Check if isolation level is REPEATABLE READ."""
    return level.upper() == "REPEATABLE READ"


def get_isolation_level_strength(level: str) -> int:
    """Get the strength of an isolation level (0-3, higher is stronger)."""
    levels = {
        "READ UNCOMMITTED": 0,
        "READ COMMITTED": 1,
        "REPEATABLE READ": 2,
        "SERIALIZABLE": 3
    }
    return levels.get(level.upper(), 1)


def compare_isolation_levels(level1: str, level2: str) -> int:
    """Compare isolation levels. Returns -1, 0, or 1."""
    s1 = get_isolation_level_strength(level1)
    s2 = get_isolation_level_strength(level2)
    if s1 < s2:
        return -1
    if s1 > s2:
        return 1
    return 0


def should_retry_serialization_failure(error_code: str) -> bool:
    """Check if an error indicates a serialization failure that should be retried."""
    retry_codes = {"40001", "40P01"}
    return error_code in retry_codes


def calculate_retry_delay(attempt: int, base_delay_ms: int, max_delay_ms: int) -> int:
    """Calculate exponential backoff delay for retry."""
    delay = base_delay_ms * (2 ** attempt)
    return min(delay, max_delay_ms)


def calculate_retry_delay_with_jitter(attempt: int, base_delay_ms: int, max_delay_ms: int, jitter_seed: int) -> int:
    """Calculate exponential backoff delay with deterministic jitter."""
    base = calculate_retry_delay(attempt, base_delay_ms, max_delay_ms)
    import hashlib
    seed_bytes = hashlib.sha256(f"{attempt}:{jitter_seed}".encode()).digest()
    jitter_factor = (int.from_bytes(seed_bytes[:4], 'big') % 100) / 100.0
    jitter = int(base * 0.25 * jitter_factor)
    return base + jitter


def should_continue_retry(attempt: int, max_attempts: int) -> bool:
    """Check if retry should continue."""
    return attempt < max_attempts


def format_deadlock_info(tables: list, operations: list) -> str:
    """Format deadlock information for logging."""
    parts = ["Deadlock detected:"]
    for i, (table, op) in enumerate(zip(tables, operations)):
        parts.append(f"  {i+1}. {op} on {table}")
    return "\n".join(parts)


def generate_select_for_update(table: str, columns: list, where_column: str) -> str:
    """Generate SELECT ... FOR UPDATE SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, build_column_list
    col_list = build_column_list(columns) if columns else "*"
    return f"SELECT {col_list} FROM {escape_sql_identifier(table)} WHERE {escape_sql_identifier(where_column)} = $1 FOR UPDATE"


def generate_select_for_share(table: str, columns: list, where_column: str) -> str:
    """Generate SELECT ... FOR SHARE SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, build_column_list
    col_list = build_column_list(columns) if columns else "*"
    return f"SELECT {col_list} FROM {escape_sql_identifier(table)} WHERE {escape_sql_identifier(where_column)} = $1 FOR SHARE"


def generate_select_for_key_share(table: str, columns: list, where_column: str) -> str:
    """Generate SELECT ... FOR KEY SHARE SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, build_column_list
    col_list = build_column_list(columns) if columns else "*"
    return f"SELECT {col_list} FROM {escape_sql_identifier(table)} WHERE {escape_sql_identifier(where_column)} = $1 FOR KEY SHARE"


def generate_select_for_no_key_update(table: str, columns: list, where_column: str) -> str:
    """Generate SELECT ... FOR NO KEY UPDATE SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, build_column_list
    col_list = build_column_list(columns) if columns else "*"
    return f"SELECT {col_list} FROM {escape_sql_identifier(table)} WHERE {escape_sql_identifier(where_column)} = $1 FOR NO KEY UPDATE"


def wrap_in_savepoint(name: str, sql: str) -> str:
    """Wrap SQL in a savepoint block."""
    return f"{generate_savepoint(name)};\n{sql};\n{generate_release_savepoint(name)};"


def build_transaction_block(statements: list, isolation_level: str) -> str:
    """Build a complete transaction block with statements."""
    parts = [generate_begin_transaction()]
    if isolation_level:
        parts.append(generate_set_transaction_isolation(isolation_level))
    parts.extend(statements)
    parts.append(generate_commit())
    return ";\n".join(parts) + ";"


def is_idempotent_operation(sql: str) -> bool:
    """Check if a SQL operation is idempotent (safe to retry)."""
    sql_upper = sql.upper().strip()
    if sql_upper.startswith("SELECT"):
        return True
    if "IF NOT EXISTS" in sql_upper:
        return True
    if sql_upper.startswith("INSERT") and "ON CONFLICT DO NOTHING" in sql_upper:
        return True
    if sql_upper.startswith("INSERT") and "ON CONFLICT" in sql_upper and "DO UPDATE" in sql_upper:
        return True
    return False


def generate_optimistic_lock_check(version_column: str, expected_version: int) -> str:
    """Generate WHERE clause for optimistic locking."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"AND {escape_sql_identifier(version_column)} = {expected_version}"


def generate_version_increment(version_column: str) -> str:
    """Generate SET clause for incrementing version column."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"{escape_sql_identifier(version_column)} = {escape_sql_identifier(version_column)} + 1"


def is_write_transaction(statements: list) -> bool:
    """Check if any statement in a transaction is a write operation."""
    from neurop_forge.sources.query_helpers import is_mutating_query, is_ddl_query
    return any(is_mutating_query(s) or is_ddl_query(s) for s in statements)


def estimate_transaction_duration(statement_count: int, complexity: str) -> int:
    """Estimate transaction duration in milliseconds."""
    base_per_statement = {"simple": 5, "medium": 20, "complex": 100}
    base = base_per_statement.get(complexity, 20)
    return statement_count * base


def is_long_running_transaction(duration_ms: int, threshold_ms: int) -> bool:
    """Check if a transaction is considered long-running."""
    return duration_ms > threshold_ms


def format_transaction_log(transaction_id: str, statements: list, status: str) -> str:
    """Format a transaction for logging."""
    stmt_count = len(statements)
    return f"Transaction {transaction_id}: {stmt_count} statements, status={status}"


def generate_pg_terminate_backend(pid: int) -> str:
    """Generate SQL to terminate a backend process."""
    return f"SELECT pg_terminate_backend({pid})"


def generate_pg_cancel_backend(pid: int) -> str:
    """Generate SQL to cancel a query on a backend process."""
    return f"SELECT pg_cancel_backend({pid})"


def generate_current_transaction_id() -> str:
    """Generate SQL to get current transaction ID."""
    return "SELECT txid_current()"


def generate_current_timestamp() -> str:
    """Generate SQL to get current timestamp in transaction."""
    return "SELECT CURRENT_TIMESTAMP"


def generate_statement_timeout(ms: int) -> str:
    """Generate SET statement_timeout SQL."""
    return f"SET statement_timeout = {ms}"


def generate_lock_timeout(ms: int) -> str:
    """Generate SET lock_timeout SQL."""
    return f"SET lock_timeout = {ms}"


def generate_idle_in_transaction_timeout(ms: int) -> str:
    """Generate SET idle_in_transaction_session_timeout SQL."""
    return f"SET idle_in_transaction_session_timeout = {ms}"
