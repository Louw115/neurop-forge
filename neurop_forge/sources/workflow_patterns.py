"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Workflow Patterns - Pure functions for business workflow logic.
All functions are pure, deterministic, and atomic.
"""

def build_workflow_step(step_id: str, name: str, action: str, next_step: str, conditions: list) -> dict:
    """Build a workflow step definition."""
    return {
        "id": step_id,
        "name": name,
        "action": action,
        "next_step": next_step,
        "conditions": conditions,
        "status": "pending"
    }


def build_workflow(workflow_id: str, name: str, steps: list, initial_step: str) -> dict:
    """Build a complete workflow definition."""
    return {
        "id": workflow_id,
        "name": name,
        "steps": {step["id"]: step for step in steps},
        "initial_step": initial_step,
        "current_step": None,
        "status": "not_started",
        "history": []
    }


def start_workflow(workflow: dict, timestamp: str) -> dict:
    """Start a workflow execution."""
    result = dict(workflow)
    result["current_step"] = workflow["initial_step"]
    result["status"] = "in_progress"
    result["started_at"] = timestamp
    result["history"] = [{"action": "started", "timestamp": timestamp}]
    return result


def advance_workflow(workflow: dict, next_step: str, timestamp: str, metadata: dict) -> dict:
    """Advance workflow to next step."""
    result = dict(workflow)
    result["history"] = list(workflow.get("history", []))
    result["history"].append({
        "action": "advanced",
        "from_step": workflow.get("current_step"),
        "to_step": next_step,
        "timestamp": timestamp,
        "metadata": metadata
    })
    result["current_step"] = next_step
    return result


def complete_workflow(workflow: dict, timestamp: str, outcome: str) -> dict:
    """Complete a workflow."""
    result = dict(workflow)
    result["status"] = "completed"
    result["completed_at"] = timestamp
    result["outcome"] = outcome
    result["history"] = list(workflow.get("history", []))
    result["history"].append({"action": "completed", "outcome": outcome, "timestamp": timestamp})
    return result


def cancel_workflow(workflow: dict, timestamp: str, reason: str) -> dict:
    """Cancel a workflow."""
    result = dict(workflow)
    result["status"] = "cancelled"
    result["cancelled_at"] = timestamp
    result["cancellation_reason"] = reason
    result["history"] = list(workflow.get("history", []))
    result["history"].append({"action": "cancelled", "reason": reason, "timestamp": timestamp})
    return result


def evaluate_condition(condition: dict, context: dict) -> bool:
    """Evaluate a workflow condition."""
    field = condition.get("field")
    operator = condition.get("operator")
    value = condition.get("value")
    actual = context.get(field)
    if operator == "equals":
        return actual == value
    elif operator == "not_equals":
        return actual != value
    elif operator == "greater_than":
        return actual > value
    elif operator == "less_than":
        return actual < value
    elif operator == "contains":
        return value in actual if actual else False
    elif operator == "in":
        return actual in value if value else False
    return False


def evaluate_all_conditions(conditions: list, context: dict) -> bool:
    """Evaluate all conditions (AND logic)."""
    return all(evaluate_condition(c, context) for c in conditions)


def evaluate_any_conditions(conditions: list, context: dict) -> bool:
    """Evaluate any condition (OR logic)."""
    return any(evaluate_condition(c, context) for c in conditions)


def get_next_step(workflow: dict, context: dict) -> str:
    """Determine next step based on conditions."""
    current = workflow["steps"].get(workflow.get("current_step"))
    if not current:
        return None
    for condition_group in current.get("conditions", []):
        if evaluate_all_conditions(condition_group.get("when", []), context):
            return condition_group.get("then")
    return current.get("next_step")


def is_workflow_complete(workflow: dict) -> bool:
    """Check if workflow is complete."""
    return workflow.get("status") in ["completed", "cancelled"]


def calculate_workflow_progress(workflow: dict) -> float:
    """Calculate workflow progress percentage."""
    total_steps = len(workflow.get("steps", {}))
    if total_steps == 0:
        return 0.0
    completed_steps = len([h for h in workflow.get("history", []) if h.get("action") == "advanced"])
    return min(100.0, (completed_steps / total_steps) * 100)


def get_workflow_duration(workflow: dict) -> int:
    """Get workflow duration in seconds."""
    from datetime import datetime
    started = workflow.get("started_at")
    ended = workflow.get("completed_at") or workflow.get("cancelled_at")
    if not started:
        return 0
    start_dt = datetime.fromisoformat(started.replace('Z', '+00:00'))
    if ended:
        end_dt = datetime.fromisoformat(ended.replace('Z', '+00:00'))
    else:
        return 0
    return int((end_dt - start_dt).total_seconds())


def build_approval_step(step_id: str, approvers: list, min_approvals: int, timeout_hours: int) -> dict:
    """Build an approval workflow step."""
    return {
        "id": step_id,
        "type": "approval",
        "approvers": approvers,
        "min_approvals": min_approvals,
        "timeout_hours": timeout_hours,
        "approvals": [],
        "rejections": []
    }


def add_approval(step: dict, approver: str, timestamp: str, comment: str) -> dict:
    """Add an approval to a step."""
    result = dict(step)
    result["approvals"] = list(step.get("approvals", []))
    result["approvals"].append({"approver": approver, "timestamp": timestamp, "comment": comment})
    return result


def add_rejection(step: dict, rejector: str, timestamp: str, reason: str) -> dict:
    """Add a rejection to a step."""
    result = dict(step)
    result["rejections"] = list(step.get("rejections", []))
    result["rejections"].append({"rejector": rejector, "timestamp": timestamp, "reason": reason})
    return result


def is_approval_complete(step: dict) -> bool:
    """Check if approval step has enough approvals."""
    return len(step.get("approvals", [])) >= step.get("min_approvals", 1)


def is_approval_rejected(step: dict) -> bool:
    """Check if approval step has been rejected."""
    return len(step.get("rejections", [])) > 0


def build_parallel_step(step_id: str, branches: list, join_type: str) -> dict:
    """Build a parallel workflow step."""
    return {
        "id": step_id,
        "type": "parallel",
        "branches": branches,
        "join_type": join_type,
        "branch_statuses": {b: "pending" for b in branches}
    }


def update_branch_status(step: dict, branch_id: str, status: str) -> dict:
    """Update status of a parallel branch."""
    result = dict(step)
    result["branch_statuses"] = dict(step.get("branch_statuses", {}))
    result["branch_statuses"][branch_id] = status
    return result


def is_parallel_step_complete(step: dict) -> bool:
    """Check if parallel step is complete based on join type."""
    statuses = step.get("branch_statuses", {})
    join_type = step.get("join_type", "all")
    if join_type == "all":
        return all(s == "completed" for s in statuses.values())
    elif join_type == "any":
        return any(s == "completed" for s in statuses.values())
    return False


def build_timer_step(step_id: str, delay_seconds: int, next_step: str) -> dict:
    """Build a timer/delay workflow step."""
    return {
        "id": step_id,
        "type": "timer",
        "delay_seconds": delay_seconds,
        "next_step": next_step,
        "scheduled_at": None,
        "fired": False
    }


def schedule_timer(step: dict, start_timestamp: str) -> dict:
    """Schedule a timer step."""
    from datetime import datetime, timedelta
    start = datetime.fromisoformat(start_timestamp.replace('Z', '+00:00'))
    fire_at = start + timedelta(seconds=step.get("delay_seconds", 0))
    result = dict(step)
    result["scheduled_at"] = fire_at.isoformat()
    return result


def is_timer_ready(step: dict, current_timestamp: str) -> bool:
    """Check if timer is ready to fire."""
    scheduled = step.get("scheduled_at")
    if not scheduled:
        return False
    return current_timestamp >= scheduled


def build_workflow_summary(workflow: dict) -> dict:
    """Build a summary of workflow execution."""
    return {
        "id": workflow.get("id"),
        "name": workflow.get("name"),
        "status": workflow.get("status"),
        "current_step": workflow.get("current_step"),
        "progress": calculate_workflow_progress(workflow),
        "duration_seconds": get_workflow_duration(workflow),
        "step_count": len(workflow.get("steps", {})),
        "history_count": len(workflow.get("history", []))
    }
