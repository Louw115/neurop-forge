"""
Batch Operation Utilities - Pure functions for batch database operations.
All functions are pure, deterministic, and atomic.
"""

def calculate_batch_count(total_items: int, batch_size: int) -> int:
    """Calculate the number of batches needed."""
    if batch_size <= 0:
        return 0
    return (total_items + batch_size - 1) // batch_size


def get_batch_range(batch_index: int, batch_size: int, total_items: int) -> tuple:
    """Get the start and end indices for a batch."""
    start = batch_index * batch_size
    end = min(start + batch_size, total_items)
    return (start, end)


def slice_into_batches(items: list, batch_size: int) -> list:
    """Slice a list into batches."""
    if batch_size <= 0:
        return []
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def calculate_optimal_batch_size(item_count: int, max_batch_size: int, target_batches: int) -> int:
    """Calculate optimal batch size to minimize total batches."""
    if item_count <= max_batch_size:
        return item_count
    calculated = (item_count + target_batches - 1) // target_batches
    return min(calculated, max_batch_size)


def estimate_batch_duration_ms(items_per_batch: int, ms_per_item: int, overhead_ms: int) -> int:
    """Estimate duration of processing a single batch."""
    return (items_per_batch * ms_per_item) + overhead_ms


def estimate_total_duration_ms(total_items: int, batch_size: int, ms_per_item: int, overhead_per_batch_ms: int) -> int:
    """Estimate total duration for processing all batches."""
    batch_count = calculate_batch_count(total_items, batch_size)
    return batch_count * estimate_batch_duration_ms(batch_size, ms_per_item, overhead_per_batch_ms)


def build_batch_insert_sql(table: str, columns: list, batch_size: int) -> str:
    """Build a batch INSERT SQL statement."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, build_insert_values_placeholders
    col_list = ", ".join(escape_sql_identifier(c) for c in columns)
    values = build_insert_values_placeholders(len(columns), batch_size)
    return f"INSERT INTO {escape_sql_identifier(table)} ({col_list}) VALUES {values}"


def build_batch_update_sql(table: str, set_columns: list, where_column: str, batch_size: int) -> str:
    """Build batch UPDATE SQL using CASE statements."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    case_parts = []
    placeholder = 1
    for col in set_columns:
        cases = []
        for i in range(batch_size):
            cases.append(f"WHEN ${placeholder} THEN ${placeholder + 1}")
            placeholder += 2
        case_parts.append(f"{escape_sql_identifier(col)} = CASE {escape_sql_identifier(where_column)} {' '.join(cases)} END")
    return f"UPDATE {escape_sql_identifier(table)} SET {', '.join(case_parts)}"


def build_batch_delete_sql(table: str, where_column: str, batch_size: int) -> str:
    """Build batch DELETE SQL with IN clause."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, build_where_in
    where_in = build_where_in(where_column, batch_size, 1)
    return f"DELETE FROM {escape_sql_identifier(table)} {where_in}"


def flatten_batch_values(records: list, columns: list) -> list:
    """Flatten batch records into a single list of values."""
    values = []
    for record in records:
        for col in columns:
            values.append(record.get(col))
    return values


def unflatten_batch_results(flat_values: list, columns: list) -> list:
    """Unflatten a list of values back into records."""
    col_count = len(columns)
    if col_count == 0:
        return []
    records = []
    for i in range(0, len(flat_values), col_count):
        record = dict(zip(columns, flat_values[i:i + col_count]))
        records.append(record)
    return records


def calculate_batch_progress(completed_batches: int, total_batches: int) -> float:
    """Calculate batch processing progress as percentage."""
    if total_batches <= 0:
        return 0.0
    return (completed_batches / total_batches) * 100.0


def format_batch_progress(completed: int, total: int, elapsed_ms: int) -> str:
    """Format batch progress as a status string."""
    progress = calculate_batch_progress(completed, total)
    items_per_sec = (completed * 1000 / elapsed_ms) if elapsed_ms > 0 else 0
    remaining = total - completed
    eta_ms = int(remaining / items_per_sec * 1000) if items_per_sec > 0 else 0
    return f"Progress: {completed}/{total} ({progress:.1f}%) - {items_per_sec:.1f}/sec - ETA: {eta_ms}ms"


def should_continue_batch(current_batch: int, total_batches: int, error_count: int, max_errors: int) -> bool:
    """Determine if batch processing should continue."""
    return current_batch < total_batches and error_count < max_errors


def calculate_error_rate(error_count: int, processed_count: int) -> float:
    """Calculate error rate as percentage."""
    if processed_count <= 0:
        return 0.0
    return (error_count / processed_count) * 100.0


def should_abort_batch(error_rate: float, threshold: float) -> bool:
    """Determine if batch should be aborted due to high error rate."""
    return error_rate >= threshold


def partition_by_key(records: list, key_column: str) -> dict:
    """Partition records by a key column value."""
    result = {}
    for record in records:
        key = record.get(key_column)
        if key not in result:
            result[key] = []
        result[key].append(record)
    return result


def merge_batch_results(batch_results: list) -> dict:
    """Merge multiple batch results into a single summary."""
    total_success = sum(r.get("success_count", 0) for r in batch_results)
    total_errors = sum(r.get("error_count", 0) for r in batch_results)
    total_time = sum(r.get("duration_ms", 0) for r in batch_results)
    return {
        "total_success": total_success,
        "total_errors": total_errors,
        "total_duration_ms": total_time,
        "batch_count": len(batch_results),
        "success_rate": (total_success / (total_success + total_errors) * 100) if (total_success + total_errors) > 0 else 0
    }


def generate_batch_id(prefix: str, timestamp: str, sequence: int) -> str:
    """Generate a unique batch ID."""
    return f"{prefix}_{timestamp}_{sequence:06d}"


def parse_batch_id(batch_id: str) -> dict:
    """Parse a batch ID into components."""
    parts = batch_id.rsplit('_', 2)
    if len(parts) == 3:
        return {
            "prefix": parts[0],
            "timestamp": parts[1],
            "sequence": int(parts[2])
        }
    return {"prefix": batch_id, "timestamp": "", "sequence": 0}


def build_upsert_batch_sql(table: str, columns: list, conflict_columns: list, update_columns: list, batch_size: int) -> str:
    """Build batch UPSERT (INSERT ON CONFLICT UPDATE) SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, build_insert_values_placeholders
    col_list = ", ".join(escape_sql_identifier(c) for c in columns)
    values = build_insert_values_placeholders(len(columns), batch_size)
    conflict_list = ", ".join(escape_sql_identifier(c) for c in conflict_columns)
    updates = ", ".join(f"{escape_sql_identifier(c)} = EXCLUDED.{escape_sql_identifier(c)}" for c in update_columns)
    return f"INSERT INTO {escape_sql_identifier(table)} ({col_list}) VALUES {values} ON CONFLICT ({conflict_list}) DO UPDATE SET {updates}"


