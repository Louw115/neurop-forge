"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Job Scheduling Utilities - Pure functions for background job scheduling.
All functions are pure, deterministic, and atomic.
"""

def generate_job_id(prefix: str, timestamp: str, sequence: int) -> str:
    """Generate a unique job ID."""
    import hashlib
    combined = f"{prefix}:{timestamp}:{sequence}"
    hash_part = hashlib.sha256(combined.encode()).hexdigest()[:12]
    return f"job_{hash_part}"


def build_job_definition(job_id: str, job_type: str, payload: dict, priority: int, max_retries: int, timeout_seconds: int) -> dict:
    """Build a job definition."""
    return {
        "id": job_id,
        "type": job_type,
        "payload": payload,
        "priority": priority,
        "max_retries": max_retries,
        "timeout_seconds": timeout_seconds,
        "status": "pending",
        "attempts": 0,
        "created_at": "",
        "scheduled_at": "",
        "started_at": None,
        "completed_at": None
    }


def calculate_next_run_time(last_run: int, interval_seconds: int) -> int:
    """Calculate next run time based on interval."""
    return last_run + interval_seconds


def parse_cron_expression(cron: str) -> dict:
    """Parse a cron expression into components."""
    parts = cron.split()
    if len(parts) != 5:
        return {"valid": False, "error": "Invalid cron format"}
    return {
        "valid": True,
        "minute": parts[0],
        "hour": parts[1],
        "day_of_month": parts[2],
        "month": parts[3],
        "day_of_week": parts[4]
    }


def cron_field_matches(field: str, value: int, min_val: int, max_val: int) -> bool:
    """Check if a cron field matches a value."""
    if field == "*":
        return True
    if field.isdigit():
        return int(field) == value
    if "/" in field:
        base, step = field.split("/", 1)
        if base == "*":
            return value % int(step) == 0
    if "-" in field:
        start, end = field.split("-", 1)
        return int(start) <= value <= int(end)
    if "," in field:
        values = [int(v) for v in field.split(",")]
        return value in values
    return False


def should_run_cron_job(cron: str, minute: int, hour: int, day: int, month: int, weekday: int) -> bool:
    """Check if a cron job should run at the given time."""
    parsed = parse_cron_expression(cron)
    if not parsed.get("valid"):
        return False
    return (
        cron_field_matches(parsed["minute"], minute, 0, 59) and
        cron_field_matches(parsed["hour"], hour, 0, 23) and
        cron_field_matches(parsed["day_of_month"], day, 1, 31) and
        cron_field_matches(parsed["month"], month, 1, 12) and
        cron_field_matches(parsed["day_of_week"], weekday, 0, 6)
    )


def calculate_job_priority_score(base_priority: int, age_seconds: int, retries: int) -> float:
    """Calculate effective job priority considering age and retries."""
    age_boost = min(age_seconds / 3600, 10)
    retry_penalty = retries * 0.5
    return base_priority + age_boost - retry_penalty


def sort_jobs_by_priority(jobs: list) -> list:
    """Sort jobs by priority (highest first)."""
    return sorted(jobs, key=lambda j: j.get("priority", 0), reverse=True)


def get_job_status(job: dict) -> str:
    """Get current job status."""
    return job.get("status", "unknown")


def is_job_runnable(job: dict, current_time: int) -> bool:
    """Check if a job is ready to run."""
    status = get_job_status(job)
    if status not in ("pending", "scheduled", "retry"):
        return False
    scheduled_at = job.get("scheduled_at_timestamp", 0)
    return current_time >= scheduled_at


def is_job_failed(job: dict) -> bool:
    """Check if a job has failed."""
    return get_job_status(job) == "failed"


def is_job_completed(job: dict) -> bool:
    """Check if a job has completed."""
    return get_job_status(job) == "completed"


def should_retry_job(job: dict) -> bool:
    """Check if a failed job should be retried."""
    attempts = job.get("attempts", 0)
    max_retries = job.get("max_retries", 0)
    return attempts < max_retries


def calculate_retry_delay(attempt: int, base_delay: int, max_delay: int, strategy: str) -> int:
    """Calculate retry delay based on strategy."""
    if strategy == "exponential":
        delay = base_delay * (2 ** attempt)
    elif strategy == "linear":
        delay = base_delay * (attempt + 1)
    elif strategy == "constant":
        delay = base_delay
    else:
        delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)


def update_job_status(job: dict, new_status: str, timestamp: str) -> dict:
    """Update job status."""
    result = dict(job)
    result["status"] = new_status
    if new_status == "running":
        result["started_at"] = timestamp
    elif new_status in ("completed", "failed"):
        result["completed_at"] = timestamp
    return result


def increment_job_attempt(job: dict) -> dict:
    """Increment job attempt counter."""
    result = dict(job)
    result["attempts"] = result.get("attempts", 0) + 1
    return result


def calculate_job_duration(started_at: int, completed_at: int) -> int:
    """Calculate job duration in seconds."""
    if started_at and completed_at:
        return completed_at - started_at
    return 0


def is_job_timed_out(job: dict, current_time: int) -> bool:
    """Check if a running job has timed out."""
    if get_job_status(job) != "running":
        return False
    started_at = job.get("started_at_timestamp", 0)
    timeout = job.get("timeout_seconds", 3600)
    return (current_time - started_at) > timeout


def build_job_result(job_id: str, success: bool, output: dict, error: str, duration_seconds: int) -> dict:
    """Build a job result object."""
    return {
        "job_id": job_id,
        "success": success,
        "output": output,
        "error": error,
        "duration_seconds": duration_seconds
    }


def calculate_queue_depth(jobs: list, status: str) -> int:
    """Calculate queue depth for a given status."""
    return sum(1 for j in jobs if j.get("status") == status)


def calculate_queue_metrics(jobs: list) -> dict:
    """Calculate queue metrics from job list."""
    total = len(jobs)
    by_status = {}
    by_type = {}
    for job in jobs:
        status = job.get("status", "unknown")
        job_type = job.get("type", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
        by_type[job_type] = by_type.get(job_type, 0) + 1
    return {
        "total": total,
        "by_status": by_status,
        "by_type": by_type
    }


def estimate_wait_time(queue_depth: int, avg_processing_time: int, workers: int) -> int:
    """Estimate wait time for new job."""
    if workers <= 0:
        return 0
    return (queue_depth * avg_processing_time) // workers


def calculate_throughput(completed_count: int, time_window_seconds: int) -> float:
    """Calculate jobs per second throughput."""
    if time_window_seconds <= 0:
        return 0.0
    return completed_count / time_window_seconds


def build_dead_letter_entry(job: dict, error: str, timestamp: str) -> dict:
    """Build a dead letter queue entry."""
    return {
        "original_job": job,
        "final_error": error,
        "failed_at": timestamp,
        "attempts": job.get("attempts", 0)
    }


def should_move_to_dead_letter(job: dict) -> bool:
    """Check if job should move to dead letter queue."""
    return is_job_failed(job) and not should_retry_job(job)


def format_job_log(job_id: str, status: str, message: str, timestamp: str) -> str:
    """Format a job log entry."""
    return f"[{timestamp}] Job {job_id} - {status}: {message}"


def build_schedule_config(job_type: str, cron: str, payload: dict, enabled: bool) -> dict:
    """Build a scheduled job configuration."""
    return {
        "job_type": job_type,
        "cron": cron,
        "payload": payload,
        "enabled": enabled,
        "last_run": None,
        "next_run": None
    }


def calculate_rate_limit_delay(current_rate: float, max_rate: float) -> int:
    """Calculate delay needed to stay under rate limit."""
    if current_rate <= max_rate:
        return 0
    return int(1000 / max_rate)


def partition_jobs_by_type(jobs: list) -> dict:
    """Partition jobs by type for parallel processing."""
    result = {}
    for job in jobs:
        job_type = job.get("type", "default")
        if job_type not in result:
            result[job_type] = []
        result[job_type].append(job)
    return result


def build_worker_assignment(jobs: list, worker_count: int) -> list:
    """Assign jobs to workers for balanced processing."""
    assignments = [[] for _ in range(worker_count)]
    for i, job in enumerate(jobs):
        worker_idx = i % worker_count
        assignments[worker_idx].append(job)
    return assignments


def calculate_optimal_worker_count(pending_jobs: int, avg_job_duration: int, target_latency: int) -> int:
    """Calculate optimal worker count based on queue and latency target."""
    if avg_job_duration <= 0 or target_latency <= 0:
        return 1
    return max(1, (pending_jobs * avg_job_duration) // target_latency)


def is_worker_idle(last_job_time: int, current_time: int, idle_threshold: int) -> bool:
    """Check if a worker has been idle too long."""
    return (current_time - last_job_time) > idle_threshold


def format_duration_human(seconds: int) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"