def calculate_parallel_batch_count(total_batches: int, max_parallel: int) -> int:
    """Calculate how many batches can run in parallel."""
    return min(total_batches, max_parallel)


def distribute_batches_to_workers(batch_count: int, worker_count: int) -> list:
    """Distribute batches evenly among workers."""
    if worker_count <= 0:
        return []
    batches_per_worker = batch_count // worker_count
    remainder = batch_count % worker_count
    distribution = []
    for i in range(worker_count):
        count = batches_per_worker + (1 if i < remainder else 0)
        distribution.append(count)
    return distribution


def estimate_parallel_duration(total_batches: int, batch_duration_ms: int, worker_count: int) -> int:
    """Estimate duration for parallel batch processing."""
    if worker_count <= 0:
        return 0
    batches_per_worker = calculate_batch_count(total_batches, worker_count)
    return batches_per_worker * batch_duration_ms


def build_copy_from_csv_sql(table: str, columns: list, delimiter: str, null_string: str) -> str:
    """Build COPY FROM SQL for bulk loading CSV data."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    col_list = ", ".join(escape_sql_identifier(c) for c in columns)
    return f"COPY {escape_sql_identifier(table)} ({col_list}) FROM STDIN WITH (FORMAT csv, DELIMITER '{delimiter}', NULL '{null_string}')"


def build_copy_to_csv_sql(table: str, columns: list, delimiter: str) -> str:
    """Build COPY TO SQL for bulk exporting to CSV."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    col_list = ", ".join(escape_sql_identifier(c) for c in columns)
    return f"COPY {escape_sql_identifier(table)} ({col_list}) TO STDOUT WITH (FORMAT csv, DELIMITER '{delimiter}', HEADER true)"


def format_csv_value(value, null_string: str) -> str:
    """Format a value for CSV output."""
    if value is None:
        return null_string
    str_value = str(value)
    if '"' in str_value or ',' in str_value or '\n' in str_value:
        return '"' + str_value.replace('"', '""') + '"'
    return str_value


def format_csv_row(values: list, delimiter: str, null_string: str) -> str:
    """Format a row of values as CSV."""
    return delimiter.join(format_csv_value(v, null_string) for v in values)


def validate_batch_data(records: list, required_columns: list) -> dict:
    """Validate batch data has all required columns."""
    errors = []
    for i, record in enumerate(records):
        missing = [c for c in required_columns if c not in record]
        if missing:
            errors.append({"index": i, "missing_columns": missing})
    return {"valid": len(errors) == 0, "errors": errors}


def deduplicate_batch(records: list, key_column: str) -> list:
    """Remove duplicates from batch, keeping first occurrence."""
    seen = set()
    result = []
    for record in records:
        key = record.get(key_column)
        if key not in seen:
            seen.add(key)
            result.append(record)
    return result


def sort_batch_for_efficiency(records: list, cluster_column: str) -> list:
    """Sort batch records to improve database insert efficiency."""
    return sorted(records, key=lambda r: r.get(cluster_column, ""))


def calculate_memory_usage_estimate(record_count: int, avg_record_size_bytes: int) -> int:
    """Estimate memory usage for batch in bytes."""
    return record_count * avg_record_size_bytes


def should_split_batch(memory_estimate_bytes: int, max_memory_bytes: int) -> bool:
    """Determine if batch should be split due to memory constraints."""
    return memory_estimate_bytes > max_memory_bytes


def calculate_safe_batch_size(avg_record_size_bytes: int, max_memory_bytes: int) -> int:
    """Calculate safe batch size based on memory constraints."""
    if avg_record_size_bytes <= 0:
        return 1000
    return max(1, max_memory_bytes // avg_record_size_bytes)
